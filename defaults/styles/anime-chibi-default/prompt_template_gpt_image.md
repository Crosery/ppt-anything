# Prompt template — gpt-image-2 variant

**Use this file when generating with `-m gpt-image-2` (any third-party bridge that
exposes the OpenAI-family `gpt-image-2` model on the Gemini-shape endpoint).**
For seedream / xais / Gemini Image (gemini-3-pro-image-preview etc), use the main
`prompt_template.md` instead.

---

## Why this file exists

`gpt-image-2` is OpenAI-family — instruction-tuned, not diffusion-tag-tuned. The default
`prompt_template.md` is shaped around seedream's preferences: dense feature-soup, name-summon
character invocation, "preserving X, Y, Z" tails, multi-ref chains, maximalist decoration.
gpt-image-2 reads those prompts and produces flat, generic, low-fidelity output.

The differences (each one drives a rule below):

| Dimension | seedream-style (main) | gpt-image-2-style (here) |
|---|---|---|
| Prompt voice | tag-soup + paragraph mash | **editorial brief** — each section has one job |
| Character ID | name-summon + "preserving …" | **explicit visual features**, every slide |
| Refs | character ref + previous slide (chain) | **single ref** — only the original character anchor |
| Style declaration | repeated 4-5× across the prompt | **one sentence**, not restated |
| Text accuracy hint | repeated 3× ("no typos / no broken strokes / no garbled glyphs") | **one** clean directive in the TEXT section |
| Decoration density | "richly scattered, fill the corners" | **3–5 items**, generous whitespace |
| Resolution flag | `--size 3k` available | **no `--size`** — gpt-image-2 only honors `-r` |

The aesthetic target stays the same: SD chibi watercolor + LXGW WenKai Chinese + content-first hierarchy.
What changes is *how* you ask the model for it.

---

## Top-level rules (gpt-image-2)

1. **Editorial brief voice, not feature-soup.** Write each section as a coherent paragraph
   that a human editor could read aloud and understand. No bullet-stuffed adjective walls.
2. **Describe characters by visible features, not by anime-canon name.** gpt-image-2's anime
   training is weaker than seedream's. "Mahiro Oyama from ONIMAI" is mostly noise; "a chibi
   girl with very long silver-pink gradient hair, one large springy ahoge, cute sailor-style
   uniform with red ribbon" actually steers the output. The ref image carries the rest.
3. **One ref only.** Pass the original `~/.anything-ppt/characters/<slug>/<slug>.<ext>` and stop. Adding the previous
   slide as a second ref makes gpt-image-2 average the two and drift toward neither. If
   continuity feels off between slides, fix the *prompt's style sentence*, don't pile on refs.
4. **State the style once.** A single sentence near the top: "Render this as a soft-watercolor
   children's-storybook illustration, super-deformed chibi characters, pastel palette, hand-drawn
   feel." Don't repeat "watercolor / chibi / pastel" five more times — gpt-image-2 reads
   redundancy as emphasis on those words and starts over-saturating that mood.
5. **Quote every Chinese string verbatim.** Each text element gets one line: position label +
   a quoted Chinese string. The model is strong at multilingual rendering when text strings
   are clearly demarcated; it falters when Chinese is buried in English prose.
6. **Default decoration count: 3–5 elements.** gpt-image-2 prefers editorial whitespace.
   "Pile on 10 cute icons everywhere" produces clutter on this model. Pick 3–5 motifs that
   serve the beat. Copy-dense slides go down to 2.
7. **Zero emoji in text slots.** Same as the main template — emoji render as flat OS glyphs
   and break the watercolor look. Use color-coded pills or describe motifs as paint strokes.
8. **Keep Chinese lines short.** Titles ≤ 12 chars, body lines ≤ 14 chars. gpt-image-2 is
   stronger than seedream on Chinese glyphs but still occasionally smears very long strings.
9. **No `--size` flag.** gpt-image-2 ignores it. Use `-r 16:9`.

---

## Core skeleton (gpt-image-2)

Every slide prompt follows this 7-block structure. Section headers are **mandatory** —
gpt-image-2 parses headers as scope boundaries and produces cleaner layouts when they're
explicit.

```
OVERVIEW
A 16:9 illustrated PPT slide. <<ONE_LINE_BEAT_DESCRIPTION>>. The title and body copy are
the visual anchor; characters and decorations support, never compete.

STYLE
Soft-watercolor children's-storybook illustration, super-deformed 2.5-head-body chibi
characters with large round shiny eyes, small pink blush circles, tiny mouths, pastel
palette, gentle rounded outlines, hand-painted brush feel.

CHARACTER(S)
<<CHARACTER_BRIEF>>  ← explicit visual description; see § Character description below.

LAYOUT
<<LAYOUT_BLOCK>>  ← one of the layout briefs from § Layouts below.

TEXT CONTENT (every Chinese string below must render exactly as written, in a bold
handwritten font similar to LXGW WenKai 霞鹜文楷, dark warm brown for titles, darker gray
for body):
- <<POSITION_1>>: "<<CHINESE_STRING_1>>"
- <<POSITION_2>>: "<<CHINESE_STRING_2>>"
- (more as needed — one line per text element)

DECORATIVE ELEMENTS
3–5 small hand-painted watercolor motifs, picked from a single topic family (see motif
table in style_guide.md § 7). Each one earns its place by reinforcing the beat.
Examples: <<DECORATION_LIST>>.

BACKGROUND
Warm cream-yellow (#FFF6E4) base with very subtle gradient and faint paper-grain texture.
No magical forest, no petal swarms, no cloud or star fields — the background frames
content, never decorates it.
```

That's the whole skeleton. Keep it under ~350 words total — gpt-image-2 starts ignoring
later sections in mega-prompts.

---

## Character description (the load-bearing rule)

For gpt-image-2, the character one-liner from `~/.anything-ppt/characters/<slug>/<slug>.md` is **not enough**. Rewrite
each character into 2–3 sentences that describe what the model needs to *paint*:

- Hair (color + length + signature shape — ahoge, twin tails, bangs, etc.)
- Eyes (color + any signature like glasses)
- Outfit (general shape + signature item like ribbon, lab coat, hoodie color)
- Body proportion (always: "super-deformed 2.5-head-body chibi")
- Pose (one specific terminal pose from style_guide.md § 3)
- Expression (named — "confident mentor smile", "sparkly-eyed amazement", etc.)

**Do NOT** rely on "Mihari Oyama from ONIMAI, drawn in chibi style — preserving her glasses
and twin tails". That sentence is 80% wasted on gpt-image-2.

**Do** write: "On the left: a chibi teenage scientist girl with long dark-brown hair in twin
tails tied with small ribbons, big round red-framed glasses, a clean white lab coat over a
school uniform, pointing firmly at the title with a small wooden pointer stick, confident
mentor smile, pink blush circles on her cheeks, super-deformed 2.5-head-body chibi proportions."

The ref image carries face/style fidelity; the prompt sentence carries the *layout-relevant*
features that need to survive into this specific scene.

---

## Layouts (A–H, gpt-image-2 phrasing)

Same eight layout IDs as the main template; rewritten as editorial briefs.

### A — Dual-banner

```
LAYOUT
The slide is split into a top title band, a left ribbon panel, a right ribbon panel, a
small central illustration between the panels, and a thin caption strip at the bottom.
The left ribbon is peach-pink (#FFB5A7), the right ribbon is mint-green (#B8DFC6); each
ribbon has a wavy hand-drawn frame and holds one main line plus one small rounded sub-label.
A single small illustration sits centered between the two ribbons.
```

### B — Centered hero

```
LAYOUT
The slide has one dominant element: a large bold title at the upper third, one hero
illustration filling the middle, and a single subtitle line at the bottom. Generous
whitespace surrounds everything. No ribbons, no sidebars — whitespace is part of the design.
```

### C — Three-column

```
LAYOUT
Below the top title, three equal vertical columns sit side by side, separated by thin soft
divider lines. Each column has a small painted icon at the top, a bold headline below the
icon, and one short body line under the headline. One small chibi character stands in a
bottom corner reacting to the three columns.
```

### D — Top-copy bottom-scene

```
LAYOUT
The top 60% of the slide holds the title (left-aligned, bold) and 2–3 short body
paragraphs in dark gray. The bottom 40% is a horizontal scene where the characters are
placed low, reacting to what the copy above says with poses and expressions that match.
```

### E — Dialogue bubbles

```
LAYOUT
A small unobtrusive title sits at the top. Two characters face each other across the
middle, each with a large hand-drawn speech bubble — peach-pink for the left character,
mint-green for the right. The bubbles are the dominant visual; the characters are in
mid-conversation poses (pointing, explaining, surprised, nodding). No ribbons.
```

### F — Flow / timeline

```
LAYOUT
Below the top title, a horizontal flow runs left to right with N small mini-scenes
connected by hand-drawn arrow strokes. Each node has a tiny illustration plus a one-line
label. One character anchors the start (far left), one character anchors the end (far
right). A small caption sits at the bottom. No additional decorations — the flow IS the
visual richness.
```

### G — Split-screen

```
LAYOUT
A diagonal split divides the slide into a cool-toned, slightly desaturated left half (the
"before / wrong / old" side) and a warm-toned, fully saturated right half (the "after /
right / new" side). The title crosses the split at the top. Each half holds one mini-scene
plus one short Chinese label and an optional hand-painted brush-stroke mark (a red brush
cross on the left, a green brush tick on the right) — never Unicode emoji. A bottom caption
crosses both halves.
```

### H — Spotlight + sidebar

```
LAYOUT
One large central illustration dominates 60% of the slide. A right sidebar holds 2–3
small stacked callouts, each with a small painted motif and a short phrase. One chibi
character interacts with the central illustration from a corner of the spotlight.
```

---

## Reference-image discipline (single-ref rule)

For every slide:

```bash
cat /tmp/<deck>_sN_prompt.txt | \
  ~/.claude/skills/ppt-anything/tools/generate-image.py \
    -m gpt-image-2 \
    -r 16:9 \
    -n <deck_slug>_sN \
    --ref ~/.anything-ppt/characters/<slug>/<slug>.<ext> \
    --no-preview
```

**One `--ref`. The original character anchor.** That's it.

If a slide has two characters, pass both character refs (two `--ref` flags is fine when
each ref is a *different identity*). What gpt-image-2 dislikes is **two refs of the same
identity** (canonical character + previous slide). That's when it averages and drifts.

If style continuity between slides starts drifting:
- Don't add a third ref.
- Tighten the STYLE sentence — same wording across slides locks tone better than a ref.
- Re-state the BACKGROUND sentence verbatim across slides — gpt-image-2 latches onto repeated
  framing copy.

---

## Worked example — DeepSeek 介绍 deck (slide 1, cover)

This is a full prompt you can pipe straight into `generate.py -m gpt-image-2`.

```
OVERVIEW
A 16:9 illustrated PPT cover slide introducing the DeepSeek language-model series. The
title is the visual anchor; one chibi character stands beside it as a friendly guide.

STYLE
Soft-watercolor children's-storybook illustration, super-deformed 2.5-head-body chibi
character with large round shiny eyes, small pink blush circles, a tiny mouth, pastel
palette, gentle rounded outlines, hand-painted brush feel.

CHARACTER
On the right side of the slide: a chibi teenage scientist girl with long dark-brown hair
tied in twin tails with small ribbons, big round red-framed glasses, a clean white lab
coat over a school uniform, holding a small wooden pointer stick that gestures upward
toward the title, confident mentor smile, pink blush circles on cheeks, super-deformed
2.5-head-body chibi proportions.

LAYOUT
The slide has one dominant element: a large bold title at the upper third, a hero
illustration filling the middle (a small painted whale silhouette gently leaping out of
soft watercolor waves, a tiny glowing terminal-prompt symbol drifting above its back), and
a single subtitle line at the bottom. The chibi character stands at the right edge framing
the hero illustration. Generous whitespace surrounds everything.

TEXT CONTENT (every Chinese string below must render exactly as written, in a bold
handwritten font similar to LXGW WenKai 霞鹜文楷, dark warm brown for titles, darker gray
for the subtitle):
- Top center title (large, bold): "认识 DeepSeek"
- Subtitle bottom (smaller, gray): "一只来自深海的开源大模型"

DECORATIVE ELEMENTS
Four small hand-painted watercolor motifs, sparingly placed around the hero illustration:
a tiny floating code window with curly braces, a small open book, a soft sparkle cluster
above the whale's back, a thin underline brush stroke beneath the subtitle. Generous
breathing room — no clutter.

BACKGROUND
Warm cream-yellow (#FFF6E4) base with a very subtle gradient toward pale teal at the
bottom edge (hinting at deep water without becoming a real sea). Faint paper-grain
texture. No magical forest, no petal swarm, no star field.
```

Generation:

```bash
cat /tmp/deepseek_intro_s1_prompt.txt | \
  ~/.claude/skills/ppt-anything/tools/generate-image.py \
    -m gpt-image-2 \
    -r 16:9 \
    -n deepseek_intro_s1 \
    --ref ~/.anything-ppt/characters/chengcheng/chengcheng.png \
    --no-preview
```

---

## Worked example — slide 3, three-column "DeepSeek 三大特点"

Shows how to use Layout C with the gpt-image-2 voice. Same style sentence, same character
ref, only LAYOUT / TEXT / DECORATION change.

```
OVERVIEW
A 16:9 illustrated PPT slide listing three signature traits of DeepSeek as a model series.
Three columns share equal weight; one chibi character comments from a corner.

STYLE
Soft-watercolor children's-storybook illustration, super-deformed 2.5-head-body chibi
character with large round shiny eyes, small pink blush circles, a tiny mouth, pastel
palette, gentle rounded outlines, hand-painted brush feel.

CHARACTER
In the bottom-right corner: the same chibi teenage scientist girl with long dark-brown
hair in twin tails, big round red-framed glasses, white lab coat over school uniform —
this slide she sits cross-legged on the floor with one hand on her chin, sparkly-eyed
admiration expression, pink blush circles, super-deformed 2.5-head-body chibi proportions.

LAYOUT
Below the top title, three equal vertical columns sit side by side, separated by thin soft
hand-drawn divider lines. Each column has a small painted icon at the top, a bold headline
below the icon, and one short body line under the headline. The chibi character sits in
the bottom-right corner reacting to the three columns.

TEXT CONTENT (every Chinese string must render exactly as written, in a bold handwritten
font similar to LXGW WenKai 霞鹜文楷; dark warm brown for the title and headlines, darker
gray for body lines):
- Top center title: "DeepSeek 三大特点"
- Column 1 headline: "开源开放"
- Column 1 body: "权重与论文同步公开"
- Column 2 headline: "推理强劲"
- Column 2 body: "数学与代码任务领先"
- Column 3 headline: "成本极低"
- Column 3 body: "训练与推理双低价"

DECORATIVE ELEMENTS
One small painted motif per column, all from the engineering family: column 1 — a small
unlocked padlock with a tiny key beside it; column 2 — a small painted brain shape with a
faint gear inside; column 3 — a small painted coin stack with a downward brush-stroke
arrow. Nothing in the gaps between columns — the columns are the visual structure.

BACKGROUND
Warm cream-yellow (#FFF6E4) base with very subtle gradient and faint paper-grain texture.
No magical forest, no petal swarm.
```

Generation (same single-ref rule):

```bash
cat /tmp/deepseek_intro_s3_prompt.txt | \
  ~/.claude/skills/ppt-anything/tools/generate-image.py \
    -m gpt-image-2 \
    -r 16:9 \
    -n deepseek_intro_s3 \
    --ref ~/.anything-ppt/characters/chengcheng/chengcheng.png \
    --no-preview
```

Note: slide 3 does **not** pass `deepseek_intro_s1.png` as a second ref. Style continuity
comes from the verbatim STYLE + BACKGROUND sentences, not from chained refs.

---

## Self-check before sending each prompt

- [ ] Has the 7 mandatory section headers (OVERVIEW / STYLE / CHARACTER(S) / LAYOUT / TEXT
      CONTENT / DECORATIVE ELEMENTS / BACKGROUND).
- [ ] Total length under ~350 words.
- [ ] STYLE sentence is stated **once**, not repeated.
- [ ] Every character is described by visible features, not by name-summon alone.
- [ ] Every Chinese string is in quotes with a position label.
- [ ] DECORATIVE ELEMENTS count is 3–5 (down to 2 on copy-dense slides).
- [ ] Zero Unicode emoji anywhere in the prompt's text slots.
- [ ] Single `--ref` per character identity; no previous-slide chain.
- [ ] Command line uses `-m gpt-image-2`, no `--size`, only `-r`.

Failing any check = fix before generating; gpt-image-2 bills success and failure equally.
