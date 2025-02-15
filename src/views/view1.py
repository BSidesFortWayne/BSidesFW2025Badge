import views.view

class View(views.view.View):
    def __init__(self, views):
        self.views = views
        self.views.displays.display1.fill(self.views.displays.gc9a01.RED)
        self.views.displays.display2.fill(self.views.displays.gc9a01.RED)

    def button_press(self, button):
        if button == 1:
            # Back to home
            self.views.switch_view(0)
