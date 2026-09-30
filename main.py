from kivy.uix.accordion import NumericProperty

from kivy.app import App
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.properties import NumericProperty

try:
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
except:pass

KV = '''
#: import HTextInput input.HTextInput
#: set font_size '20dp'
BoxLayout:
    orientation: 'vertical'
    padding: '20dp'
    spacing: '10dp'
    HTextInput:
        id: target
        font_size: font_size
        size_hint_y: None
        height: self.minimum_height
        multiline: False
        input_type: "text"
        text: 'normal😂'
        foreground_color: 0, 1, 0, 1
        font_name: 'prettytext/DejaVuSans.ttf'

    HTextInput:
        size_hint_y: None
        font_size: font_size
        height: self.minimum_height
        multiline: False
        password: True
        password_mask: '•'
        foreground_color: 1, 0, 0, 1
        text: 'password'

    HTextInput:
        font_size: font_size
        size_hint_y: None
        height: self.minimum_height
        multiline: False
        readonly: True
        text: 'readonly'

    HTextInput:
        font_size: font_size
        size_hint_y: None
        height: self.minimum_height
        multiline: False
        disabled: True
        text: 'disabled'

    HTextInput:
        font_size: font_size
        hint_text: 'normal with hint text'

    HTextInput:
        font_size: font_size
        text: 'default'

    HTextInput:
        font_size: font_size
        text: 'bubble & handles'
        use_bubble: True
        use_handles: True

    HTextInput:
        font_size: font_size
        text: 'no wrap'
        do_wrap: False

    HTextInput:
        font_size: font_size
        text: 'multiline readonly'
        disabled: app.time % 5 < 2.5
    Button:
        text: 'Print'
        on_release: print(str(target.text))
'''

class TextInputApp(App):
    time = NumericProperty()

    def build(self):
        Clock.schedule_interval(self.update_time, 0)
        return Builder.load_string(KV)

    def update_time(self, dt):
        self.time += dt
            
if __name__ == '__main__':
    TextInputApp().run()
