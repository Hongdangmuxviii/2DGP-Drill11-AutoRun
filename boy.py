import math
from pathlib import Path
from pico2d import *
from transitions import Machine
from auto_run import AutoRun

ASSET_DIR = Path(__file__).resolve().parent / 'assets'


class Boy:
    FALL_DURATION = 0.5
    RUN_SPEED = 200.0  # Pixels per second.
    ANIMATION_FPS = 10.0
    FRAME_COUNT = 8
    HALF_SIZE = 50

    def __init__(self):
        self.x, self.y = 400, 90
        self.frame = 0
        self.animation_time = 0.0
        self.last_update_time = get_time()
        self.face_dir = 1
        self.direction = 0
        self.held_keys = set()
        self.last_direction_key = SDLK_RIGHT
        self.fall_started_at = 0.0
        self.fall_progress = 0.0
        self.image = load_image(str(ASSET_DIR / 'animation_sheet.png'))
        self.auto_run = AutoRun(self)
        self.machine = Machine(
            model=self,
            states=[
                {'name': 'IDLE', 'on_enter': 'enter_idle'},
                {'name': 'RUN', 'on_enter': 'enter_run'},
                {'name': 'AUTORUN', 'on_enter': self.auto_run.enter,
                 'on_exit': self.auto_run.exit},
                {'name': 'FALLEN', 'on_enter': 'enter_fallen'},
            ],
            transitions=[
                {'trigger': 'start_running', 'source': 'IDLE', 'dest': 'RUN'},
                {'trigger': 'stop_running', 'source': 'RUN', 'dest': 'IDLE'},
                {'trigger': 'start_auto_run', 'source': 'IDLE', 'dest': 'AUTORUN'},
                {'trigger': 'finish_auto_run', 'source': 'AUTORUN', 'dest': 'IDLE'},
                {'trigger': 'cancel_auto_run', 'source': 'AUTORUN', 'dest': 'RUN'},
                {'trigger': 'fall', 'source': ['IDLE', 'RUN'], 'dest': 'FALLEN'},
                {'trigger': 'stand_up', 'source': 'FALLEN', 'dest': 'IDLE'},
            ],
            initial='IDLE',
            auto_transitions=False,
        )

    def enter_idle(self):
        self.frame = 0
        self.direction = 0
        self.animation_time = 0.0
        self.fall_progress = 0.0

    def enter_run(self):
        self.frame = 0
        self.animation_time = 0.0

    def enter_fallen(self):
        self.frame = 0
        self.fall_started_at = get_time()
        self.fall_progress = 0.0

    def handle_event(self, event):
        if event.type in (SDL_KEYDOWN, SDL_KEYUP) and event.key in (SDLK_LEFT, SDLK_RIGHT):
            if event.type == SDL_KEYDOWN:
                self.held_keys.add(event.key)
                self.last_direction_key = event.key
                if self.state == 'AUTORUN':
                    self.face_dir = 1 if event.key == SDLK_RIGHT else -1
                    self.cancel_auto_run()
            else:
                self.held_keys.discard(event.key)
            self.update_movement()
        elif event.type == SDL_KEYDOWN:
            if event.key == SDLK_a and self.state == 'IDLE':
                self.start_auto_run()
            elif event.key == SDLK_f and self.state in ('IDLE', 'RUN'):
                self.fall()
            elif event.key == SDLK_SPACE and self.state == 'FALLEN':
                self.stand_up()
                self.update_movement()

    def update_movement(self):
        self.direction = int(SDLK_RIGHT in self.held_keys) - int(SDLK_LEFT in self.held_keys)
        if len(self.held_keys) == 2:
            self.direction = 1 if self.last_direction_key == SDLK_RIGHT else -1
        if self.state in ('FALLEN', 'AUTORUN'):
            return
        if self.direction:
            self.face_dir = self.direction
            if self.state == 'IDLE':
                self.start_running()
        elif self.state == 'RUN':
            self.stop_running()

    def update(self):
        now = get_time()
        elapsed = max(0.0, now - self.last_update_time)
        self.last_update_time = now
        if self.state in ('IDLE', 'RUN', 'AUTORUN'):
            self.animation_time += elapsed
            self.frame = int(self.animation_time * self.ANIMATION_FPS) % self.FRAME_COUNT
            if self.state == 'RUN':
                self.x += self.direction * self.RUN_SPEED * elapsed
                self.x = max(self.HALF_SIZE, min(get_canvas_width() - self.HALF_SIZE, self.x))
            elif self.state == 'AUTORUN':
                self.auto_run.update(elapsed)
        elif self.state == 'FALLEN':
            fall_elapsed = now - self.fall_started_at
            self.fall_progress = max(0.0, min(fall_elapsed / self.FALL_DURATION, 1.0))

    def draw(self):
        if self.state == 'IDLE':
            row = 300 if self.face_dir == 1 else 200
            self.image.clip_draw(self.frame * 100, row, 100, 100, self.x, self.y)
        elif self.state == 'RUN':
            row = 100 if self.face_dir == 1 else 0
            self.image.clip_draw(self.frame * 100, row, 100, 100, self.x, self.y)
        elif self.state == 'AUTORUN':
            self.auto_run.draw()
        elif self.state == 'FALLEN':
            # Fall toward the facing direction and keep the sprite on screen.
            progress = self.fall_progress
            row = 300 if self.face_dir == 1 else 200
            draw_x = self.x + self.face_dir * 30 * progress
            draw_x = max(self.HALF_SIZE, min(get_canvas_width() - self.HALF_SIZE, draw_x))
            self.image.clip_composite_draw(
                0, row, 100, 100,
                -self.face_dir * math.pi / 2 * progress, '',
                draw_x, self.y - 15 * progress,
                100, 100,
            )


