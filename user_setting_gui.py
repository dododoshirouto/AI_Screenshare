import flet

class UserSettingGUI:
    def __init__(self):
        pass

    def create_user_setting_gui(self, page: flet.Page):
        page.add(flet.Text("OpenAI API Key"))
        page.add(flet.TextField(value="your-openai-api-key-here"))
        page.add(flet.Button("Save"))
        pass

    def update_user_setting_gui(self, page: flet.Page):
        pass
    
    def create_debug_gui(self, page: flet.Page):
        pass

    def update_debug_gui(self, page: flet.Page):
        pass





if __name__ == "__main__":

    setting = UserSettingGUI()
    flet.app(target=setting.create_user_setting_gui)