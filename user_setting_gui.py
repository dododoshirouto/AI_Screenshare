import flet

class UserSettingGUI:
    def __init__(self):
        pass

    def create_user_setting_gui(self, page: flet.Page):
        pass

    def update_user_setting_gui(self, page: flet.Page):
        pass
    
    def create_debug_gui(self, page: flet.Page):
        pass

    def update_debug_gui(self, page: flet.Page):
        pass





if __name__ == "__main__":

    def main(page: flet.Page):
        page.add(flet.Text("Hello, World!"))

    flet.app(target=main)