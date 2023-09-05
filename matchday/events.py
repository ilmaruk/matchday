import datetime


class Event:
    def __init__(self, type: str, meta: dict) -> None:
        self.type = type
        self.meta = meta
        self.time = datetime.datetime.now()

    def is_type(self, type: str) -> bool:
        return self.type == type

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
