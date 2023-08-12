import datetime

from dataclasses import dataclass

HOME = 0
AWAY = 1


class BaseEvent():
    def __init__(self, at: datetime.datetime):
        self.at = at


@dataclass
class GoalEvent(BaseEvent):
    def __init__(self, at: datetime.datetime, who: str):
        super().__init__(at)
        self.who = who

    def __dict__(self):
        return {
            "time": self.at,
            "who": self.who,
        }


class Score:
    def __init__(self) -> None:
        self._score = [0, 0]

    def goal(self, who: int) -> None:
        self._score[who] += 1

    def __str__(self) -> str:
        return f"{self._score[HOME]}-{self._score[AWAY]}".replace("0", "O")


class Clock:
    def __init__(self) -> None:
        self._duration = 0
        self._started_at = None
        self._seconds = 0
        self._running = False

    def start(self, duration: int) -> None:
        self._duration = duration
        self._started_at = datetime.datetime.now()
        self._seconds = self._duration
        self._running = True

    def update(self, now: datetime.datetime = None) -> None:
        if now is None:
            now = datetime.datetime.now()
        diff = (now - self._started_at).total_seconds()
        self._seconds = self._duration - diff
        self._running = diff < self._duration
    
    def is_running(self) -> bool:
        return self._running

    def __str__(self) -> str:
        if self._seconds >= 60:
            s = round(self._seconds, 0)
            mins = int(s / 60)
            secs = int(s % 60)
            text = f"{mins:02d}:{secs:02d}"
        else:
            text = f"{self._seconds:02.2f}"

        return text.replace("0", "O")
