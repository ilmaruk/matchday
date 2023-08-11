import datetime
import random
import time

import luma.core.legacy as llegacy
import luma.core.legacy.font as lfont
import luma.core.render as lrender
import luma.core.virtual as lvirtual

import matchday.models as mmodels
from matchday.board.routines import goal
from matchday.board.utils import init_device, display_centered, get_centered_pos

# the_font = lfont.proportional(lfont.CP437_FONT)
the_font = lfont.proportional(lfont.LCD_FONT)
# the_font = lfont.proportional(lfont.SINCLAIR_FONT)
the_font = lfont.proportional(lfont.SPECCY_FONT)
the_font = lfont.proportional(lfont.ATARI_FONT)

score_font = lfont.proportional(lfont.CP437_FONT)
clock_font = lfont.proportional(lfont.ATARI_FONT)

CLOCK_VIEW = 0
SCORE_VIEW = 1


def seconds_to_str(seconds: float) -> str:
    if seconds >= 60:
        s = round(seconds, 0)
        mins = int(s / 60)
        secs = int(s % 60)
        return f"{mins:02d}:{secs:02d}"

    return f"{seconds:02.2f}"


def draw(virtual, text: str, score: mmodels.Score):
    """Draws clock and score on a virtual 2-lined display.
    """
    with lrender.canvas(virtual) as draw:
        # Clock
        pos = get_centered_pos(virtual, text, clock_font)
        llegacy.text(draw, (pos[0], 0), text, fill="white", font=clock_font)

        # Score
        s = str(score)
        pos = get_centered_pos(virtual, s, score_font, yoffs=device.height)
        llegacy.text(draw, (pos[0], 9), s, fill="white",
                     font=score_font)


def switch_view(virtual, view, delay=.07) -> int:
    """Switches from one view to another and viceversa.
    """
    device_height = int(virtual.height / 2)
    vals = [(device_height - 1, -1, -1), (1, device_height + 1, 1)]
    view = (view + 1) % 2
    for i in range(*vals[view]):
        virtual.set_position((0, i))
        time.sleep(delay)

    return view


def is_goal(prob: float) -> int:
    """Returns the id of the scorer of -1 if no goal happened.
    Biased :D
    """
    if random.random() > prob:
        return -1

    # return random.randint(0, 1)
    return 0


def clock(device, duration: int, start: datetime.datetime, font, with_score=True, delay=.1):
    prob = 3 / 60 / 90 * duration * delay
    score = mmodels.Score()
    clock = mmodels.Clock(duration)
    text = seconds_to_str(duration)

    clock.start()
    print("GO GO GO!")

    view = 0

    virtual = lvirtual.viewport(
        device, width=device.width, height=device.height*2)
    # draw(virtual, text, score)
    draw(virtual, str(clock), score)

    tick = 0
    while True:
        now = datetime.datetime.now()
        diff = (now - start).total_seconds()
        if diff >= duration:
            break
        text = seconds_to_str(duration - diff)

        # draw(virtual, text, score)
        draw(virtual, str(clock), score)

        tick += 1
        if with_score and tick % 50 == 0:
            view = switch_view(virtual, view)

        who = is_goal(prob)
        if who != -1:
            score.goal(who)
            goal(device, None, ["home", "away"][who])
            # draw(virtual, text, score)
            draw(virtual, str(clock), score)
            if view == CLOCK_VIEW:
                view = switch_view(virtual, view)

        time.sleep(delay)

    display_centered(device, "Time's Up", lfont.proportional(
        lfont.TINY_FONT), fg="black", bg="white")
    time.sleep(4)

    display_centered(device, str(score), score_font)
    time.sleep(4)


if __name__ == "__main__":
    device = init_device()
    clock(device, 90, datetime.datetime.now(), the_font, with_score=True)
