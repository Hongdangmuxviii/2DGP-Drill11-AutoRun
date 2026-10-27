import unittest
from contextlib import ExitStack
from types import SimpleNamespace
from unittest.mock import patch

import boy


class BoyTestCase(unittest.TestCase):
    def setUp(self):
        self.clock = [0.0]
        self.patches = ExitStack()
        self.addCleanup(self.patches.close)
        self.image = self.patches.enter_context(patch('boy.load_image')).return_value
        for module in ('boy', 'auto_run'):
            self.patches.enter_context(patch(module + '.get_time', side_effect=lambda: self.clock[0]))
            self.patches.enter_context(patch(module + '.get_canvas_width', return_value=800))
        self.boy = boy.Boy()

    def key(self, key, down=True):
        self.boy.handle_event(SimpleNamespace(
            type=boy.SDL_KEYDOWN if down else boy.SDL_KEYUP, key=key,
        ))

    def advance(self, seconds):
        self.clock[0] += seconds
        self.boy.update()

    def start_auto(self):
        self.key(boy.SDLK_a)
        self.assertEqual(self.boy.state, 'AUTORUN')
