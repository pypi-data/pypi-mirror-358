"""
Wallpaper.
"""
import os
import platform
import subprocess
import ctypes

def get(path,name):
    """
    Get the current desktop wallpaper. 
    :param path: save location.
    :param name: wallpaper name.
    """
    import os
    try:
        import shutil

        source_file_path = fr"{os.path.expanduser("~")}\AppData\Roaming\Microsoft\Windows\Themes\TranscodedWallpaper"

        try:
            shutil.copy2(source_file_path, path)
        except FileNotFoundError as e:
            print(f"Error: {e}")

        old_file_name = 'TranscodedWallpaper'

        if name == None:
            new_file_name = 'wallpaper.jpg'

        else:
            new_file_name = name

        try:
            old_full_path = os.path.join(path, old_file_name)
            new_full_path = os.path.join(path, new_file_name)

            # Check if the file exists before attempting to rename it.
            if not os.path.exists(old_full_path):
                raise FileNotFoundError(f"The specified file does not exist at location: '{old_full_path}'")

            os.rename(old_full_path, new_full_path)
        except Exception as e:
            print(f"An error occurred while trying to rename the file: {e}")
    except Exception as e:
        print(f"Error: {e}")

def set_wallpaper(image_path):
    """
    Set your desktop wallpaper
    :param image_path (str) - The path to the image file
    """
    # 转换为绝对路径
    image_path = os.path.abspath(image_path)
    
    # 检查文件是否存在
    if not os.path.isfile(image_path):
        raise FileNotFoundError(f"File does not exist: {image_path}")

    system = platform.system()

    try:
        if system == "Windows":
            # Windows API
            SPI_SETDESKWALLPAPER = 0x0014
            SPIF_UPDATEINIFILE = 0x01
            SPIF_SENDCHANGE = 0x02
            ctypes.windll.user32.SystemParametersInfoW(
                SPI_SETDESKWALLPAPER,
                0,
                image_path,
                SPIF_UPDATEINIFILE | SPIF_SENDCHANGE
            )

        elif system == "Linux":
            # GNOME桌面环境
            uri = f"file://{image_path}"
            subprocess.run([
                "gsettings", "set",
                "org.gnome.desktop.background",
                "picture-uri", uri
            ], check=True)

        elif system == "Darwin":
            # macOS系统
            script = f'''
            tell application "Finder"
                set desktop picture to POSIX file "{image_path}"
            end tell
            '''
            subprocess.run(["osascript", "-e", script], check=True)

        else:
            raise NotImplementedError("The current operating system is not supported at this time.")

    except subprocess.CalledProcessError as e:
        print(f"Setup failed: {str(e)}")
    except Exception as e:
        print(f"Error: {str(e)}")
