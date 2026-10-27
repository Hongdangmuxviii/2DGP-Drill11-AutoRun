import boy
from helpers import BoyTestCase


class MovementRegressions(BoyTestCase):
    def test_left_direction_is_preserved_between_frames(self):
        self.boy.face_dir = -1
        self.start_auto()
        self.advance(0.1)
        first = self.boy.x
        self.advance(0.1)
        self.assertLess(self.boy.x, first)
        self.assertEqual(self.boy.face_dir, -1)

    def test_both_edges_reflect_with_enlarged_bounds(self):
        self.boy.x = 720
        self.start_auto()
        self.advance(0.1)
        self.assertAlmostEqual(self.boy.x, 690)
        self.assertEqual(self.boy.face_dir, -1)
        self.boy.x = 80
        self.advance(0.1)
        self.assertAlmostEqual(self.boy.x, 110)
        self.assertEqual(self.boy.face_dir, 1)

    def test_entry_near_edge_clamps_enlarged_sprite(self):
        for x, expected in ((50, 75), (750, 725)):
            with self.subTest(x=x):
                self.boy.x = x
                self.start_auto()
                self.assertEqual(self.boy.x, expected)
                self.boy.finish_auto_run()

    def test_direction_key_cancels_auto_in_requested_direction(self):
        for key, direction in ((boy.SDLK_LEFT, -1), (boy.SDLK_RIGHT, 1)):
            with self.subTest(key=key):
                self.start_auto()
                self.key(key)
                self.assertEqual(self.boy.state, 'RUN')
                self.assertEqual(self.boy.face_dir, direction)
                start = self.boy.x
                self.advance(0.1)
                self.assertAlmostEqual(self.boy.x, start + direction * 20)
                self.boy.draw()
                self.assertEqual(len(self.image.clip_draw.call_args.args), 6)
                self.key(key, down=False)
                self.assertEqual(self.boy.state, 'IDLE')

    def test_last_pressed_direction_and_remaining_key(self):
        self.key(boy.SDLK_LEFT)
        self.key(boy.SDLK_RIGHT)
        self.assertEqual(self.boy.face_dir, 1)
        self.key(boy.SDLK_RIGHT, down=False)
        self.assertEqual(self.boy.state, 'RUN')
        self.assertEqual(self.boy.face_dir, -1)
        self.key(boy.SDLK_LEFT, down=False)
        self.assertEqual(self.boy.state, 'IDLE')

    def test_fallen_stops_movement_and_space_recovers(self):
        self.key(boy.SDLK_LEFT)
        self.key(boy.SDLK_f)
        start = self.boy.x
        self.advance(0.5)
        self.assertEqual(self.boy.state, 'FALLEN')
        self.assertEqual(self.boy.x, start)
        self.assertEqual(self.boy.fall_progress, 1)
        self.boy.draw()
        self.assertEqual(self.image.clip_composite_draw.call_args.args[1], 200)
        self.key(boy.SDLK_SPACE)
        self.assertEqual(self.boy.state, 'RUN')
        self.key(boy.SDLK_LEFT, down=False)
        self.key(boy.SDLK_f)
        self.key(boy.SDLK_SPACE)
        self.assertEqual(self.boy.state, 'IDLE')

    def test_normal_run_stays_on_screen(self):
        self.key(boy.SDLK_LEFT)
        self.advance(10)
        self.assertEqual(self.boy.x, 50)
        self.key(boy.SDLK_RIGHT)
        self.advance(10)
        self.assertEqual(self.boy.x, 750)

    def test_coarse_and_fine_updates_preserve_bounce_distance(self):
        results = []
        for step, count in ((4.5, 1), (0.1, 45)):
            self.clock[0] = 0
            self.boy = boy.Boy()
            self.start_auto()
            for _ in range(count):
                self.advance(step)
                self.assertTrue(75 <= self.boy.x <= 725)
            results.append((self.boy.x, self.boy.face_dir))
        self.assertAlmostEqual(results[0][0], results[1][0])
        self.assertEqual(results[0][1], results[1][1])

    def test_long_frame_only_moves_for_five_seconds(self):
        self.start_auto()
        self.advance(20)
        self.assertEqual(self.boy.state, 'IDLE')
        self.assertAlmostEqual(self.boy.x, 350)

    def test_state_machine_has_only_explicit_transitions(self):
        self.assertNotIn('to_AUTORUN', self.boy.machine.events)
        self.assertEqual(self.boy.machine.get_triggers('AUTORUN'),
                         ['finish_auto_run', 'cancel_auto_run'])
