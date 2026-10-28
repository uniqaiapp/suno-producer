<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/banner.svg">
  <source media="(prefers-color-scheme: light)" srcset="assets/banner-light.svg">
  <img alt="suno-producer: Suno style prompts and lyrics structure that behave" src="assets/banner.svg" width="1280" height="320">
</picture>

[![License: MIT](https://img.shields.io/badge/license-MIT-d1fe17?style=flat-square&labelColor=0d0f12)](LICENSE)
[![Claude Code skill](https://img.shields.io/badge/Claude_Code-skill-d1fe17?style=flat-square&labelColor=0d0f12)](#설치)
[![Cursor](https://img.shields.io/badge/Cursor-rules-d1fe17?style=flat-square&labelColor=0d0f12)](#설치)
[![Codex](https://img.shields.io/badge/Codex-AGENTS.md-d1fe17?style=flat-square&labelColor=0d0f12)](#설치)
[![Made by UniqAI](https://img.shields.io/badge/made_by-UniqAI-fdfc07?style=flat-square&labelColor=0d0f12)](https://uniqai.app/?utm_source=github&utm_medium=readme-ko&utm_campaign=suno-producer)

**모델이 실제로 따르는 Suno 프롬프트, 메타태그, 가사 구조. 영어와 러시아어를 지원합니다.**

[빠른 시작](#빠른-시작) · [동작 방식](#동작-방식) · [Lint 규칙](#lint-규칙) · [예제](#예제) · [설치](#설치) · [FAQ](#faq)

</div>

[English](README.md) · [Русский](README.ru.md) · [简体中文](README.zh-CN.md) · [Español](README.es.md) · [Português (BR)](README.pt-BR.md) · [日本語](README.ja.md) · 한국어

# suno-producer: Suno 프롬프트, 메타태그, 가사 구조

Suno 프롬프트를 세 부분으로 나눕니다: 한 줄짜리 **스타일 프롬프트**(장르, BPM, 조성, 분위기, 악기, 프로덕션, 보컬), 메타태그(`[Intro]`, `[Verse]`, `[Pre-Chorus]`, `[Chorus]`, `[Drop]`, `[Bridge]`, `[Outro]`)로 이루어진 **섹션 구조**, 그리고 생성된 보컬이 급하게 몰아치지 않고 부를 수 있을 만큼 줄 길이가 고른 **가사**입니다. 모두 Suno 에디터의 Style 필드와 Lyrics 필드에 넣기 위해 작성합니다. 태그 목록과 필드 예산은 Suno v4.5 이상을 기준으로 정리했습니다(2026년 10월 현재 최신 모델은 v5.5입니다. [Suno의 2026년 3월 출시 보도](https://www.musicbusinessworldwide.com/suno-launches-v5-5-ai-model-with-voice-capture-and-personalization-features) 참고). 실제 제한은 에디터가 보여 주고, lint의 예산은 플래그로 바꿀 수 있습니다. Claude Code 스킬, Cursor 규칙, Codex `AGENTS.md` 스니펫으로 동작하며, 세 개의 스크립트는 단독으로도 lint가 딸린 체크리스트처럼 쓸 수 있습니다. UniqAI는 사진, 영상, 채팅 도구를 만들지 음악 도구를 만들지는 않습니다. 이 프로젝트는 저희가 직접 쓰려고 만든 사이드 프로젝트입니다.

| **브리프를 넣으면 프롬프트가 나옵니다** | **가사 운율, 영어 + 러시아어** | **크레딧을 쓰기 전에 lint** |
|:---|:---|:---|
| `brief.py`는 "sad synthwave, female vocal" 같은 설명을 스타일 프롬프트, 한 축만 바꾼 A/B 변형 두 개, 태그가 붙은 구조, 섹션별 음절 목표로 바꿉니다. | `lyric_meter.py`는 줄마다 음절을 세고, 섹션별 라임 스킴을 도출하며, 섹션 중앙값에서 벗어난 줄을 표시합니다. 영어는 휴리스틱, 러시아어는 모음을 정확히 셉니다. | `suno_lint.py`는 태그 철자와 위치, 구조 순서, 섹션 길이, 필드 예산, 아티스트 모방 문구를 검사합니다. 규칙 id가 고정되어 있고, 오류가 있으면 종료 코드 1을 반환합니다. |

## 빠른 시작

```bash
git clone https://github.com/uniqaiapp/suno-producer
cd suno-producer
python3 scripts/brief.py --genre synthwave --fuse "indie pop" --mood melancholic --seed 7
python3 scripts/lyric_meter.py examples/lyrics/midnight-bus.txt
python3 scripts/suno_lint.py examples/lyrics/bad-tags.txt --style examples/style/bad-style.txt
```

첫 번째 명령은 변형 B와 C가 포함된 스타일 프롬프트, `[Intro] … [Outro]` 구조, 가사 브리프를 출력합니다. 두 번째 명령은 샘플 곡의 모든 섹션에 대해 줄별 음절 수와 라임 스킴을 출력합니다. 세 번째 명령은 오류 3개와 경고 9개로 실패하며, 각 항목에 규칙 id와 줄 번호가 붙습니다. Python 3.9+, 설치할 패키지는 없습니다.

## 데모

<img alt="suno-producer demo: lyric_meter reports syllables and rhyme scheme per section of the sample song, then suno_lint lists two errors and seven warnings with rule ids and line numbers on a deliberately broken file" src="assets/demo.svg" width="900">

## 동작 방식

1. **브리프.** `scripts/brief.py`는 `references/genres.json`(장르별 템포 범위, 조성, 악기, 프로덕션 용어, 기본 보컬. 측정값이 아니라 편집 기준의 기본값입니다)을 읽어, 모델이 가중치를 두는 순서대로 쉼표로 구분된 스타일 프롬프트를 조립합니다: 장르, 퓨전, 템포, 조성, 분위기 단어 두 개, 악기, 프로덕션, 보컬, 언어. `--fuse`를 주면 두 템포 범위가 겹치는 구간을 사용합니다. 장르에 맞는 섹션 구조도 고르고, 섹션별 줄 수와 음절 예산을 출력합니다.

2. **변형.** 각 변형은 디스크립터 하나만 바꿉니다(보컬, 프로덕션, 또는 템포 약 8 %). 그래서 A/B로 들어 보면 어떤 변화가 효과가 있었는지 알 수 있습니다. `tests/test_brief.py`가 디스크립터 하나만 다르다는 점을 검증합니다. 같은 `--seed`면 출력은 항상 같습니다.

3. **운율.** `scripts/lyric_meter.py`는 가사를 `[Section]` 태그 단위로 나누고, 음절을 세고(영어: 모음 묶음에 묵음 e, -ed, -es, -le 규칙 적용; 러시아어: 모음 하나당 음절 하나), 단어 끝소리로 라임 스킴을 만들며(대문자 = 완전 라임, 소문자 = 불완전 라임), 섹션 중앙값에서 두 음절 넘게 벗어난 줄에 경고를 냅니다. 한 줄 전체가 `(backing vocals)`인 경우는 제외합니다.

4. **Lint.** `scripts/suno_lint.py`는 가사를 한 번 훑으면서 아래 규칙 표에 따라 보고하고, 이어서 스타일 프롬프트의 태그, 아티스트 문구, 줄 수, 템포, 예산을 검사합니다. 기계용 출력은 `--json`, 경고도 실패로 처리하려면 `--strict`를 사용합니다.

5. **스킬**(`SKILL.md`)이 이 과정을 에이전트용으로 묶습니다: 브리프를 명확히 하고, `brief.py`를 실행하고, 구조에 맞춰 가사를 쓰고, 두 검사를 모두 돌리고, Style + Lyrics + 변형을 정해진 형식으로 전달합니다. 사용자가 생성 결과가 나빴다며 다시 오면 `references/troubleshooting.md`에 따라 한 가지만 바꿉니다.

```
description ──► brief.py ──► style prompt A/B/C + structure + lyric brief
                                   │
                              write lyrics
                                   │
                 lyric_meter.py ◄──┴──► suno_lint.py
                 syllables, scheme       tags, order, budgets, L001–L016
                                   │
                           Style + Lyrics + variants
```

## Lint 규칙

| Id | 수준 | 검사 항목 |
|---|---|---|
| L001 | warn | 알려진 목록(`references/section-tags.md`)에 없는 태그. 모델이 태그를 노래로 부를 수 있습니다 |
| L002 | warn | 첫 태그 앞에 가사가 있거나, 태그가 아예 없음 |
| L003 | warn | `[Chorus]`, `[Hook]`, `[Drop]` 중 어느 것도 없음(`--instrumental`로 건너뜀) |
| L004 | warn | 같은 태그가 연달아 두 번 |
| L005 | warn | `[Intro]`가 맨 앞이 아니거나 `[Outro]`가 맨 뒤가 아님 |
| L006 | error / warn | 한 줄에서 `[ ]`(error) 또는 `( )`(warn)의 짝이 맞지 않음 |
| L007 | error | 가사나 스타일에 아티스트 모방 문구("in the style of", "sounds like", "в стиле", "как у")가 있음 |
| L008 | error / warn | 스타일 프롬프트가 예산 초과(`--max-style`, 기본 1000) / 비어 있음 |
| L009 | error | 가사가 예산 초과(`--max-lyrics`, 기본 5000) |
| L010 | warn | 가사 줄 안에 태그가 있음 |
| L011 | warn | 섹션이 `--max-section-lines`(기본 12)보다 김 |
| L012 | warn | 스타일 프롬프트에 `[Tags]`가 있음 |
| L013 | warn | 스타일 프롬프트가 세 줄 넘게 펼쳐져 있음 |
| L014 | warn | 소문자 태그 |
| L015 | info | 스타일 프롬프트에 템포가 없음 |
| L016 | warn | 줄이 하나도 없는 가사 섹션(연주 태그는 제외) |

예산은 사양이 아니라 기본값입니다. Suno 에디터가 각 필드 옆에 실제 제한을 보여 줍니다.

## 예제

아래의 모든 출력은 `examples/outputs/`에 커밋되어 있고 `python3 tests/run.py`가 바이트 단위로 동일하게 재현합니다. 명령은 `examples/README.md`에 정리되어 있습니다.

<details>
<summary><b>영어 곡의 운율 리포트(신스웨이브 / 인디 팝)</b></summary>

입력: `examples/lyrics/midnight-bus.txt`. 명령: `python3 scripts/lyric_meter.py examples/lyrics/midnight-bus.txt`.

```text
[Verse 1]      4 lines · syllables 6-8 · scheme ABAB
   1   6  Streetlights hum a tired song                A
   2   7  Rain keeps tapping on the glass              B
   3   8  Every stop takes twice as long               A
   4   7  Watching all the faces pass                  B
[Pre-Chorus]   2 lines · syllables 8-9 · scheme AA
   1   8  I count the stops, I count the miles         A
   2   9  I keep your seat warm for a while            A
[Chorus]       4 lines · syllables 6-9 · scheme AABB
   1   6  Midnight bus, take me home                   A
   2   7  Through a city made of chrome                A
   3   9  Every window's a telephone                   B
   4   7  Ringing nowhere, ringing on                  B
```

전체 리포트: `examples/outputs/midnight-bus.meter.txt`. 이 곡은 스타일 프롬프트 `examples/style/midnight-bus.txt`와 함께 lint를 깨끗하게 통과합니다.

</details>

<details>
<summary><b>러시아어 곡의 운율 리포트(록 발라드)</b></summary>

입력: `examples/lyrics/severny-veter.ru.txt`. 명령: `python3 scripts/lyric_meter.py examples/lyrics/severny-veter.ru.txt`.

```text
[Verse 1]      4 lines · syllables 10 · scheme AABB
   1  10  Северный ветер стучится в окно               A
   2  10  Чай на столе остывает давно                  A
   3  10  Я не ответил на тысячу слов                  B
   4  10  Город молчит, и молчать я готов              B
[Chorus]       4 lines · syllables 8 · scheme ABAB
   1   8  Не уходи, пока горит                         A
   2   8  Последний свет в моём окне                   B
   3   8  Пусть этот город говорит                     A
   4   8  О ком-то, но не обо мне                      B
```

스크립트의 끝소리 규칙으로는 여기 있는 라임이 모두 완전 라임입니다. 불완전 라임은 위 영어 곡의 2절을 보면 됩니다: `scheme ABaB`에서 소문자 `a`는 `door` / `for`가 끝소리만 맞는다는 표시입니다. 러시아어 관련 세부 사항: `references/russian-vocals.md`.

</details>

<details>
<summary><b>일부러 망가뜨린 파일에 lint 실행</b></summary>

명령: `python3 scripts/suno_lint.py examples/lyrics/bad-tags.txt --style examples/style/bad-style.txt`(종료 코드 1).

```text
! L002  lyrics before the first section tag; Suno treats untagged text as a verse
x L007  artist-imitation phrase in style prompt ("sounds like"); describe the sound instead
! L012  style prompt contains [tags]; tags belong in the lyrics field
! L014  line 2: tag [intro] is lower-case; write tags Capitalised for consistency
x L007  line 4: artist-imitation phrase in lyrics ("sound like"); Suno rejects named artists
! L016  line 5: section [Verse 1] has no lines
! L001  line 6: unknown tag [Guitar Shred]; Suno may sing it instead of following it
x L006  line 7: unbalanced square brackets
! L010  line 9: tag inside a lyric line; put each tag on its own line
! L011  line 10: [Chorus] has 13 lines (limit 12); long sections tend to get rushed or cut
! L005  line 24: [Outro] is not the last tag
= 3 error(s), 9 warning(s), 1 info
```

</details>

<details>
<summary><b>한 축만 바꾼 변형이 포함된 브리프</b></summary>

명령: `python3 scripts/brief.py --genre synthwave --fuse "indie pop" --mood melancholic --seed 7`.

```text
Style prompt (paste into the Style field)
  A  [base] synthwave, indie pop, 108 BPM, C minor, melancholic, wistful, gated reverb drums, retro drum machine, jangly electric guitar, 80s production, lo-fi warmth, warm female vocal
  B  [vocal] … 80s production, lo-fi warmth, breathy female vocal
  C  [production] … jangly electric guitar, wide stereo pads, lo-fi warmth, warm female vocal

Structure (pop)
  [Intro] [Verse 1] [Pre-Chorus] [Chorus] [Verse 2] [Pre-Chorus] [Chorus] [Bridge] [Chorus] [Outro]
```

전체 출력(B와 C 전문, 가사 브리프 포함): `examples/outputs/brief-synthwave-indie-pop.txt`. 러시아어 변형: `examples/outputs/brief-russian-rock.ru.txt`.

</details>

## 설치

지시 파일을 읽는 모든 에이전트에서 동작합니다. 쓰는 것을 고르세요. 요구 사항: Python 3.9+. 설치할 패키지는 없습니다.

<details open>
<summary><b>Claude Code</b></summary>

```bash
# global
git clone https://github.com/uniqaiapp/suno-producer ~/.claude/skills/suno-producer
# or project-local
git clone https://github.com/uniqaiapp/suno-producer .claude/skills/suno-producer
# or via the skills CLI
npx skills add uniqaiapp/suno-producer
```

그다음 아무 세션에서나 `/suno-producer`를 입력하거나, 그냥 곡을 설명하면 됩니다. 스킬의 `description`이 트리거합니다. uniqaiapp 마켓플레이스가 공개되면 플러그인으로도 설치할 수 있습니다: `/plugin marketplace add uniqaiapp/skills` 다음 `/plugin install suno-producer@uniqaiapp`.

</details>

<details>
<summary><b>Cursor</b></summary>

`SKILL.md`, `scripts/`, `references/`, [`.cursor/rules/suno-producer.mdc`](.cursor/rules/suno-producer.mdc)를 프로젝트에 복사합니다. 규칙 파일이 스킬을 포함합니다.

</details>

<details>
<summary><b>Codex / AGENTS.md를 읽는 모든 에이전트</b></summary>

`SKILL.md`, `scripts/`, `references/`를 `.agents/skills/suno-producer/`에 복사하고, [`codex/INSTRUCTIONS.md`](codex/INSTRUCTIONS.md)의 스니펫을 `AGENTS.md`에 추가합니다.

</details>

<details>
<summary><b>일반 프롬프트, 또는 에이전트 없이</b></summary>

[`SKILL.md`](SKILL.md)를 아무 모델의 시스템 프롬프트에 붙여 넣으면 됩니다. 프런트매터를 제외하면 에이전트 전용 문법이 없습니다. 모든 스크립트는 단독으로 실행됩니다: `python3 scripts/<name>.py --help`.

</details>

## 한계와 정직한 안내

- 음절 수는 영어의 경우 휴리스틱이고(보통 사전 수치와 1 이내 차이. "fire", "idea", "every"가 대표적으로 틀리는 단어입니다), 러시아어는 모음 수를 정확히 셉니다. 라임 감지는 끝소리만 비교하며 강세는 전혀 모릅니다.
- 스크립트는 Suno를 호출하지 않습니다. 알려진 나쁜 생성 원인을 제거할 뿐, 좋은 결과를 보장하지는 못합니다.
- 이 README의 모든 숫자(음절 수, 규칙 수, `3 error(s), 9 warning(s)`)는 이 저장소의 스크립트를 이 저장소의 파일에 실행한 출력이며, 테스트로 재현됩니다. 장르 표의 템포 범위는 측정값이 아니라 편집 기준의 기본값이며, 파일에도 그렇게 적혀 있습니다.
- Suno와 제휴 관계가 없습니다. 저작권이 있는 가사는 포함되어 있지 않고 요청해서도 안 됩니다. lint는 특정 아티스트를 가리키는 "in the style of" 문구를 거부합니다.

## 관련 프로젝트

- [video-director](https://github.com/uniqaiapp/video-director): 한 줄 아이디어를 AI 영상 모델(Kling, Veo, Sora 등)용 샷 단위 프롬프트로 바꿉니다. 카메라, 조명, 모션 용어 포함.
- [deslop-ru](https://github.com/uniqaiapp/deslop-ru): 러시아어 텍스트에서 AI 티가 나는 군더더기를 제거합니다. 흔한 패턴을 찾아 고쳐 쓰는 스킬과 표준 라이브러리 스크립트.
- [token-diet](https://github.com/uniqaiapp/token-diet): 의미를 잃지 않고 프롬프트와 컨텍스트 토큰을 줄입니다. 측정 가능한 규칙, 표준 라이브러리 추정기, 전후 비교 예제.

## FAQ

<details>
<summary><b>Suno가 왜 "Chorus"라는 단어를 노래로 부르나요?</b></summary>

태그가 구조로 인식되지 않은 것입니다. 철자가 틀렸거나, 소문자이거나, 가사와 같은 줄에 있는 경우입니다. `references/section-tags.md`에 있는 태그를 한 줄에 하나씩, 첫 글자를 대문자로 써서 넣으세요. `suno_lint.py`가 세 경우를 모두 표시합니다(L001, L010, L014).

</details>

<details>
<summary><b>특정 아티스트 스타일의 곡을 요청할 수 있나요?</b></summary>

아니요. Suno는 아티스트 이름을 거부하고, 결과도 모방에 그칩니다. 들리는 것을 사운드 용어(시대, 악기, 프로덕션, 보컬)로 옮기세요. `references/style-prompts.md`에 표가 있고, lint가 해당 문구를 표시합니다(L007).

</details>

<details>
<summary><b>러시아어 가사에도 동작하나요?</b></summary>

네. 러시아어는 음절을 정확히 셉니다(모음 하나당 음절 하나). 라임 규칙은 열린 끝소리와 닫힌 끝소리를 모두 처리하고, `brief.py --lang ru`는 스타일 프롬프트에 `Russian-language vocals, clear diction`을 추가하며 가사 브리프를 러시아어 예산으로 바꿉니다. `references/russian-vocals.md`는 러시아어로 작성되어 있습니다.

</details>

<details>
<summary><b>글자 수 제한은 어디서 온 값인가요?</b></summary>

`suno_lint.py`의 기본값(`--max-style 1000`, `--max-lyrics 5000`)이며, 안전한 쪽으로 잡았습니다. Suno 에디터가 각 필드 옆에 현재 제한을 보여 주니, 다르면 플래그로 넘기세요.

</details>

<details>
<summary><b>음악을 생성하나요?</b></summary>

아니요. 입력(스타일 프롬프트, 구조, 가사)을 쓰고 검사합니다. 그것을 Suno에 붙여 넣는 것은 사용자의 몫입니다. UniqAI도 음악을 생성하지 않습니다.

</details>

## 기여하기

이슈와 풀 리퀘스트를 환영합니다. 변경은 작게 유지하고, PR 설명에 전후 비교 예제를 넣어 주세요. 로컬 검사 방법(`python3 tests/run.py`, 의존성 없음)은 [CONTRIBUTING.md](CONTRIBUTING.md)를 참고하세요.

## 라이선스

코드와 스킬: [MIT](LICENSE) © UniqAI. `references/`의 프롬프트 라이브러리는 CC BY 4.0입니다(저작자 표시: UniqAI, https://github.com/uniqaiapp/suno-producer). 어떤 경로가 어떤 라이선스에 속하는지는 [LICENSE](LICENSE) 파일에 적혀 있습니다.

---

<div align="center">

<sub><a href="https://uniqai.app/?utm_source=github&utm_medium=readme-ko&utm_campaign=suno-producer">UniqAI</a> 제작 — Kling 3.0, Veo 3, Flux, Nano Banana, 그리고 GPT-5/Claude/Gemini/Grok를 하나의 앱에서.</sub>

</div>
