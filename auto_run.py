"""과제에서 요구한 독립적인 자동 달리기 상태 클래스."""


class AutoRun:
    def __init__(self, boy):
        self.boy = boy

    def enter(self):
        self.boy.frame = 0
        self.boy.animation_time = 0.0

    def update(self, elapsed):
        self.boy.x += self.boy.face_dir * self.boy.RUN_SPEED * elapsed

    def draw(self):
        row = 100 if self.boy.face_dir == 1 else 0
        self.boy.image.clip_draw(
            self.boy.frame * 100, row, 100, 100,
            self.boy.x, self.boy.y,
        )
