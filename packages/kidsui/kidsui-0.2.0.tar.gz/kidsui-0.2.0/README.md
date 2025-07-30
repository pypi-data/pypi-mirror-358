# KidsUI

A simple and fun GUI library for kids using Python and Kivy.

## Features
- Easy to use syntax
- Designed for mobile and desktop
- Build buttons, labels, inputs, and popups easily
- Now supports colors and images

## Installation
```bash
pip install kidsui
```

## Example Usage
```python
from kidsui import KidsUIApp

app = KidsUIApp("My First App")
app.label("Welcome to the App!", color=(0, 1, 0, 1))
name_input = app.text_input("Your name")
app.button("Say Hello", lambda: app.alert("Hi " + name_input.text), background_color=(1, 1, 0, 1))
app.image("my_image.png", width=300, height=200)
app.colored_box(color=(1, 0, 1, 1), height=50)
app.run()
```

## Requirements
- Python 3.7+
- Kivy

## License
MIT License
