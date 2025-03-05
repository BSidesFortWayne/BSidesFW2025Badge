import views.view

class View(views.view.View):
    def __init__(self, views):
        self.view = 2
        self.views = views
        self.views.displays.display1.fill(self.views.displays.gc9a01.GREEN)
        self.views.displays.display2.fill(self.views.displays.gc9a01.GREEN)

    def button_press(self, button):
        if button == 1:
            # Back to home
            self.views.switch_view(0)
