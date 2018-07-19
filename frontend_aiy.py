#!/usr/bin/env python3

# Basic AIY-based amygdala model frontend - sends joy score from AIY to Nengo
# via Bluetooth.

import argparse
import collections
import io
import logging
import math
import os
import queue
import signal
import threading
import time
import bluetooth
import redis

from aiy._drivers._hat import get_aiy_device_name
from aiy.toneplayer import TonePlayer
from aiy.vision.inference import CameraInference
from aiy.vision.leds import Leds
from aiy.vision.leds import PrivacyLed
from aiy.vision.models import face_detection

from contextlib import contextmanager
from gpiozero import Button
from picamera import PiCamera

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

JOY_COLOR = (255, 70, 0)
SAD_COLOR = (0, 0, 64)

JOY_SCORE_PEAK = 0.85
JOY_SCORE_MIN = 0.10

JOY_SOUND = ('C5q', 'E5q', 'C6q')
SAD_SOUND = ('C6q', 'E5q', 'C5q')
MODEL_LOAD_SOUND = ('C6w', 'G6w', 'C6w')
BEEP_SOUND = ('E6q', 'C6q')

@contextmanager
def stopwatch(message):
    try:
        logger.info('%s...', message)
        begin = time.time()
        yield
    finally:
        end = time.time()
        logger.info('%s done. (%fs)', message, end - begin)


def blend(color_a, color_b, alpha):
    return tuple([math.ceil(alpha * color_a[i] + (1.0 - alpha) * color_b[i]) for i in range(3)])


def average_joy_score(faces):
    if faces:
        return sum([face.joy_score for face in faces]) / len(faces)
    return 0.0


def draw_rectangle(draw, x0, y0, x1, y1, border, fill=None, outline=None):
    assert border % 2 == 1
    for i in range(-border // 2, border // 2 + 1):
        draw.rectangle((x0 + i, y0 + i, x1 - i, y1 - i), fill=fill, outline=outline)

class AtomicValue(object):

    def __init__(self, value):
        self._lock = threading.Lock()
        self._value = value

    @property
    def value(self):
        with self._lock:
            return self._value

    @value.setter
    def value(self, value):
        with self._lock:
            self._value = value

class MovingAverage(object):

    def __init__(self, size):
        self._window = collections.deque(maxlen=size)

    def next(self, value):
        self._window.append(value)
        return sum(self._window) / len(self._window)

class Service(object):

    def __init__(self):
        self._requests = queue.Queue()
        self._thread = threading.Thread(target=self._run)
        self._thread.start()

    def _run(self):
        while True:
            request = self._requests.get()
            if request is None:
                break
            self.process(request)
            self._requests.task_done()

    def join(self):
        self._thread.join()

    def stop(self):
        self._requests.put(None)

    def process(self, request):
        pass

    def submit(self, request):
        self._requests.put(request)

class Player(Service):
    """Controls buzzer."""

    def __init__(self, gpio, bpm):
        super().__init__()
        self._toneplayer = TonePlayer(gpio, bpm)

    def process(self, sound):
        self._toneplayer.play(*sound)

    def play(self, sound):
        self.submit(sound)

class Animator(object):
    """Controls RGB LEDs."""

    def __init__(self, leds, done):
        self._leds = leds
        self._done = done
        self._joy_score = AtomicValue(0.0)
        self._thread = threading.Thread(target=self._run)
        self._thread.start()

    def _run(self):
        while not self._done.is_set():
            joy_score = self._joy_score.value
            if joy_score > 0:
                self._leds.update(Leds.rgb_on(blend(JOY_COLOR, SAD_COLOR, joy_score)))
            else:
                self._leds.update(Leds.rgb_off())

    def update_joy_score(self, value):
        self._joy_score.value = value

    def join(self):
        self._thread.join()


class JoyDetector(object):

    def __init__(self):
        self._done = threading.Event()
        signal.signal(signal.SIGINT, lambda signal, frame: self.stop())
        signal.signal(signal.SIGTERM, lambda signal, frame: self.stop())

    def stop(self):
        logger.info('Stopping...')
        self._done.set()

    def run(self, r, num_frames, verbose):
        """@Timmer, this is the function where we send out data via Bluetooth
         (or REDIS)."""
        logger.info('Starting...')
        leds = Leds()
        player = Player(gpio=22, bpm=10)
        animator = Animator(leds, self._done)

        try:
            # Forced sensor mode, 1640x1232, full FoV. See:
            # https://picamera.readthedocs.io/en/release-1.13/fov.html#sensor-modes
            # This is the resolution inference run on.
            with PiCamera(sensor_mode=4, resolution=(1640, 1232)) as camera, PrivacyLed(leds):

                def halt():
                    self.stop()
                    bd_sock.close()
                    player.stop()
                    player.join()
                    animator.join()

                camera.start_preview()

                button = Button(23)
                button.when_pressed = halt

                joy_score_moving_average = MovingAverage(10)
                prev_joy_score = 0.0
                with CameraInference(face_detection.model()) as inference:
                    logger.info('Model loaded.')
                    player.play(MODEL_LOAD_SOUND)
                    for i, result in enumerate(inference.run()):
                        faces = face_detection.get_faces(result)

                        joy_score = joy_score_moving_average.next(average_joy_score(faces))
                        animator.update_joy_score(joy_score)

                        if joy_score > JOY_SCORE_PEAK > prev_joy_score:
                            player.play(JOY_SOUND)
                        elif joy_score < JOY_SCORE_MIN < prev_joy_score:
                            player.play(SAD_SOUND)

                        prev_joy_score = joy_score

                        # Every num_frames frames, output score via Bluetooth, redis, etc.
                        #num_frames = 2
                        if (i % 3):
                            if len(faces) > 0:
                                bd_out = -2 * joy_score + 1
                            else:
                                bd_out = 0.0
                            r.set('AmyJoyScore',bd_out)  # redis send command

                            if verbose:
                                print("Value sent to Nengo: " + str(bd_out))

                        if self._done.is_set() or i == num_frames:
                            break
        finally:
            player.stop()

            player.join()
            animator.join()


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('--num_frames', '-n', type=int, dest='num_frames', default=-1,
        help='Number of frames to run for, -1 to not terminate')
    parser.add_argument('--host', '-rh',
        dest='REDIS_HOST', default='10.0.0.2',
        help="IP address of server host.")
    parser.add_argument('--auth', '-ra',
        dest="REDIS_AUTH", default='neuromorph', help="Password for redis server")
    parser.add_argument('--verbose', '-v', type=bool, dest="VERBOSE", default=True,
        help="Print joy score to stdout")
    args = parser.parse_args()

    r = redis.StrictRedis(host=args.REDIS_HOST, password=args.REDIS_AUTH)

    device = get_aiy_device_name()
    if not device or not 'Vision' in device:
        logger.error('AIY VisionBonnet is not detected.')
        return

    detector = JoyDetector()
    detector.run (r,args.num_frames,args.VERBOSE)

if __name__ == '__main__':
    main()
