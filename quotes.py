import datetime
import time

import requests

import luma.core.legacy as llegacy
import luma.core.legacy.font as lfont
import luma.core.render as lrender

from matchday.board.utils import init_device
# from matchday.board.routines import goal
# from matchday.board.virtual import VirtualBoard
# import matchday.models as mmodels

# score_font = lfont.proportional(lfont.CP437_FONT)
clock_font = lfont.proportional(lfont.ATARI_FONT)
# tiny_font = lfont.proportional(lfont.TINY_FONT)

NINJA_API_URL = "https://api.api-ninjas.com/v1/quotes"
NINJA_API_API_KEY = "yfNcExW4lF1ZTUPUTy4BzQ==Jr0gxqxEGhoUNNYv"


def get_quote() -> str:
    resp = requests.get(NINJA_API_URL, headers={"X-Api-Key": NINJA_API_API_KEY}).json()
    quote = f"{resp[0]['quote']} ({resp[0]['author']})"
    print("got quote", quote)
    return quote

if __name__ == "__main__":
    device = init_device()

    ticks = 0
    while True:
        ticks += 1
        if ticks % 120 == 1:
            quote = get_quote()
            llegacy.show_message(device, quote, fill="white", font=clock_font, scroll_delay=0.02)

        with lrender.canvas(device) as draw:
            llegacy.text(draw, (2, 0), datetime.datetime.now().strftime("%H:%M:%S"), font=clock_font, fill="white")

        time.sleep(.5)