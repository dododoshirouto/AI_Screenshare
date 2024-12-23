import pystray
from PIL import Image
import winreg
import threading
import time
import sys
from func import Logger

from user_setting_gui import UserSettingGUI
from main import API_KEY

logger = Logger("TaskTray", enable=True)

setting_gui = UserSettingGUI(API_KEY)

class TaskTray:
    def __init__(self):
        self.darkmode = self.get_darkmode_from_system()
        self.icon = pystray.Icon("tasktray")
        self.icon.title = "DODO AI"
        self.set_icon()
    
    def start(self):
        self.thread = threading.Thread(target=self.run_tray, daemon=True)
        self.thread.start()
        self.active = True

    def run_tray(self):
        self.set_menu()
        self.icon.run()

    def menu_on_open_settings(self):
        setting_gui.open()

    def menu_on_exit(self):
        self.icon.stop()
        self.active = False
    
    def set_menu(self):
        self.icon.menu = pystray.Menu(
            pystray.MenuItem("Settings", self.menu_on_open_settings),
            pystray.MenuItem("Exit", self.menu_on_exit),
        )

    def set_icon(self):
        self.icon.icon = Image.open(f"icon/icon_{'dark' if self.darkmode else 'light'}.ico")

    def set_darkmode(self, darkmode:bool):
        self.darkmode = darkmode
        self.set_icon()
    
    def toggle_darkmode(self):
        self.darkmode = not self.darkmode
        self.set_icon()

    def get_darkmode_from_system(self):
        try:
            # レジストリキーを開く
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
            )
            # AppsUseLightThemeの値を取得
            value, regtype = winreg.QueryValueEx(key, "AppsUseLightTheme")
            winreg.CloseKey(key)
            return value == 0  # 0ならダークモード
        except FileNotFoundError:
            # レジストリキーが存在しない場合
            logger.print("レジストリキーが見つかりません。デフォルトのテーマを使用している可能性があります。", "ERROR")
            return False  # デフォルトでライトモードと仮定


if __name__ == "__main__":
    tasktray = TaskTray()
    logger.print("dark" if tasktray.get_darkmode_from_system() else "light")
    tasktray.start()

    while tasktray.active:
        # print("タスクトレイアイコンが実行中...")
        print(tasktray.active)
        time.sleep(1)