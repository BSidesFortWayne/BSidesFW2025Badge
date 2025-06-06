from lib.smart_config import Config

class Driver:
    name = ""
    def __init__(self):
        self.name = self.name or self.__class__.__name__
        self.config = Config(f"config/drivers/{self.name}.json")

