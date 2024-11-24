from config import *
from backend import Backend

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.clock import Clock


class GUI(Widget):
    backend = Backend()
    backend.init_main()

    def update(self, *args):
        self.backend.update('')


class WordChainApp(App):
    def build(self):
        gui = GUI()
        Clock.schedule_interval(gui.update, 1.0 / FPS)
        return gui


if __name__ == '__main__':
    WordChainApp().run()
