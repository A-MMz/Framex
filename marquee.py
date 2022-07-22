from kivy import Config
import os
from ast import literal_eval
from kivy.animation import Animation
from kivy.lang import Builder
from kivy.properties import ObjectProperty, StringProperty, NumericProperty, BooleanProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.clock import Clock
from kivy.core.text import Label as CoreLabel


if 'KIVY_DOC' not in os.environ:
    _default_font_paths = literal_eval(Config.get('kivy', 'default_font'))
    DEFAULT_FONT = _default_font_paths.pop(0)
else:
    DEFAULT_FONT = None

Builder.load_string('''
<Marquee>:
    StencilView:
        id: sten
        pos: root.pos
        size_hint: None, None
        size: root.size
        Image:
            id: label
            texture: root.texture
            pos: root.pos
            size_hint: None, None
            size: self.texture_size
''')


class Marquee(FloatLayout):
    texture = ObjectProperty()
    text = StringProperty()
    duration = NumericProperty(2)
    font_name = StringProperty(DEFAULT_FONT)
    font_size = NumericProperty(15)
    bold = BooleanProperty(False)
    italic = BooleanProperty(False)
    padding = NumericProperty(0)

    def __init__(self, **kwargs):
        super(Marquee, self).__init__(**kwargs)
        self.anim = None
        self.x_original = None
        fbind = self.fbind
        redraw = self.redraw
        fbind('text', redraw)
        fbind('duration', redraw)
        fbind('font_name', redraw)
        fbind('font_size', redraw)
        fbind('bold', redraw)
        fbind('italic', redraw)
        fbind('padding', redraw)

    def on_x(self, *args):
        self.x_original = self.x
        Clock.schedule_once(self.redraw)

    def redraw(self, *args):
        if self.x_original is None:
            return
        if self.text == '':
            self.texture = None
            return
        label = CoreLabel(text=self.text, font_name=self.font_name, font_size=self.font_size,
                          bold=self.bold, italic=self.italic, padding=self.padding)
        label.refresh()
        self.texture = label.texture
        Clock.schedule_once(self.do_anim)

    def do_anim(self, *args):
        if self.anim is not None:
            self.anim.cancel(self.ids.label)
            self.anim = None
        self.ids.label.x = self.x_original
        x_end = self.ids.label.x - self.ids.label.width
        self.anim = Animation(x=x_end, duration=self.duration)
        self.anim.bind(on_complete=self.do_anim)
        self.anim.start(self.ids.label)


if __name__ == "__main__":
    from kivy.app import App

    class TestApp(App):
        def build(self):
            return Builder.load_string('''
FloatLayout:
    Marquee:
        text: 'This is a long text for testing the Marquee widget.'
        font_name: 'DejaVuSans'
        duration: 7
        padding: 10
        pos_hint: {'center_x': 0.5, 'center_y': 0.5}
        size_hint: None, None
        size: 100, 50
            ''')

    TestApp().run()