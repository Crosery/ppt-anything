# Outline: a thinking scaffold, not a form

**This is not a form to fill.** It's a thinking aid — you use it to articulate your design intent slide by slide so the user (and you) can tell the deck is deliberate before burning generation money.

The user wants a deck that tells a **story** — varied rhythm, purposeful characters, beats that breathe. The outline's job is to make sure you've actually thought about each slide, not just queued up copies of a template.

## What to show the user

A free-form document (in Chinese or English, whichever is more natural) that communicates:

1. **Story shape of the deck** — how many slides, why that count, the emotional arc from opening to close
2. **Per-slide beats** — for each slide, in your own words:
   - What this slide is **doing** in the story (a beat, not a bullet)
   - The **copy** it carries — title + body in their final Chinese form, with density that matches the beat
   - The **layout or custom scene** you chose (A–H from `style_guide.md`, or a scene metaphor per § Scene-ify — scrapbook / corkboard / chat window / recipe card...) and **why** it fits this beat's shape
   - The **characters and poses** you're casting, and what emotion they're serving
   - The **decorations** — which ones earn their place here, and what they reinforce

No fixed fields, no required minima. A copy-sparse opening slide might only need three lines to explain. A dense teaching slide might need a full paragraph of design reasoning. Let the slide's own needs drive how much you write about it.

## The hard constraints to honor (these are about craft, not quantity)

When planning, make sure:

- Adjacent slides use **different layouts** — rhythm > repetition
- Adjacent slides use **different poses** for any shared character — movement > staring
- Every element on every slide can answer "why is this here?" with a **story reason**, not a rule reason
- No slide is a copy-paste of the previous slide with different words
- Characters and decorations **serve** the copy — they never compete with it or dilute it. The main message must land first.

## Before showing the user

Re-read the outline end to end. Ask yourself honestly: *if I were the user, would I be excited by this deck, or bored?* If bored: revise. If you can't tell: ask the user directly before generating.

**The slide ORDER is a separate decision the user owns.** After the per-slide design, include a one-line glanceable sequence (e.g. `cover → 项目准备 → 提示词公式 → superpowers → ...`). If the user has to extract the order from per-slide prose, they'll spot order problems only *after* generation — and reordering a finished deck is cheap (rename files) but reframing beats to fit a new order is not.

## After approval

Proceed to slide generation per the workflow in `SKILL.md` — strictly sequential, `--ref` from slide 2 onward.
