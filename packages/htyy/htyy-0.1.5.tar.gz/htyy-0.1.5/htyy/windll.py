from htyy._infront._htyy_d.windll import windll
import sys

if sys.platform.startswith("win32"):
    platform = "windows"

elif sys.platform.startswith("linux"):
    platform = "linux"

elif sys.platform.startswith("darwin"):
    platform = "darwin"

else:
    platform = sys.platform
