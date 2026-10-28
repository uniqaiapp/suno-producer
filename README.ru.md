<p align="center"><a href="README.md">English version</a></p>

# suno-producer: промпты для Suno, мета-теги и структура текста

Скилл и три скрипта на чистом Python для Suno (теги и лимиты полей собраны под Suno v4.5 и новее; на октябрь 2026 актуальна v5.5, лимиты редактор показывает сам): стиль-промпт (жанр, BPM, тональность, настроение, инструменты, продакшн, вокал), структура с тегами `[Intro]`, `[Verse]`, `[Pre-Chorus]`, `[Chorus]`, `[Bridge]`, `[Outro]` и текст, у которого строки внутри секции одной длины, чтобы вокал не частил и не глотал слова. Русский вокал: отдельный раздел `references/russian-vocals.md`.

- `scripts/brief.py`: из описания «грустный синтвейв, женский вокал» делает стиль-промпт, два A/B-варианта (каждый меняет ровно одну вещь), структуру и слоговые нормы по секциям. `--lang ru` добавляет `Russian-language vocals, clear diction`.
- `scripts/lyric_meter.py`: слоги в каждой строке (по гласным, для русского точно), схема рифмовки по секциям, предупреждения о строках, выбивающихся из медианы секции.
- `scripts/suno_lint.py`: проверка тегов, порядка секций, длины, бюджета полей и фраз «в стиле такого-то» (правила `L001`–`L016`, код выхода 1 при ошибках).

Скрипты не вызывают Suno и музыку не генерируют: они готовят и проверяют то, что вы вставите в поля Style и Lyrics. Числа в README получены этими скриптами на файлах из `examples/` и проверяются тестами.

## Установка

**Claude Code**

```bash
git clone https://github.com/uniqaiapp/suno-producer ~/.claude/skills/suno-producer
```

Дальше `/suno-producer` или просто «напиши песню для Suno …».

**Cursor**

Скопируйте `SKILL.md`, `scripts/`, `references/` и `.cursor/rules/suno-producer.mdc` в проект.

Требования: Python 3.9+, пакетов нет.

## Пример

```bash
python3 scripts/lyric_meter.py examples/lyrics/severny-veter.ru.txt
```

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

Полный отчёт: `examples/outputs/severny-veter.meter.txt`, стиль-промпт к этой песне: `examples/style/severny-veter.ru.txt`.

Полная документация, правила линта и FAQ в [английском README](README.md). Лицензия MIT (код), CC BY 4.0 (`references/`).

---

<p align="center"><sub>Сделано <a href="https://uniqai.app/?utm_source=github&utm_medium=readme-ru&utm_campaign=suno-producer-ru">UniqAI</a> — Kling 3.0, Veo 3, Flux, Nano Banana и GPT-5/Claude/Gemini/Grok в одном приложении.</sub></p>
