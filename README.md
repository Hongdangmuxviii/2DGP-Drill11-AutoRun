# Drill #11 — 소년 자동 무적 런 (AutoRun)

`transitions`로 기존 IDLE·RUN·FALLEN에 AUTORUN을 추가한 2D 게임 프로그래밍 과제입니다.
**A 한 번으로 5초간 속도 2배·크기 1.5배의 자동 달리기**가 시작됩니다.
양쪽 끝에서는 방향을 바꾸고, 방향키를 누르면 즉시 일반 RUN으로 전환합니다.

## 설치와 실행

Python 3.9 이상과 그래픽 창을 표시할 수 있는 데스크톱 환경이 필요합니다.
GitHub에서 내려받은 **이 저장소 폴더**에서 실행합니다.

```bash
python -m venv .venv
```

Windows:

```powershell
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python boy_game.py
```

macOS / Linux:

```bash
source .venv/bin/activate
python -m pip install -r requirements.txt
python boy_game.py
```

Windows에서 `python`이 없다면 `py`를 사용할 수 있습니다.
이미지는 소스 파일 위치를 기준으로 읽으므로 다른 작업 폴더에서도 실행할 수 있습니다.
게임 창을 클릭해 입력 초점을 준 뒤 키를 누르세요. 수정 후에는 게임을 종료하고 다시 실행합니다.

## 조작

| 입력 | 동작 |
| --- | --- |
| ← / → 누르기 | 일반 달리기. 양쪽을 함께 누르면 마지막 입력 방향 우선 |
| 방향키 놓기 | 남은 방향키가 없으면 IDLE |
| IDLE에서 A | AUTORUN 시작. A를 놓아도 유지 |
| AUTORUN에서 ← / → | 자동 모드 취소 후 해당 방향의 일반 RUN |
| IDLE 또는 RUN에서 F | FALLEN으로 쓰러지기 |
| FALLEN에서 SPACE | 다시 서기. 방향키가 눌려 있으면 RUN 재개 |
| ESC / 창 닫기 | 종료 |

## 채점 항목과 구현

| 채점 항목 | 구현 위치 | 확인 방법 |
| --- | --- | --- |
| IDLE에서 A로 자동 상태 진입 | `boy.py` 상태 머신·입력 처리 | A 누른 뒤 손을 떼기 |
| 별도 AutoRun 상태 클래스 | `auto_run.py: AutoRun` | `enter`, `update`, `draw`, `exit` 확인 |
| 빠르고 커지는 소년 | `AutoRun.SPEED_MULTIPLIER`, `SIZE_MULTIPLIER` | 200→400px/s, 100→150px 비교 |
| 좌우 끝 방향 반전 | `AutoRun.update`, `bounds` | 확대된 폭을 고려해 75~725 안에서 이동 |
| 5초 뒤 IDLE 복귀 | `AutoRun.DURATION`, `finish_auto_run` | 5초 대기 후 정지·크기 원복 |
| 방향키로 일반 RUN 복귀 | `cancel_auto_run` | 속도·크기 원복 후 키 방향 이동 |
| 상태 그림 파일 | `docs/state-diagram.png` | 아래 이미지와 SVG·Mermaid 원본 확인 |

![상태 다이어그램](docs/state-diagram.png)

방향 반전은 AUTORUN 내부 동작이므로 별도의 좌·우 상태를 만들지 않았습니다.
과제에는 피격 대상이 없어 전투용 무적 판정은 별도로 추가하지 않았습니다.

## 구성

```text
boy_game.py              실행 진입점과 게임 루프
boy.py                   소년·상태 머신·키 입력·일반 동작
auto_run.py              과제에서 요구한 AutoRun 상태 클래스
grass.py                 지면
assets/                  실제 실행에 쓰는 두 이미지와 출처
docs/state-diagram.*     PNG 제출용 이미지, SVG·Mermaid 원본
tests/                   요구사항 및 기존 동작 자동 테스트
PRD.md                   기획·요구사항·범위
requirements.txt         실행 의존성
```

## 자동 테스트

```bash
python -m unittest discover -s tests -v
```

창을 띄우지 않고 상태 전이·경계 반사·5초 시점·입력 취소·쓰러짐을 검증합니다.
이미지 표시는 별도의 실제 SDL 렌더링 검증으로 확인합니다.

## 개발 기록과 출처

기획부터 기능 구현, 오류 보완, 테스트, 다이어그램, 실행 검증, 제출 점검까지
20개 실제 단계에 걸쳐 한글 메시지로 커밋합니다. 빈 커밋이나 날짜 조작은 사용하지 않습니다.
기존 수업 코드에 AI 보조로 기능과 검증을 추가했습니다.
이미지 출처는 [assets/ASSETS.md](assets/ASSETS.md)에 기록했습니다.
요구사항 원본은 사용자가 제공한 Drill #11 안내 이미지입니다.
