from os.path import dirname, join
import re


class PrettyText:
    _TAG = re.compile(r'\[(/?)(b|color|font)(?:=([^\]]*))?\]')

    def __init__(self):
        ZWJ = "\u200D"
        VS16 = "\uFE0F"
        SKIN = "[\U0001F3FB-\U0001F3FF]"

        BASE = (
            "["
            "\U0001F300-\U0001FAFF"
            "\U0001F170\U0001F171\U0001F17E\U0001F17F"
            "\U0001F18E\U0001F191-\U0001F19A"
            "\U0001F201\U0001F202\U0001F21A\U0001F22F"
            "\U0001F232-\U0001F23A\U0001F250\U0001F251"
            "\u3030\u303D\u3297\u3299"
            "\u2600-\u27BF"
            "\u2B50\u2B55\u2B1B\u2B1C"
            "\u231A\u231B\u23E9-\u23F3"
            "\u2934\u2935"
            "]"
        )

        element = f"{BASE}(?:{VS16}|{SKIN})?"

        tag_flag = "\U0001F3F4[\U000E0020-\U000E007E]+\U000E007F"
        keycap = "[0-9#*]\uFE0F?\u20E3"
        flag = "[\U0001F1E6-\U0001F1FF]{2}"
        sequence = f"{element}(?:{ZWJ}{element})*"

        self.emoji_pattern = re.compile(f"{tag_flag}|{keycap}|{flag}|{sequence}")
        self._emoji_font = self.getfont("twemoji.ttf")

        # Small memoization caches. Kept as plain dicts with a hard size
        # cap (rather than functools.lru_cache) since the cache key needs
        # to normalize an incoming color list/tuple first.
        self._markup_cache = {}
        self._parse_cache = {}
        self._cache_limit = 512

    def getfont(self, font_name):
        return join(dirname(__file__), font_name)

    @staticmethod
    def _escape(text):
        return text.replace("&", "&amp;").replace("[", "&bl;").replace("]", "&br;")

    @staticmethod
    def _unescape(text):
        return text.replace("&bl;", "[").replace("&br;", "]").replace("&amp;", "&")

    @staticmethod
    def _to_hex(color):
        """(r, g, b[, a]) floats 0-1  ->  'rrggbb' or 'rrggbbaa'."""
        vals = [max(0, min(255, round(c * 255))) for c in color]
        return "".join(f"{v:02x}" for v in vals[:4])

    @staticmethod
    def _from_hex(code):
        """'#rrggbb' / 'rrggbb' / '#rrggbbaa'  ->  (r, g, b, a) floats."""
        code = code.lstrip("#")
        try:
            r = int(code[0:2], 16) / 255
            g = int(code[2:4], 16) / 255
            b = int(code[4:6], 16) / 255
            a = int(code[6:8], 16) / 255 if len(code) >= 8 else 1
            return (r, g, b, a)
        except ValueError:
            return (1, 1, 1, 1)

    def create_markup_text(self, text, normal_font="", foreground_color=(1, 1, 1, 1)):
        """
        Returns a single string with Kivy markup for text + emoji.
        Plain text gets the font and foreground_color; emoji only get the
        emoji font, so the color never tints them.
        """
        color_key = tuple(foreground_color)
        cache_key = (text, normal_font, color_key)
        cached = self._markup_cache.get(cache_key)
        if cached is not None:
            return cached

        color_hex = self._to_hex(foreground_color)

        def plain_markup(chunk):
            chunk = self._escape(chunk)
            if normal_font:
                chunk = f"[font={normal_font}]{chunk}[/font]"
            return f"[color=#{color_hex}]{chunk}[/color]"

        markup = []
        last = 0
        for m in self.emoji_pattern.finditer(text):
            if m.start() > last:
                markup.append(plain_markup(text[last:m.start()]))
            markup.append(f"[font={self._emoji_font}]{m.group()}[/font]")
            last = m.end()

        if last < len(text):
            markup.append(plain_markup(text[last:]))

        result = "".join(markup)

        if len(self._markup_cache) >= self._cache_limit:
            self._markup_cache.clear()
        self._markup_cache[cache_key] = result

        return result

    def parse_markup(self, text):
        """
        Returns a list of dicts: text, bold, color, font, emoji.
        Handles nested tags, e.g. [color=..][font=..]abc[/font][/color].
        """
        cached = self._parse_cache.get(text)
        if cached is not None:
            return cached

        parts = []
        state = {"b": False, "color": (1, 1, 1, 1), "font": "Roboto"}
        stack = []  # (tag, previous value)

        def emit(chunk):
            if not chunk:
                return
            parts.append({
                "text": self._unescape(chunk),
                "bold": state["b"],
                "color": state["color"],
                "font": state["font"],
                "emoji": state["font"] == self._emoji_font,
            })

        pos = 0
        for m in self._TAG.finditer(text):
            emit(text[pos:m.start()])
            pos = m.end()

            closing, tag, value = m.group(1), m.group(2), m.group(3)

            if not closing:
                stack.append((tag, state[tag]))
                if tag == "b":
                    state["b"] = True
                elif tag == "color":
                    state["color"] = self._from_hex(value or "")
                else:
                    state["font"] = value or "Roboto"
            else:
                for i in range(len(stack) - 1, -1, -1):
                    if stack[i][0] == tag:
                        state[tag] = stack[i][1]
                        del stack[i]
                        break

        emit(text[pos:])

        if len(self._parse_cache) >= self._cache_limit:
            self._parse_cache.clear()
        self._parse_cache[text] = parts

        return parts