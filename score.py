#!/usr/bin/env python3

import datetime
import os
import queue
import random
import threading
import time

from dotenv import load_dotenv

import certifi

import paho.mqtt.client as paho
import paho.mqtt as mqtt

from luma.led_matrix.device import max7219
from luma.core.interface.serial import spi, noop
import luma.core.legacy as llegacy
import luma.core.legacy.font as lfont #import proportional, CP437_FONT, TINY_FONT, SINCLAIR_FONT, LCD_FONT
import luma.core.render as lrender

load_dotenv()

the_font = lfont.proportional(lfont.CP437_FONT)
the_font = lfont.proportional(lfont.LCD_FONT)
the_font = lfont.proportional(lfont.SINCLAIR_FONT)


def subscriber(lock: threading.Lock, event: threading.Event, q: queue.Queue, display):
    def on_message(client, userdata, msg):
        who = random.choice(["home", "away"])
        lock.acquire()
        goal(display, the_font, who)
        lock.release()
        q.put(who)

    client = paho.Client(client_id="score_client", userdata=None, protocol=paho.MQTTv5)
    client.tls_set(certifi.where(), tls_version=mqtt.client.ssl.PROTOCOL_TLS)
    client.username_pw_set(os.getenv("MQTT_USER"), os.getenv("MQTT_PASS"))
    client.connect(os.getenv("MQTT_HOST"), int(os.getenv("MQTT_PORT", 8333)))
    client.subscribe("matchday/#", qos=1)

    client.on_message = on_message

    while True:
        client.loop()
        time.sleep(.1)


def displayer(lock: threading.Lock, event: threading.Event, q: queue.Queue, display, clicks: int):
    score = [0, 0]
    display_score(display, score, the_font)

    ticks = 0
    while True:
        who = q.get(block=True)
        idx = 0 if who == "home" else 1
        score[idx] += 1
        ticks = 0
        display_score(display, score, the_font)


def display_score(display, score, font):
    text = f"{score[0]}-{score[1]}"
    display_centered(display, text, font)


def display_centered(display, text, font):
    pos = get_centered_pos(display, text, font)
    with lrender.canvas(device) as draw:
        llegacy.text(draw, pos, text, fill="white", font=font)


def get_centered_pos(display, text, font):
    size = llegacy.textsize(text, font)
    x = (display.width - size[0]) / 2
    y = (display.height - size[1]) / 2
    return (x, y)


def goal(device, font, who):
    texts = [who.upper(), "GOAL"]
    fonts = [
                lfont.proportional(lfont.CP437_FONT),
                lfont.proportional(lfont.LCD_FONT),
                lfont.proportional(lfont.SINCLAIR_FONT),
            ]
    for i in range(12):
        fg = random.choice(["white", "black"])
        bg = "white" if fg == "black" else "black"
        with lrender.canvas(device) as draw:
           draw.rectangle([(0, 0), (31,7)], fill=bg)
           txt = texts[i%2]
           font = random.choice(fonts)
           pos = get_centered_pos(device, txt, font)
           llegacy.text(draw, pos, txt, fill=fg, font=font)
        time.sleep(.25)


if __name__ == "__main__":
    serial = spi(port=0, device=0, gpio=noop())
    device = max7219(serial, cascaded=4, block_orientation=-90, rotate=2)
    device.contrast(1)

    lock = threading.Lock()
    event = threading.Event()
    q = queue.Queue()

    s = threading.Thread(target=subscriber, args=(lock, event, q, device), daemon=True)
    d = threading.Thread(target=displayer, args=(lock, event, q, device, 20), daemon=True)
    d.start()
    s.start()
    s.join()

