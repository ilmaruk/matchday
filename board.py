# import datetime
# import json

# from matchday.models import GoalEvent

# ge = GoalEvent(at=datetime.datetime.now(), who="home")
# print(json.dumps(ge))

import datetime
import json
import os
import queue
import threading
import time

from dotenv import load_dotenv

import certifi
import paho.mqtt.client as paho
import paho.mqtt as mqtt

import jsonpickle

import luma.core.legacy as llegacy
import luma.core.legacy.font as lfont
import luma.core.render as lrender

from matchday.board.utils import init_device
from matchday.board.routines import goal
import matchday.models as mmodels
from matchday.events import *

DISPLAY_CLOCK = 0
DISPLAY_SCORE = 1

score_font = lfont.proportional(lfont.CP437_FONT)
clock_font = lfont.proportional(lfont.ATARI_FONT)
tiny_font = lfont.proportional(lfont.TINY_FONT)


def display_centered_text(device, text: str, **kwargs) -> None:
    text_width, text_height = llegacy.textsize(text, kwargs.get("font"))
    x = int((device.width - (text_width - 1)) / 2)
    y = int((device.height - (text_height - 1)) / 2)
    with lrender.canvas(device) as draw:
        llegacy.text(draw, (x, y), text, **kwargs)


def display_time(device, prev_time: str = "", **kwargs) -> str:
    curr_time = datetime.datetime.now().strftime("%H:%M:%S")
    if curr_time != prev_time:
        display_centered_text(device, curr_time, **kwargs)

    return curr_time


def display_clock(device, clock: mmodels.Clock, **kwargs) -> str:
    display_centered_text(device, str(clock), **kwargs)


def display_score(device, score: mmodels.Score, **kwargs) -> str:
    display_centered_text(device, str(score), **kwargs)


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
            curr_time = display_time(
                device, curr_time, font=clock_font, fill="white")
        else:
            if event.is_type("MATCH_START"):
                clock.start(event._meta["duration"])
                break

        time.sleep(.1)

    # clock.start(600)
    score = mmodels.Score()

    print("game started")
    display = DISPLAY_CLOCK
    ticks = 0
    while True:
        try:
            event = events.get(block=False)
        except queue.Empty:
            clock.update()
            if not clock.is_running():
                break

            if display == DISPLAY_CLOCK:
                # display_clock(device, clock, font=clock_font, fill="white")
                text = f"{score._score[0]}|{str(clock)}|{score._score[1]}"
                display_centered_text(
                    device, text, font=clock_font, fill="white")
            elif display == DISPLAY_SCORE:
                display_score(device, score, font=score_font, fill="white")

            ticks += 1
            if ticks == 50:
                ticks = 0
                display = DISPLAY_SCORE if display == DISPLAY_CLOCK else DISPLAY_CLOCK
        else:
            if event.is_type("GOAL"):
                score.goal(0 if event.meta["who"] == "home" else 1)
                goal(device, score_font, event.meta["who"])
                display_score(device, score, font=score_font, fill="white")
                display = DISPLAY_SCORE
                ticks = 0
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

    def on_message(client, userdata, msg):
        print(msg.payload)
        event = jsonpickle.decode(msg.payload)
        print(event)
        q.put(event)

    client = paho.Client(client_id="score_client",
                         userdata=None, protocol=paho.MQTTv5)
    client.tls_set(certifi.where(), tls_version=mqtt.client.ssl.PROTOCOL_TLS)
    client.username_pw_set(os.getenv("MQTT_USER"), os.getenv("MQTT_PASS"))
    client.connect(os.getenv("MQTT_HOST"), int(os.getenv("MQTT_PORT", 8333)))
    client.subscribe("matchday/#", qos=1)

    client.on_message = on_message

    while True:
        client.loop()


if __name__ == "__main__":
    load_dotenv()

    device = init_device(4)

    events_queue = queue.Queue()
    p = threading.Thread(target=board_manager, args=(device, events_queue))
    s = threading.Thread(target=events_subscriber,
                         args=(events_queue,), daemon=True)
    s.start()
    p.start()
    p.join()
