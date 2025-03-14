import json
import os
import random

import apps
import apps.app
from bsp import BSP
from hardware_rev import HardwareRev


class AppMetadata:
    def __init__(
            self, 
            friendly_name: str, 
            module_name: str,
            icon_file: str | bytes | None = None,
            constructor: type[apps.app.BaseApp] | None = None,
    ):
        self.friendly_name = friendly_name
        self.module_name = module_name
        self.constructor = constructor
        self.icon_file = icon_file
    
    def __str__(self):
        return self.friendly_name

class AppDirectory(list):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.ignore_app_files = [
            '__init__.py',
            'app.py'
        ]

        try:
            with open('config/app_directory_cache.json') as f:
                app_data_cache = json.load(f)
                for app_data in app_data_cache['apps']:
                    self.append(AppMetadata(**app_data))
        except Exception:
            print("No app cache found")


        app_files = os.listdir('apps')
        for app_file in app_files:
            # If this already exists in our app directory, we don't
            # need to create it here. It can update its cache when it
            # runs
            if app_file in self:
                continue
            
            if app_file in self.ignore_app_files:
                continue

            if not app_file.endswith('.py'):
                continue

            module_name = app_file[:-3]
            self.append(AppMetadata(module_name, module_name, None))
    
    
    def save_app_directory_cache(self):
        with open('config/app_directory_cache.json', 'w') as f:
            apps = [{
                'friendly_name': app.friendly_name,
                'module_name': app.module_name,
                'icon_file': app.icon_file,
            } for app in self]
            json.dump({
                'apps': apps
            }, f)

    def get_app_by_name(self, name: str):
        for app in self:
            if app.module_name == name or app.friendly_name == name:
                return app
        
        return None

    def __contains__(self, item: str | AppMetadata):
        if isinstance(item, str):
            for app in self:
                if app.module_name == item or app.friendly_name == item:
                    return True
                
        return False

        

class Controller(object):
    current_view: apps.app.BaseApp
    apps: list[AppMetadata]
    app_names: list[str]

    # This is a singleton pattern which gives us a single instance of the 
    # controller object. This is useful for global state 
    def __new__(cls):
        """ creates a singleton object, if it is not created, 
        or else returns the previous singleton object"""
        if not hasattr(cls, 'instance'):
            cls.instance = super(Controller, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        # some things that the views will need
        self.bsp = BSP(HardwareRev.V2)

        print("Callback handlers")

        self.app_directory = AppDirectory()

        try:
            name_file = open('name.json')
            self.name = json.loads(name_file.read())
            name_file.close()
        except Exception:
           print("Name file not found")
           self.name = {
               'first': "Bilbo",
               'last': "Baggins",
                'background_image': [
                    'img/bsides_logo.jpg',
                    'img/bsides_logo.jpg'
                ],
                'fg_color': [
                    '#FFFFFF',
                    '#FFFFFF'
                ],
                'bg_color': [
                    '#000000',
                    '#000000'
                ],
                'company': 'Company',
                'title': 'Title'
           }


        print("Register buttons")
        self.bsp.buttons.button_pressed_callbacks.append(self.button_press)
        self.bsp.buttons.button_released_callbacks.append(self.button_release)

        self.switch_app("view0")


    # TODO temporary shadow property for backwards compatibility
    @property
    def displays(self):
        return self.bsp.displays

    @property
    def neopixel(self):
        return self.bsp.leds.leds
    
    def button_press(self, button: int):
        print(f"Button Press {button}")
        if button == 0:
            self.random_app()


    def button_release(self, button: int):
        print(f"Button Relased {button}")
        self.bsp.leds.turn_off_led(button)


    def update(self):
        self.current_view.update()

    def random_app(self):
        app = random.choice(self.app_directory)
        self.switch_app(app.module_name)


    def switch_app(self, app_name: str):
        if not app_name:
            # TODO show a popup or just return?
            print("No view provided")
            return

        app: AppMetadata = self.app_directory.get_app_by_name(app_name) # type: ignore
        if not app:
            print(f"App {app_name} not found")
            return

        if app.constructor:
            print(f"Switched to {app_name} (already loaded)")
            self.current_view = app.constructor(self)
            # start threading callback to save app directory cache

            return

        module_name = app.module_name
        print(f"Loading {module_name}")
        __import__(f"apps.{module_name}")
        module = getattr(apps, module_name, None)
        if not module:
            # TODO show a popup or just return?
            print("No module found")
            return

        print(dir(module))
        print(module.__dict__.items())
        for _, obj in module.__dict__.items():
            if isinstance(obj, type) and issubclass(obj, apps.app.BaseApp) and obj != apps.app.BaseApp:
                print(f"Found constructor, switched to {app_name} with {obj}")
                app.constructor = obj
                self.current_view = app.constructor(self)
                return

        print("No constructor found")
        return  
