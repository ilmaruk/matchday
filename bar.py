import time

import luma.core.legacy.font as lfont

from matchday.board.utils import init_device
from matchday.board.virtual import VirtualBoard

cp437_font = lfont.proportional(lfont.CP437_FONT)
atari_font = lfont.proportional(lfont.ATARI_FONT)
speccy_font = lfont.proportional(lfont.SPECCY_FONT)

if __name__ == "__main__":
    device = init_device()
    board = VirtualBoard(device, 3)

    board.set_text(0, "ciao", cp437_font)
    board.set_text(1, "hi", cp437_font)
    board.set_text(2, "szia", cp437_font)

    board.update(fill="white")
    time.sleep(2)

    board.set_row(1)
    time.sleep(2)

    board.scroll_down()
    time.sleep(2)

    board.scroll_up()
    time.sleep(2)
    board.scroll_up()
    time.sleep(2)

    board.set_text(1, "0-0", speccy_font)
    board.update(fill="white")
    board.scroll_down(delay=0.05)
    time.sleep(2)
