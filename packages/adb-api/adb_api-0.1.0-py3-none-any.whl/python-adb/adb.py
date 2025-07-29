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
adb_path = os.path.join(os.path.dirname(__file__)
, "adb", use_system)
if use_system == "windows":
    adb_path = os.path.join(adb_path, "adb.exe")
else:
    adb_exec_path = os.path.join(adb_path, "adb")

def set_adb_path(path):
    global adb_path
    global adb_exec_path
    adb_path = path
    if use_system == "windows":
        adb_path = os.path.join(path, "adb.exe")
    else:
        adb_exec_path = os.path.join(path, "adb")

def get_adb_path():
    return adb_path

def __get_version():
    return os.popen(adb_exec_path + " version").read().strip()

def get_version():
    return __get_version().split(" ")[4].split("\n")[0]

def get_version_code():
    return __get_version().split(" ")[5].split("\n")[0]

def net_connect(ip, port = 5555):
    os.system(adb_exec_path + " connect " + ip + ":" + str(port))

def __get_devices():
    return os.popen(adb_exec_path + " devices").read()

def _get_devices():
    ret = []
    for i in __get_devices().split("\n"):
        if i != "" and i != "List of devices attached":
            ret.append(i.split("\t")[0])
    return ret

def get_device(no = 0):
    return _get_devices()[no]

def get_devices_count():
    return len(_get_devices())

def get_devices_list():
    return _get_devices()

device = get_device()

def get_device_status(device_id = device):
    for i in __get_devices().split("\n"):
        if i != "" and i != "List of devices attached":
            if i.split("\t")[0] == device_id:
                return i.split("\t")[1]
    return "unknown"

def set_device(device_id):
    global device
    device = device_id

def auto_set_device():
    global device
    device = _get_devices()[0]

def install_apk(path):
    os.system(adb_exec_path + " install " + path + " " + device)

def uninstall_apk(package_name):
    os.system(adb_exec_path + " uninstall " + package_name + " " + device)

def install_test_apk(path):
    os.system(adb_exec_path + " install -t " + path + " " + device)

def root():
    os.system(adb_exec_path + " root" + " " + device)

def reboot():
    os.system(adb_exec_path + " reboot" + " " + device)

def reboot_recovery():
    os.system(adb_exec_path + " reboot recovery" + " " + device)

def reboot_bootloader():
    os.system(adb_exec_path + " reboot bootloader" + " " + device)

def sideload_rom_pack(path):
    os.system(adb_exec_path + " sideload " + path + " " + device)

def push(local_path, remote_path):
    os.system(adb_exec_path + " push " + local_path + " " + remote_path + " " + device)

def pull(remote_path, local_path):
    os.system(adb_exec_path + " pull " + remote_path + " " + local_path + " " + device)

def run_shell(command):
    os.system(adb_exec_path + " shell " + command + " " + device)

def shell():
    os.system(adb_exec_path + " shell " + device)

def remount():
    os.system(adb_exec_path + " remount" + " " + device)

def kill_server():
    os.system(adb_exec_path + " kill-server")

def start_server():
    os.system(adb_exec_path + " start-server")

def adb_tcpip(port):
    os.system(adb_exec_path + " tcpip " + str(port) + " " + device)

def adb_run(command):
    os.system(adb_exec_path + " " + command + " " + device)

def get_device_connect_method(device_id = device):
    for i in os.popen(adb_exec_path + " devices -l").read().split("\n"):
        if i != "" and i != "List of devices attached":
            if i.split("\t")[0] == device_id:
                return i.split("\t")[2]
    return "unknown"

def get_device_l_output(device_id = device,no = 2):
    for i in os.popen(adb_exec_path + " devices -l").read().split("\n"):
        if i != "" and i != "List of devices attached":
            if i.split("\t")[0] == device_id:
                return i.split("\t")[no]
    return "unknown"

def adb_forward(p1, p2):
    os.system(adb_exec_path + " forward " + p1 + " " + p2)

def adb_help():
    os.system(adb_exec_path + " --help")

def disconnect_device(ip,port = 5555):
    os.system(adb_exec_path + " disconnect " + ip + ":" + port)

def reconnect():
    os.system(adb_exec_path + " reconnect")

def reconnect_device():
    os.system(adb_exec_path + " reconnect device")

def reconnect_offline():
    os.system(adb_exec_path + " reconnect offline")