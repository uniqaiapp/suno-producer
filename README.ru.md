<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/banner.svg">
  <source media="(prefers-color-scheme: light)" srcset="assets/banner-light.svg">
  <img alt="suno-producer: Suno style prompts and lyrics structure that behave" src="assets/banner.svg" width="1280" height="320">
</picture>

[![License: MIT](https://img.shields.io/badge/license-MIT-d1fe17?style=flat-square&labelColor=0d0f12)](LICENSE)
[![Claude Code skill](https://img.shields.io/badge/Claude_Code-skill-d1fe17?style=flat-square&labelColor=0d0f12)](#установка)
[![Cursor](https://img.shields.io/badge/Cursor-rules-d1fe17?style=flat-square&labelColor=0d0f12)](#установка)
[![Codex](https://img.shields.io/badge/Codex-AGENTS.md-d1fe17?style=flat-square&labelColor=0d0f12)](#установка)
[![Made by UniqAI](https://img.shields.io/badge/made_by-UniqAI-fdfc07?style=flat-square&labelColor=0d0f12)](https://uniqai.app/?utm_source=github&utm_medium=readme-ru&utm_campaign=suno-producer)

**Промпты для Suno, мета-теги и структура текста, которым модель действительно следует, на английском и русском.**

[Быстрый старт](#быстрый-старт) · [Как это работает](#как-это-работает) · [Правила линта](#правила-линта) · [Примеры](#примеры) · [Установка](#установка) · [FAQ](#faq)

</div>

[English](README.md) · Русский · [简体中文](README.zh-CN.md) · [Español](README.es.md) · [Português (BR)](README.pt-BR.md) · [日本語](README.ja.md) · [한국어](README.ko.md)

# suno-producer: промпты для Suno, мета-теги и структура текста

Промпт для Suno из трёх частей: однострочный **стиль-промпт** (жанр, BPM, тональность, настроение, инструменты, продакшн, вокал), **структура секций** с мета-тегами (`[Intro]`, `[Verse]`, `[Pre-Chorus]`, `[Chorus]`, `[Drop]`, `[Bridge]`, `[Outro]`) и **текст**, у которого строки достаточно ровные, чтобы сгенерированный вокал не частил и не глотал слова; всё это пишется под поля Style и Lyrics редактора Suno. Список тегов и бюджеты полей собраны под Suno v4.5 и новее (на октябрь 2026 актуальна модель v5.5, см. [обзор мартовского релиза Suno 2026 года](https://www.musicbusinessworldwide.com/suno-launches-v5-5-ai-model-with-voice-capture-and-personalization-features)); живые лимиты показывает редактор, а бюджеты линта — это флаги, которые можно переопределить. Работает как скилл Claude Code, правило Cursor или фрагмент `AGENTS.md` для Codex, а три скрипта обходятся и без агента: обычный чеклист с линтом. UniqAI делает инструменты для фото, видео и чата, а не музыку; это побочный проект, которым мы пользуемся сами.

| **Описание на входе, промпт на выходе** | **Метр текста, EN + RU** | **Линт до того, как потратите кредиты** |
|:---|:---|:---|
| `brief.py` превращает «грустный синтвейв, женский вокал» в стиль-промпт, два A/B-варианта по одной оси, размеченную тегами структуру и слоговые нормы по секциям. | `lyric_meter.py` считает слоги в каждой строке, выводит схему рифмовки по секциям и помечает строки, выбивающиеся из медианы секции. Для английского эвристики, для русского точный подсчёт гласных. | `suno_lint.py` проверяет написание и расстановку тегов, порядок структуры, длину секций, бюджеты полей и фразы с подражанием артисту. Стабильные идентификаторы правил, код выхода 1 при ошибках. |

## Быстрый старт

```bash
git clone https://github.com/uniqaiapp/suno-producer
cd suno-producer
python3 scripts/brief.py --genre synthwave --fuse "indie pop" --mood melancholic --seed 7
python3 scripts/lyric_meter.py examples/lyrics/midnight-bus.txt
python3 scripts/suno_lint.py examples/lyrics/bad-tags.txt --style examples/style/bad-style.txt
```

Первая команда печатает стиль-промпт с вариантами B и C, структуру `[Intro] … [Outro]` и бриф для текста. Вторая печатает слоги по строкам и схему рифмовки каждой секции песни-примера. Третья завершается с тремя ошибками и девятью предупреждениями, у каждого свой идентификатор правила и номер строки. Python 3.9+, пакеты устанавливать не нужно.

## Демо

<img alt="suno-producer demo: lyric_meter reports syllables and rhyme scheme per section of the sample song, then suno_lint lists two errors and seven warnings with rule ids and line numbers on a deliberately broken file" src="assets/demo.svg" width="900">

## Как это работает

1. **Бриф.** `scripts/brief.py` читает `references/genres.json` (диапазон темпа, тональности, инструменты, слова про продакшн и вокал по умолчанию для каждого жанра; редакционные значения, а не измерения) и собирает стиль-промпт через запятую в том порядке, который модель взвешивает: жанр, смешение, темп, тональность, два слова про настроение, инструменты, продакшн, вокал, язык. С `--fuse` берётся пересечение двух диапазонов темпа. Заодно скрипт выбирает структуру секций для жанра и печатает число строк на секцию и слоговые бюджеты.

2. **Варианты.** Каждый вариант меняет ровно один дескриптор (вокал, продакшн или темп примерно на 8 %), так что A/B-прослушивание показывает, какое изменение сработало. `tests/test_brief.py` проверяет, что отличие ровно в одном дескрипторе. При заданном `--seed` вывод детерминирован.

3. **Метр.** `scripts/lyric_meter.py` разбивает текст по тегам `[Section]`, считает слоги (английский: группы гласных с правилами для немого e, -ed, -es и -le; русский: одна гласная, один слог), строит схему рифмовки по окончаниям слов (заглавная буква = точная рифма, строчная = неточная) и предупреждает, если строка отклоняется от медианы секции больше чем на два слога. Строки целиком из `(backing vocals)` не учитываются.

4. **Линт.** `scripts/suno_lint.py` проходит текст один раз и сверяет его с таблицей правил ниже, затем проверяет стиль-промпт на теги, фразы про артистов, число строк, темп и бюджет. `--json` для машин, `--strict`, чтобы падать и на предупреждениях.

5. **Скилл** (`SKILL.md`) собирает всё это для агента: уточнить задачу, запустить `brief.py`, вписать текст в структуру, прогнать обе проверки, выдать Style + Lyrics + варианты в фиксированном формате, а когда пользователь возвращается с неудачной генерацией, изменить одну вещь по `references/troubleshooting.md`.

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

## Правила линта

| Id | Уровень | Проверка |
|---|---|---|
| L001 | warn | Тега нет в известном списке (`references/section-tags.md`); модель может его спеть |
| L002 | warn | Текст до первого тега или тегов нет вовсе |
| L003 | warn | Нет `[Chorus]`, `[Hook]` или `[Drop]` (отключается флагом `--instrumental`) |
| L004 | warn | Один и тот же тег два раза подряд |
| L005 | warn | `[Intro]` не первый или `[Outro]` не последний |
| L006 | error / warn | Непарные `[ ]` (error) или `( )` (warn) в строке |
| L007 | error | Фраза с подражанием артисту ("in the style of", "sounds like", "в стиле", "как у") в тексте или стиле |
| L008 | error / warn | Стиль-промпт превышает бюджет (`--max-style`, по умолчанию 1000) / пустой |
| L009 | error | Текст превышает бюджет (`--max-lyrics`, по умолчанию 5000) |
| L010 | warn | Тег внутри строки текста |
| L011 | warn | Секция длиннее `--max-section-lines` (по умолчанию 12) |
| L012 | warn | `[Tags]` в стиль-промпте |
| L013 | warn | Стиль-промпт растянут больше чем на три строки |
| L014 | warn | Тег в нижнем регистре |
| L015 | info | В стиль-промпте нет темпа |
| L016 | warn | Секция текста без строк (инструментальные теги не учитываются) |

Бюджеты — значения по умолчанию, а не спецификация; редактор Suno показывает актуальный лимит рядом с каждым полем.

## Примеры

Каждый вывод ниже лежит в `examples/outputs/` и воспроизводится байт в байт командой `python3 tests/run.py`; команды перечислены в `examples/README.md`.

<details>
<summary><b>Отчёт о метре для английской песни (синтвейв / инди-поп)</b></summary>

Вход: `examples/lyrics/midnight-bus.txt`. Команда: `python3 scripts/lyric_meter.py examples/lyrics/midnight-bus.txt`.

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

Полный отчёт: `examples/outputs/midnight-bus.meter.txt`. Песня проходит линт без замечаний вместе со своим стиль-промптом `examples/style/midnight-bus.txt`.

</details>

<details>
<summary><b>Отчёт о метре для русской песни (рок-баллада)</b></summary>

Вход: `examples/lyrics/severny-veter.ru.txt`. Команда: `python3 scripts/lyric_meter.py examples/lyrics/severny-veter.ru.txt`.

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

Все рифмы здесь точные по правилу окончаний, которое использует скрипт. Пример неточной рифмы — второй куплет английской песни выше: `scheme ABaB`, где строчная `a` помечает `door` / `for` как совпадение только по окончанию. Особенности русского вокала: `references/russian-vocals.md`.

</details>

<details>
<summary><b>Линт на намеренно сломанном файле</b></summary>

Команда: `python3 scripts/suno_lint.py examples/lyrics/bad-tags.txt --style examples/style/bad-style.txt` (код выхода 1).

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
<summary><b>Бриф с вариантами по одной оси</b></summary>

Команда: `python3 scripts/brief.py --genre synthwave --fuse "indie pop" --mood melancholic --seed 7`.

```text
Style prompt (paste into the Style field)
  A  [base] synthwave, indie pop, 108 BPM, C minor, melancholic, wistful, gated reverb drums, retro drum machine, jangly electric guitar, 80s production, lo-fi warmth, warm female vocal
  B  [vocal] … 80s production, lo-fi warmth, breathy female vocal
  C  [production] … jangly electric guitar, wide stereo pads, lo-fi warmth, warm female vocal

Structure (pop)
  [Intro] [Verse 1] [Pre-Chorus] [Chorus] [Verse 2] [Pre-Chorus] [Chorus] [Bridge] [Chorus] [Outro]
```

Полный вывод (B и C без сокращений плюс бриф для текста): `examples/outputs/brief-synthwave-indie-pop.txt`. Русский вариант: `examples/outputs/brief-russian-rock.ru.txt`.

</details>

## Установка

Работает с любым агентом, который читает файлы инструкций. Выберите свой. Требования: Python 3.9+. Пакеты устанавливать не нужно.

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

Дальше `/suno-producer` в любой сессии или просто опишите песню; скилл срабатывает по своему `description`. Как плагин, когда будет опубликован маркетплейс uniqaiapp: `/plugin marketplace add uniqaiapp/skills`, затем `/plugin install suno-producer@uniqaiapp`.

</details>

<details>
<summary><b>Cursor</b></summary>

Скопируйте `SKILL.md`, `scripts/`, `references/` и [`.cursor/rules/suno-producer.mdc`](.cursor/rules/suno-producer.mdc) в проект. Файл правила встраивает скилл.

</details>

<details>
<summary><b>Codex / любой агент с AGENTS.md</b></summary>

Скопируйте `SKILL.md`, `scripts/` и `references/` в `.agents/skills/suno-producer/` и добавьте фрагмент из [`codex/INSTRUCTIONS.md`](codex/INSTRUCTIONS.md) в свой `AGENTS.md`.

</details>

<details>
<summary><b>Обычный промпт или вообще без агента</b></summary>

Вставьте [`SKILL.md`](SKILL.md) в системный промпт любой модели; кроме фронтматтера в нём нет синтаксиса, привязанного к агенту. Каждый скрипт запускается сам по себе: `python3 scripts/<name>.py --help`.

</details>

## Ограничения и честность

- Подсчёт слогов для английского — эвристика (обычно расходится со словарём не больше чем на один слог; «fire», «idea», «every» — типичные промахи), для русского — точный подсчёт гласных. Определение рифмы сравнивает окончания и ничего не знает об ударении.
- Скрипты не вызывают Suno. Они убирают известные причины плохих генераций, но хорошую обещать не могут.
- Каждое число в этом README (слоги, количество правил, `3 error(s), 9 warning(s)`) — вывод скрипта из этого репозитория на файле из этого репозитория, воспроизводимый тестами. Диапазоны темпа в таблице жанров — редакционные значения по умолчанию, а не измерения, и в файле так и написано.
- Проект не связан с Suno. Тексты, защищённые авторским правом, не включены, и запрашивать их не следует; линт отклоняет «в стиле» конкретного артиста.

## Похожие проекты

- [video-director](https://github.com/uniqaiapp/video-director): превращает идею в одну строку в покадровый промпт для видеомоделей (Kling, Veo, Sora и другие) со словарём камеры, света и движения.
- [deslop-ru](https://github.com/uniqaiapp/deslop-ru): убирает ИИ-штампы из русского текста: скилл плюс скрипт на чистом stdlib, который находит и переписывает типичные признаки.
- [token-diet](https://github.com/uniqaiapp/token-diet): сокращает токены промпта и контекста без потери смысла: измеримые правила, оценщик на stdlib и примеры до/после.

## FAQ

<details>
<summary><b>Почему Suno поёт слово «Chorus»?</b></summary>

Тег не был распознан как структура: опечатка, нижний регистр или тег на одной строке с текстом. Поставьте известный тег из `references/section-tags.md` на отдельную строку, с заглавной буквы. `suno_lint.py` ловит все три случая (L001, L010, L014).

</details>

<details>
<summary><b>Можно попросить песню в стиле конкретного артиста?</b></summary>

Нет; Suno отклоняет имена артистов, а результат был бы подражанием. Переведите то, что слышите, в слова о звуке (эпоха, инструменты, продакшн, вокал). В `references/style-prompts.md` есть таблица, а линт помечает такие фразы (L007).

</details>

<details>
<summary><b>Работает ли с русскими текстами?</b></summary>

Да. Для русского слоги считаются точно (одна гласная, один слог), правило рифмы учитывает открытые и закрытые окончания, а `brief.py --lang ru` добавляет `Russian-language vocals, clear diction` в стиль-промпт и переключает бриф для текста на русские бюджеты. `references/russian-vocals.md` написан по-русски.

</details>

<details>
<summary><b>Откуда взяты лимиты на символы?</b></summary>

Это значения по умолчанию в `suno_lint.py` (`--max-style 1000`, `--max-lyrics 5000`), выбранные с запасом. Редактор Suno показывает текущий лимит рядом с каждым полем; если у вас другой, передайте флаг.

</details>

<details>
<summary><b>Он генерирует музыку?</b></summary>

Нет. Он пишет входные данные (стиль-промпт, структуру, текст) и проверяет их. Вставляете их в Suno вы сами. UniqAI музыку тоже не генерирует.

</details>

## Как помочь проекту

Issues и pull request приветствуются. Делайте изменения небольшими и прикладывайте пример до/после в описании PR. Локальные проверки описаны в [CONTRIBUTING.md](CONTRIBUTING.md) (`python3 tests/run.py`, без зависимостей).

## Лицензия

Код и скилл: [MIT](LICENSE) © UniqAI. Библиотеки промптов в `references/` распространяются под CC BY 4.0 (указание авторства: UniqAI, https://github.com/uniqaiapp/suno-producer); в файле [LICENSE](LICENSE) сказано, какие пути под какой лицензией.

---

<div align="center">

<sub>Сделано <a href="https://uniqai.app/?utm_source=github&utm_medium=readme-ru&utm_campaign=suno-producer">UniqAI</a> — Kling 3.0, Veo 3, Flux, Nano Banana и GPT-5/Claude/Gemini/Grok в одном приложении.</sub>

</div>
