# Prompt template

Fill every `<<SLOT>>`. Never ship to `generate.py` with a slot still present.

## Top-level rules (baked into every prompt)

1. **Content is the hero** — the title and body copy must dominate the visual weight. Characters frame/support, they don't upstage.
2. **Chinese text accuracy** — pass the exact Chinese strings in quotes; always add `"no typos, no broken strokes, no garbled glyphs"` + `LXGW WenKai (霞鹜文楷)` font directive.
3. **Contextual decoration — density is your judgment, not a number.** Every decoration must earn its place (reinforces the beat, anchors emotion, illustrates the point). Copy-dense slide → fewer, sharper decorations. Copy-sparse slide → more welcome. Never scatter filler like "petals, sparkles, stars everywhere" — filler ≠ richness.
4. **Fresh pose per slide** — pull from `style_guide.md` § Character pose vocabulary. Name the exact pose + expression.
5. **Different layout per slide** — pick a layout ID from § 4 below that differs from the previous slide.
6. **Watercolor vocabulary, not UI-design vocabulary.** The deck is hand-painted watercolor chibi. Words like `icon`, `card`, `drop-shadow`, `badge`, `tile`, `vector`, `flat` trigger the model's Material-Design / flat-vector style and clash with everything else in the deck. Always prefer: `hand-painted watercolor miniature scene`, `small still-life vignette`, `a tiny watercolor-painted folder / scroll / gift-box`, `pencil-outlined`, `brush-stroked arrow`. Same for prop nouns: pick a **concrete iconic substitute** (gift box with a `.md` paper tag, a rolled scroll, an archery target, a bound folder) over an **abstract digital object** (`file`, `symbol`, `icon`).
7. **Zero emoji in text slots.** Never pass 🙅 🤝 ❌ ✅ ⚠️ 💡 🎭 ⚖️ 💥 ✨ 🌸 etc. anywhere the model reads as text (titles, pills, labels, captions, body copy). They render as flat OS glyphs and photobomb the watercolor deck. See `style_guide.md` § 12 for the full blocklist and replacement patterns. If you need visual contrast or a check mark, **describe** it as a painted motif ("a small watercolor brush-stroke tick mark on a paper tag") — don't pass the Unicode character. Math operators (`=` `≠` `×` `÷`) and Chinese punctuation (「」『』) are fine.
8. **Keep Chinese lines short (soft hint).** Titles ≤ 12 Chinese chars; body lines ≤ 14 chars. Long strings occasionally get one misshapen stroke in the middle. Prefer to split long phrases across two lines rather than cram into one.

## Core skeleton (every prompt starts with this)

```
Illustrated PPT slide, 16:9 landscape. Content-first infographic design — the title and body copy are the visual anchor; characters and decorations support, not compete.

ART STYLE: super-deformed chibi kawaii anime illustration, 2.5-head-body proportions, soft colored-pencil / watercolor finish, rounded gentle outlines, pastel palette. Characters have large round shiny eyes, small pink blush circles on cheeks, tiny mouths, exaggerated cute expressions.

CHINESE TEXT: every Chinese character must be perfectly accurate and clearly legible, rendered in a bold handwritten Chinese font similar to LXGW WenKai (霞鹜文楷). No typos, no broken strokes, no garbled glyphs.

BACKGROUND: warm cream-yellow (#FFF6E4) with very subtle gradient, optional faint paper-grain texture. NO "magical forest", NO petal swarms, NO cloud or star fields — background frames content, does not decorate.

<<LAYOUT_BLOCK>>

CHARACTERS (SD chibi style, <<CHARACTER_PLACEMENT_HINT>>):
<<CHARACTER_LINES>>

DECORATIVE ELEMENTS (density chosen to match the copy — lighter when copy is dense, richer when copy is sparse; every element must earn its place by serving the beat): <<DECORATION_LIST>>

Overall mood: <<MOOD>>. High quality, crisp hand-drawn feel, every Chinese character sharp and accurate.
```

`<<LAYOUT_BLOCK>>` gets swapped for one of the layout templates below.

---

## Layout A — Dual-banner

**Use when**: comparing/listing two things (pros/cons, two techniques, do/don't).

```
LAYOUT: title top, two ribbon banners left & right, small center figure, caption bottom.

- TOP CENTER large bold dark-brown title: <<TITLE>>

- LEFT RIBBON BANNER (peach-pink #FFB5A7 ribbon with wavy frame):
  Main line: <<LEFT_BANNER_MAIN>>
  Sub-label pill: <<LEFT_BANNER_SUB>>
  Small icon beside ribbon: <<LEFT_ICON>>

- RIGHT RIBBON BANNER (mint-green #B8DFC6 ribbon with wavy frame):
  Main line: <<RIGHT_BANNER_MAIN>>
  Sub-label pill: <<RIGHT_BANNER_SUB>>
  Small icon beside ribbon: <<RIGHT_ICON>>

- CENTER (between banners): <<CENTER_ILLUSTRATION>>

- BOTTOM CENTER small gray caption: <<BOTTOM_CAPTION>>
```

## Layout B — Centered hero

**Use when**: cover, section intro, single big message.

```
LAYOUT: one big title center, one hero illustration large, one-line subtitle bottom. Generous whitespace.

- CENTER TOP large bold dark-brown title (dominant visual element): <<TITLE>>

- BELOW TITLE: a single hero illustration — <<HERO_ILLUSTRATION>>

- BOTTOM CENTER clean subtitle line in gray: <<SUBTITLE>>

No ribbons. No sidebars. Whitespace is part of the design.
```

## Layout C — Three-column

**Use when**: three points, three steps, triad comparison.

```
LAYOUT: title top, three equal vertical columns below, each column has an icon + headline + 1-line body. Thin soft divider lines between columns.

- TOP CENTER title: <<TITLE>>

- COLUMN 1 (left):
  Icon: <<COL1_ICON>>
  Headline (bold, dark brown): <<COL1_HEADLINE>>
  Body (gray, smaller): <<COL1_BODY>>

- COLUMN 2 (center):
  Icon: <<COL2_ICON>>
  Headline: <<COL2_HEADLINE>>
  Body: <<COL2_BODY>>

- COLUMN 3 (right):
  Icon: <<COL3_ICON>>
  Headline: <<COL3_HEADLINE>>
  Body: <<COL3_BODY>>

- BOTTOM: one small character (chibi) commenting from a corner, small supporting pose.
```

## Layout D — Top-copy bottom-scene

**Use when**: dense body copy slide.

```
LAYOUT: title + body copy fills top 60%, characters reacting to the copy fill bottom 40%.

- TOP title (left-aligned, bold): <<TITLE>>

- BODY COPY (3 short paragraphs or bullet points, dark gray): <<BODY_COPY>>

- BOTTOM HALF: characters placed low, <<CHARACTER_REACTION_SCENE>> — their pose/expression reacts to what the copy says.
```

## Layout E — Dialogue bubbles

**Use when**: Q&A, conversation-style teaching.

```
LAYOUT: two characters facing each other with speech bubbles. Title minimal at top. No ribbons.

- TOP title (small, unobtrusive): <<TITLE>>

- LEFT CHARACTER with speech bubble (peach pink): <<LEFT_BUBBLE_TEXT>>
- RIGHT CHARACTER with speech bubble (mint green): <<RIGHT_BUBBLE_TEXT>>

Bubbles should be the main visual — large, clear, readable. Characters are in mid-conversation poses (pointing / explaining / surprised / nodding).
```

## Layout F — Flow / timeline

**Use when**: sequential steps, before→after, timeline.

```
LAYOUT: title top, horizontal arrow flow across the middle with N nodes, each node has a mini-scene + label. Characters appear at start and end points only.

- TOP title: <<TITLE>>

- FLOW (left to right with arrow connectors):
  Node 1: <<NODE_1_SCENE>> — label: <<NODE_1_LABEL>>
  Node 2: <<NODE_2_SCENE>> — label: <<NODE_2_LABEL>>
  Node 3: <<NODE_3_SCENE>> — label: <<NODE_3_LABEL>>
  (more nodes as needed)

- START CHARACTER (far left): <<START_POSE>>
- END CHARACTER (far right): <<END_POSE>>

- BOTTOM small gray caption: <<BOTTOM_CAPTION>>
```

## Layout G — Split-screen

**Use when**: before/after, wrong/right, old/new.

```
LAYOUT: vertical diagonal split dividing the slide into two contrasting halves.

- TOP title crossing the split: <<TITLE>>

- LEFT HALF (cool tint, slight desaturation for the "before/wrong" side):
  Scene: <<LEFT_SCENE>>
  Character state: <<LEFT_CHARACTER_STATE>>
  Label: <<LEFT_LABEL>> — plain Chinese text only, no emoji (e.g. 以前 / 错误 / 过时)
  Optional corner mark: a large hand-painted watercolor brush-stroke red cross, painted as part of the scene — NEVER a Unicode ❌

- RIGHT HALF (warm tint, full saturation for the "after/right" side):
  Scene: <<RIGHT_SCENE>>
  Character state: <<RIGHT_CHARACTER_STATE>>
  Label: <<RIGHT_LABEL>> — plain Chinese text only, no emoji (e.g. 现在 / 正确 / 如今)
  Optional corner mark: a large hand-painted watercolor brush-stroke green tick, painted as part of the scene — NEVER a Unicode ✅

- BOTTOM small gray caption (crossing both halves): <<BOTTOM_CAPTION>>
```

## Layout H — Spotlight + sidebar

**Use when**: one big concept + supporting details.

```
LAYOUT: one large central element (concept/illustration) takes 60% of the slide, sidebar on the right has 2-3 small callouts.

- TOP title: <<TITLE>>

- CENTER SPOTLIGHT (large, 60% of slide): <<SPOTLIGHT_SCENE>>

- RIGHT SIDEBAR (vertical stack of 2–3 callout cards, each with icon + short phrase):
  Callout 1: <<CALLOUT_1>>
  Callout 2: <<CALLOUT_2>>
  Callout 3: <<CALLOUT_3>>

- CHARACTER placement: one chibi character interacting with the spotlight element from a corner of the spotlight.
```

---

## Slot reference (global)

| Slot | What goes in |
|---|---|
| `TITLE` | Main Chinese title, bold, with 「」！ allowed |
| `CHARACTER_LINES` | Per character, one line: position + pose + expression + signature details (pull signature details from `characters/<name>.md`) |
| `CHARACTER_PLACEMENT_HINT` | Overall placement guidance, e.g. "framing the central content from both sides" |
| `DECORATION_LIST` | Contextual items — density judged per slide, NOT a fixed count (see `style_guide.md` § 7). Copy-dense beat → fewer, sharper. Copy-sparse beat → more welcome. Flow/timeline slides → near-zero extras (nodes + arrows already carry the visual load). Pick from ONE dominant motif family (see `style_guide.md` § 7 motif table). |
| `MOOD` | One-line vibe sentence |

Layout-specific slots (`LEFT_BANNER_MAIN`, `HERO_ILLUSTRATION`, `NODE_1_SCENE`, etc.) are defined in each layout block above.

## Character line format (name-summon, not feature-soup)

**Strategy**: the image model already knows the character from its training data. Invoke its memory with the name + source; don't reconstruct the character from a list of features — that fights the model's own knowledge and produces "a random anime girl that vaguely matches", not "that character".

For each character in the slide, grab the **one-liner** from `~/.ppt-anything/characters/<slug>/<slug>.md` and fill in `<POSITION>`, `<POSE>`, `<EXPRESSION>`. The `preserving ...` tail already covers the 2–3 signature details the model flattens during chibi — don't re-describe the rest of the appearance.

Format:

```
- <POSITION>: <PASTE ONE-LINER WITH POSE / EXPRESSION FILLED>
```

Example (Mahiro, right side of the slide, in a jumping pose):

```
- Right side: Mahiro Oyama from ONIMAI (Onii-chan wa Oshimai) anime, drawn in super-deformed 2.5-head-body chibi style — jumping with joy, arms raised high, sparkly-eyed amazed expression, preserving her iconic oversized springy AHOGE and silver-pink gradient hair.
```

Example (Mihari, left side, pointing pose):

```
- Left side: Mihari Oyama from ONIMAI (Onii-chan wa Oshimai) anime, drawn in super-deformed 2.5-head-body chibi style — pointing firmly at the title with a wooden pointer stick, confident mentor smile, preserving her red-framed round glasses, dark-brown twin tails, and white lab coat.
```

**Do NOT** re-add "petite girl with long hair reaching her waist, big round eyes, sailor uniform with red ribbon, notebook in hand, pink blush circles, chibi proportions..." — the name invocation + the "preserving ..." tail already carry that. Over-specifying fights the model.

**When to add a feature** that's NOT in the one-liner's tail: only when the slide's specific scene requires it (e.g. "holding a glowing test tube" — prop belongs to the scene, not the character profile). Do not describe default appearance.

## Example of a fully-filled prompt

See `examples/claude-code-engineering/final-prompt.md` — baseline example (Layout A, dual-banner). For future generations, rotate layouts per the § Layout variation table.

## Invoking generate.py

Default provider: seedream (Doubao). Default output ~2k at `-r 16:9`. Use `--size 3k` when the slide is Chinese-text-heavy and glyph crispness matters.

```bash
# Slide 1 — anchor to character reference image(s) ONLY
cat /tmp/<deck>_s1_prompt.txt | \
  ~/.claude/skills/ppt-anything/tools/generate-image.py \
    -r 16:9 \
    [--size 3k] \
    -n <deck_slug>_s1 \
    --ref ~/.ppt-anything/characters/<slug_a>/<slug_a>.<ext> \
    [--ref ~/.ppt-anything/characters/<slug_b>/<slug_b>.<ext>] \
    --no-preview

# Slide 2+ — anchor to BOTH character refs AND previous slide
cat /tmp/<deck>_sN_prompt.txt | \
  ~/.claude/skills/ppt-anything/tools/generate-image.py \
    -r 16:9 \
    [--size 3k] \
    -n <deck_slug>_sN \
    --ref ~/.ppt-anything/characters/<slug_a>/<slug_a>.<ext> \
    [--ref ~/.ppt-anything/characters/<slug_b>/<slug_b>.<ext>] \
    --ref <absolute path to previous slide PNG> \
    --no-preview
```

**Why re-pass character refs every slide**: daisy-chaining only the previous slide accumulates drift across 5–6 slides. The original character image is the ground-truth anchor; re-pass it every time. Seedream supports multiple `--ref` flags natively.

Long prompts: pipe from a file (`cat prompt.txt | generate.py ...`) to avoid shell quoting issues.

## ⚠️ Sequential execution — no exceptions

Call `generate.py` one slide at a time. Wait for the printed file path. Then move to the next slide. Do not use `run_in_background: true` for image calls. Do not batch multiple `generate.py` calls in one tool-use block. Do not fan out to subagents for parallel image work. Both seedream and Xais backends enforce rate-control; concurrent calls trigger throttling or temporary bans.
