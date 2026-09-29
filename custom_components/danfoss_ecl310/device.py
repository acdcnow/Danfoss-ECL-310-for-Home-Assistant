"""Danfoss ECL 310 device layer.

This module owns everything that knows how the controller is wired: which
register holds what, how a word is decoded, and how to read a group of
registers in as few Modbus requests as possible.

It deliberately knows nothing about Home Assistant. It receives a ``ModbusUnit``
handed out by the ``modbus`` integration and returns plain values, which makes
it testable against the ``modbus_connection`` mock backend with no Home
Assistant and no hardware in the loop.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
import logging
from typing import TYPE_CHECKING, Any

from modbus_connection import ModbusError

from .const import MAX_BLOCK_LENGTH

if TYPE_CHECKING:
    from modbus_connection import ModbusUnit

_LOGGER = logging.getLogger(__name__)

#: Register spaces the ECL 310 is read from.
INPUT = "input"
HOLDING = "holding"


@dataclass(frozen=True, slots=True)
class RegisterRef:
    """A single register this integration cares about."""

    key: str
    address: int
    space: str
    signed: bool = False


def decode_signed(word: int) -> int:
    """Decode a raw register as a two's-complement int16."""
    return word - 0x10000 if word > 0x7FFF else word


def encode_signed(value: int) -> int:
    """Encode a negative value as a two's-complement register word."""
    return value + 0x10000 if value < 0 else value


def build_register_refs(
    configs: Iterable[Mapping[str, Any]], *, keys: Iterable[str] | None = None
) -> list[RegisterRef]:
    """Turn declarative sensor configs into register references.

    ``keys`` limits the result to the named registers.
    """
    wanted = None if keys is None else set(keys)
    return [
        RegisterRef(
            key=config["key"],
            address=config["addr"],
            space=config.get("type", HOLDING),
            signed=bool(config.get("signed", False)),
        )
        for config in configs
        if wanted is None or config["key"] in wanted
    ]


def plan_block_reads(
    refs: Iterable[RegisterRef],
) -> list[tuple[str, int, list[RegisterRef]]]:
    """Group references into contiguous runs.

    The controller answers one request at a time, so reading five neighbouring
    registers as one block instead of five requests cuts a poll cycle
    substantially. Runs never cross a register space and never exceed
    :data:`~.const.MAX_BLOCK_LENGTH` registers.
    """
    blocks: list[tuple[str, int, list[RegisterRef]]] = []
    for space in (INPUT, HOLDING):
        ordered = sorted(
            (ref for ref in refs if ref.space == space), key=lambda ref: ref.address
        )
        current: list[RegisterRef] = []
        for ref in ordered:
            if current and (
                ref.address != current[-1].address + 1
                or len(current) >= MAX_BLOCK_LENGTH
            ):
                blocks.append((space, current[0].address, current))
                current = []
            current.append(ref)
        if current:
            blocks.append((space, current[0].address, current))
    return blocks


class DanfossEcl310:
    """The controller as seen over one Modbus unit.

    Every read and write raises :class:`~modbus_connection.ModbusError` on
    failure; callers decide whether that means "retry later" or "this register
    has no value right now".
    """

    def __init__(self, unit: ModbusUnit) -> None:
        """Bind the device to a Modbus unit."""
        self._unit = unit

    async def async_read_group(
        self, refs: Sequence[RegisterRef]
    ) -> dict[str, int | None]:
        """Read a group of registers, batching contiguous addresses.

        A block that fails leaves its registers at ``None`` rather than
        discarding the whole cycle, so one bad register does not blank every
        entity. If nothing at all answered the first error is re-raised, which
        the coordinator turns into an unavailable device.
        """
        values: dict[str, int | None] = {}
        errors: list[ModbusError] = []
        answered = 0

        for space, address, block in plan_block_reads(refs):
            try:
                raw = await self._async_read(space, address, len(block))
            except ModbusError as err:
                _LOGGER.debug("Block read %s@%s failed: %s", space, address, err)
                errors.append(err)
                raw = []

            if len(raw) != len(block):
                if raw:
                    _LOGGER.warning(
                        "Block read %s@%s returned %s of %s registers",
                        space,
                        address,
                        len(raw),
                        len(block),
                    )
                for ref in block:
                    values[ref.key] = None
                continue

            answered += 1
            for ref, word in zip(block, raw, strict=True):
                values[ref.key] = decode_signed(word) if ref.signed else word

        if not answered:
            # Nothing at all came back: the link is down or the controller is
            # silent. Let the coordinator mark the device unavailable.
            if errors:
                raise errors[0]
            raise ModbusError("The controller returned no registers")

        if errors:
            failed = sorted(key for key, value in values.items() if value is None)
            _LOGGER.warning(
                "%s register(s) did not answer this cycle: %s",
                len(failed),
                ", ".join(failed),
            )

        return values

    async def async_write_value(self, address: int, value: int) -> None:
        """Write a single holding register."""
        await self._unit.write_register(address, encode_signed(int(value)))

    async def _async_read(self, space: str, address: int, count: int) -> list[int]:
        """Read ``count`` registers from one space."""
        if space == INPUT:
            return await self._unit.read_input_registers(address, count)
        return await self._unit.read_holding_registers(address, count)
