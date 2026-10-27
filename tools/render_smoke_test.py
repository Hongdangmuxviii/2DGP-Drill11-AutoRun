"""실제 SDL 입력 큐와 이미지 렌더링을 검증하고 화면을 BMP로 저장한다."""

import argparse
import ctypes
import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import boy as boy_module
import auto_run
import boy_game as game
import pico2d.pico2d as renderer
from sdl2 import (
    SDL_CreateRenderer, SDL_RENDERER_SOFTWARE, SDL_Event, SDL_PushEvent,
    SDL_CreateRGBSurfaceWithFormat, SDL_PIXELFORMAT_RGBA32,
    SDL_RenderReadPixels, SDL_SaveBMP, SDL_FreeSurface,
)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=Path('tmp/render-check'))
    output = parser.parse_args().output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    clock = [0.0]

    def key(code, down=True):
        event = SDL_Event()
        event.type = game.SDL_KEYDOWN if down else game.SDL_KEYUP
        event.key.keysym.sym = code
        event.key.repeat = 0
        assert SDL_PushEvent(ctypes.byref(event)) == 1
        game.handle_events()

    def tick(seconds):
        clock[0] += seconds
        game.update_world()
        game.render_world()

    def capture(name):
        game.clear_canvas()
        for obj in game.world:
            obj.draw()
        surface = SDL_CreateRGBSurfaceWithFormat(0, 800, 600, 32, SDL_PIXELFORMAT_RGBA32)
        assert surface
        try:
            assert SDL_RenderReadPixels(renderer.renderer, None, SDL_PIXELFORMAT_RGBA32,
                                        surface.contents.pixels, surface.contents.pitch) == 0
            assert SDL_SaveBMP(surface, str(output / (name + '.bmp')).encode()) == 0
        finally:
            SDL_FreeSurface(surface)

    game.open_canvas()
    # pico2d 1.5.1은 가속 렌더러의 null 포인터를 None으로 확인한다.
    # 화면 없는 검증 환경에서는 소프트웨어 렌더러를 명시적으로 사용한다.
    if not renderer.renderer:
        renderer.renderer = SDL_CreateRenderer(renderer.window, -1, SDL_RENDERER_SOFTWARE)
    assert renderer.renderer, 'SDL 렌더러를 만들 수 없습니다.'
    try:
        with patch.object(boy_module, 'get_time', side_effect=lambda: clock[0]), \
             patch.object(auto_run, 'get_time', side_effect=lambda: clock[0]):
            game.running = True
            game.reset_world()
            assert game.boy.state == 'IDLE'
            capture('idle')
            key(game.SDLK_RIGHT)
            tick(0.25)
            assert game.boy.state == 'RUN' and game.boy.x == 450
            capture('run')
            key(game.SDLK_RIGHT, down=False)
            key(game.SDLK_a)
            key(game.SDLK_a, down=False)
            tick(0.1)
            assert game.boy.state == 'AUTORUN'
            assert abs(game.boy.x - 490) < 0.001
            capture('autorun')
            tick(0.6)
            assert game.boy.face_dir == -1
            assert 75 <= game.boy.x <= 725
            capture('autorun_bounce')
            key(game.SDLK_LEFT)
            assert game.boy.state == 'RUN' and game.boy.face_dir == -1
            tick(0.1)
            capture('cancel_to_run')
            key(game.SDLK_f)
            tick(0.5)
            assert game.boy.state == 'FALLEN' and game.boy.fall_progress == 1
            capture('fallen')
            key(game.SDLK_LEFT, down=False)
            key(game.SDLK_SPACE)
            assert game.boy.state == 'IDLE'
            key(game.SDLK_a)
            tick(5)
            assert game.boy.state == 'IDLE'
            capture('timeout_to_idle')
            key(game.SDLK_ESCAPE)
            assert not game.running
            game.running = True
            event = SDL_Event()
            event.type = game.SDL_QUIT
            assert SDL_PushEvent(ctypes.byref(event)) == 1
            game.handle_events()
            assert not game.running
        print('SDL 입력·이미지·상태 전이·경계 반사·종료 검증 통과:', output)
    finally:
        game.close_canvas()


if __name__ == '__main__':
    main()
