import json
import os

class SmartConfigValue(dict):
    # abstract class
    def to_html_input(self):
        pass

    def parse_value(self, value):
        pass



class EnumConfig(SmartConfigValue):
    def __init__(self, name: str, options: list[str], default = None):
        super().__init__()
        self.name = name
        self.options = options
        self.current = default if default and default in options else options[0]


class Config(dict):
    def __init__(self, filename: str):
        super().__init__()
        self.filename = filename
        print(f"Loading smart config from {self.filename}")
        self.load()
        print(f"Loaded smart config: {self}")

    def update(self, data: dict):
        print(f"Updating config with {data}")
        updates = {}
        for key, value in data.items():
            if key not in self:
                updates[key] = value
                continue

            # if the value is a dict... Check if it is a SmartConfigValue object
            # Check the original value type and convert it if different
            existing_value_type = type(self[key])
            if isinstance(self[key], SmartConfigValue):
                updates[key] = self[key].parse_value(value)
            elif existing_value_type is type(value):
                updates[key] = value
            elif existing_value_type is int and type(value) is str:
                updates[key] = int(value)
            elif existing_value_type is bool and type(value) is str:
                updates[key] = value.lower() == "true"
            else:
                raise ValueError(f"Type mismatch for {key}: {existing_value_type} != {type(value)}")
        
        # Only update the config at the end so if anything throws we don't accept the update
        super().update(updates)

        self.save()

    def load(self):
        try:
            with open(self.filename, "r") as f:
                # TODO custom transformer for smart config...
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
        print(f"Setting {key} to {value} (file: {self.filename})")
        super().__setitem__(key, value)
        self.save()


if __name__ == "__main__":
    config = EnumConfig("test", ["a", "b", "c"], "d")
    print(config.name)
    print(config.current)