<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/banner.svg">
  <source media="(prefers-color-scheme: light)" srcset="assets/banner-light.svg">
  <img alt="suno-producer: Suno style prompts and lyrics structure that behave" src="assets/banner.svg" width="1280" height="320">
</picture>

[![License: MIT](https://img.shields.io/badge/license-MIT-d1fe17?style=flat-square&labelColor=0d0f12)](LICENSE)
[![Claude Code skill](https://img.shields.io/badge/Claude_Code-skill-d1fe17?style=flat-square&labelColor=0d0f12)](#安装)
[![Cursor](https://img.shields.io/badge/Cursor-rules-d1fe17?style=flat-square&labelColor=0d0f12)](#安装)
[![Codex](https://img.shields.io/badge/Codex-AGENTS.md-d1fe17?style=flat-square&labelColor=0d0f12)](#安装)
[![Made by UniqAI](https://img.shields.io/badge/made_by-UniqAI-fdfc07?style=flat-square&labelColor=0d0f12)](https://uniqai.app/?utm_source=github&utm_medium=readme-zh-cn&utm_campaign=suno-producer)

**模型真正会听话的 Suno 提示词、元标签和歌词结构，支持英文和俄文。**

[快速开始](#快速开始) · [工作原理](#工作原理) · [Lint 规则](#lint-规则) · [示例](#示例) · [安装](#安装) · [FAQ](#faq)

</div>

[English](README.md) · [Русский](README.ru.md) · 简体中文 · [Español](README.es.md) · [Português (BR)](README.pt-BR.md) · [日本語](README.ja.md) · [한국어](README.ko.md)

# suno-producer：Suno 提示词、元标签与歌词结构

Suno 提示词分三部分：一行**风格提示词**（曲风、BPM、调性、情绪、乐器、制作风格、人声），一套带元标签的**段落结构**（`[Intro]`、`[Verse]`、`[Pre-Chorus]`、`[Chorus]`、`[Drop]`、`[Bridge]`、`[Outro]`），以及每行长度足够均匀、让生成的人声唱起来不赶拍的**歌词**，分别对应 Suno 编辑器的 Style 和 Lyrics 两个字段。标签列表和字段预算是按 Suno v4.5 及以上版本整理的（截至 2026 年 10 月，当前模型为 v5.5，见 [Suno 2026 年 3 月发布报道](https://www.musicbusinessworldwide.com/suno-launches-v5-5-ai-model-with-voice-capture-and-personalization-features)）；编辑器会显示实时上限，lint 的预算只是可以覆盖的参数。它可以作为 Claude Code 技能、Cursor 规则或 Codex 的 `AGENTS.md` 片段运行，三个脚本也能脱离代理独立使用，相当于一份带 lint 的检查清单。UniqAI 做的是图片、视频和聊天工具，不做音乐；这是我们自己在用的一个副项目。

| **输入简报，输出提示词** | **歌词音节，英文 + 俄文** | **花积分之前先 lint** |
|:---|:---|:---|
| `brief.py` 把“sad synthwave, female vocal”这样的描述变成一条风格提示词、两个单变量 A/B 变体、一套带标签的结构和每段的音节目标。 | `lyric_meter.py` 统计每行音节数，推导每段的押韵格式，并标出偏离该段中位数的行。英文用启发式规则，俄文按元音精确计数。 | `suno_lint.py` 检查标签拼写和位置、结构顺序、段落长度、字段预算以及模仿歌手的措辞。规则 id 固定，有错误时退出码为 1。 |

## 快速开始

```bash
git clone https://github.com/uniqaiapp/suno-producer
cd suno-producer
python3 scripts/brief.py --genre synthwave --fuse "indie pop" --mood melancholic --seed 7
python3 scripts/lyric_meter.py examples/lyrics/midnight-bus.txt
python3 scripts/suno_lint.py examples/lyrics/bad-tags.txt --style examples/style/bad-style.txt
```

第一条命令输出一条风格提示词及其 B、C 变体、一套 `[Intro] … [Outro]` 结构和一份歌词简报。第二条输出示例歌曲每段的每行音节数和押韵格式。第三条会失败，报出三个错误和九个警告，每条都带规则 id 和行号。Python 3.9+，无需安装任何包。

## 演示

<img alt="suno-producer demo: lyric_meter reports syllables and rhyme scheme per section of the sample song, then suno_lint lists two errors and seven warnings with rule ids and line numbers on a deliberately broken file" src="assets/demo.svg" width="900">

## 工作原理

1. **简报。** `scripts/brief.py` 读取 `references/genres.json`（每种曲风的速度范围、调性、乐器、制作风格词汇和默认人声；这些是编辑性默认值，不是测量结果），按模型的权重顺序拼出一条逗号分隔的风格提示词：曲风、融合曲风、速度、调性、两个情绪词、乐器、制作风格、人声、语言。使用 `--fuse` 时取两个速度范围的交集。它还会为该曲风选定段落结构，并打印每段行数和音节预算。

2. **变体。** 每个变体只改动一个描述项（人声、制作风格，或把速度调整约 8%），这样 A/B 试听就能判断是哪个改动起了作用。`tests/test_brief.py` 会断言两者只差一个描述项。给定 `--seed` 时输出是确定的。

3. **音节。** `scripts/lyric_meter.py` 按 `[Section]` 标签切分歌词，统计音节（英文：按元音组计数，并处理不发音的 e、-ed、-es 和 -le 规则；俄文：一个元音一个音节），根据词尾构建押韵格式（大写 = 全韵，小写 = 半韵），并在某行与该段中位数相差超过两个音节时发出警告。整行的 `(backing vocals)` 不计入。

4. **Lint。** `scripts/suno_lint.py` 遍历一遍歌词，按下方规则表报告问题，然后检查风格提示词中的标签、模仿歌手的措辞、行数、速度和预算。`--json` 供程序读取，`--strict` 让警告也视为失败。

5. **技能**（`SKILL.md`）把这一切串给代理：澄清简报，运行 `brief.py`，按结构写歌词，运行两项检查，以固定格式交付 Style + Lyrics + 变体；当用户拿着一次糟糕的生成结果回来时，按 `references/troubleshooting.md` 只改一处。

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

## Lint 规则

| Id | 级别 | 检查内容 |
|---|---|---|
| L001 | warn | 标签不在已知列表中（`references/section-tags.md`）；模型可能会把它唱出来 |
| L002 | warn | 第一个标签之前出现了歌词，或者完全没有标签 |
| L003 | warn | 没有 `[Chorus]`、`[Hook]` 或 `[Drop]`（可用 `--instrumental` 跳过） |
| L004 | warn | 同一个标签连续出现两次 |
| L005 | warn | `[Intro]` 不在最前，或 `[Outro]` 不在最后 |
| L006 | error / warn | 某一行的 `[ ]`（error）或 `( )`（warn）不配对 |
| L007 | error | 歌词或风格中出现模仿歌手的措辞（"in the style of"、"sounds like"、"в стиле"、"как у"） |
| L008 | error / warn | 风格提示词超出预算（`--max-style`，默认 1000）/ 为空 |
| L009 | error | 歌词超出预算（`--max-lyrics`，默认 5000） |
| L010 | warn | 标签混在歌词行中间 |
| L011 | warn | 段落长度超过 `--max-section-lines`（默认 12） |
| L012 | warn | 风格提示词中出现 `[Tags]` |
| L013 | warn | 风格提示词超过三行 |
| L014 | warn | 标签为小写 |
| L015 | info | 风格提示词中没有速度 |
| L016 | warn | 某个歌词段落没有内容行（纯乐器标签除外） |

这些预算是默认值，不是规范；Suno 编辑器会在每个字段旁显示实时上限。

## 示例

下面的每个输出都提交在 `examples/outputs/` 下，并由 `python3 tests/run.py` 逐字节复现；`examples/README.md` 列出了对应命令。

<details>
<summary><b>英文歌曲的音节报告（synthwave / indie pop）</b></summary>

输入：`examples/lyrics/midnight-bus.txt`。命令：`python3 scripts/lyric_meter.py examples/lyrics/midnight-bus.txt`。

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

完整报告：`examples/outputs/midnight-bus.meter.txt`。这首歌配合其风格提示词 `examples/style/midnight-bus.txt` 可以干净地通过 lint。

</details>

<details>
<summary><b>俄文歌曲的音节报告（摇滚抒情曲）</b></summary>

输入：`examples/lyrics/severny-veter.ru.txt`。命令：`python3 scripts/lyric_meter.py examples/lyrics/severny-veter.ru.txt`。

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

按脚本的词尾规则，这里每一处都是全韵。半韵的例子见上面英文歌曲的第二段主歌：`scheme ABaB`，其中小写 `a` 表示 `door` / `for` 只是词尾相近。俄文的特殊之处见 `references/russian-vocals.md`。

</details>

<details>
<summary><b>对一个故意写坏的文件做 lint</b></summary>

命令：`python3 scripts/suno_lint.py examples/lyrics/bad-tags.txt --style examples/style/bad-style.txt`（退出码 1）。

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
<summary><b>带单变量变体的简报</b></summary>

命令：`python3 scripts/brief.py --genre synthwave --fuse "indie pop" --mood melancholic --seed 7`。

```text
Style prompt (paste into the Style field)
  A  [base] synthwave, indie pop, 108 BPM, C minor, melancholic, wistful, gated reverb drums, retro drum machine, jangly electric guitar, 80s production, lo-fi warmth, warm female vocal
  B  [vocal] … 80s production, lo-fi warmth, breathy female vocal
  C  [production] … jangly electric guitar, wide stereo pads, lo-fi warmth, warm female vocal

Structure (pop)
  [Intro] [Verse 1] [Pre-Chorus] [Chorus] [Verse 2] [Pre-Chorus] [Chorus] [Bridge] [Chorus] [Outro]
```

完整输出（B 和 C 的全文，外加歌词简报）：`examples/outputs/brief-synthwave-indie-pop.txt`。俄文版本：`examples/outputs/brief-russian-rock.ru.txt`。

</details>

## 安装

任何会读取指令文件的代理都能用，选你的那个即可。要求：Python 3.9+，无需安装任何包。

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

之后在任意会话中输入 `/suno-producer`，或者直接描述你要的歌；技能的 `description` 会自动触发它。作为插件使用（待 uniqaiapp 市场发布后）：先 `/plugin marketplace add uniqaiapp/skills`，再 `/plugin install suno-producer@uniqaiapp`。

</details>

<details>
<summary><b>Cursor</b></summary>

把 `SKILL.md`、`scripts/`、`references/` 和 [`.cursor/rules/suno-producer.mdc`](.cursor/rules/suno-producer.mdc) 复制到你的项目中。规则文件会内嵌整个技能。

</details>

<details>
<summary><b>Codex / 任何读取 AGENTS.md 的代理</b></summary>

把 `SKILL.md`、`scripts/` 和 `references/` 复制到 `.agents/skills/suno-producer/`，再把 [`codex/INSTRUCTIONS.md`](codex/INSTRUCTIONS.md) 中的片段加到你的 `AGENTS.md` 里。

</details>

<details>
<summary><b>纯提示词，或者完全不用代理</b></summary>

把 [`SKILL.md`](SKILL.md) 粘贴到任意模型的系统提示词中；除 frontmatter 外它没有任何代理专属语法。每个脚本都能独立运行：`python3 scripts/<name>.py --help`。

</details>

## 限制与诚实说明

- 英文音节数是启发式估计（通常与词典计数相差不超过一个；“fire”“idea”“every”是典型的误判），俄文按元音精确计数。押韵检测只比较词尾，不了解重音。
- 脚本从不调用 Suno。它们消除的是已知的出坏结果的原因，并不能保证出好结果。
- 本 README 中的每个数字（音节数、规则数、`3 error(s), 9 warning(s)`）都是本仓库脚本在本仓库文件上的输出，并由测试复现。曲风表里的速度范围是编辑性默认值，不是测量结果，文件里也是这么写的。
- 与 Suno 无关联。不包含任何受版权保护的歌词，也不应索取；lint 会拒绝“模仿某歌手风格”的写法。

## 相关项目

- [video-director](https://github.com/uniqaiapp/video-director)：把一句话创意变成 AI 视频模型（Kling、Veo、Sora 等）的分镜提示词，附带镜头、灯光和运动词汇。
- [deslop-ru](https://github.com/uniqaiapp/deslop-ru)：去掉俄文文本中的 AI 腔套话：一个技能加一个标准库脚本，标记并改写常见的 AI 痕迹。
- [token-diet](https://github.com/uniqaiapp/token-diet)：在不损失语义的前提下削减提示词和上下文的 token：可度量的规则、一个标准库估算器和前后对比示例。

## FAQ

<details>
<summary><b>为什么 Suno 把“Chorus”这个词唱了出来？</b></summary>

因为这个标签没有被识别为结构：拼写错误、小写，或者和歌词写在同一行。请把 `references/section-tags.md` 中的已知标签单独放一行，并使用首字母大写。`suno_lint.py` 会标出这三种情况（L001、L010、L014）。

</details>

<details>
<summary><b>能不能要求一首“某某歌手风格”的歌？</b></summary>

不能；Suno 会拒绝歌手姓名，而且结果也只是模仿。把你听到的东西翻译成声音词汇（年代、乐器、制作风格、人声）。`references/style-prompts.md` 里有一张对照表，lint 也会标出这类措辞（L007）。

</details>

<details>
<summary><b>支持俄文歌词吗？</b></summary>

支持。俄文的音节计数是精确的（一个元音一个音节），押韵规则能处理开音节和闭音节结尾，`brief.py --lang ru` 会在风格提示词中加入 `Russian-language vocals, clear diction`，并把歌词简报切换为俄文预算。`references/russian-vocals.md` 本身是俄文写的。

</details>

<details>
<summary><b>字符上限是从哪来的？</b></summary>

它们是 `suno_lint.py` 中的默认值（`--max-style 1000`、`--max-lyrics 5000`），取得偏保守。Suno 编辑器会在每个字段旁显示当前上限；如果你的不一样，传入对应参数即可。

</details>

<details>
<summary><b>它会生成音乐吗？</b></summary>

不会。它负责写输入（风格提示词、结构、歌词）并做检查，你再把它们粘贴到 Suno 里。UniqAI 也不生成音乐。

</details>

## 参与贡献

欢迎提 issue 和 pull request。改动尽量小，并在 PR 描述中附上前后对比示例。本地检查方式见 [CONTRIBUTING.md](CONTRIBUTING.md)（`python3 tests/run.py`，无依赖）。

## 许可证

代码和技能：[MIT](LICENSE) © UniqAI。`references/` 中的提示词库采用 CC BY 4.0（署名：UniqAI，https://github.com/uniqaiapp/suno-producer ）；[LICENSE](LICENSE) 文件说明了哪些路径适用哪种许可证。

---

<div align="center">

<sub>由 <a href="https://uniqai.app/?utm_source=github&utm_medium=readme-zh-cn&utm_campaign=suno-producer">UniqAI</a> 出品 — Kling 3.0、Veo 3、Flux、Nano Banana 和 GPT-5/Claude/Gemini/Grok，集成在一个应用里。</sub>

</div>
