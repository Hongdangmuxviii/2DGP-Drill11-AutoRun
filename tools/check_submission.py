"""제출용 파일, 독립 저장소, 실제 한글 커밋 20개를 점검한다."""

import ast
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REQUIRED = (
    'PRD.md', 'README.md', 'SUBMISSION.md', 'requirements.txt',
    'boy_game.py', 'boy.py', 'auto_run.py', 'grass.py',
    'assets/animation_sheet.png', 'assets/grass.png', 'assets/ASSETS.md',
    'docs/state-diagram.png', 'docs/state-diagram.svg', 'docs/state-diagram.mmd',
    'docs/VERIFICATION.md', 'tests/test_autorun.py', 'tests/test_regressions.py',
    'tools/render_smoke_test.py',
)


def git(*args):
    return subprocess.check_output(['git', '-C', str(ROOT), *args], text=True).strip()


def main():
    assert Path(git('rev-parse', '--show-toplevel')).resolve() == ROOT
    tracked = set(git('ls-files').splitlines())
    for name in REQUIRED:
        assert name in tracked, '커밋에서 누락된 파일: ' + name
        data = (ROOT / name).read_bytes()
        assert data, '빈 파일: ' + name
        if name.endswith('.png'):
            assert data.startswith(b'\x89PNG\r\n\x1a\n'), 'PNG 형식 오류: ' + name
    tree = ast.parse((ROOT / 'auto_run.py').read_text(encoding='utf-8'))
    assert any(isinstance(node, ast.ClassDef) and node.name == 'AutoRun' for node in tree.body)
    commits = git('rev-list', '--reverse', 'HEAD').splitlines()
    assert len(commits) == 20, f'커밋 수: {len(commits)} (20개 필요)'
    for commit in commits:
        message = git('show', '-s', '--format=%s', commit)
        assert re.search('[가-힣]', message), '한글 메시지가 아닌 커밋: ' + commit
        assert git('diff-tree', '--root', '--no-commit-id', '--name-only', '-r', commit), \
            '변경 파일이 없는 커밋: ' + commit
    assert not git('status', '--porcelain'), '아직 커밋되지 않은 변경이 있습니다.'
    assert not any(Path(name).name == '.env' for name in tracked)
    print('제출 점검 통과: 독립 저장소 / 필수 코드·이미지·기획·상태 그림 / 실제 한글 커밋 20개 / 깨끗한 작업 폴더')


if __name__ == '__main__':
    main()
