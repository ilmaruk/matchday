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
from matchday.board.virtual import VirtualBoard
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


def sub(device, q: queue.Queue):
    print("sub started")

    clock = mmodels.Clock()
    score = mmodels.Score()

    board = VirtualBoard(device, 2)

    now = datetime.datetime.now()
    board.set_text(1, now.strftime("%H:%M:%S"), clock_font)
    board.update(fill="white")
    board.set_row(1)

    while True:
        try:
            event = q.get(block=False)
        except queue.Empty:
            # No event
            now = datetime.datetime.now()
            board.set_text(1, now.strftime("%H:%M:%S"), clock_font)
            board.update(fill="white")
        else:
            if event.is_type("MATCH_START"):
                clock.start(event._meta["duration"])
                board.set_text(0, str(clock), clock_font)
                board.update(fill="white")
                board.set_row(0)
                break
        
        time.sleep(.1)

    print("game started")
    while True:
        try:
            event = q.get(block=False)
        except queue.Empty:
            # No event
            pass
        else:
            if event.is_type("GOAL"):
                goal(device, score_font, event._meta["who"])
                score.goal(0 if event._meta["who"] == "home" else 1)
                board.set_text(1, str(score), score_font)
                board.update(fill="white")
                board.set_row(1)

        time.sleep(0.1)

        clock.update()
        if not clock.is_running():
            break

        board.set_text(0, str(clock), clock_font)
        board.update(fill="white")

    board.set_text(0, "Time's Up", tiny_font)
    board.update(fill="white")
    board.set_row(0)
    time.sleep(4)

    board.scroll_up()
    time.sleep(4)


def pub(q: queue.Queue):
    print("pub started")
    started = False
    t = 0
    while True:
        if t == 500:
            started = True
            q.put(MatchStartEvent(11))
        elif started and random.random() < .001:
            q.put(GoalEvent(random.choice(["home", "away"])))

        t += 1
        time.sleep(0.1)


if __name__ == "__main__":
    device = init_device()

    q = queue.Queue()
    p = threading.Thread(target=pub, args=(q,), daemon=True)
    s = threading.Thread(target=sub, args=(device, q))
    s.start()
    p.start()
    s.join()