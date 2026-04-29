# Debate AI

Claude AI와 1:1 토론을 진행하는 CLI 애플리케이션입니다.  
원하는 주제로 찬성/반대 입장을 선택하면 AI가 반대 측에서 논리적으로 맞서고, 토론이 끝나면 별도의 심판 AI가 승패를 판정합니다.

---

## 주요 기능

- **1:1 토론** — 사용자가 입장을 선택하면 Claude AI가 반대 입장에서 맞상대
- **라운드제** — 원하는 라운드 수(1~10)로 진행
- **심판 판정** — 토론 종료 후 공정한 AI 심판이 강점·약점·승자 평가
- **실시간 스트리밍** — AI 응답을 타이핑되는 것처럼 실시간 출력
- **Rich 터미널 UI** — 패널, 컬러, 룰 구분선으로 가독성 높은 인터페이스

---

## 사전 요구사항

- Python 3.9 이상
- [Anthropic API 키](https://console.anthropic.com/)

---

## 설치

```bash
# 1. 저장소 클론
git clone https://github.com/dntwk707/debate-ai.git
cd debate-ai

# 2. 가상환경 생성 및 활성화 (선택사항이지만 권장)
python -m venv venv
source venv/bin/activate      # macOS/Linux
venv\Scripts\activate         # Windows

# 3. 의존성 설치
pip install -r requirements.txt

# 4. 환경변수 설정
cp .env.example .env
# .env 파일을 열어 ANTHROPIC_API_KEY 값을 입력하세요
```

`.env` 파일 형식:

```
ANTHROPIC_API_KEY=sk-ant-...
```

---

## 사용법

### 기본 실행 (대화형 입력)

```bash
python debate_ai.py
```

실행 후 주제와 입장을 프롬프트에서 입력합니다.

### 옵션으로 바로 시작

```bash
python debate_ai.py --topic "인공지능은 인간의 일자리를 빼앗는다" --side 찬성 --rounds 3
```

| 옵션 | 단축 | 설명 | 기본값 |
|------|------|------|--------|
| `--topic` | `-t` | 토론 주제 | 대화형 입력 |
| `--side` | `-s` | 사용자 입장 (`찬성` / `반대`) | 대화형 입력 |
| `--rounds` | `-r` | 라운드 수 (1~10) | `3` |

### 도움말

```bash
python debate_ai.py --help
```

---

## 실행 예시

```
╭─────────────────────────────────────────────────╮
│  토론 주제: 인공지능은 인간의 일자리를 빼앗는다  │
│  당신: 찬성  |  AI: 반대  |  라운드: 3회         │
╰─────────────────────────────────────────────────╯

──────────────── 라운드 1 / 3 ────────────────

╭─ AI (반대) ──╮
╰──────────────╯
AI는 일자리를 빼앗는 것이 아니라 새로운 직업을 창출합니다 ...

당신의 주장 (찬성): 하지만 단순 반복 업무는 이미 자동화로 사라지고 있습니다 ...

──────────────── 심판 판정 ────────────────
1. 찬성 측 평가 ...
2. 반대 측 평가 ...
3. 최종 판정 ...
```

---

## 프로젝트 구조

```
debate-ai/
├── debate_ai.py       # 메인 애플리케이션
├── requirements.txt   # 의존성 목록
├── .env               # API 키 (git 미추적)
└── README.md
```

---

## 기술 스택

| 라이브러리 | 용도 |
|-----------|------|
| [anthropic](https://github.com/anthropics/anthropic-sdk-python) | Claude API 호출 및 스트리밍 |
| [rich](https://github.com/Textualize/rich) | 터미널 UI |
| [click](https://click.palletsprojects.com/) | CLI 인수 처리 |
| [python-dotenv](https://github.com/theskumar/python-dotenv) | 환경변수 로드 |

---

## 라이선스

MIT
