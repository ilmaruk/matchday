import datetime
import time

import luma.core.legacy as llegacy
import luma.core.legacy.font as lfont
import luma.core.render as lrender
import luma.core.virtual as lvirtual

from matchday.board.utils import init_device, display_centered, get_centered_pos_draw


the_font = lfont.proportional(lfont.SINCLAIR_FONT)


def seconds_to_str(seconds: int) -> str:
    mins = int(seconds / 60)
    secs = seconds % 60
    return f"{mins:02d}:{secs:02d}"


def clock(device, duration: int, start: datetime.datetime, font):
    print("GO GO GO!")
    score = "2-1"
    text = seconds_to_str(duration)

    view = 0

    virtual = lvirtual.viewport(
        device, width=device.width, height=device.height*2)
    with lrender.canvas(virtual) as draw:
        pos = get_centered_pos_draw(
            device.width, device.height, text, font)
        llegacy.text(draw, pos, text, fill="white", font=font)
        pos = get_centered_pos_draw(
            device.width, device.height, score, font, yoffs=device.height)
        llegacy.text(draw, pos, score, fill="white", font=font)

    tick = 0
    while True:
        now = datetime.datetime.now()
        diff = int((now - start).total_seconds())
        if diff >= duration:
            break
        text = seconds_to_str(duration - diff)

        with lrender.canvas(virtual) as draw:
            pos = get_centered_pos_draw(
                device.width, device.height, text, font)
            llegacy.text(draw, pos, text, fill="white", font=font)
            pos = get_centered_pos_draw(
                device.width, device.height, score, font, yoffs=device.height)
            llegacy.text(draw, pos, score, fill="white", font=font)

        tick += 1
        if tick % 50 == 0:
            # switch to other view
            view = (view + 1) % 2
            vals = [(7, -1, -1), (1, 9, 1)]
            for i in range(*vals[view]):
                virtual.set_position((0, i))
                time.sleep(.1)

        time.sleep(.1)

    display_centered(device, "Time's Up", lfont.proportional(
        lfont.TINY_FONT), fg="black", bg="white")
    time.sleep(4)


if __name__ == "__main__":
    device = init_device()
    clock(device, 600, datetime.datetime.now(), the_font)
