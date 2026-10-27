"""과제에서 요구한 독립적인 자동 달리기 상태 클래스."""

from pico2d import get_canvas_width, get_time


class AutoRun:
    SPEED_MULTIPLIER = 2.0
    SIZE_MULTIPLIER = 1.5
    DURATION = 5.0

    def __init__(self, boy):
        self.boy = boy
        self.started_at = 0.0
        self.elapsed = 0.0

    def enter(self):
        self.boy.frame = 0
        self.boy.animation_time = 0.0
        self.started_at = get_time()
        self.elapsed = 0.0
        left, right = self.bounds()
        self.boy.x = max(left, min(right, self.boy.x))

    def update(self, elapsed):
        # 진입 전 시간과 5초 이후 시간은 자동 이동에 포함하지 않는다.
        total = min(self.DURATION, max(0.0, get_time() - self.started_at))
        elapsed = max(0.0, total - self.elapsed)
        self.elapsed = total
        left, right = self.bounds()
        span = right - left
        # 한 번의 갱신에 경계를 여러 번 넘더라도 이동 거리를 보존한다.
        position = self.boy.x - left + self.boy.face_dir * self.speed * elapsed
        phase = position % (2 * span)
        if phase < span:
            self.boy.x = left + phase
            self.boy.face_dir = 1
        else:
            self.boy.x = right - (phase - span)
            self.boy.face_dir = -1
        if total >= self.DURATION:
            self.boy.finish_auto_run()

    def bounds(self):
        half = 100 * self.SIZE_MULTIPLIER / 2
        return half, get_canvas_width() - half

    @property
    def speed(self):
        return self.boy.RUN_SPEED * self.SPEED_MULTIPLIER

    def draw(self):
        row = 100 if self.boy.face_dir == 1 else 0
        size = int(100 * self.SIZE_MULTIPLIER)
        # 발 위치를 유지하면서 몸 크기만 확대한다.
        draw_y = self.boy.y + (size - 100) * 0.4
        self.boy.image.clip_draw(
            self.boy.frame * 100, row, 100, 100,
            self.boy.x, draw_y, size, size,
        )
