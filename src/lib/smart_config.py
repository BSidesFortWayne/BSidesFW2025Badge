import json
import os

from lib.file_hash import calculate_file_hash


def python_type_to_html_type(value_type):
    if value_type is str:
        return "text"
    elif value_type is int:
        return "number"
    elif value_type is bool:
        return "checkbox"
    else:
        return "text"

def config_item_to_html(key, value):
    print(value, type(value))
    if issubclass(type(value), SmartConfigValue):
        # if the value is a SmartConfigValue object, call its to_html_input method
        return value.to_html_input(key)
    
    value_type = python_type_to_html_type(type(value))

    # if bool
    if isinstance(value, bool):
        return f"""
            <label for="{key}">{key}</label>
            <input type="{value_type}" name="{key}" {"checked" if value else ""} value={str(value).lower()} onchange="updateCheckboxValue(this)">
        """

    return f"""
        <label for="{key}">{key}</label>
        <input type="{value_type}" name="{key}" value={value}>
    """



class SmartConfigValue(dict):
    def __init__(self):
        super().__init__()
        self['type'] = self.__class__.__name__

    # abstract class
    def to_html_input(self, key: str) -> str:
        return ""
    
    def parse_value(self, value):
        pass
    
    def to_dict(self):
        """
        Convert the object to a dictionary representation.
        This is used for serialization.
        """
        return {key: value for key, value in self.items() if not key.startswith('_')}


    # TODO develop base "renderable" component for on screen editing of config values


    # TODO deal with serializaton and deserialization of smart config values...
#     def to_json(self):
#         return json.dumps(self)


# class SmartConfigEncoder(json.JSONEncoder):
#     def default(self, obj):
#         """called by json.dumps to translate an object obj to
#         a json serialisable data"""
#         if isinstance(obj, SmartConfigValue):
#             return obj.to_json()
#         return json.JSONEncoder.default(self, obj)


class RangeConfig(SmartConfigValue):
    def __init__(
            self, 
            name: str, 
            min: int, 
            max: int, 
            current = None, 
            step: int = 1
    ):
        super().__init__()
        self['name'] = name
        self['min'] = min
        self['max'] = max
        self['current'] = current if current is not None and min <= current <= max else min
        self['step'] = step

    def to_html_input(self, key) -> str:
        return f"""
            <label for="{self['name']}">{self['name']}</label>
            <input type="range" name="{key}" min="{self['min']}" max="{self['max']}" step="{self['step']}" value="{self['current']}">
        """

    def __int__(self):
        print("RangeConfig __int__")
        return int(self['current'])
    
    def value(self):
        return self['current']
    
    def parse_value(self, value):
        print("RangeConfig parse_value", value)
        # Check if the value is a string and convert it to an int
        if isinstance(value, str):
            try:
                value = int(value)
            except ValueError:
                raise ValueError(f"Invalid value for {self['name']}: {value}")

        # Check if the value is within the range
        if not (self['min'] <= value <= self['max']):
            raise ValueError(f"Value {value} out of range for {self['name']}: {self['min']} - {self['max']}")

        # Set the current value
        self['current'] = value
        return value
    
    def __str__(self):
        return f"{self['name']}: {self['current']} ({self['min']}-{self['max']})"
    
    def __repr__(self):
        return f"<RangeConfig {self['name']} ({self['min']}-{self['max']})>"


class ColorConfig(RangeConfig):
    def __init__(self, name: str, current = None):
        super().__init__(name, 0, 0xFFFF, current)


class EnumConfig(SmartConfigValue):
    def __init__(self, name: str, options: list[str], current = None):
        super().__init__()
        self['name'] = name
        self['options'] = options
        self['current'] = current if current and current in options else options[0]
    
    def to_html_input(self, key) -> str:
        options_html = "".join([f'<option value="{option}" {"selected" if option == self['current'] else ""}>{option}</option>' for option in self['options']])
        return f"""
            <label for="{self['name']}">{self['name']}</label>
            <select name="{key}">
                {options_html}
            </select>
        """
    
    def parse_value(self, value):
        print("EnumConfig parse_value", value)
        # Check if the value is a string and convert it to an int
        if isinstance(value, str):
            if value not in self['options']:
                raise ValueError(f"Invalid value for {self['name']}: {value}")

        # Set the current value
        self['current'] = value
        return value
    
    def value(self):
        return self['current']
    
    def __int__(self):
        return int(self['current'])

    def __str__(self):
        return f"{self['name']}: {self['current']} ({', '.join(self['options'])})"


class BoolDropdownConfig(EnumConfig):
    def __init__(self, name: str, current = None, **kwargs):
        super().__init__(name, ['True', 'False'], current)
        self['current'] = 'True' if str(current).lower() == 'true' else 'False'
    
    def value(self):
        return self['current'] == 'True'


class Config(dict):
    def __init__(self, filename: str):
        super().__init__()
        self.filename = filename
        self.load()

    def add(self, key: str, value, force: bool = False):
        """
        Add a key to the config. If the key already exists, it will not be added
        unless force is set to True.
        :param key: The key to add
        :param value: The value to add
        :param force: If True, the key will be added even if it already exists
        :return: None
        """
        print(f"Adding {key} to config")
        
        if force:
            self[key] = value
            return value
        else:
            return self.setdefault(key, value)

    def checksum(self):
        print(f'Calculating checksum for {self.filename}')
        return calculate_file_hash(self.filename)

    def update(self, data: dict):
        updates = {}
        for key, value in data.items():
            if key not in self:
                updates[key] = value
                continue

            # if the value is a dict... Check if it is a SmartConfigValue object
            # Check the original value type and convert it if different
            existing_value_type = type(self[key])
            if isinstance(self[key], SmartConfigValue):
                # TODO we might need to make a copy of this object to not update state until validated...
                self[key].parse_value(value)
                updates[key] = self[key]
            elif existing_value_type is type(value):
                updates[key] = value
            elif existing_value_type is int and type(value) is str:
                updates[key] = int(value)
            elif existing_value_type is bool:
                updates[key] = value.lower() == "true"
            else:
                raise ValueError(f"Type mismatch for {key}: {existing_value_type} != {type(value)}")
        
        # Only update the config at the end so if anything throws we don't accept the update
        super().update(updates)

        self.save()

    def as_html(self):
        sorted_config_items = sorted(self.items(), key=lambda x: x[0])
        return "".join([config_item_to_html(k, v) for k, v in sorted_config_items])

    def load(self):
        try:
            with open(self.filename, "r") as f:
                # TODO custom transformer for smart config...
                data = json.load(f)
                for key,value in data.items():
                    # Check if the value is a dict and if it is a SmartConfigValue object
                    if isinstance(value, dict) and 'type' in value:
                        # Create an instance of the SmartConfigValue subclass
                        class_name = value.pop('type')
                        # Check if the class exists in the current module
                        # look up class name in the this module
                        if class_name in globals():
                            # Create an instance of the class
                            config_value_class = globals()[class_name]
                            config_value = config_value_class(**value)
                            self[key] = config_value
                        else:
                            print(f"Class {class_name} not found")
                    else:
                        # Just set the value
                        self[key] = value
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
                data = json.dumps(self)
                print("Data to save:", data)
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

