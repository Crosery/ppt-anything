# Style Guide: anime-chibi story slides

Default aesthetic. Override only when the user explicitly requests a different style.

## 1. Content is the hero

**Content > characters > decoration.** The viewer's eye must land on the title and body copy first. Characters express emotion about the content; decorations only reinforce the content's topic.

Warning signs you've violated this:
- A character is in the dead-center of the slide and the title is squeezed to a corner
- Decorations fill >50% of the slide area
- The title is smaller than the character's face

## 2. Character art

- **Proportion**: SD chibi, 2.5 head-body ratio. Not realistic anime, not micro-chibi.
- **Face**: large round shiny eyes with sparkle highlights, small pink blush circles on both cheeks, tiny simple mouth.
- **Linework**: soft colored-pencil / watercolor finish, rounded gentle outlines. NOT sharp line art.
- **Palette**: pastel, warm cream-beige base, soft accents.
- **Signature preservation**: every character keeps their iconic details even when chibified. Emphasize these in prompt (the model flattens them otherwise).

## 3. Character pose vocabulary

**Every slide must use a different pose than the previous slide.** Pick from the vocabulary below — match pose to slide's emotion. Do NOT default to the same "holding notebook / pointing at board" every time.

### Action poses
- Pointing at something (board, screen, object) with one finger
- Holding an open book / tablet / glowing object with both hands
- Thumbs up with a big smile
- Arms raised in celebration / cheering
- Jumping with joy, legs off the ground
- Running / sprinting pose
- Fist pump with determined face
- Clapping hands

### Emotion poses
- Confused head-tilt with a small painted question-mark bubble above the head
- Sparkly-eyed admiration / amazement with a few small hand-painted sparkle dots around the head
- Flustered with both hands near face, sweat drops
- Sleepy yawn or dozing off
- Shocked with mouth-O and bulging eyes
- Proud arms-crossed with smirk
- Shy half-hiding behind an object
- Lightbulb-moment with a small hand-painted lightbulb motif above the head

### Interaction poses (for duos)
- High-five between characters
- One pointing + one taking notes
- Back-to-back pose (disagreement or teamwork)
- One pulling the other by the sleeve
- Whispering into ear with hand cupped
- Argumentative (hands on hips, facing each other)
- Hugging or pat-on-head
- Handshake / pinky promise

**Rule**: write the exact pose in the prompt, e.g. `holding an open glowing book with both hands, sparkly-eyed admiration expression, a few small hand-painted sparkle dots around her head`. Never leave it vague.

### Pose traps (SD chibi watercolor renders these badly)

- **Mid-action poses fail**. "About to press the stamp", "mid-swing", "mid-handoff" — the model freezes the action at an awkward frame (prop held at a weird angle, body torqued wrong). Use the **terminal state** instead: "holding the stamp AFTER pressing, mark already on the paper" or "arms crossed after finishing". Static endpoints read cleanly in chibi; motion blur doesn't exist in this style.
- **Abstract digital props** (`.md file`, `a code file`, `a symbol`) have no iconic silhouette — the model renders a generic rectangle and the viewer can't tell what it is. Use **concrete iconic substitutes**: a glowing gift box with a `.md` paper tag tied to the ribbon, a rolled scroll with a code snippet peeking out, a bound folder stamped with a visible label. The viewer needs to recognize "what is that thing" in ~200ms without reading.

## 4. Layout variation

**Pick a different layout per slide.** Repeating the same layout = monotonous deck. Rotate through the types below based on the slide's content shape.

### Layout types

| ID | Name | When to use | Visual shape |
|---|---|---|---|
| **A** | Dual-banner | Comparing/listing two things (pros/cons, two techniques, do/don't) | Title top / left ribbon + right ribbon + center figure / caption bottom |
| **B** | Centered hero | Cover, section intro, single big message | Big title center / one key illustration large / one line of copy bottom |
| **C** | Three-column | Three points, three steps, triad comparison | Title top / three vertical columns with icon + headline + body |
| **D** | Top-copy bottom-scene | Dense body copy slide | Title + 2-3 paragraphs top / characters reacting to the copy bottom |
| **E** | Dialogue bubbles | Q&A, conversation-style teaching | Two characters with speech bubbles, no ribbons |
| **F** | Flow / timeline | Sequential steps, before→after, timeline | Title top / horizontal arrow flow with mini scenes at each node |
| **G** | Split-screen | Before/After, wrong/right, old/new | Vertical diagonal split, two contrasting scenes on each side |
| **H** | Spotlight + sidebar | One big concept + supporting details | Large central figure/concept / 2-3 small sidebar callouts on one edge |

**Planning tip**: if the deck has N slides, write down the layout ID for each slide BEFORE generating, and verify no two adjacent slides share the same ID.

### Layout × beat fit (traps)

- **Layout D is didactic, not rhetorical.** For impact beats that must OVERTURN a belief (`用户≠上帝`, `❌ vs ✅`, `破除共识`), D makes the message feel like a textbook page — the dense top-copy neutralizes the punch. Use **G (split-screen)** or **B (punchy hero + one line)** for mindset-flip beats. D shines when teaching three related points, not when flipping a mindset.
- **Don't force a "formula" beat into a sidebar/list layout.** If the title reads as `A × B × C = Z` (an equation), the visual must mirror that structure — use **F (flow)** with three scenes in a line + arrows. Layouts C (three columns) and H (spotlight + sidebar) turn equations into "three tips" and break the formula feel.

### Scene-ify — when the beat wants a scene, not a layout

**Layouts A–H are a scaffolding, not a cage.** When a beat is a memory, an emotion, a story moment, or a lived experience, the most faithful "layout" is often a **scene** — a scrapbook page, a corkboard, a chat thread, a handwritten recipe card, a postcard stack, a desk workspace — where the slide's content lives *inside* the metaphor object and the characters *participate* in it.

Three moves that unlock this:

1. **场景化 (scene-ify)**: ask "what real-world place or object would physically hold this content?" A nostalgic recap lives inside a photo album. A lessons-learned beat lives on a corkboard with pinned notes. A playbook lives on a handwritten recipe card. Pick the metaphor; the slide becomes that metaphor.
2. **角色演绎 (characters act it out)**: let characters DO what the slide is saying, not stand beside the title presenting it. "Slumped at a desk with coffee cups" beats "pointing at a bullet about fatigue". Reactions — a finger poking at a card, a small "哇！" comic bubble above a Polaroid — carry the beat.
3. **画面演绎 (picture-first)**: when the copy would read as a bullet list, ask whether each bullet could be a **vignette inside the scene** instead — three Polaroids on a desk, three notes pinned to a board, three speech bubbles in a chat. The reader absorbs the story visually, not by reading down a list.

### Before picking — ask the beat's hidden modifiers

A beat never has just one shape. It carries **hidden modifiers** that narrow which scene can actually hold it. Before pattern-matching to the nearest Scene vocabulary row below, ask:

- **POV (whose perspective?)** — whose eyes are we in? The container should look like something *that observer* would actually inhabit. An adult's memory of a childhood day = a curated photo album; the child's same day, rendered from the child's POV = a crayon-drawn diary page. Same topic, different container.
- **Tense / mode** — memory (past), live moment (present), future-imagining, or simultaneous cross-section (many things at once)? A scrapbook holds the past; a stage curtain holds a reveal *instant*; no sequential scene (chat thread, recipe steps) can hold true simultaneity — you need a tableau / panorama.
- **Register** — tender / bittersweet / sarcastic / defeated / triumphant / ceremonial. Pick a container that already carries that register in real life. A corkboard reads pragmatic; a photo album reads tender; a newspaper front page reads high-stakes.
- **Sequence vs simultaneity** — does the beat want the reader to travel through it in order, or see it all in one glance? Sequential beats map to flow / timeline / comic-strip; simultaneous beats need a tableau.

**Why this order matters**: if you skip this check and pattern-match a beat to the nearest starter match below, you'll pick a container that holds the *topic* but not the *shape*. The slide will look right and feel wrong.

### Scene vocabulary — probable starting matches (not a menu, not a cage)

**Read this as**: probable matches for common beat shapes *after* you've run the modifier check above. Not a menu to pick from blind. Not a cage to escape for show. If a row fits your beat's modifiers cleanly, trust it. If no row holds them, invent.

| Beat shape | Scene metaphor |
|---|---|
| Memory / nostalgia / recap | Scrapbook page, photo album, old postcard stack |
| Lessons learned / principles / retrospective | Corkboard with pinned notes, chalkboard, bulletin board |
| Dialogue / Q&A / "their take vs mine" | Chat window, speech-bubble exchange |
| Playbook / how-to / recipe | Handwritten recipe card, journal spread |
| Reveal / product / feature showcase | Shop window, stage curtain, gallery wall |
| Active work / behind-the-scenes | Desk workspace with tools scattered, maker bench |

### If a row fits 1:1 after the modifier check, trust it

After running the modifier check, the nearest row may be **genuinely the right answer**. If the beat is literally about flipping through photos and the Memory row says "photo album", pick photo album. If the beat is literally a curtain being pulled aside and the Reveal row says "stage curtain", pick stage curtain.

> **The table exists precisely so the right answer is available. Penalizing it for being easy is vanity, not craft.**

Two signals that you're about to overcorrect:

- "I should pick something less obvious to prove I'm thinking."
- "This looks too on-the-nose — let me invent something fancier."

Both are performance, not design. Depart from the nearest row **only** when a modifier actually fails — POV mismatch, tense mismatch, simultaneity the row can't hold, a mechanical constraint like 4 dialogue turns when Layout E only holds 2 bubbles. Not when the match just "feels too easy."

### When to keep A–H instead

- Pure teaching / reference / taxonomy slides (三大玩法, API summary, step-by-step how-to)
- The content IS a list, not a story
- Visual rhythm needs a clean didactic page to balance richer scenes

Scenes earn their weight *by contrast* with simpler slides — aim for **~1 in every 3–4 slides** to lean scene-ified, not every slide. A whole deck of dioramas reads chaotic.

### How to invoke scene-ify in the prompt

- Name the containing object concretely: `"a wooden desk with an open scrapbook spread"` / `"a corkboard covered in pinned paper notes"`
- List what's on it: `"three Polaroid cards arranged in a gentle arc, each taped with pastel washi tape"`
- Let each piece of content live inside one object: each Polaroid's caption IS what would have been a bullet
- Place characters as *participants*, not presenters: `"leaning on one elbow, pointing excitedly at Card 2"` — never `"standing beside the scrapbook gesturing at the title"`
- Optional: one small in-scene comic bubble (`"哇！"`, `"诶！"`, `"？"`, `"嗯…"`) is often all you need to land the emotional beat

### Adjacent-layout rule still applies

A custom scene counts as "a different layout" from any A–H. Don't use two consecutive scrapbook scenes — scene-ify keeps the variety rule by offering MORE vocabulary, not less.

### Anti-rule (both directions)

This is a **lens, not a mandate**, and the lens has two symmetric failure modes:

- **Anchor bias**: pattern-matching the nearest vocabulary row without the modifier check — the container holds the topic but not the shape. "Memory → scrapbook" reflex, "retrospective → corkboard" reflex.
- **Overcorrection**: drifting away from a 1:1 right answer to "look creative" — a worse scene produced to perform thinking. "Stage curtain was too obvious, let me invent something fancier" reflex.

If A–H already serves a beat cleanly, don't force a scene. If a vocabulary row already serves your beat cleanly after the modifier check, don't force an invention. The core principle hasn't changed: **better shows the content**. Scenes and novelty are tools, not trophies.

### Motivating case (real failure — keep for calibration)

- Beat: `15 年的老伙伴，一直都在` (nostalgic recap of a game across eras)
- Initial choice: Layout D — `title + 3 bullet lines` with two characters reacting below
- Result: stiff. The bullet list read like a manual page. The nostalgic *feeling* didn't land — user feedback: 「三段文字的形式过于生硬」
- Fix: custom scrapbook scene — 3 tilted Polaroid cards (each carrying what was previously a bullet), pastel washi tape at the corners, a pencil laid on the desk, the two characters leaning in like friends flipping through an album; one small comic bubble `"哇！"` above the middle card
- Outcome: same information, but now the slide *feels* like a memory instead of a recap

## 5. Chinese text accuracy

- **Font**: bold handwritten style similar to **LXGW WenKai (霞鹜文楷)**. State this in every prompt.
- **Color**: dark brown / charcoal for title, darker gray for body.
- **Accuracy demand**: always add *"every Chinese character must be perfectly accurate, no typos, no broken strokes, no garbled glyphs"* to the prompt.
- **Pass strings in quotes**: never paraphrase — pass the exact Chinese text the slide should show.
- **Punctuation**: prefer 「」『』 over `""`. English nouns like "Claude Code" / "API" stay English.

## 6. Background (restrained)

- Warm cream-yellow or pale pink base with **very subtle** gradient.
- Optional: faint paper-grain texture.
- **Forbidden filler**: "magical forest", petal swarms, star fields, cloud fields, butterflies — anything that competes with content for attention.
- The background **frames** content, doesn't **decorate** it.
- Never pure white (harsh) or saturated solid color (distracting).

## 7. Decoration density — context decides, not a number

**There is no fixed target.** Density is a creative judgment per slide. The rule of thumb:

- Copy-dense slide (teaching beat with bullets / paragraphs) → fewer, more focused decorations. Don't let visuals compete with the text the reader is working through.
- Copy-sparse slide (emotional beat, cover, single hero message) → more decorations welcome, because the visuals ARE the story.
- Cover / hero slides → can lean either way; match the energy of the title.

**Less is more when the copy is already information-rich. More is welcome when the slide leans visual.**

The one-sentence test for any decoration: *"Why is this element on this slide?"*
- **Keep if** — "It illustrates the slide's point / reinforces the ambience / anchors the emotion"
- **Drop if** — "It's cute" / "To fill space" / "The style_guide told me to"

Pick from topic-appropriate motifs:

| Topic family | Appropriate motifs |
|---|---|
| Engineering / dev | `{ }` code window, `>_` terminal, git branch, bug mascot, gear, shield+check, laptop, magnifying glass |
| Learning / education | open book, pencil, lightbulb, star badge, bookmark, quill, question mark bubble |
| Process / workflow | arrow, gears interlocking, checklist, flowchart nodes, clock |
| Storytelling / fantasy | scroll, key, treasure chest, trophy, magic wand, small shield |
| Daily life / emotional | coffee cup, cat, plant pot, heart, speech bubble, sparkles |

**Mix ≤2 motif families per slide.** Pick ONE dominant family (60%+ of the decorations) + at most 1 accent family. This keeps the slide visually coherent while still rich.

### Flow / timeline is a trap for "copy-sparse → add decorations"

Flow/timeline slides (Layout F) look copy-sparse because each node has a few words — but **the flow structure itself (nodes + arrows + connectors) IS the visual richness**. Adding gears, × symbols, halos, sparkles, glow rings on top of already-present nodes compounds into clutter fast. Decoration quota for F ≈ **zero extras** — just the three node scenes + two arrows + two end characters. If the slide still feels empty, make each node scene richer (from a flat icon to a watercolor mini still-life), don't sprinkle motifs into the gaps.

## 8. Color palette defaults

- Background: `#FFF6E4` ~ `#FDEFD6` (warm cream)
- Title text: `#5A3A2A` (dark warm brown)
- Body text: `#7A6A5A`
- Peach ribbon (layout A left): `#FFB5A7`
- Mint ribbon (layout A right): `#B8DFC6`
- Accent sparkle / highlight: `#F4C95D` / `#FFD6E0`

## 9. Ref chaining (mandatory from slide 2)

Pass prior slide's absolute PNG path via `--ref`:

```bash
~/.claude/skills/ppt-anything/tools/generate-image.py \
  -r 16:9 -n mydeck_s2 \
  --ref /absolute/path/to/mydeck_s1.png \
  "<filled prompt for slide 2>"
```

Anchors character faces, hair color, outfits, and banner style across the deck.

## 10. ⚠️ NEVER parallelize image generation

The Xais API enforces rate-control. Concurrent calls trigger throttling or temporary bans.

- **Never** use `run_in_background: true` for image generation
- **Never** batch multiple `generate.py` calls in a single tool-call turn
- **Never** fan out to subagents for image generation
- **Always** one call at a time. Wait for the file path to return. Then start the next.

Planning, outlining, filling prompts, reading character profiles — all fine in parallel. Only the `generate.py` call itself must be sequential.

## 11. Generation defaults

- `-r 16:9` (PPT-standard)
- `-m Nano_Banana_Pro_2K_0` (0.15 元/张, strong Chinese text rendering — do NOT downgrade unless the user explicitly asks for budget mode)
- `-n <deck_slug>_s<N>` (e.g. `-n claudecode_story_s1`)

## 12. No emoji, ever (hard rule)

**PPT slides must contain ZERO Unicode emoji** in titles, labels, pills, captions, body copy, or anywhere else the model reads as text. Emoji render as flat OS-native glyphs (Apple Color Emoji / Noto / Twemoji) — they look visually foreign pasted into a hand-painted watercolor deck, and instantly break the aesthetic.

### Blocked (never pass these to the prompt's text slots)

- **People / gesture**: 🙅 🤝 👍 🙏 💪 🧑‍💻
- **Symbols / marks**: ❌ ✅ ✔ ✖ ⚠️ 💡 ⭐
- **Face / feature icons**: 🎭 ⚖️ 💥 🔍 ⚙️
- **Decorative**: ✨ 🌸 💫 ⭐ 🔥

### Replacements

| Emoji use case | Replace with |
|---|---|
| `❌ 错` / `✅ 对` pill prefix | color-coded pill + plain text — cool gray/red pill says `用户 = 上帝`, warm green pill says `工程搭档` |
| `🎭` / `⚖️` / `💥` sidebar callout icon | describe the icon as a **hand-painted watercolor motif** in the prompt: "a small painted watercolor theater mask", "a painted brass scale with two pans", "a brush-stroked lightning bolt" |
| `✨` / `💫` accent sparkles | "a few soft hand-drawn sparkle dots", "small watercolor star motifs" — the model will paint them, not type them |
| `✓` / `✗` check mark / cross on a sign held by a character | "holding a small painted sign with a watercolor brush-stroke tick mark on it" (never the Unicode `✓`) |

**Exception**: Chinese punctuation 「」『』 is welcome. Mathematical operators in titles (`=` `≠` `×` `÷`) are fine — they're typographic, not emoji.

**Why this matters**: emoji leak into `generate.py`'s text rendering path verbatim. The model paints around them but can't replace them — you end up with a watercolor slide with an iOS emoji photobombing the label.

## 13. Chinese glyph clarity (soft hint)

The model occasionally outputs one or two slightly misshapen strokes in a long Chinese string. It's rare, doesn't justify a hard rule, but two habits reduce it:

- **Keep lines short** — titles ≤ 12 Chinese chars, body lines ≤ 14 chars. Long strings raise the chance of a blurred character somewhere in the middle.
- **Split long phrases across two lines** instead of cramming into one — line breaks give each half its own render budget.

The existing prompt directive `every Chinese character must be perfectly accurate and clearly legible ... no broken strokes, no garbled glyphs` stays — this is additive.
