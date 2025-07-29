## epmux
This is a python binding for epmux cross-platform library for Multiplexer EyePoint MUX.

![MUX](https://raw.githubusercontent.com/EPC-MSU/EPLab/851dc110dd48f778766e33a604f93fdae4b685a9/media/ep_mux.jpg)

### Installation
```
pip install epmux
```

### Minimal example

For more information on API functions please consult documentation (see section "More information").

```python
from epmux import EpmuxDeviceHandle

module_type = {
    0: "placeholder",  # No module present
    1: "A",            # Module of type A (connects to line A only)
    2: "AB"            # Module of type AB (connects to both line A and B)
}

# Set correct device URI here
# Format for Windows: com:\\.\COM1
# Format for Linux: /dev/ttyACM1
# Format for MacOS: com:///dev/tty.usbmodem000001721
device_uri = r'com:\\.\COM433'

# Open device
try:
    device = EpmuxDeviceHandle(device_uri)
    print("Device opened")
    print("Read device information... ", end="")
    device_info = device.get_identity_information()
    print("Done")
    print("  -- Device information --")
    print("  Product: {} {}".format(bytes(device_info.manufacturer).decode("utf-8"),
                                    bytes(device_info.product_name).decode("utf-8")))
    print("  Hardware version: {}.{}.{}".format(device_info.hardware_major,
                                                device_info.hardware_minor,
                                                device_info.hardware_bugfix))
    print("  Serial number: {}".format(device_info.serial_number))
    print("  Firmware version: {}.{}.{}".format(device_info.firmware_major,
                                                device_info.firmware_minor,
                                                device_info.firmware_bugfix))
except RuntimeError:
    print("Cannot open device {}.".format(device_uri))
    print("Please check URI and try again.")
    exit()

# Get module chain structure (number of modules and their types)
chain = device.get_chain_structure()
print("Device chain length: {}".format(chain.chain_length))
print("Device chain structure: ", end="")
print(*("{}".format(module_type[chain.chain_structure[k]])
        for k in range(chain.chain_length)), sep=", ")

# Set active output channel
print("Set active output channel to: module 1, line A, channel 1")
active_channel_a = device.get_channel_for_line_a()
active_channel_a.module_number = 1   # Module chain position
active_channel_a.channel_number = 1  # Channel number within the module
device.set_channel_for_line_a(active_channel_a)

print("Turn off all channels of all modules")
device.all_channels_off()

# Close device
device.close_device()
print("Device closed")
```

### More information
For documentation, software, examples of using the API and bindings for Python and C#, you can visit our website:
* English version: https://eyepoint.physlab.ru/en/product/EyePoint_MUX_M/
* Russian version: https://eyepoint.physlab.ru/ru/product/EyePoint_MUX_M/. 