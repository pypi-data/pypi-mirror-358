# py-adb
A simple python library for Android Debug Bridge (ADB)
developed by [zhangjiahuichenxi](https://github.com/zhangjiahuichenxi)
# Install
```bash
pip install python-adb
```
# Usage
```python
from py_adb import *
## get all devices
get_devices_list()
## get No.1 device
get_device()
## get No.x device
get_device(x-1)
## install apk
install_apk(apk_path)
uninstall_apk(package_name)
## set device
set_device(device_id)
## set adb path
set_adb_path(adb_path)
## get adb path
get_adb_path()
## get adb vsersion
get_adb_version()
## get adb vsersion code
get_adb_version_code()
## connect device using network
net_connect(device_ip)
## get devices count
get_devices_count()
## get devices list
get_devices_list()
## auto set device
auto_set_device()
## root 
root()
