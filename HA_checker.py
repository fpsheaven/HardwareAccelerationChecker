import os,winreg,webbrowser,time,json,subprocess


def registry_path_exists(hive, path):
    try:
        winreg.OpenKey(getattr(winreg, hive), path)
        return True
    except FileNotFoundError:
        return False

def check_registry_key(key_path, value_name):
    try:
        result = subprocess.check_output(['reg', 'query', key_path, '/v', value_name], stderr=subprocess.STDOUT, universal_newlines=True)
        return value_name in result
    except subprocess.CalledProcessError:
        return False

def get_registry_value(key_path, value_name):
    try:
        result = subprocess.check_output(['reg', 'query', key_path, '/v', value_name], stderr=subprocess.STDOUT, universal_newlines=True)
        lines = result.split('\n')
        for line in lines:
            if value_name in line:
                return line.split()[-1]
    except subprocess.CalledProcessError:
        return None

def set_registry_value(key_path, value_name, value):
    subprocess.run(['reg', 'add', key_path, '/v', value_name, '/t', 'REG_DWORD', '/d', str(value), '/f'], check=True)

def is_chrome_installed():
    chrome_path = os.path.join(os.getenv('PROGRAMFILES'), 'Google', 'Chrome', 'Application', 'chrome.exe')
    return os.path.exists(chrome_path)

def is_steam_installed():
    steam_path_to_check = "Software\\Valve\\Steam"
    return registry_path_exists('HKEY_CURRENT_USER', steam_path_to_check)
    
def is_spotify_installed():
    spotify_path = os.path.join(os.getenv('APPDATA'), 'Spotify', 'Spotify.exe')
    return os.path.exists(spotify_path)

def is_edge_installed():
    global edge_user_data_dir
    edge_user_data_dir = os.path.join(os.getenv('LOCALAPPDATA'), 'Microsoft', 'Edge', 'User Data')
    return os.path.exists(edge_user_data_dir)

def is_gx_installed():
    global gx_user_data_dir
    gx_user_data_dir = os.path.join(os.getenv('APPDATA'), 'Opera Software', 'Opera GX Stable')
    return os.path.exists(gx_user_data_dir)

def is_brave_installed():
    brave_path = os.path.join(os.getenv('LOCALAPPDATA'), 'BraveSoftware', 'Brave-Browser',)
    return os.path.exists(brave_path)

def is_firefox_installed():
    firefox_path = os.path.join(os.getenv('PROGRAMFILES'), 'Mozilla Firefox', 'firefox.exe')
    return os.path.exists(firefox_path)

def is_discord_installed():
    discord_path = os.path.join(os.getenv('APPDATA'), 'discord')
    return os.path.exists(discord_path)

def main():
    if not is_chrome_installed():
        print("Chrome is not installed.")
    else:
        chrome_value = get_registry_value('HKLM\\SOFTWARE\\Policies\\Google\\Chrome', 'HardwareAccelerationModeEnabled')

    if not is_steam_installed():
        print("Steam is not installed.")
    else:
        h264_value = get_registry_value('HKEY_CURRENT_USER\\Software\\Valve\\Steam', 'H264HWAccel')
        gpu_value = get_registry_value('HKEY_CURRENT_USER\\Software\\Valve\\Steam', 'GPUAccelWebViewsV3')
        steam_ha = 'enabled' if h264_value != "0x0" and gpu_value != "0x0" else 'disabled'

    if not is_spotify_installed():
        print("Spotify is not installed.")
    else:
        spotify_prefs_file = os.path.join(os.getenv('APPDATA'), 'Spotify', 'prefs')
        spotify_value = 'unknown'
        try:
            with open(spotify_prefs_file, 'r') as file:
                for line in file:
                    if 'ui.hardware_acceleration=false' in line:
                        spotify_value = 'disabled'
                        break
                else:
                    spotify_value = 'enabled'
        except FileNotFoundError:
            spotify_value = 'unknown'

    if not is_brave_installed():
        print("Brave is not installed.")
    else:
        brave_file_path = os.path.join(os.getenv('LOCALAPPDATA'), 'BraveSoftware', 'Brave-Browser', 'User Data', 'Local State')
        brave_ha = None
        try:
            with open(brave_file_path, 'r') as file:
                data = json.load(file)
                brave_ha = 'enabled' if data.get("hardware_acceleration_mode", {}).get("enabled", False) else 'disabled'
        except (FileNotFoundError, json.JSONDecodeError):
            brave_ha = 'unknown'

    if not is_firefox_installed():
        print("Firefox is not installed.")
    else:
        firefox_pref_loc = os.path.join(os.getenv('APPDATA'),'Mozilla', 'Firefox', 'Profiles')
        ff_acc = 0
        profile_found = False
        for profile_name in os.listdir(firefox_pref_loc):
            if profile_name.endswith('default-release'):
                PROFILE_PATH = os.path.join(firefox_pref_loc, profile_name)
                profile_found = True
                break
        if not profile_found:
            print("Profile folder ending with 'default-release' not found.")
            return
        PREFS_FILE = os.path.join(PROFILE_PATH, 'prefs.js')
        if os.path.exists(PREFS_FILE):
            with open(PREFS_FILE, 'r') as prefs_file:
                ff_acc = 0 if 'user_pref("layers.acceleration.disabled", true);' in prefs_file.read() else 1
        else:
            print("prefs.js file not found.")
            return

    if not is_discord_installed():
        print("Discord is not installed.")
    else:
        dc_pref_loc=os.path.join(os.getenv('APPDATA'),'discord')
        dc_acc = "Enabled"
        dc_cfg_path = os.path.join(dc_pref_loc, 'settings.json')
        if os.path.exists(dc_cfg_path):
            with open(dc_cfg_path, 'r') as dc_cfg_file:
                dc_cfg_content = json.load(dc_cfg_file)
                dc_acc = 0 if not dc_cfg_content.get('enableHardwareAcceleration', True) else 1
        else:
            print("settings.json file not found.")
    #EDGE 
    if not is_edge_installed():
        print("Edge is not installed.")
    else:
        edge_cfg_path = os.path.join(edge_user_data_dir, 'Local State')
        if os.path.exists(edge_cfg_path):
            with open(edge_cfg_path, 'r') as edge_cfg_file:
                edge_cfg_content = json.load(edge_cfg_file)
                hardware_acceleration_enabled = edge_cfg_content.get('hardware_acceleration_mode', {}).get('enabled', False)
                edge_acc = 1 if hardware_acceleration_enabled else 0
        else:
            print("Local State file not found.")
    
    #GX 
    #global gx_acc
    if not is_gx_installed():
        print("OperaGX is not installed.")
    else:
        gx_cfg_path = os.path.join(gx_user_data_dir, 'Local State')
        if os.path.exists(gx_cfg_path):
            with open(gx_cfg_path, 'r') as gx_cfg_file:
                gx_cfg_content = json.load(gx_cfg_file)
                hardware_acceleration_enabled = gx_cfg_content.get('hardware_acceleration_mode', {}).get('enabled', False)
                gx_acc = 1 if hardware_acceleration_enabled else 0
        else:
            print("Local State file not found.")

    if is_brave_installed():
        print(f'Brave Hardware Acceleration is currently {"enabled" if brave_ha == "enabled" else "disabled"}')
    if is_chrome_installed():
        print(f'Chrome Hardware Acceleration Mode is currently {"enabled" if chrome_value == "1" else "disabled"}.')
    if is_steam_installed():
        print(f'Steam Hardware Acceleration is currently {"disabled" if steam_ha == "disabled" else "enabled"}.')
    if is_spotify_installed():
        print(f'Spotify Hardware Acceleration is currently {"enabled" if spotify_value == "enabled" else "disabled"}.')
    if is_firefox_installed():
        print(f'Firefox Hardware Acceleration is currently {"enabled" if ff_acc == 1 else "disabled"}.')
    if is_discord_installed():
        print(f'Discord Hardware Acceleration is currently {"enabled" if dc_acc == 1 else "disabled"}.')
    if is_edge_installed():
        print(f'MS edge Hardware Acceleration is currently {"enabled" if edge_acc == 1 else "disabled"}.')
    if is_gx_installed():
        print(f'Opera gx Hardware Acceleration is currently {"enabled" if gx_acc == 1 else "disabled"}.')
    print("")
    
    if is_edge_installed():
        edge_cfg_path = os.path.join(edge_user_data_dir, 'Local State')
    if os.path.exists(edge_cfg_path):
        with open(edge_cfg_path, 'r') as edge_cfg_file:
            lines = edge_cfg_file.readlines()
        edge_choice = input(f"Keep Edge's Acceleration {'ON?' if edge_acc == 1 else 'OFF?'} (0=Off, 1=On)? ")
        if edge_choice in ['0', '1']:
            with open(edge_cfg_path, 'w') as edge_cfg_file:
                for line in lines:
                    if 'hardware_acceleration_mode":{"enabled":' in line:
                        if edge_choice == '1':
                            line = line.replace('"hardware_acceleration_mode":{"enabled":false}', '"hardware_acceleration_mode":{"enabled":true}')
                        else:
                            line = line.replace('"hardware_acceleration_mode":{"enabled":true}', '"hardware_acceleration_mode":{"enabled":false}')
                    edge_cfg_file.write(line)
            print("Hardware acceleration is now", "ON" if edge_choice == '1' else "OFF")
        else:
            print('Invalid choice for Edge. Please enter 0 for off or 1 for on.')
    else:
        print("Local State file not found.")



    if is_chrome_installed():
        chrome_choice = input(f"Keep Chrome's Acceleration {'ON?' if chrome_value == '1' else 'OFF?'} (0=Off, 1=On)? ")
        if chrome_choice in ['0', '1']:
            set_registry_value('HKLM\\SOFTWARE\\Policies\\Google\\Chrome', 'HardwareAccelerationModeEnabled',int(chrome_choice))
        else:
            print('Invalid choice for Chrome. Please enter 0 for off or 1 for on.')
            return

    if is_steam_installed():
        print("")
        steam_choice = input(f"Keep Steam's Acceleration {'ON?' if steam_ha == 'enabled' else 'OFF?'} (0=Off, 1=On)? ")
        if steam_choice == "1":
            set_registry_value('HKEY_CURRENT_USER\\Software\\Valve\\Steam', 'H264HWAccel', 1)
            set_registry_value('HKEY_CURRENT_USER\\Software\\Valve\\Steam', 'GPUAccelWebViewsV3', 1)
            print("Turning Steam's Hardware Acceleration ON.")
        elif steam_choice == "0":
            set_registry_value('HKEY_CURRENT_USER\\Software\\Valve\\Steam', 'H264HWAccel', 0)
            set_registry_value('HKEY_CURRENT_USER\\Software\\Valve\\Steam', 'GPUAccelWebViewsV3', 0)
            print("Steam's Hardware Acceleration OFF.")
        else:
            print('Invalid choice for Steam. Please enter 0 for off or 1 for on.')
            return

    if is_spotify_installed():
        print("")
        spotify_choice = input(f"Keep Spotify's Hardware Acceleration {'ON?' if spotify_value == 'enabled' else 'OFF?'} (0=Off, 1=On)? ")
        try:
            with open(spotify_prefs_file, 'r') as file:
                lines = file.readlines()
        except FileNotFoundError:
            print("Spotify preferences file not found.")
            return

        try:
            with open(spotify_prefs_file, 'w') as file:
                if spotify_choice == "0":
                    if not any("ui.hardware_acceleration=false" in line for line in lines):
                        lines.append("ui.hardware_acceleration=false\n")
                    file.writelines(lines)
                    print("Turned Spotify's hardware acceleration OFF.")
                elif spotify_choice == "1":
                    file.writelines(line for line in lines if "ui.hardware_acceleration=false" not in line)
                    print("Turned Spotify's hardware acceleration ON.")
                else:
                    print('Invalid choice for Spotify. Please enter 0 for off or 1 for on.')
                    return
        except Exception as e:
            print(f"An error occurred while updating Spotify preferences: {e}")
            return

    if is_brave_installed():
        brave_choice = input(f"Keep Brave's Hardware Acceleration {'ON?' if brave_ha == 'enabled' else 'OFF?'} (0=Off, 1=On)? ")
        if brave_choice in ["0", "1"]:
            data["hardware_acceleration_mode"]["enabled"] = (brave_choice == "1")
            with open(brave_file_path, 'w') as file:
                json.dump(data, file, indent=4)
            print(f"Turned Brave's hardware acceleration {'OFF' if brave_choice == '0' else 'ON'}.")
        else:
            print('Invalid choice for Brave. Please enter 0 for off or 1 for on.')
            return

    if is_firefox_installed():
        ff_choice = input(f"Keep Firefox's Hardware Acceleration {'ON?' if ff_acc == 1 else 'OFF?'} (0=Off, 1=On)? ")
        if ff_choice == '1':
            with open(PREFS_FILE, 'r') as prefs_file:
                lines = prefs_file.readlines()
            with open(PREFS_FILE, 'w') as prefs_file:
                for line in lines:
                    if 'user_pref("layers.acceleration.disabled", true);' in line:
                        prefs_file.write(line.replace('user_pref("layers.acceleration.disabled", true);', ''))
                    else:
                        prefs_file.write(line)
            print("Hardware acceleration is now ON.")
        elif ff_choice == '0':
            with open(PREFS_FILE, 'a') as prefs_file:
                prefs_file.write('user_pref("layers.acceleration.disabled", true);\n')
            print("Keeping hardware acceleration OFF.")
        else:
            print('Invalid choice for Firefox. Please enter 0 for off or 1 for on.')
            return

    if is_discord_installed():
        dc_choice = input(f"Keep Discord's Hardware Acceleration {'ON?' if dc_acc == 1 else 'OFF?'} (0=Off, 1=On)? ")
        if dc_choice in ["0", "1"]:
            with open(dc_cfg_path, 'r') as file:
                dc_cfg_content = json.load(file)

            dc_cfg_content['enableHardwareAcceleration'] = (dc_choice == "1")

            with open(dc_cfg_path, 'w') as file:
                json.dump(dc_cfg_content, file, indent=4)

            print(f"Turned Discord's hardware acceleration {'OFF' if dc_choice == '0' else 'ON'}.")
        else:
            print('Invalid choice for Discord. Please enter 0 for off or 1 for on.')


#GX
    
    if is_gx_installed():
        gx_cfg_path = os.path.join(gx_user_data_dir, 'Local State')
    if os.path.exists(gx_cfg_path):
        with open(gx_cfg_path, 'r') as gx_cfg_file:
            lines = gx_cfg_file.readlines()
        gx_choice = input(f"Keep OperaGX's Acceleration {'ON?' if gx_acc == 1 else 'OFF?'} (0=Off, 1=On)? ")
        if gx_choice in ['0', '1']:
            with open(gx_cfg_path, 'w') as gx_cfg_file:
                for line in lines:
                    if 'hardware_acceleration_mode":{"enabled":' in line:
                        if gx_choice == '1':
                            line = line.replace('"hardware_acceleration_mode":{"enabled":false}', '"hardware_acceleration_mode":{"enabled":true}')
                        else:
                            line = line.replace('"hardware_acceleration_mode":{"enabled":true}', '"hardware_acceleration_mode":{"enabled":false}')
                    gx_cfg_file.write(line)
            print("Hardware acceleration is now", "ON" if gx_choice == '1' else "OFF")
        else:
            print('Invalid choice for OperaGX. Please enter 0 for off or 1 for on.')
    else:
        print("Local State file not found.")



    print("Thank you and take care ,@frequencycs")
    time.sleep(2)
    webbrowser.open('https://twitter.com/frequencycs')
    webbrowser.open('https://fpsheaven.com/services')
if __name__ == '__main__':
    main()
#v1.3
