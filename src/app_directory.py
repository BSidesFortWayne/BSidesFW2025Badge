import apps.app
import json
import os

from lib.file_hash import calculate_file_hash

class AppMetadata:
    def __init__(
        self,
        module_name: str,
        class_name: str,
        friendly_name: str,
        icon_file: str | bytes | None = None,
        constructor: type[apps.app.BaseApp] | None = None,
    ):
        self.friendly_name = friendly_name
        self.module_name = module_name
        self.class_name = class_name
        self.constructor = constructor
        self.icon_file = icon_file

    @staticmethod
    def from_module(module_name: str) -> list["AppMetadata"]:
        if not module_name:
            print(f"Module {module_name} not found")
            return []
        
        print(f"Loading {module_name}")
        __import__(f"apps.{module_name}")
        module = getattr(apps, module_name, None)
        if not module:
            # TODO show a popup or just return?
            print("No module found")
            return []

        results: list[AppMetadata] = []
        for _, obj in module.__dict__.items():
            if isinstance(obj, type) and issubclass(obj, apps.app.BaseApp) and obj != apps.app.BaseApp:
                new_app = AppMetadata(
                    friendly_name=obj.name,
                    class_name=obj.__name__,
                    module_name=module_name,
                    constructor=obj,
                )
                results.append(new_app)
        
        return results
                
    def __str__(self):
        return self.friendly_name if self.friendly_name else self.class_name

    def __repr__(self):
        return f'<AppMetadata {self.friendly_name} from {self.module_name}>'


def is_python_file(filename: str) -> bool:
    return filename.endswith(".py") or filename.endswith(".pyc")
class ModuleMetadata:
    def __init__(self, filename: str, checksum: str):
        if not is_python_file(filename):
            raise ValueError(f"File {filename} is not a python file")
        
        self.filename = filename
        self.module_name = filename.replace(".py", "").replace(".pyc", "")
        self.checksum = checksum
        self.apps: list[AppMetadata] = []

    def __str__(self):
        return self.filename

    @staticmethod
    def from_file(root: str, filename: str):
        # TODO doesn't exist in MicroPython?
        # if not os.path.exists(py_filepath):
        #     raise FileNotFoundError(f"File {py_filepath} not found")

        filepath = f"{root}/{filename}"
        if not is_python_file(filename):
            raise ValueError(f"File {filename} is not a python file")

        checksum = calculate_file_hash(filepath)

        module = ModuleMetadata(
            filename=filename, 
            checksum=checksum
        )

        return module

    def __repr__(self):
        return f'<ModuleMetadata {self.filename}, apps={[app.friendly_name for app in self.apps]}>'


# See example_app_cache.json
class AppDirectory:
    def __init__(
        self,
        root_app_directory: str = "apps",
        cache_location: str = "config/app_directory_cache.json",
        ignore_app_files: list[str] = ["__init__.py", "app.py"],
    ):
        self.ignore_app_files: list[str] = ignore_app_files
        self.root_app_directory = root_app_directory
        self.modules: dict[str, ModuleMetadata] = {}
        self.cache_location: str = cache_location

        try:
            # TODO refactor this to another method
            with open(self.cache_location) as f:
                cache = json.load(f)
                for filename, module_data in cache["modules"].items():
                    module = ModuleMetadata(
                        filename=filename,
                        checksum=module_data["checksum"],
                    )
                    module.apps = [
                        AppMetadata(
                            friendly_name=app_data["friendly_name"],
                            module_name=app_data["module_name"],
                            class_name=app_data["class_name"],
                            icon_file=app_data["icon_file"],
                        )
                        for app_data in module_data["apps"]
                    ]
                    self.modules[module.module_name] = module
        
        except Exception as e:
            print(e)
            print("No app cache found")

        app_files = os.listdir(root_app_directory)
        modules_updated = False
        for app_file in app_files:
            if app_file in self.ignore_app_files:
                continue

            if not is_python_file(app_file):
                continue

            # Create the new module metadata from the file itself
            module = ModuleMetadata.from_file(root_app_directory, app_file)

            # Do we need to refresh our app cache?
            new_module = module.module_name not in self.modules
            module_has_changed = not new_module and self.modules[module.module_name].checksum != module.checksum
            if new_module or module_has_changed:
                modules_updated = True
                self.modules[module.module_name] = module
                new_apps = AppMetadata.from_module(module.module_name)
                print(f"- Found {len(new_apps)} apps in {module.module_name}")
                for app in new_apps:
                    print(f"  - {app}")
                self.modules[module.module_name].apps = new_apps
            
        if modules_updated:
            self.save_app_directory_cache()


    @staticmethod
    def create_from_directory(path: str):
        app_dir = AppDirectory()

        return app_dir

    def save_app_directory_cache(self):
        print("Saving app directory cache")
        with open(self.cache_location, "w") as f:
            modules = {
                # TODO refactor the app serialization to come from the AppMetadata class
                module.filename: {
                    "checksum": module.checksum,
                    "apps": [
                        {
                            "friendly_name": app.friendly_name,
                            "class_name": app.class_name,
                            "module_name": app.module_name,
                            "icon_file": app.icon_file,
                        }
                        for app in module.apps
                    ],
                }
                for module in self.modules.values()
            }
            # We are dumping this under the "modules" key in case we want
            # to add other global metadata to the cache
            json.dump({
                "modules": modules,
            }, f)

    def get_app_by_name(self, name: str):
        for module_name,module in self.modules.items():

            # If this doesn't match the module name, check if it matches
            # a friendly app name
            for app in module.apps:
                if app.friendly_name == name:
                    print("Found app by friendly name")
                    return app

            # If we're given a module name, we will just return the first app
            # in that module
            if module_name == name:
                if len(module.apps) == 0:
                    raise ValueError(f"No apps found in module {module_name}")
                elif len(module.apps) > 1:
                    print(f"Multiple apps found in module {module_name}")
                
                print("Found app by module name")
                return module.apps[0]

    def __len__(self):
        # Return the total number of module keyed apps
        return sum([len(module.apps) for module in self.modules.values()])
    

    # Even though we will allow users to get the apps by name
    def __getitem__(self, key):
        for module in self.modules.values():
            for app in module.apps:
                if app.friendly_name == key:
                    return app

        raise KeyError(f"App {key} not found")


    def __iter__(self):
        # For consumers of the app directory, they don't care that we key
        # based on the module, they just care to get the app names
        for module in self.modules.values():
            for app in module.apps:
                yield app
