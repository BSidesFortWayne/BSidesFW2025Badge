
from bsp import BSP

from lib.smart_config import Config

# This is just a placeholder definition... should integrate with main app
class IApp:
    def __init__(self, controller):
        self.controller = controller
        self.config: Config = Config("")
        self.bsp = controller.bsp

    async def update(self):
        """
        Update the app. This method should be implemented in the derived class.
        """
        raise NotImplementedError("update method not implemented in the derived class.")

class IController:
    def __init__(self, hardware_version: str):
        self._bsp = BSP(hardware_version)
        self.current_view: IApp | None = None

    # TODO still have a circular import issue when we import AppDirectory....
    # @property
    # def app_directory(self) -> AppDirectory:
    #     """
    #     Returns the app directory instance.
    #     """
    #     return self._app_directory
    
    # @app_directory.setter
    # def app_directory(self, value: AppDirectory):
    #     """
    #     Sets the app directory instance.
    #     """
    #     self._app_directory = value
    

    @property
    def bsp(self):
        return self._bsp

    # TODO still here for backwards compatbility...
    @property
    def neopixel(self):
        return self._bsp.leds.leds

    # TODO still here for backwards compatbility...
    @property
    def displays(self):
        return self._bsp.displays

    def is_current_app(self, app_instance):
        """
        Check if the given app instance is the current app.
        """
        raise NotImplementedError("is_current_app method not implemented in the derived class.")
    
    async def switch_app(self, app_name: str):
        """
        Switch to the specified app. This method should be implemented in the derived class.
        """
        raise NotImplementedError("switch_app method not implemented in the derived class.")
    