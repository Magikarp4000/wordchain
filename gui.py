from kivy.app import App
from kivy.uix.widget import Widget


class GUI(Widget):
    pass


class WordChainApp(App):
    def build(self):
        return GUI()


if __name__ == '__main__':
    WordChainApp().run()
