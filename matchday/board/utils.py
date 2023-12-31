from luma.led_matrix.device import max7219
from luma.core.interface.serial import spi, noop

import luma.core.legacy as llegacy
import luma.core.legacy.font as lfont
import luma.core.render as lrender


def init_device():
    serial = spi(port=0, device=0, gpio=noop())
    device = max7219(serial, cascaded=4, block_orientation=-90, rotate=2)
    device.contrast(1)
    print("Board initialised")
    return device


def display_score(device, score, font):
    """Displays the current score.
    """
    text = f"{score[0]}-{score[1]}"
    display_centered(device, text, font)


def display_centered(device, text, font, fg="white", bg="black", xoffs=0, yoffs=0):
    """Displays a text centered.
    """
    pos = get_centered_pos(device, text, font, xoffs, yoffs)
    with lrender.canvas(device) as draw:
        draw.rectangle([(0, 0), (31, 7)], fill=bg)
        llegacy.text(draw, pos, text, fill=fg, font=font)


def get_centered_pos(device, text, font, xoffs=0, yoffs=0):
    """Returns the start position to render a centered text.
    """
    size = llegacy.textsize(text, font)
    x = (device.width - size[0]) / 2
    y = (device.height - size[1]) / 2
    return (x + xoffs, y + yoffs)
