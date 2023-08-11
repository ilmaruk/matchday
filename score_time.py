#!/usr/bin/env python3

import os
import queue
import random
import threading
import time

from dotenv import load_dotenv

import certifi

import paho.mqtt.client as paho
import paho.mqtt as mqtt

import luma.core.legacy.font as lfont

from matchday.board.routines import goal
from matchday.board.utils import init_device, display_score

load_dotenv()

# the_font = lfont.proportional(lfont.CP437_FONT)
# the_font = lfont.proportional(lfont.LCD_FONT)
the_font = lfont.proportional(lfont.SINCLAIR_FONT)


def subscriber(lock: threading.Lock, event: threading.Event, q: queue.Queue, device):
    def on_message(client, userdata, msg):
        who = random.choice(["home", "away"])
        lock.acquire()
        goal(device, the_font, who)
        lock.release()
        q.put(who)

    client = paho.Client(client_id="score_client",
                         userdata=None, protocol=paho.MQTTv5)
    client.tls_set(certifi.where(), tls_version=mqtt.client.ssl.PROTOCOL_TLS)
    client.username_pw_set(os.getenv("MQTT_USER"), os.getenv("MQTT_PASS"))
    client.connect(os.getenv("MQTT_HOST"), int(os.getenv("MQTT_PORT", 8333)))
    client.subscribe("matchday/#", qos=1)

    client.on_message = on_message

    while True:
        client.loop()
        time.sleep(.1)


def displayer(lock: threading.Lock, event: threading.Event, q: queue.Queue, device, clicks: int):
    score = [0, 0]
    display_score(device, score, the_font)

    while True:
        who = q.get(block=True)
        idx = 0 if who == "home" else 1
        score[idx] += 1
        display_score(device, score, the_font)


if __name__ == "__main__":
    device = init_device()

    lock = threading.Lock()
    event = threading.Event()
    q = queue.Queue()

    s = threading.Thread(target=subscriber, args=(
        lock, event, q, device), daemon=True)
    d = threading.Thread(target=displayer, args=(
        lock, event, q, device, 20), daemon=True)
    d.start()
    s.start()
    s.join()
