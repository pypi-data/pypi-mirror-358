import os
import sys
if sys.platform.startswith('linux'):
    use_system = "linux"
elif sys.platform.startswith('darwin'):
    use_system = "darwin"
elif sys.platform.startswith('win32'):
    use_system = "windows"
else:
    print("Unsupported system")
    exit(1)
fastboot_path = os.path.join(os.path.dirname(__file__)
, "adb", use_system)
if use_system == "windows":
    fastboot_path = os.path.join(fastboot_path, "fastboot.exe")
else:
    fastboot_exec_path = os.path.join(fastboot_path, "fastboot")

def get_fastboot_path():
    return fastboot_path

def set_fastboot_path(path):
    global fastboot_path
    fastboot_path = path

def __get_devices():
    return os.popen(fastboot_exec_path + " devices").read()
