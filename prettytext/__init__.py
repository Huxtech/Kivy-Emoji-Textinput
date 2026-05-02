
from os.path import dirname, join
import re



class PrettyText:
    def __init__(self):
        self.emoji_pattern = re.compile(
            "["
            "\U0001F300-\U0001F5FF"
            "\U0001F600-\U0001F64F"
            "\U0001F680-\U0001F6FF"
            "\U0001F700-\U0001F77F"
            "\U0001F780-\U0001F7FF"
            "\U0001F800-\U0001F8FF"
            "\U0001F900-\U0001F9FF"
            "\U0001FA00-\U0001FA6F"
            "\U0001FA70-\U0001FAFF"
            "]+"
        )
        
    def getfont(self, font_name):
        return join(dirname(__file__), font_name)



    def create_markup_text(self, text):
        normal_font=self.getfont("DejaVuSans.ttf")
        emoji_font=self.getfont("twemoji.ttf")
        """
        Returns a single string with Kivy markup for text + emoji.
        Normal text uses normal_font, emoji uses emoji_font.
        """
        
        parts = self.emoji_pattern.split(text)
        emojis = self.emoji_pattern.findall(text)
        
        markup = ""
        for i, part in enumerate(parts):
            if part:
                markup += f"[font={normal_font}]{part}[/font]"
            if i < len(emojis):
                markup += f"[font={emoji_font}]{emojis[i]}[/font]"
        
        return markup
    
    def parse_markup(self, text):
        parts = []
        pattern = r'(\[b\].*?\[/b\]|\[color=.*?\].*?\[/color\]|\[font=.*?\].*?\[/font\])'
        split = re.split(pattern, text)

        for part in split:
            if not part:
                continue

            style = {
                "text": "",
                "bold": False,
                "color": (1, 1, 1, 1),
                "font": "Roboto"  # default font
            }

            # BOLD
            if part.startswith("[b]"):
                style["text"] = part[3:-4]
                style["bold"] = True

            # COLOR
            elif part.startswith("[color="):
                color_code = re.findall(r'\[color=(.*?)\]', part)[0]
                content = re.sub(r'\[color=.*?\]|\[/color\]', '', part)

                r = int(color_code[1:3], 16) / 255
                g = int(color_code[3:5], 16) / 255
                b = int(color_code[5:7], 16) / 255

                style["text"] = content
                style["color"] = (r, g, b, 1)

            # FONT
            elif part.startswith("[font="):
                font_name = re.findall(r'\[font=(.*?)\]', part)[0]
                content = re.sub(r'\[font=.*?\]|\[/font\]', '', part)

                style["text"] = content
                style["font"] = font_name

            else:
                style["text"] = part

            parts.append(style)
        
        return parts
            
        