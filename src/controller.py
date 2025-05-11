import asyncio
import json
import random

import time

from app_directory import AppDirectory, AppMetadata
import apps.app
from bsp import BSP
from hardware_rev import HardwareRev
from icontroller import IController

class Controller(IController):
    # This is a singleton pattern which gives us a single instance of the 
    # controller object. This is useful for global state 
    # def __new__(cls, load_menu: bool = True):
    #     """ creates a singleton object, if it is not created, 
    #     or else returns the previous singleton object"""
        
    #     if not hasattr(cls, 'instance'):
    #         cls.instance = super(Controller, cls).__new__(cls, load_menu=load_menu)
    #     return cls.instance

    def __init__(self, displays, load_menu: bool = True):
        # some things that the views will need
        self._bsp = BSP(HardwareRev.V3, displays)

        print("Callback handlers")

        self.app_directory = AppDirectory()
        self.current_view: apps.app.BaseApp | None = None

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
        self.bsp.buttons.button_clicked_callbacks.append(self.button_click)
        self.bsp.buttons.button_released_callbacks.append(self.button_release)
        self.bsp.buttons.button_long_press_callbacks.append(self.button_long_press)

        self.current_app_lock = asyncio.Lock()

        if load_menu:
            asyncio.run(self.switch_app("Menu"))


    async def run(self):
        total_times = 0
        total_counts = 0
        while True:
            x = time.ticks_ms()
            async with self.current_app_lock:
                if self.current_view:
                    await self.current_view.update()
                await asyncio.sleep(0.01)
            d = time.ticks_diff(time.ticks_ms(), x)
            total_times += d
            total_counts += 1
            if total_counts % 100 == 0:
                average = total_times/total_counts
                print(f"Average: {average} ms")
                print(f"Average Hz: {int(1000/average)} Hz")


    def button_long_press(self, button: int):
        print(f'Button long press {button}')
        if self.current_view:
            self.current_view.button_long_press(button)
        if button == 3:
            asyncio.create_task(self.switch_app("Menu"))

    def button_press(self, button: int):
        if self.current_view:
            self.current_view.button_press(button)
        print(f"Button Press {button}")

    def button_click(self, button: int):
        print(f'Button click {button}')
        if self.current_view:
            self.current_view.button_click(button)

    def button_release(self, button: int):
        if self.current_view:
            self.current_view.button_release(button)
        print(f"Button Released {button}")

    def is_current_app(self, app_instance):
        """
        Check if the current app is the same as the one passed in
        """
        if not self.current_view:
            return False
        return self.current_view == app_instance
    

    async def update(self):
        if self.current_view:
            await self.current_view.update()

    async def random_app(self):
        app = random.choice(self.app_directory)
        await self.switch_app(app.module_name)

    async def switch_app(self, app_name: str):
        if not app_name:
            # TODO show a popup or just return?
            print("No view provided")
            return

        app: AppMetadata = self.app_directory.get_app_by_name(app_name) # type: ignore
        if not app:
            print(f"App {app_name} not found")
            return

        self.bsp.speaker.stop_song()

        if not app.constructor:
            module_name = app.module_name
            print(f"Loading {module_name}")
            __import__(f"apps.{module_name}")
            module = getattr(apps, module_name, None)
            if not module:
                # TODO show a popup or just return?
                print("No module found")
                return

            # TODO normalize with code in module metadata?
            for _, obj in module.__dict__.items():
                # This check makes sure we don't just load the first "BaseApp" we find and instead
                # load the correct app based on `name`
                if isinstance(obj, type) \
                        and issubclass(obj, apps.app.BaseApp) \
                        and obj != apps.app.BaseApp \
                        and obj.name == app.friendly_name: 
                    print(f"Found constructor, switched to {app_name} with {obj}")

                    app.constructor = obj
                    break
        
        if not app.constructor:
            print(f"App {app_name} not found")
            return

        if self.current_view:
            print("teardown current view")
            await self.current_view.teardown()

        print("Starting attempt to lock")
        async with self.current_app_lock:
            print(f"creating new instance of {app_name}")
            self.current_view = None
            self.current_view = app.constructor(self)
        
        print(f"Calling {app_name} app setup function")
        await self.current_view.setup()

        print("Done with app switch")
        
        await asyncio.sleep(0.01)

        print("Switching to new app")

        return  
