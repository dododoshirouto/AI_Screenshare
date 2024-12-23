import flet
import os


class UserSettingGUI:
    def __init__(self, openai_api_key: str=""):
        self.openai_api_key: str = openai_api_key
        # 他の関数とかでも使うfletパーツ
        self.f_api_key: flet.TextField
        self.f_alert_text: flet.Text
        pass

    def open(self):
        flet.app(target=self.create_user_setting_gui)
        pass

    def create_user_setting_gui(self, page: flet.Page):
        page.title = "User Settings - DODO Screen AI"

        def toggle_password(_):
            self.f_api_key.password = not self.f_api_key.password
            self.f_api_key.update()
            pass

        def on_save_and_close(_):
            print(self.f_api_key.value)
            self.openai_api_key = self.f_api_key.value or ""
            self.update_dotenv_file("OPENAI_API_KEY", self.openai_api_key)
            page.window.close()
            exit()
            pass

        def on_close(_):
            page.window.close()
            pass

        # set public flet fields
        self.f_api_key = flet.TextField(value=self.openai_api_key, password=True)
        self.f_alert_text = flet.Text("")
        # add flet parts
        page.add(flet.Text("OpenAI API Key"))
        page.add(self.f_api_key)
        page.add(flet.Button("Show API Key", on_click=toggle_password))
        page.add(flet.Button("Save and Close", on_click=on_save_and_close))
        page.add(flet.Button("Cancel", on_click=on_close))
        page.add(self.f_alert_text)
        pass

    def create_debug_gui(self, page: flet.Page):
        pass

    @staticmethod
    def update_dotenv_file(key: str, value: str):
        # もし.envファイルが存在しない場合は作成
        if not os.path.exists(".env"):
            with open(".env", "w") as file:
                file.write("")

        key_exists = False
        # .envファイルを開く
        with open(".env", "r") as file:
            lines = file.readlines()
            for line in lines:
                if line.startswith(f"{key}="):
                    key_exists = True
                    break

        # .envファイルを更新
        with open(".env", "w") as file:
            for line in lines:
                if line.startswith(f"{key}="):
                    file.write(f"{key}={value}\n")
                else:
                    file.write(line)

            # 新しいキーを追加
            if not key_exists:
                file.write(f"\n{key}={value}\n")


if __name__ == "__main__":

    setting = UserSettingGUI("")
    setting.open()
