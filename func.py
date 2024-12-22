class Logger:
    def __init__(self, class_name: str, enable: bool = True):
        self.class_name = class_name
        self.enable = enable

    def print(self, message, type:str=""):
        if self.enable:
            print(f"[{self.class_name}] {(type+": " if type else "")}{message}")

    def set_class_name(self, class_name: str):
        self.class_name = class_name

    def set_enable(self, enable: bool):
        self.enable = enable

