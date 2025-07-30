from kivy.app import App as KivyApp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.image import Image
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle

class KidsUIApp(KivyApp):
    def __init__(self, title="Kids App", width=400, height=600, **kwargs):
        super().__init__(**kwargs)
        self.title = title
        Window.size = (width, height)
        self.layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        self.inputs = []

    def build(self):
        return self.layout

    def label(self, text, color=(1, 1, 1, 1), font_size=24):
        lbl = Label(text=text, font_size=font_size, color=color)
        self.layout.add_widget(lbl)

    def button(self, text, action, background_color=(0.2, 0.6, 0.8, 1), text_color=(1, 1, 1, 1)):
        btn = Button(text=text, size_hint=(1, None), height=50, font_size=20,
                     background_normal='', background_color=background_color)
        btn.color = text_color
        btn.bind(on_press=lambda instance: action())
        self.layout.add_widget(btn)

    def text_input(self, hint=""):
        input_box = TextInput(hint_text=hint, multiline=False, font_size=20, size_hint=(1, None), height=50)
        self.layout.add_widget(input_box)
        self.inputs.append(input_box)
        return input_box

    def image(self, path, width=200, height=200):
        img = Image(source=path, size_hint=(None, None), size=(width, height))
        self.layout.add_widget(img)

    def colored_box(self, color=(1, 0, 0, 1), height=100):
        box = Widget(size_hint=(1, None), height=height)
        with box.canvas.before:
            Color(*color)
            box.rect = Rectangle(size=box.size, pos=box.pos)
            box.bind(size=lambda instance, value: setattr(box.rect, 'size', value))
            box.bind(pos=lambda instance, value: setattr(box.rect, 'pos', value))
        self.layout.add_widget(box)

    def alert(self, message):
        popup = Popup(title='Message', content=Label(text=message), size_hint=(None, None), size=(300, 200))
        popup.open()

    def run(self):
        super().run()
