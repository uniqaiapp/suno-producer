<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/banner.svg">
  <source media="(prefers-color-scheme: light)" srcset="assets/banner-light.svg">
  <img alt="suno-producer: Suno style prompts and lyrics structure that behave" src="assets/banner.svg" width="1280" height="320">
</picture>

[![License: MIT](https://img.shields.io/badge/license-MIT-d1fe17?style=flat-square&labelColor=0d0f12)](LICENSE)
[![Claude Code skill](https://img.shields.io/badge/Claude_Code-skill-d1fe17?style=flat-square&labelColor=0d0f12)](#instalação)
[![Cursor](https://img.shields.io/badge/Cursor-rules-d1fe17?style=flat-square&labelColor=0d0f12)](#instalação)
[![Codex](https://img.shields.io/badge/Codex-AGENTS.md-d1fe17?style=flat-square&labelColor=0d0f12)](#instalação)
[![Made by UniqAI](https://img.shields.io/badge/made_by-UniqAI-fdfc07?style=flat-square&labelColor=0d0f12)](https://uniqai.app/?utm_source=github&utm_medium=readme-pt-br&utm_campaign=suno-producer)

**Prompts para Suno, metatags e estrutura da letra que o modelo realmente segue, em inglês e em russo.**

[Início rápido](#início-rápido) · [Como funciona](#como-funciona) · [Regras do lint](#regras-do-lint) · [Exemplos](#exemplos) · [Instalação](#instalação) · [FAQ](#faq)

</div>

[English](README.md) · [Русский](README.ru.md) · [简体中文](README.zh-CN.md) · [Español](README.es.md) · Português (BR) · [日本語](README.ja.md) · [한국어](README.ko.md)

# suno-producer: prompts para Suno, metatags e estrutura da letra

Prompts para Suno em três partes: um **prompt de estilo** de uma linha (gênero, BPM, tom, clima, instrumentos, produção, vocal), uma **estrutura de seções** com metatags (`[Intro]`, `[Verse]`, `[Pre-Chorus]`, `[Chorus]`, `[Drop]`, `[Bridge]`, `[Outro]`) e uma **letra** com versos regulares o bastante para um vocal gerado cantar sem atropelar as palavras, tudo escrito para os campos Style e Lyrics do editor do Suno. A lista de tags e os limites de campo foram levantados com base no Suno v4.5 e posteriores (o v5.5 é o modelo atual em 2026-10, segundo a [cobertura do lançamento de março de 2026](https://www.musicbusinessworldwide.com/suno-launches-v5-5-ai-model-with-voice-capture-and-personalization-features)); o editor mostra os limites vigentes, e os limites do lint são flags que você pode sobrescrever. Funciona como skill do Claude Code, regra do Cursor ou snippet de `AGENTS.md` para o Codex, e os três scripts rodam sozinhos como um checklist simples com lint. A UniqAI faz ferramentas de foto, vídeo e chat, não de música; este é um projeto paralelo que usamos no dia a dia.

| **Entra o briefing, sai o prompt** | **Métrica da letra, EN + RU** | **Lint antes de gastar créditos** |
|:---|:---|:---|
| `brief.py` transforma "sad synthwave, female vocal" em um prompt de estilo, duas variantes A/B de um eixo só, uma estrutura com tags e metas de sílabas por seção. | `lyric_meter.py` conta as sílabas de cada verso, deriva o esquema de rimas por seção e marca os versos que fogem da mediana da seção. Heurística para inglês, contagem exata de vogais para russo. | `suno_lint.py` verifica grafia e posição das tags, ordem da estrutura, tamanho das seções, limites dos campos e frases de imitação de artista. Ids de regra estáveis, código de saída 1 quando há erros. |

## Início rápido

```bash
git clone https://github.com/uniqaiapp/suno-producer
cd suno-producer
python3 scripts/brief.py --genre synthwave --fuse "indie pop" --mood melancholic --seed 7
python3 scripts/lyric_meter.py examples/lyrics/midnight-bus.txt
python3 scripts/suno_lint.py examples/lyrics/bad-tags.txt --style examples/style/bad-style.txt
```

O primeiro comando imprime um prompt de estilo com as variantes B e C, uma estrutura `[Intro] … [Outro]` e um briefing da letra. O segundo imprime as sílabas por verso e o esquema de rimas de cada seção da música de exemplo. O terceiro falha com três erros e nove avisos, cada um com id de regra e número de linha. Python 3.9+, nenhum pacote para instalar.

## Demo

<img alt="suno-producer demo: lyric_meter reports syllables and rhyme scheme per section of the sample song, then suno_lint lists two errors and seven warnings with rule ids and line numbers on a deliberately broken file" src="assets/demo.svg" width="900">

## Como funciona

1. **Briefing.** `scripts/brief.py` lê `references/genres.json` (faixa de andamento, tons, instrumentos, palavras de produção e vocal padrão por gênero; padrões editoriais, não medições) e monta um prompt de estilo separado por vírgulas na ordem em que o modelo dá peso: gênero, fusão, andamento, tom, duas palavras de clima, instrumentos, produção, vocal, idioma. Com `--fuse`, usa a interseção das duas faixas de andamento. Também escolhe a estrutura de seções do gênero e imprime os versos por seção e os orçamentos de sílabas.

2. **Variantes.** Cada variante muda exatamente um descritor (vocal, produção ou andamento em cerca de 8 %), para que uma audição A/B diga qual mudança importou. `tests/test_brief.py` garante a diferença de um descritor só. A saída é determinística para um dado `--seed`.

3. **Métrica.** `scripts/lyric_meter.py` divide a letra pelas tags `[Section]`, conta as sílabas (inglês: grupos de vogais com regras para e mudo, -ed, -es e -le; russo: uma vogal, uma sílaba), monta o esquema de rimas a partir das terminações das palavras (maiúscula = rima completa, minúscula = rima toante) e avisa quando um verso está a mais de duas sílabas da mediana da seção. Versos inteiros entre parênteses `(backing vocals)` ficam isentos.

4. **Lint.** `scripts/suno_lint.py` percorre a letra uma vez e reporta contra a tabela de regras abaixo; depois verifica o prompt de estilo quanto a tags, frases de artista, número de linhas, andamento e limite. `--json` para máquinas, `--strict` para falhar também nos avisos.

5. **A skill** (`SKILL.md`) amarra tudo para um agente: esclarecer o briefing, rodar `brief.py`, escrever a letra dentro da estrutura, rodar as duas verificações, entregar Style + Lyrics + variantes em um formato fixo e, quando o usuário voltar com uma geração ruim, mudar uma coisa só a partir de `references/troubleshooting.md`.

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

## Regras do lint

| Id | Nível | Verificação |
|---|---|---|
| L001 | warn | Tag fora da lista conhecida (`references/section-tags.md`); o modelo pode cantá-la |
| L002 | warn | Letra antes da primeira tag, ou nenhuma tag |
| L003 | warn | Sem `[Chorus]`, `[Hook]` ou `[Drop]` (pule com `--instrumental`) |
| L004 | warn | A mesma tag duas vezes seguidas |
| L005 | warn | `[Intro]` não é a primeira ou `[Outro]` não é a última |
| L006 | error / warn | `[ ]` (error) ou `( )` (warn) desbalanceados em uma linha |
| L007 | error | Frase de imitação de artista ("in the style of", "sounds like", "в стиле", "как у") na letra ou no estilo |
| L008 | error / warn | Prompt de estilo acima do limite (`--max-style`, padrão 1000) / vazio |
| L009 | error | Letra acima do limite (`--max-lyrics`, padrão 5000) |
| L010 | warn | Uma tag dentro de um verso |
| L011 | warn | Seção maior que `--max-section-lines` (padrão 12) |
| L012 | warn | `[Tags]` no prompt de estilo |
| L013 | warn | Prompt de estilo espalhado por mais de três linhas |
| L014 | warn | Tag em minúsculas |
| L015 | info | Sem andamento no prompt de estilo |
| L016 | warn | Seção de letra sem versos (tags instrumentais ficam isentas) |

Os limites são padrões, não uma especificação; o editor do Suno mostra o limite vigente ao lado de cada campo.

## Exemplos

Toda saída abaixo está versionada em `examples/outputs/` e é reproduzida byte a byte por `python3 tests/run.py`; `examples/README.md` lista os comandos.

<details>
<summary><b>Relatório de métrica de uma música em inglês (synthwave / indie pop)</b></summary>

Entrada: `examples/lyrics/midnight-bus.txt`. Comando: `python3 scripts/lyric_meter.py examples/lyrics/midnight-bus.txt`.

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

Relatório completo: `examples/outputs/midnight-bus.meter.txt`. A música passa limpa no lint com seu prompt de estilo `examples/style/midnight-bus.txt`.

</details>

<details>
<summary><b>Relatório de métrica de uma música em russo (balada rock)</b></summary>

Entrada: `examples/lyrics/severny-veter.ru.txt`. Comando: `python3 scripts/lyric_meter.py examples/lyrics/severny-veter.ru.txt`.

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

Aqui toda rima é completa pela regra de terminação do script. Para uma rima toante, veja a segunda estrofe da música em inglês acima: `scheme ABaB`, em que o `a` minúsculo marca `door` / `for` como coincidência só de terminação. Particularidades do russo: `references/russian-vocals.md`.

</details>

<details>
<summary><b>Lint em um arquivo quebrado de propósito</b></summary>

Comando: `python3 scripts/suno_lint.py examples/lyrics/bad-tags.txt --style examples/style/bad-style.txt` (código de saída 1).

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
<summary><b>Briefing com variantes de um eixo só</b></summary>

Comando: `python3 scripts/brief.py --genre synthwave --fuse "indie pop" --mood melancholic --seed 7`.

```text
Style prompt (paste into the Style field)
  A  [base] synthwave, indie pop, 108 BPM, C minor, melancholic, wistful, gated reverb drums, retro drum machine, jangly electric guitar, 80s production, lo-fi warmth, warm female vocal
  B  [vocal] … 80s production, lo-fi warmth, breathy female vocal
  C  [production] … jangly electric guitar, wide stereo pads, lo-fi warmth, warm female vocal

Structure (pop)
  [Intro] [Verse 1] [Pre-Chorus] [Chorus] [Verse 2] [Pre-Chorus] [Chorus] [Bridge] [Chorus] [Outro]
```

Saída completa (B e C sem cortes, mais o briefing da letra): `examples/outputs/brief-synthwave-indie-pop.txt`. Variante em russo: `examples/outputs/brief-russian-rock.ru.txt`.

</details>

## Instalação

Funciona com qualquer agente que leia arquivos de instrução. Escolha o seu. Requisitos: Python 3.9+. Nenhum pacote para instalar.

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

Depois, `/suno-producer` em qualquer sessão, ou apenas descreva a música; a `description` da skill a aciona. Como plugin, quando o marketplace uniqaiapp for publicado: `/plugin marketplace add uniqaiapp/skills` e então `/plugin install suno-producer@uniqaiapp`.

</details>

<details>
<summary><b>Cursor</b></summary>

Copie `SKILL.md`, `scripts/`, `references/` e [`.cursor/rules/suno-producer.mdc`](.cursor/rules/suno-producer.mdc) para o seu projeto. O arquivo de regra incorpora a skill.

</details>

<details>
<summary><b>Codex / qualquer agente que leia AGENTS.md</b></summary>

Copie `SKILL.md`, `scripts/` e `references/` para `.agents/skills/suno-producer/` e adicione o snippet de [`codex/INSTRUCTIONS.md`](codex/INSTRUCTIONS.md) ao seu `AGENTS.md`.

</details>

<details>
<summary><b>Prompt puro, ou sem agente nenhum</b></summary>

Cole [`SKILL.md`](SKILL.md) no system prompt de qualquer modelo; ele não tem sintaxe específica de agente fora do frontmatter. Todo script roda sozinho: `python3 scripts/<name>.py --help`.

</details>

## Limites e honestidade

- A contagem de sílabas é heurística para inglês (em geral erra por no máximo uma sílaba em relação ao dicionário; "fire", "idea", "every" são os tropeços típicos) e contagem exata de vogais para russo. A detecção de rimas compara terminações e não sabe nada sobre tonicidade.
- Os scripts nunca chamam o Suno. Eles removem as causas conhecidas de gerações ruins; não podem prometer uma boa.
- Todo número deste README (contagens de sílabas, contagens de regras, `3 error(s), 9 warning(s)`) é a saída de um script deste repositório sobre um arquivo deste repositório, reproduzida pelos testes. As faixas de andamento da tabela de gêneros são padrões editoriais, não medições, e o próprio arquivo diz isso.
- Sem vínculo com o Suno. Nenhuma letra protegida por direitos autorais está incluída nem deve ser pedida; o lint rejeita "in the style of" seguido de artista.

## Projetos relacionados

- [video-director](https://github.com/uniqaiapp/video-director): transforma uma ideia de uma linha em um prompt plano a plano para modelos de vídeo por IA (Kling, Veo, Sora e outros), com vocabulário de câmera, luz e movimento.
- [deslop-ru](https://github.com/uniqaiapp/deslop-ru): remove o enchimento com cara de IA de textos em russo: uma skill mais um script só com a biblioteca padrão que marca e reescreve os vícios de sempre.
- [token-diet](https://github.com/uniqaiapp/token-diet): corta tokens de prompt e de contexto sem perder significado: regras mensuráveis, um estimador só com a biblioteca padrão e exemplos de antes/depois.

## FAQ

<details>
<summary><b>Por que o Suno canta a palavra "Chorus"?</b></summary>

A tag não foi reconhecida como estrutura: grafia errada, minúsculas ou na mesma linha da letra. Coloque uma tag conhecida de `references/section-tags.md` em uma linha própria, com inicial maiúscula. `suno_lint.py` marca os três casos (L001, L010, L014).

</details>

<details>
<summary><b>Posso pedir uma música no estilo de um artista específico?</b></summary>

Não; o Suno rejeita nomes de artistas, e o resultado seria uma imitação. Traduza o que você ouve em palavras de som (época, instrumentos, produção, vocal). `references/style-prompts.md` tem uma tabela, e o lint marca as frases (L007).

</details>

<details>
<summary><b>Funciona com letras em russo?</b></summary>

Sim. A contagem de sílabas é exata para russo (uma vogal, uma sílaba), a regra de rima trata terminações abertas e fechadas, e `brief.py --lang ru` adiciona `Russian-language vocals, clear diction` ao prompt de estilo e muda o briefing da letra para os orçamentos do russo. `references/russian-vocals.md` está em russo.

</details>

<details>
<summary><b>De onde vêm os limites de caracteres?</b></summary>

São padrões em `suno_lint.py` (`--max-style 1000`, `--max-lyrics 5000`), escolhidos para ficar do lado seguro. O editor do Suno mostra o limite atual ao lado de cada campo; passe a flag se o seu for diferente.

</details>

<details>
<summary><b>Isso gera música?</b></summary>

Não. Ele escreve as entradas (prompt de estilo, estrutura, letra) e as verifica. Você cola tudo no Suno. A UniqAI também não gera música.

</details>

## Como contribuir

Issues e pull requests são bem-vindos. Mantenha as mudanças pequenas e inclua um exemplo de antes/depois na descrição do PR. Veja [CONTRIBUTING.md](CONTRIBUTING.md) para as verificações locais (`python3 tests/run.py`, sem dependências).

## Licença

Código e skill: [MIT](LICENSE) © UniqAI. As bibliotecas de prompts em `references/` são CC BY 4.0 (atribuição: UniqAI, https://github.com/uniqaiapp/suno-producer); o arquivo [LICENSE](LICENSE) diz quais caminhos ficam sob qual licença.

---

<div align="center">

<sub>Feito por <a href="https://uniqai.app/?utm_source=github&utm_medium=readme-pt-br&utm_campaign=suno-producer">UniqAI</a> — Kling 3.0, Veo 3, Flux, Nano Banana e GPT-5/Claude/Gemini/Grok em um só app.</sub>

</div>
