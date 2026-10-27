import boy
from auto_run import AutoRun
from helpers import BoyTestCase


class AutoRunRequirements(BoyTestCase):
    def test_initial_state_and_separate_class(self):
        self.assertEqual(self.boy.state, 'IDLE')
        self.assertIsInstance(self.boy.auto_run, AutoRun)
        self.assertEqual(set(self.boy.machine.states), {'IDLE', 'RUN', 'AUTORUN', 'FALLEN'})

    def test_a_starts_and_release_keeps_automatic_movement(self):
        self.start_auto()
        self.key(boy.SDLK_a, down=False)
        self.advance(0.25)
        self.assertEqual(self.boy.state, 'AUTORUN')
        self.assertAlmostEqual(self.boy.x, 500)

    def test_speed_and_enlarged_rendering(self):
        self.start_auto()
        self.assertEqual(self.boy.auto_run.speed, self.boy.RUN_SPEED * 2)
        self.boy.draw()
        args = self.image.clip_draw.call_args.args
        self.assertEqual(args[-2:], (150, 150))
        self.assertEqual(args[5], 110)

    def test_timeout_at_five_seconds(self):
        self.start_auto()
        self.advance(4.999)
        self.assertEqual(self.boy.state, 'AUTORUN')
        self.advance(0.001)
        self.assertEqual(self.boy.state, 'IDLE')
        position = self.boy.x
        self.advance(1)
        self.assertEqual(self.boy.x, position)
        self.boy.draw()
        self.assertEqual(len(self.image.clip_draw.call_args.args), 6)

    def test_repeat_a_does_not_restart_timer(self):
        self.start_auto()
        self.advance(3)
        self.key(boy.SDLK_a)
        self.advance(2)
        self.assertEqual(self.boy.state, 'IDLE')

    def test_new_entry_gets_its_own_five_seconds(self):
        self.start_auto()
        self.advance(5)
        self.advance(10)
        self.start_auto()
        self.advance(4)
        self.assertEqual(self.boy.state, 'AUTORUN')
        self.advance(1)
        self.assertEqual(self.boy.state, 'IDLE')

    def test_a_does_not_start_while_running(self):
        self.key(boy.SDLK_RIGHT)
        self.key(boy.SDLK_a)
        self.assertEqual(self.boy.state, 'RUN')

    def test_unrelated_keys_do_not_cancel_auto(self):
        self.start_auto()
        self.key(boy.SDLK_f)
        self.key(boy.SDLK_SPACE)
        self.assertEqual(self.boy.state, 'AUTORUN')
