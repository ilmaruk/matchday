import random
import time

import luma.core.legacy as llegacy
import luma.core.legacy.font as lfont
import luma.core.render as lrender

from .utils import get_centered_pos


def goal(device, font, who):
    texts = [who.upper(), "GOAL"]
    fonts = [
        lfont.proportional(lfont.CP437_FONT),
        lfont.proportional(lfont.LCD_FONT),
        lfont.proportional(lfont.SINCLAIR_FONT),
        lfont.proportional(lfont.ATARI_FONT),
    ]
    for i in range(12):
        fg = random.choice(["white", "black"])
        bg = "white" if fg == "black" else "black"
        with lrender.canvas(device) as draw:
            draw.rectangle([(0, 0), (31, 7)], fill=bg)
            txt = texts[i % 2]
            font = random.choice(fonts)
            pos = get_centered_pos(device, txt, font)
            llegacy.text(draw, pos, txt, fill=fg, font=font)
        time.sleep(.25)
