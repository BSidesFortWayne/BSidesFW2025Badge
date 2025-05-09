class FakeController():
    def __init__(self):
        pass

    def is_current_app(self, app_instance):
        """
        Check if the current app is the same as the one passed in
        """
        print(f"Checking if current app is {app_instance}")
        return False

    def switch_app(self, name):
        print(f"Switching to app: {name}")