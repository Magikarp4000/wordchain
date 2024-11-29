from config import *
from backend import Backend

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.graphics import Ellipse
from kivy.vector import Vector
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button


class WordChainApp(App):
    def build(self):
        gui = GUI()
        return gui


class GUI(BoxLayout):
    def __init__(self):
        super().__init__(orientation='vertical')
        input_box = InputBox(font_size=30,
                              size_hint_y=None,
                              height=100)
        
        self.add_widget(input_box)


class InputBox(TextInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs, multiline=False)
        self.bind(on_text_validate=InputBox.on_enter)
        self.text_validate_unfocus = False
    
    def clear(self):
        self.text = ""
    
    def on_enter(self):
        print(self, self.text)
        self.clear()


# class GUI(Widget):
#     backend = Backend()
#     backend.init_main()
#     nodes = []

#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)
#         self.textbox = TextBox()
#         self.add_widget(self.textbox)

#     def update(self, *args):
#         pass
#         # self.backend.update('')
    
#     def on_touch_down(self, touch):
#         with self.canvas:
#             self.nodes.append(Node(Vector(touch.pos)))


class Node(Widget):
    size = Vector(50, 50)

    def __init__(self, pos=Vector(0, 0)):
        self.pos = pos - self.size / 2
        self.image = Ellipse(pos=self.pos, size=self.size)
    

if __name__ == '__main__':
    WordChainApp().run()
