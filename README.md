Installation and Usage

Place the files in the custom_components/danfoss_ecl/ folder.

Restart Home Assistant.

In the Home Assistant UI, go to Settings > Devices & Services > Add integration.

Search for "Danfoss ECL 310 Modbus".

Enter your IP address and port.

The integration will then attempt to read the specific registers hard-coded in sensor.py. You must manually maintain the DANFOSS_REGISTERS list in sensor.py to obtain all relevant values.
