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
    def __init__(self, duration: int) -> None:
        self._duration = duration
        self._started_at = None

    def start(self) -> None:
        self._started_at = datetime.datetime.now()

    def is_over(self) -> bool:
        return self._diff() >= self._duration

    def __str__(self) -> str:
        seconds = self._duration - self._diff()
        if seconds >= 60:
            s = round(seconds, 0)
            mins = int(s / 60)
            secs = int(s % 60)
            text = f"{mins:02d}:{secs:02d}"
        else:
            text = f"{seconds:02.2f}"

        return text.replace("0", "O")

    def _diff(self) -> float:
        now = datetime.datetime.now()
        return (now - self._started_at).total_seconds()