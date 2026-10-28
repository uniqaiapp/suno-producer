<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/banner.svg">
  <source media="(prefers-color-scheme: light)" srcset="assets/banner-light.svg">
  <img alt="suno-producer: Suno style prompts and lyrics structure that behave" src="assets/banner.svg" width="1280" height="320">
</picture>

[![License: MIT](https://img.shields.io/badge/license-MIT-d1fe17?style=flat-square&labelColor=0d0f12)](LICENSE)
[![Claude Code skill](https://img.shields.io/badge/Claude_Code-skill-d1fe17?style=flat-square&labelColor=0d0f12)](#インストール)
[![Cursor](https://img.shields.io/badge/Cursor-rules-d1fe17?style=flat-square&labelColor=0d0f12)](#インストール)
[![Codex](https://img.shields.io/badge/Codex-AGENTS.md-d1fe17?style=flat-square&labelColor=0d0f12)](#インストール)
[![Made by UniqAI](https://img.shields.io/badge/made_by-UniqAI-fdfc07?style=flat-square&labelColor=0d0f12)](https://uniqai.app/?utm_source=github&utm_medium=readme-ja&utm_campaign=suno-producer)

**モデルが実際に従う Suno プロンプト、メタタグ、歌詞構成。英語とロシア語の歌詞に対応。**

[クイックスタート](#クイックスタート) · [仕組み](#仕組み) · [Lint ルール](#lint-ルール) · [例](#例) · [インストール](#インストール) · [FAQ](#faq)

</div>

[English](README.md) · [Русский](README.ru.md) · [简体中文](README.zh-CN.md) · [Español](README.es.md) · [Português (BR)](README.pt-BR.md) · 日本語 · [한국어](README.ko.md)

# suno-producer：Suno のプロンプト、メタタグ、歌詞構成

Suno のプロンプトを 3 つの部分に分けて作ります。1 行の**スタイルプロンプト**（ジャンル、BPM、キー、ムード、楽器、プロダクション、ボーカル）、メタタグ（`[Intro]`、`[Verse]`、`[Pre-Chorus]`、`[Chorus]`、`[Drop]`、`[Bridge]`、`[Outro]`）による**セクション構成**、そして生成ボーカルが急がずに歌えるだけ行の長さが揃った**歌詞**です。いずれも Suno エディタの Style フィールドと Lyrics フィールドに貼り付ける前提で書かれています。タグ一覧とフィールドの上限は Suno v4.5 以降を基準にまとめました（2026 年 10 月時点の最新モデルは v5.5、出典は [Suno の 2026 年 3 月のリリース報道](https://www.musicbusinessworldwide.com/suno-launches-v5-5-ai-model-with-voice-capture-and-personalization-features)）。実際の上限はエディタに表示され、lint の上限はフラグで上書きできます。Claude Code のスキル、Cursor のルール、Codex の `AGENTS.md` スニペットとして動作し、3 本のスクリプトは単体でも lint 付きのチェックリストとして使えます。UniqAI が作っているのは写真、動画、チャットのツールであって音楽ではありません。これは私たち自身が使っているサイドプロジェクトです。

| **ブリーフを入れると、プロンプトが出る** | **歌詞の音節数、英語とロシア語** | **クレジットを使う前に lint** |
|:---|:---|:---|
| `brief.py` は「sad synthwave, female vocal」のような説明から、スタイルプロンプト、1 軸だけ変えた A/B バリアント 2 つ、タグ付きの構成、セクションごとの音節数の目安を作ります。 | `lyric_meter.py` は行ごとの音節を数え、セクションごとの韻のスキームを導き、セクションの中央値から外れた行にフラグを立てます。英語はヒューリスティック、ロシア語は母音の正確なカウントです。 | `suno_lint.py` はタグの綴りと位置、構成の順序、セクションの長さ、フィールドの上限、アーティスト模倣の表現をチェックします。ルール id は固定で、エラー時は終了コード 1 です。 |

## クイックスタート

```bash
git clone https://github.com/uniqaiapp/suno-producer
cd suno-producer
python3 scripts/brief.py --genre synthwave --fuse "indie pop" --mood melancholic --seed 7
python3 scripts/lyric_meter.py examples/lyrics/midnight-bus.txt
python3 scripts/suno_lint.py examples/lyrics/bad-tags.txt --style examples/style/bad-style.txt
```

最初のコマンドは、バリアント B と C 付きのスタイルプロンプト、`[Intro] … [Outro]` の構成、歌詞ブリーフを出力します。2 つ目はサンプル曲の各セクションについて、行ごとの音節数と韻のスキームを出力します。3 つ目は 3 件のエラーと 9 件の警告で失敗し、それぞれにルール id と行番号が付きます。Python 3.9 以上、インストールするパッケージはありません。

## デモ

<img alt="suno-producer demo: lyric_meter reports syllables and rhyme scheme per section of the sample song, then suno_lint lists two errors and seven warnings with rule ids and line numbers on a deliberately broken file" src="assets/demo.svg" width="900">

## 仕組み

1. **ブリーフ。** `scripts/brief.py` は `references/genres.json`（ジャンルごとのテンポ範囲、キー、楽器、プロダクションの語彙、デフォルトのボーカル。編集上のデフォルトであって計測値ではありません）を読み、モデルが重視する順、つまりジャンル、フュージョン、テンポ、キー、ムード 2 語、楽器、プロダクション、ボーカル、言語の順でカンマ区切りのスタイルプロンプトを組み立てます。`--fuse` を付けると 2 つのテンポ範囲の重なりを使います。ジャンルに合ったセクション構成も選び、セクションごとの行数と音節数の目安を出力します。

2. **バリアント。** 各バリアントは記述子をちょうど 1 つだけ変えます（ボーカル、プロダクション、またはテンポを約 8 %）。そのため A/B で聴き比べれば、どの変更が効いたかが分かります。`tests/test_brief.py` が「記述子 1 つだけの差」であることを検証します。`--seed` を指定すれば出力は決定的です。

3. **音節数。** `scripts/lyric_meter.py` は歌詞を `[Section]` タグで分割し、音節を数え（英語：母音のまとまりに silent-e、-ed、-es、-le の規則を適用。ロシア語：母音 1 つが音節 1 つ）、語尾から韻のスキームを作り（大文字は完全韻、小文字は不完全韻）、セクションの中央値から 2 音節を超えて外れた行を警告します。行全体が `(backing vocals)` の行は対象外です。

4. **Lint。** `scripts/suno_lint.py` は歌詞を一度走査して下のルール表に照らして報告し、次にスタイルプロンプトのタグ、アーティストの表現、行数、テンポ、上限をチェックします。機械向けには `--json`、警告でも失敗させるには `--strict` を使います。

5. **スキル**（`SKILL.md`）がエージェント向けにこれらをまとめます。ブリーフを明確にし、`brief.py` を実行し、構成に沿って歌詞を書き、両方のチェックを実行し、Style、Lyrics、バリアントを決まった形式で納品します。生成結果が良くなかったとユーザーが戻ってきたら、`references/troubleshooting.md` に従って 1 つだけ変更します。

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

## Lint ルール

| Id | レベル | チェック内容 |
|---|---|---|
| L001 | warn | 既知の一覧（`references/section-tags.md`）にないタグ。モデルが歌ってしまうことがあります |
| L002 | warn | 最初のタグより前に歌詞がある、またはタグがまったくない |
| L003 | warn | `[Chorus]`、`[Hook]`、`[Drop]` のいずれもない（`--instrumental` でスキップ） |
| L004 | warn | 同じタグが 2 回続いている |
| L005 | warn | `[Intro]` が先頭にない、または `[Outro]` が末尾にない |
| L006 | error / warn | 行内で `[ ]`（error）または `( )`（warn）の対応が取れていない |
| L007 | error | 歌詞またはスタイルにアーティスト模倣の表現（"in the style of"、"sounds like"、"в стиле"、"как у"）がある |
| L008 | error / warn | スタイルプロンプトが上限超過（`--max-style`、デフォルト 1000）／空 |
| L009 | error | 歌詞が上限超過（`--max-lyrics`、デフォルト 5000） |
| L010 | warn | 歌詞の行の中にタグがある |
| L011 | warn | セクションが `--max-section-lines`（デフォルト 12）より長い |
| L012 | warn | スタイルプロンプトに `[Tags]` がある |
| L013 | warn | スタイルプロンプトが 3 行を超えている |
| L014 | warn | 小文字のタグ |
| L015 | info | スタイルプロンプトにテンポがない |
| L016 | warn | 行のない歌詞セクション（インストゥルメンタルのタグは対象外） |

上限はデフォルト値であって仕様ではありません。Suno エディタが各フィールドの横に現在の上限を表示します。

## 例

以下の出力はすべて `examples/outputs/` にコミットされており、`python3 tests/run.py` でバイト単位で再現されます。コマンドは `examples/README.md` に一覧があります。

<details>
<summary><b>英語の曲のメーターレポート（シンセウェイブ／インディーポップ）</b></summary>

入力：`examples/lyrics/midnight-bus.txt`。コマンド：`python3 scripts/lyric_meter.py examples/lyrics/midnight-bus.txt`。

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

完全なレポート：`examples/outputs/midnight-bus.meter.txt`。この曲はスタイルプロンプト `examples/style/midnight-bus.txt` と合わせて lint をクリーンに通過します。

</details>

<details>
<summary><b>ロシア語の曲のメーターレポート（ロックバラード）</b></summary>

入力：`examples/lyrics/severny-veter.ru.txt`。コマンド：`python3 scripts/lyric_meter.py examples/lyrics/severny-veter.ru.txt`。

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

ここでの韻は、スクリプトの語尾ルールではすべて完全韻です。不完全韻の例は上の英語の曲の 2 番の Verse を参照してください。`scheme ABaB` の小文字 `a` は、`door` / `for` が語尾だけの一致であることを示します。ロシア語固有の事項：`references/russian-vocals.md`。

</details>

<details>
<summary><b>わざと壊したファイルに対する lint</b></summary>

コマンド：`python3 scripts/suno_lint.py examples/lyrics/bad-tags.txt --style examples/style/bad-style.txt`（終了コード 1）。

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
<summary><b>1 軸バリアント付きのブリーフ</b></summary>

コマンド：`python3 scripts/brief.py --genre synthwave --fuse "indie pop" --mood melancholic --seed 7`。

```text
Style prompt (paste into the Style field)
  A  [base] synthwave, indie pop, 108 BPM, C minor, melancholic, wistful, gated reverb drums, retro drum machine, jangly electric guitar, 80s production, lo-fi warmth, warm female vocal
  B  [vocal] … 80s production, lo-fi warmth, breathy female vocal
  C  [production] … jangly electric guitar, wide stereo pads, lo-fi warmth, warm female vocal

Structure (pop)
  [Intro] [Verse 1] [Pre-Chorus] [Chorus] [Verse 2] [Pre-Chorus] [Chorus] [Bridge] [Chorus] [Outro]
```

完全な出力（B と C の全文と歌詞ブリーフ）：`examples/outputs/brief-synthwave-indie-pop.txt`。ロシア語版：`examples/outputs/brief-russian-rock.ru.txt`。

</details>

## インストール

指示ファイルを読むエージェントならどれでも使えます。お使いのものを選んでください。要件：Python 3.9 以上。インストールするパッケージはありません。

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

その後、任意のセッションで `/suno-producer` と入力するか、曲の内容を説明するだけで、スキルの `description` がトリガーになります。プラグインとしては、uniqaiapp マーケットプレイスの公開後に `/plugin marketplace add uniqaiapp/skills` に続けて `/plugin install suno-producer@uniqaiapp` を実行してください。

</details>

<details>
<summary><b>Cursor</b></summary>

`SKILL.md`、`scripts/`、`references/`、[`.cursor/rules/suno-producer.mdc`](.cursor/rules/suno-producer.mdc) をプロジェクトにコピーしてください。ルールファイルがスキルを埋め込みます。

</details>

<details>
<summary><b>Codex / AGENTS.md を読む任意のエージェント</b></summary>

`SKILL.md`、`scripts/`、`references/` を `.agents/skills/suno-producer/` にコピーし、[`codex/INSTRUCTIONS.md`](codex/INSTRUCTIONS.md) のスニペットを `AGENTS.md` に追加してください。

</details>

<details>
<summary><b>プレーンなプロンプト、またはエージェントなし</b></summary>

[`SKILL.md`](SKILL.md) を任意のモデルのシステムプロンプトに貼り付けてください。フロントマター以外にエージェント固有の構文はありません。各スクリプトは単体で動きます：`python3 scripts/<name>.py --help`。

</details>

## 制限事項と正直な注記

- 音節数は、英語についてはヒューリスティックです（辞書の数との差はたいてい 1 以内。"fire"、"idea"、"every" が典型的な外れです）。ロシア語については母音の正確なカウントです。韻の検出は語尾を比べるだけで、アクセントについては何も知りません。
- スクリプトは Suno を呼び出しません。生成が悪くなる既知の原因を取り除くだけで、良い生成を約束することはできません。
- この README にある数字（音節数、ルール数、`3 error(s), 9 warning(s)`）はすべて、このリポジトリのスクリプトをこのリポジトリのファイルに対して実行した出力で、テストで再現されます。ジャンル表のテンポ範囲は編集上のデフォルトであって計測値ではなく、ファイル内でもそう明記しています。
- Suno とは提携していません。著作権のある歌詞は含まれておらず、求めるべきでもありません。lint はアーティストの "in the style of" を拒否します。

## 関連プロジェクト

- [video-director](https://github.com/uniqaiapp/video-director)：1 行のアイデアを AI 動画モデル（Kling、Veo、Sora など）向けのショットごとのプロンプトに変換します。カメラ、ライティング、動きの語彙付き。
- [deslop-ru](https://github.com/uniqaiapp/deslop-ru)：ロシア語テキストから AI っぽい冗長表現を取り除きます。スキルと、典型的な特徴を検出して書き換える stdlib スクリプト。
- [token-diet](https://github.com/uniqaiapp/token-diet)：意味を落とさずにプロンプトとコンテキストのトークンを削減します。計測可能なルール、stdlib の推定ツール、ビフォー／アフターの例。

## FAQ

<details>
<summary><b>Suno が「Chorus」という単語を歌ってしまうのはなぜですか</b></summary>

タグが構成として認識されなかったためです。綴りの誤り、小文字、歌詞と同じ行にある、のいずれかです。`references/section-tags.md` にある既知のタグを、先頭を大文字にして 1 行に単独で置いてください。`suno_lint.py` はこの 3 つのケースすべてにフラグを立てます（L001、L010、L014）。

</details>

<details>
<summary><b>特定のアーティストの曲風で頼めますか</b></summary>

できません。Suno はアーティスト名を拒否しますし、結果は模倣になります。聞こえている音を、音の言葉（時代、楽器、プロダクション、ボーカル）に置き換えてください。`references/style-prompts.md` に対応表があり、lint がこうした表現にフラグを立てます（L007）。

</details>

<details>
<summary><b>ロシア語の歌詞でも使えますか</b></summary>

はい。ロシア語の音節カウントは正確で（母音 1 つが音節 1 つ）、韻のルールは開音節と閉音節の語尾を扱い、`brief.py --lang ru` はスタイルプロンプトに `Russian-language vocals, clear diction` を追加して、歌詞ブリーフをロシア語向けの目安に切り替えます。`references/russian-vocals.md` はロシア語で書かれています。

</details>

<details>
<summary><b>文字数の上限はどこから来ていますか</b></summary>

`suno_lint.py` のデフォルト値（`--max-style 1000`、`--max-lyrics 5000`）で、安全側に取っています。Suno エディタは各フィールドの横に現在の上限を表示するので、違っていればフラグで渡してください。

</details>

<details>
<summary><b>これは音楽を生成しますか</b></summary>

いいえ。入力（スタイルプロンプト、構成、歌詞）を書いてチェックするだけです。それを Suno に貼り付けるのはあなたです。UniqAI も音楽は生成しません。

</details>

## コントリビュート

Issue とプルリクエストを歓迎します。変更は小さく保ち、PR の説明にビフォー／アフターの例を含めてください。ローカルでのチェック（`python3 tests/run.py`、依存関係なし）については [CONTRIBUTING.md](CONTRIBUTING.md) を参照してください。

## ライセンス

コードとスキル：[MIT](LICENSE) © UniqAI。`references/` のプロンプトライブラリは CC BY 4.0（帰属表示：UniqAI, https://github.com/uniqaiapp/suno-producer ）です。どのパスがどちらのライセンスに当たるかは [LICENSE](LICENSE) ファイルに記載しています。

---

<div align="center">

<sub>制作：<a href="https://uniqai.app/?utm_source=github&utm_medium=readme-ja&utm_campaign=suno-producer">UniqAI</a> — Kling 3.0、Veo 3、Flux、Nano Banana、そして GPT-5/Claude/Gemini/Grok をひとつのアプリで。</sub>

</div>
