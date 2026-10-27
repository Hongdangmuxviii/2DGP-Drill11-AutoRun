# Drill #11 제출 안내

## e-Class에 제출할 저장소 주소

```text
https://github.com/Hongdangmuxviii/2DGP-Drill11-AutoRun.git
```

주소 끝의 `.git`을 포함해 제출한다. e-Class 제출 동작은 사용자가 수행한다.
저장소의 기본 브랜치는 `main`이며 이 과제 전용 독립 저장소다.

## 제출 전 확인

1. GitHub 저장소 이름 옆에 **Public**이 표시되는지 확인한다.
2. 커밋 목록에 실제 변경이 있는 **한글 커밋 20개**가 있는지 확인한다.
3. `PRD.md`, 실행 코드 네 파일, `requirements.txt`가 보이는지 확인한다.
4. `assets/animation_sheet.png`, `assets/grass.png`가 실제로 열리는지 확인한다.
5. `docs/state-diagram.png`가 이미지로 표시되는지 확인한다.
6. README의 설치·실행·조작법에 따라 실행한다.

## 재현 가능한 로컬 점검

```bash
python -m unittest discover -s tests -v
python tools/check_submission.py
git log --reverse --oneline
git rev-list --count HEAD
```

이미지 렌더링 검증 방법과 실제 화면은 [검증 기록](docs/VERIFICATION.md)에 있다.
기획부터 기능·수정·검증·문서까지 각 변경을 따로 커밋했으며,
빈 커밋이나 커밋 날짜 변경은 사용하지 않았다.

## 원격 업로드 확인

업로드 후 `git ls-remote origin refs/heads/main`의 해시와
`git rev-parse HEAD`의 해시가 같은지 확인한다.
공개 주소에서 내려받은 새 복사본에서도 위 로컬 점검을 실행할 수 있다.
