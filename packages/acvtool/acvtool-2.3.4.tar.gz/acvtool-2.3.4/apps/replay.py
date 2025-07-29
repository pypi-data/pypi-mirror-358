import logging
import time
from context import running
import os


class Tap(object):
    def __init__(self, ts, x, y):
        self.ts = ts # time stamp "SECONDS.MILLISECONDS"
        self.x = x
        self.y = y
    
    def run(self):
        cmd = "adb shell input touchscreen tap {} {}".format(self.x, self.y)
        logging.info(cmd)
        os.system(cmd)

class Swipe(object):
    def __init__(self, ts, x1, y1, x2, y2, duration):
        self.ts = ts
        self.x1 = x1
        self.x2 = x2
        self.y1 = y1
        self.y2 = y2
        self.duration = duration

    def run(self):
        cmd = "adb shell input touchscreen swipe {} {} {} {} {}".format(
            self.x1, self.y1, self.x2, self.y2, self.duration
        )
        logging.info(cmd)
        os.system(cmd)

def get_duration_ms(ts1, ts2):
    sec1, mill1 = map(int, ts1.split('.'))
    sec2, mill2 = map(int, ts2.split('.'))
    seconds = sec2-sec1
    milliseconds = mill2-mill1
    if milliseconds < 0:
        seconds -= 1
        milliseconds += 1000000
    return seconds*1000 + milliseconds/1000

def read(path):
    with open(path,'r') as f:
        lines = map(lambda x: x.split(), f.readlines())
    event_sequence = []
    i = 0
    logging.info("start reading cycle")
    while i < len(lines):
        logging.info(" ".join(lines[i]))
        if lines[i][-1] == 'DOWN':
            i += 1
            points = []
            while lines[i][-1] != 'UP':
                logging.info(" ".join(lines[i]))
                if lines[i][-2] == 'ABS_MT_POSITION_X' and \
                    lines[i+1][-2] == 'ABS_MT_POSITION_Y':
                    time_point = (lines[i][1][:-1], int(lines[i][-1], 16), int(lines[i+1][-1], 16))
                    points.append(time_point)
                i += 1
            if lines[i][-1] == 'UP':
                if len(points) > 3:
                    logging.info("swipe identified")
                    p1 = points[0]
                    p2 = points[-1]
                    duration = get_duration_ms(p1[0], p2[0])
                    event = Swipe(p1[0], p1[1], p1[2], p2[1], p2[2], duration)
                    event_sequence.append(event)
                else:
                    if points:
                        logging.info("tap identified")
                        p1 = points[0]
                        event = Tap(p1[0], p1[1], p1[2])
                        event_sequence.append(event)
        i += 1
    return event_sequence

def play(sequence):
    last_ts = sequence[0].ts
    for e in sequence:
        delay_ms = get_duration_ms(last_ts, e.ts)
        time.sleep(delay_ms/1000.)
        e.run()
        last_ts = e.ts

logging.basicConfig(format="%(asctime)s: %(message)s", datefmt="%H:%M:%S", level=logging.INFO)

logging.info("read")
sequence = read("test.txt")
logging.info("play")
play(sequence)

