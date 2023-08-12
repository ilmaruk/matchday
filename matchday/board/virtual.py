import time
import typing

import luma.core.legacy as llegacy
import luma.core.render as lrender
import luma.core.virtual as lvirtual

from matchday.board.utils import get_centered_pos

DIRECTION_UP = 1
DIRECTION_DOWN = -1


class InvalidVirtualBoardRowError(Exception):
    def __init__(self, message: str):
        super().__init__(message=message)


class VirtualBoard:
    """A virtual board with a number or rows.
    The top most row (default) has index 0.
    """

    def __init__(self, device, rows) -> None:
        self._device = device
        self._rows = rows
        self._row = 0
        self._virtual = lvirtual.viewport(device, width=device.width, height=device.height*rows)
        self._texts = [("", None)] * 3

    def set_text(self, row: int, text: str, font):
        """Set text and font for a specific row.
        """
        if row < 0 or row >= self._rows:
            raise InvalidVirtualBoardRowError(f"{row:d} is not a valid row for this virtual board")
        
        self._texts[row] = (text.replace("0", "O"), font)

    def update(self, **kwargs) -> None:
        """Update the board.
        """
        with lrender.canvas(self._virtual) as draw:
            for row, (text, font) in enumerate(self._texts):
                pos = get_centered_pos(self._device, text, font)
                llegacy.text(draw, (pos[0], pos[1] + self._device.height * row), text, font=font, **kwargs)

    def set_row(self, row: int) -> None:
        """Display the selected row.
        """
        if row < 0 or row >= self._rows:
            raise InvalidVirtualBoardRowError(f"{row:d} is not a valid row for this virtual board")
        
        self._row = row
        pos = (0, self._device.height * self._row)
        self._virtual.set_position(pos)

    def scroll_up(self, delay: float = 0.1) -> None:
        """Scroll up (e.g.: 1 to 0)
        """
        if self._row == self._rows - 1:
            raise InvalidVirtualBoardRowError("cannot scroll up from bottom row")

        self._scroll(DIRECTION_UP, delay)
        self._row += 1

    def scroll_down(self, delay: float = 0.1) -> None:
        """Scroll up (e.g.: 1 to 2)
        """
        if self._row == 0:
            raise InvalidVirtualBoardRowError("cannot scroll down from top row")

        self._scroll(DIRECTION_DOWN, delay)
        self._row -= 1
        
    def _scroll(self, direction: int, delay: float = 0.1) -> None:
        range_meta = (
            self._row * self._device.height + direction,
            (self._row + direction) * self._device.height + direction, direction
            )
        for y in range(*range_meta):
            self._virtual.set_position((0, y))
            time.sleep(delay)
