import json
import os

class SmartConfig(dict):
    pass

class EnumConfig(SmartConfig):
    def __init__(self, name: str, options: list[str], default = None):
        super().__init__()
        self.name = name
        self.options = options
        self.current = default if default and default in options else options[0]


class Config(dict):
    def __init__(self, filename: str):
        super().__init__()
        self.filename = filename
        self.load()

    def load(self):
        try:
            with open(self.filename, "r") as f:
                data = json.load(f)
                self.update(data)
        except OSError:
            print("No file found?")
        except Exception as e:
            print(e)
            print("Error loading config file")

    def save(self):
        print(f"Saving smart config to {self.filename}")
        # Make sure the file exists
        try:
            with open(self.filename, "w") as f:
                json.dump(self, f)
        except OSError:
            print("No file found?")
            # Make the file
            os.mkdir("/".join(self.filename.split("/")[:-1]))
            with open(self.filename, "w") as f:
                json.dump(self, f)


    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        self.save()


if __name__ == "__main__":
    config = EnumConfig("test", ["a", "b", "c"], "d")
    print(config.name)
    print(config.current)