# import datetime
# import json

# from matchday.models import GoalEvent

# ge = GoalEvent(at=datetime.datetime.now(), who="home")
# print(json.dumps(ge))

import datetime
import queue
import random
import threading
import time

import luma.core.legacy.font as lfont

from matchday.board.utils import init_device
from matchday.board.routines import goal
import matchday.models as mmodels

score_font = lfont.proportional(lfont.CP437_FONT)
clock_font = lfont.proportional(lfont.ATARI_FONT)
tiny_font = lfont.proportional(lfont.TINY_FONT)


class Event:
    def __init__(self, type: str, meta: dict) -> None:
        self._type = type
        self._meta = meta
        self._time = datetime.datetime.now()

    def is_type(self, type: str) -> bool:
        return self._type == type

    def __repr__(self) -> str:
        return str(self.__dict__)


class MatchStartEvent(Event):
    def __init__(self, duration: str) -> None:
        meta = {
            "duration": duration
        }
        super().__init__("MATCH_START", meta)


class GoalEvent(Event):
    def __init__(self, who: str) -> None:
        meta = {
            "who": who
        }
        super().__init__("GOAL", meta)


def parse_match_started_event(e: Event) -> None:
    pass


def parse_match_started_event(e: Event) -> None:
    pass


def parse_event(e: Event) -> None:
    print("parsing event", e)


def display_centered_text(device, text: str, **kwargs) -> None:
    with lrender.canvas(device, kwargs.get("background", "black")) as draw:
        llegacy.text(device, (0, 0), text, **kwargs)


def display_time(device, prev_time: str = "", **kwargs) -> str:
    curr_time = datetime.datetime.now().strftime("%H:%M:%S")
    if curr_time != prev_time:
        display_centered_text(device, curr_time, **kwargs)
        
    return curr_time


def display_clock(device, clock: mmodels.Clock, **kwargs) -> str:
    display_centered_text(device, str(clock), **kwargs)


def board_manager(device, events: queue.Queue):
    """Drives what's shown on the board, given the received events.
    Before a game is started, it shows the current time (HH:MM:SS).
    Once the game is started, it alternates between the current score and the game clock.
    """
    print("board_manager started")

    clock = mmodels.Clock()

    curr_time = display_time(device, "", font=clock_font, fill="white")

    # Before a game is started
    while True:
        try:
            event = events.get(block=False)
        except queue.Empty:
            # No event
            curr_time = display_time(device, curr_time, font=clock_font, fill="white")
        else:
            if event.is_type("MATCH_START"):
                clock.start(event._meta["duration"])
                break
        
        time.sleep(.1)

    score = mmodels.Score()

    print("game started")
    while True:
        try:
            event = events.get(block=False)
        except queue.Empty:
            clock.update()
            if not clock.is_running():
                break
            display_clock(device, clock, font=clock_font, fill="white")
        else:
            if event.is_type("GOAL"):
                goal(device, score_font, event._meta["who"])
                score.goal(0 if event._meta["who"] == "home" else 1)
                # board.set_text(1, str(score), score_font)
                # board.update(fill="white")
                # board.set_row(1)

        time.sleep(0.1)

    #     board.set_text(0, str(clock), clock_font)
    #     board.update(fill="white")

    # board.set_text(0, "Time's Up", tiny_font)
    # board.update(fill="white")
    # board.set_row(0)
    # time.sleep(4)

    # board.scroll_up()
    # time.sleep(4)


def events_subscriber(q: queue.Queue):
    """Subscribes to a MQTT topic and process events.
    """
    print("events_subscriber started")
    while True:
        time.sleep(0.1)


if __name__ == "__main__":
    device = init_device()

    events_queue = queue.Queue()
    p = threading.Thread(target=board_manager, args=(events_queue,), daemon=True)
    s = threading.Thread(target=events_subscriber, args=(device, q))
    s.start()
    p.start()
    s.join()