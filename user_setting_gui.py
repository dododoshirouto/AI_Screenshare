import flet
import os
from dotenv import load_dotenv


load_dotenv()

class UserSettingGUI:
    def __init__(self, openai_api_key:str):
        self.openai_api_key:str = openai_api_key
        pass

    def create_user_setting_gui(self, page: flet.Page):
        page.add(flet.Text("OpenAI API Key"))
        self.f_api_key = flet.TextField(value=self.openai_api_key, password=True)
        page.add(self.f_api_key)
        def toggle_password(e):
            self.f_api_key.password = not self.f_api_key.password
            self.f_api_key.update()
        page.add(flet.Button("Show API Key", on_click=toggle_password))
        page.add(flet.Button("Save", on_click=self.on_save_user_setting))
        pass

    def update_user_setting_gui(self, page: flet.Page):
        pass
    
    def create_debug_gui(self, page: flet.Page):
        pass

    def update_debug_gui(self, page: flet.Page):
        pass



    def on_save_user_setting(self, e):
        print(self.f_api_key.value)
        self.openai_api_key = self.f_api_key.value or ""
        os.environ["OPENAI_API_KEY"] = self.openai_api_key
        self.update_dotenv_file("OPENAI_API_KEY", self.openai_api_key)
        pass


    def update_dotenv_file(self, key:str, value:str):
        # もし.envファイルが存在しない場合は作成
        if not os.path.exists('.env'):
            with open('.env', 'w') as file:
                file.write("")

        key_exists = False
        # .envファイルを開く
        with open('.env', 'r') as file:
            lines = file.readlines()
            for line in lines:
                if line.startswith(f"{key}="):
                    key_exists = True
                    break
        
        # .envファイルを更新
        with open('.env', 'w') as file:
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
    flet.app(target=setting.create_user_setting_gui)

    setting.update_dotenv_file("test", "asdfads")