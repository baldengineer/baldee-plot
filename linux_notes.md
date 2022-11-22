
# Get the required packages installed for Serial AND USB
pip install pyvisa pyvisa-py pyusb pyserial 

# For troubleshooting USBTMC, install this package
helpful: python-usbtmc

# To find the COM port that a Serial device is using... (or just pyvisa.ResourceManager('@py').list_resources())
ls /sys/bus/usb-serial/devices/ -ltrah 

# Create a udev rule for USBTMC
echo 'SUBSYSTEM=="usb", MODE="0666", GROUP="usbusers"' >> 99-com.rules
sudo mv 99-com.rules /etc/udev/rules.d/99-com.rules

# Add user to dialout group to fix Permission Denied on serial devices
sudo addgroup baldee dialout
# I had to reboot... I dunno why