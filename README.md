# RPi-BlueScratch
Simple Bluetooth Rfcomm driver for Scratch 1.4 on Raspberry Pi 3

Dependencies:

- [/pilliq/scratchpy](https://github.com/pilliq/scratchpy)
- [/karulis/pybluez](https://github.com/karulis/pybluez)

Example:

![alt example](example.png?raw=true "Example")

How to run it?
1. Turn on scratch IDE
2. Right-click on the Sensor Value block, found in the sensing category.
3. Select the "Enable remote sensor connections" option.
4. Run BlueScratch.py
5. Connect to RPi BT address and send some data via Rfcomm socket to it
