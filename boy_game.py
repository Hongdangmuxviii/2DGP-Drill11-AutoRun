from pico2d import *
import math
from pathlib import Path
from transitions import Machine


ASSET_DIR = Path(__file__).resolve().parent / 'assets'


# Game object class here

class Grass:
    def __init__(self):
        self.image = load_image(str(ASSET_DIR / 'grass.png'))

    def draw(self):
        self.image.draw(400, 30)

    def update(self):
        pass


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
        self.fall_started_at = 0.0
        self.fall_progress = 0.0
        self.image = load_image(str(ASSET_DIR / 'animation_sheet.png'))
        self.machine = Machine(
            model=self,
            states=[
                {'name': 'IDLE', 'on_enter': 'enter_idle'},
                {'name': 'RUN', 'on_enter': 'enter_run'},
                {'name': 'FALLEN', 'on_enter': 'enter_fallen'},
            ],
            transitions=[
                {'trigger': 'start_running', 'source': 'IDLE', 'dest': 'RUN'},
                {'trigger': 'stop_running', 'source': 'RUN', 'dest': 'IDLE'},
                {'trigger': 'fall', 'source': ['IDLE', 'RUN'], 'dest': 'FALLEN'},
                {'trigger': 'stand_up', 'source': 'FALLEN', 'dest': 'IDLE'},
            ],
            initial='IDLE',
            auto_transitions=False,
        )

    def enter_idle(self):
        self.frame = 0
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
            else:
                self.held_keys.discard(event.key)
            self.update_movement()
        elif event.type == SDL_KEYDOWN:
            if event.key == SDLK_f and self.state in ('IDLE', 'RUN'):
                self.fall()
            elif event.key == SDLK_SPACE and self.state == 'FALLEN':
                self.stand_up()
                self.update_movement()

    def update_movement(self):
        self.direction = int(SDLK_RIGHT in self.held_keys) - int(SDLK_LEFT in self.held_keys)
        if self.state == 'FALLEN':
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
        if self.state in ('IDLE', 'RUN'):
            self.animation_time += elapsed
            self.frame = int(self.animation_time * self.ANIMATION_FPS) % self.FRAME_COUNT
            if self.state == 'RUN':
                self.x += self.direction * self.RUN_SPEED * elapsed
                self.x = max(self.HALF_SIZE, min(get_canvas_width() - self.HALF_SIZE, self.x))
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


def handle_events():
    global running

    event_list = get_events()
    for event in event_list:
        if event.type == SDL_QUIT:
            running = False
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            running = False
        else:
            boy.handle_event(event)


def reset_world():
    global world
    global boy

    world = []

    grass = Grass()
    world.append(grass)

    boy = Boy()
    world.append(boy)



def update_world():
    for o in world:
        o.update()
    pass


def render_world():
    clear_canvas()
    for o in world:
        o.draw()
    update_canvas()


def main():
    global running
    running = True

    open_canvas()
    reset_world()
    # game loop
    while running:
        handle_events()
        update_world()
        render_world()
        delay(0.01)
    close_canvas()


if __name__ == '__main__':
    main()
