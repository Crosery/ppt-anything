---
name: ppt-anything
description: Use when creating illustrated PPT / infographic slide decks that tell a continuous story about a topic (tech sharing, onboarding, concept walkthrough, lesson recap, 萌系分享图, 故事 slide). Triggered by "做一套 PPT 讲 xxx", "生成故事图讲 xxx", "用萌系/日漫风做 xxx 分享图", "做一套故事 slide", or direct /ppt-anything invocation.
---

# ppt-anything

Generate a cohesive series of anime-chibi-style illustrated infographic slides that tell a story about a user-provided topic. Default aesthetic: SD chibi Japanese anime characters + clean infographic layout + pinpoint-accurate Chinese text. (Users can override the style explicitly; otherwise this is what they get.)

## Core principle — content is the hero

**The content is the main subject. Characters, poses, scenes, and decorations exist to make the content come alive — not to steal attention from it.**

Read hierarchy per slide: `内容清晰可读 > 人物表达情绪 > 装饰点缀氛围`. If a pose or decoration makes the viewer read slower, it's a bug. Whenever a choice competes — e.g., a bigger character portrait vs. a larger title — the content wins.

Everything downstream (character selection, reference-image discipline, layout rotation, pose vocabulary, decoration density) is a supporting mechanism. When one of those mechanisms pulls focus from the copy or the beat, it's malfunctioning — cut or shrink it.

## Runtime layout (must know)

This skill is **self-contained** — no external sub-skills required.

| Path | Role |
|---|---|
| `~/.claude/skills/ppt-anything/tools/generate-image.py` | Image client. Supports nanobanana / seedream / xais. |
| `~/.anything-ppt/providers/<name>.toml` | API credentials (`[auth].api_key` + `[auth].base_url` + `[auth].docs_url`). **Source of truth for keys.** |
| `~/.anything-ppt/characters/<slug>/<slug>.{md,png}` | Character library. Skill reads from here at runtime. |
| `~/.anything-ppt/styles/<style-name>/` | Style packs. Default `anime-chibi-default/` ships with the skill. |
| `~/.anything-ppt/demo/<YYYY-MM-DD>-<slug>/` | Auto-archive of every generated deck (outline + slides + html + meta). |
| `~/.claude/skills/ppt-anything/tools/build-html-ppt-external.py` | Default HTML packager (WebP external refs, ~3KB shell). |
| `~/.claude/skills/ppt-anything/tools/build-html-ppt.py` | Single-file HTML packager (base64, only for WeChat/email use cases). |

**Provider-zero startup check (mandatory)**: On every invocation, scan `~/.anything-ppt/providers/*.toml`. If no provider has all three of `api_key` / `base_url` / `docs_url` filled, STOP — give the user two paths (self-fill or AI-assisted-fill with an explicit danger warning). Never invent / guess these values.

`generate-image.py` reads credentials from `~/.anything-ppt/providers/<name>.toml` first (lookup table: `NANOBANANA_API_KEY` -> `nanobanana.toml`, `ARK_API_KEY` -> `seedream.toml`, `XAIS_API_KEY` -> `xais.toml`). Falls back to `tools/.env` and process env for legacy users.

## When to use

- User asks for a story-telling illustrated slide deck / 故事 PPT / 萌系分享图 / 绘本 slide
- Topic needs multiple slides to walk through (onboarding, tech talk, concept recap, workflow explanation)
- User wants anime-chibi aesthetic combined with Chinese text

## When NOT to use

- Single standalone picture with no slide context → use `generate-image` directly
- Realistic / photographic / non-anime style → wrong skill
- Only a cover image needed → `generate-image` with one prompt is faster

## Workflow

1. **Clarify the brief.** Topic, target audience, register (serious/playful), character preferences (if any), slide-count preference (if user has one).
2. **Resolve characters — and ALWAYS anchor with a real reference image.** Text description alone is never enough; the model will drift toward its training-data bias (e.g. a 2012 version of a character that's been redesigned in 2024). Every character used in the deck must end this step with BOTH (a) a profile file `~/.anything-ppt/characters/<slug>/<slug>.md` AND (b) a local reference image `~/.anything-ppt/characters/<slug>/<slug>.<ext>` that Claude has Read (vision input) at least once this session.

   Three branches:

   - **Branch A — character already in library**: check `~/.anything-ppt/characters/<slug>/<slug>.md`. If the profile exists AND `~/.anything-ppt/characters/<slug>/<slug>.<ext>` exists on disk, `Read` both. Done.
   - **Branch B — public character, not yet in library**: `WebSearch` + `curl` the canonical image into `~/.anything-ppt/characters/<slug>/<slug>.<ext>` → `Read` it with vision → write the profile file from WHAT YOU SAW, not from text summaries. If multiple canonical versions exist (old vs redesign), confirm with the user which version to use, and record the choice in `version_note`.
   - **Branch C — user-provided image** (character can't be found online / OC / obscure): ask the user for the image path/URL if not given → copy into `~/.anything-ppt/characters/<slug>/<slug>.<ext>` (never leave in `/tmp`) → `Read` it → write the profile with `image_provenance: user-provided`, leaning more on explicit feature description since the model has no latent memory to summon.

   See `~/.anything-ppt/characters/README.md` for the full schema, two-branch workflow details, and the real failure this rule was written to prevent. **Skipping the Read step is the #1 source of character drift. Do not skip it even if the name feels famous.**
3. **Plan the story arc — think, don't fill a form.** Decide slide count based on what the topic needs. For each slide, you are designing a beat in a story — think through it, don't fill a checklist:
   - What is the ONE core message of this slide? What emotion should the viewer feel?
   - Which layout (A–H from `~/.anything-ppt/styles/<active-style>/style_guide.md` § Layout variation) best fits that message — OR does this beat earn a **custom scene** (scrapbook, corkboard, chat window, recipe card, desk workspace...) per § Scene-ify? Scene-ify for memory / emotion / lived-experience; A–H for teaching / reference / taxonomy. **Before committing**: run § Scene-ify's modifier check (POV / tense / register / simultaneity). If a vocabulary row fits 1:1 after the check, trust it — don't drift to look creative. If no row holds your modifiers, invent.
   - How much copy does this beat need? A big emotional moment might be three bold words; a teaching beat may need a paragraph. **Let the content drive density, not a rule.**
   - Which characters serve this beat, in what pose? Pick poses that amplify the emotion, not to fill a slot.
   - Which decorations reinforce the beat without stealing focus? Could be 2, could be 10 — context decides. **Less is often more when the copy is already information-rich; more welcome when the copy is sparse and the story leans visual.**
   - **Hard constraint (not a quantity rule, a variety rule)**: adjacent slides MUST use different layouts AND different character poses. This is about rhythm, not quota.
   - **Anti-rule**: never pad a slide with decorations / characters / copy just because some template said to. If an element doesn't earn its place, drop it.

   Use `~/.anything-ppt/styles/<active-style>/outline_template.md` as a thinking scaffold — articulate your design intent in your own words, not by filling blanks.

4. **Gate: share the outline, wait for approval.** Write out your design intent for every slide (using `~/.anything-ppt/styles/<active-style>/outline_template.md` as a thinking scaffold) and show it to the user. Include enough so the user can tell: is each slide purposeful? Do layouts and poses vary? Does any slide feel over/under-filled? Do NOT call `generate.py` yet. Wait for explicit approval.
5. **Generate slides STRICTLY IN SEQUENCE.** For each slide: fill every `<<SLOT>>` in `~/.anything-ppt/styles/<active-style>/prompt_template.md`, invoke `generate.py`, WAIT for it to return a file path, then start the next.

   **`--ref` discipline (load-bearing for character fidelity):**
   - EVERY slide passes the character reference image(s) `~/.anything-ppt/characters/<slug>/<slug>.<ext>` as `--ref`. These are the ground truth; they anchor signature details across the whole deck.
   - From slide 2 onward, ALSO pass the previous slide's PNG as `--ref` for style continuity (watercolor tone, decoration style).
   - Seedream supports multiple `--ref` flags — pass all relevant ones. Typical slide 2+ invocation: `--ref ~/.anything-ppt/characters/chengcheng/chengcheng.png --ref ~/.anything-ppt/characters/lanlan/lanlan.png --ref <previous_slide>.png`.
   - Daisy-chaining ONLY the previous slide (without re-anchoring to the original character image) accumulates drift across 5–6 slides. Always re-anchor every slide.
   - Resolution: use `--size 3k` when Chinese-text-heavy slides need crisp glyph rendering; default `-r 16:9` (2k) is fine otherwise.

   **⚠️ NEVER parallelize image generation.** The Xais API enforces rate-control; concurrent calls trigger throttling or temporary bans. No background jobs for image calls, no parallel Bash tool uses, no subagent fan-out for generation. One slide at a time. Every time.
6. **Package & deliver.**

   **Default — lightweight external-reference HTML (recommended for almost every deck):**
   Compress each PNG to visually-lossless WebP (q=95; typically ~80-90% smaller than PNG for watercolor illustrations) and wrap them in a ~3 KB HTML that references them via relative paths. Opens instantly; folder is self-contained and droppable into GH Pages or any static host.

   ```
   tools/build-html-ppt-external.py --dir <out> --pattern '<slug>_s*.png' -t '<title>'
   ```

   Defaults: q=95 WebP, source PNGs removed after compression, output at `<dir>/index.html`. Flags:
   - `--lossless` — bit-perfect WebP (~30% smaller than PNG; use only if user explicitly requires no lossy compression)
   - `--keep-png` — preserve the source PNGs (default deletes them to keep the folder minimal)
   - `--quality N` — override q=95 (q=90 for more aggressive, q=98 if you worry about fine text)

   Requires `cwebp` (on macOS: `brew install webp`).

   **Alternative — self-contained single-file HTML (rare):**
   Use only when the user needs the deck as ONE file (WeChat/email attachment, air-gapped share, can't deploy a folder). Base64 inflates file size ~33% on top of PNG — a 5-slide deck becomes ~70 MB HTML that takes several seconds to open every time.

   ```
   tools/build-html-ppt.py --dir <out> --pattern '<slug>_s*.png' -o <out>/<slug>.html -t '<title>'
   ```

   **Open locally:** `open <dir>/index.html` (macOS) / `xdg-open` (linux). Controls: ← → space for nav, `F` for fullscreen, edge-click for prev/next. Don't skip this step — a silent "here's the file path" delivery makes the user do work.

   **Optional — GH Pages prep.** ASK the user: *"Want a GitHub-Pages-ready folder for this deck?"* Only prepare on explicit yes. For the external-reference variant the deck folder IS the deploy folder — just drop a `.nojekyll` file in it. For the base64 variant, create `<slug>-deploy/` with the html copied in as `index.html` + `.nojekyll`. Never push, never `gh repo create`, never touch their GitHub account on their behalf.

   **Report:** HTML path + total deliverable size (print output of the build script already gives this) + one-paragraph story recap.

## Quality gates (self-check every run)

- [ ] **T1**: Reused a character from the library without re-searching (when the character was already on disk)
- [ ] **T2**: New character got a profile written BEFORE generation, not after
- [ ] **T2b**: Every character in the deck has a local reference image on disk (`~/.anything-ppt/characters/<slug>/<slug>.<ext>`) AND Claude has Read it (vision input) at least once this session. No text-only character goes into generation.
- [ ] **T3**: Full outline approved by user before the first `generate.py` call
- [ ] **T4**: EVERY `generate.py` call passes the character reference image(s) as `--ref`; slides 2+ ALSO pass the previous slide as `--ref`. No slide relies on daisy-chained previous slides alone.
- [ ] **T5**: Each slide uses a DIFFERENT layout from the previous slide (no 5× identical ribbon-banner template)
- [ ] **T6**: Each slide uses a DIFFERENT character pose from the previous slide
- [ ] **T7**: Image generation was STRICTLY SEQUENTIAL — zero parallel / background / subagent-fanout calls to `generate.py`
- [ ] **T8**: Every element on every slide earns its place — no filler character / decoration / sentence added to meet a quota. If asked "why is this here?" you can answer with a story reason, not a rule reason.
- [ ] **T9**: Design intent was articulated per slide and shown to the user BEFORE any generation — covering beat, layout choice, pose choice, copy, decorations (with reasoning)
- [ ] **T10 (content-first sanity check)**: On each finished slide, the viewer's eye lands on the title/copy first, then the character, then the decorations. If a character or decoration is stealing the scene, shrink or reposition — characters serve the content, not the other way around.

Failing any gate = restart from the failing step. Do not patch on top of a broken gate.

## Style rules

See `~/.anything-ppt/styles/<active-style>/style_guide.md`. Default aesthetic: SD chibi 2.5-head-body characters, hand-painted watercolor finish, clean pastel infographic layout, LXGW WenKai Chinese font, content-first hierarchy. Key sub-sections to consult:

- § 3 **Character pose vocabulary** — pick a fresh pose each slide; avoid mid-action poses and abstract props (§ 3 *Pose traps*)
- § 4 **Layout variation** — pick a different layout each slide; match layout to beat shape (§ 4 *Layout × beat fit*); for memory / emotion / lived-experience beats, consider a **custom scene** over A–H (§ 4 *Scene-ify*)
- § 6 **Background** — clean, restrained, no "magical forest" filler
- § 7 **Decoration density** — context decides, not a number; flow/timeline slides = near-zero extras
- § 12 **No emoji, ever** (hard rule) — zero Unicode emoji in any text slot; describe marks as painted motifs
- § 13 **Chinese glyph clarity** (soft hint) — keep lines short, split long phrases across two lines

Deviate only when the user explicitly requests a different style. Drift within a single deck is the #1 failure mode.

## Prompt template

See `~/.anything-ppt/styles/<active-style>/prompt_template.md`. All slots are `<<ALL_CAPS>>`. Never ship to `generate.py` with a slot still in place.

## Character library

See `~/.anything-ppt/characters/README.md` for profile schema, the mandatory reference-image rule, and the two branches (public vs user-provided). Every new character — whether researched online or given to you by the user — must be persisted as **BOTH** a profile `.md` AND a local image file. Text description without a verified image = character drift in production.

## Common mistakes

| Mistake | Why bad | Fix |
|---|---|---|
| Generating images before showing outline | Burns money on wrong direction | Gate T3 is mandatory |
| Forgetting `--ref` from slide 2 onward | Characters drift between slides | Check Gate T4 before each call |
| Parallel / background `generate.py` calls | API risk-control throttles or bans | Strictly sequential, wait for each return (T7) |
| Same layout on every slide | Monotonous deck, reader disengages | Vary layouts per `~/.anything-ppt/styles/<active-style>/style_guide.md` § Layout variation (T5) |
| Same character pose every slide (e.g. "holding notebook") | Dead deck, no motion | Pick fresh pose from vocabulary per slide (T6) |
| Padding a slide with filler (extra characters / decorations / copy) to "look rich" | Dilutes the main message; filler ≠ richness | Every element earns its place or gets dropped (T8) |
| Character in the visual center with content pushed to the side | Character steals focus from the message | Characters serve the story — place content at the visual anchor, characters frame/support |
| Copy-pasting the previous slide's design with different words | Deck feels flat and machine-made | Each slide is a distinct beat — think it through, don't template it |
| Researching a character but skipping the profile write | Defeats the library's purpose | Write first, then generate |
| Writing a character profile from a text description WITHOUT reading an actual image | Model drifts to the training-data default version (e.g. 2012 老版 when you wanted 2024 redesign); by slide 3 the character is unrecognizable | Branch A/C: always download or receive a real image, `Read` it as vision input, then write the profile from what you saw. Gate T2b. |
| Passing only the previous slide as `--ref` for slides 2+ (daisy-chain) | Character features drift a little each hop; by slide 5 the accumulated drift is visible | Every slide passes the ORIGINAL `~/.anything-ppt/characters/<slug>/<slug>.<ext>` as `--ref` in addition to the previous slide. Gate T4. |
| User says "this character can't be found online, here's a picture" and you ignore the picture, reasoning from their verbal description | Their words miss 3/5 visual details that matter for consistent regeneration (eye shape, prop texture, exact hair part) | Branch C: copy the provided image to `~/.anything-ppt/characters/<slug>/<slug>.<ext>`, `Read` it, let the image drive the profile. |
| Passing vague English gloss for Chinese text | Model hallucinates characters | Pass exact Chinese string in quotes, demand accuracy explicitly |
| Asking model to "be creative with font" | Chinese glyphs break | Always specify LXGW WenKai (霞鹜文楷) style |
| Picking Layout D for a mindset-flip beat (e.g. 破除共识 / 用户≠上帝) | Didactic layout neutralizes the punch — message reads like a manual page | Use Layout G (split) or B (hero) — see `~/.anything-ppt/styles/<active-style>/style_guide.md` § 4 *Layout × beat fit* |
| Defaulting to Layout D + bullet list for an emotional / memory / lived-experience beat (e.g. 回忆录 / 情怀 / 复盘 / "这周我们经历了…") | Turns a story moment into a manual recap — the feeling doesn't land; user reads bullets, not the memory | Consider a custom scene (scrapbook, corkboard, chat window, recipe card...) where content lives inside the metaphor and characters act it out — see `~/.anything-ppt/styles/<active-style>/style_guide.md` § 4 *Scene-ify* |
| Grabbing the nearest § Scene-ify vocabulary row without checking the beat's hidden modifiers (POV / tense / register / simultaneity) | Container holds the topic but not the shape — the slide "looks right" but the emotion doesn't land | Run the modifier check first — see `~/.anything-ppt/styles/<active-style>/style_guide.md` § 4 *Before picking — ask the beat's hidden modifiers* |
| Departing from a § Scene-ify vocabulary row that was already 1:1 right, to "avoid looking table-dependent" or "show creativity" | Overcorrection — the easy answer was correct; you picked a worse scene to perform thinking | If the modifier check comes back clean, trust the row — see `~/.anything-ppt/styles/<active-style>/style_guide.md` § 4 *If a row fits 1:1 after the modifier check, trust it* |
| Writing UI-design words (`icon`, `card`, `drop-shadow`, `badge`) into a watercolor deck | Triggers flat-vector Material Design style, clashes with the rest of the deck | Use watercolor vocabulary — see `~/.anything-ppt/styles/<active-style>/prompt_template.md` top-level rule 6 |
| Dynamic mid-action chibi poses ("about to press stamp", "mid-swing") + abstract digital props (`.md file`, `code file`) | Model freezes mid-action as awkward, and abstract props render as generic rectangles | Use terminal-state poses + concrete iconic substitutes (gift box, scroll, target) — see `~/.anything-ppt/styles/<active-style>/style_guide.md` § 3 *Pose traps* |
| Outline shows per-slide design but buries the slide ORDER inside prose | User spots order problems only after generation — reframing finished beats is expensive | Separate a glanceable one-line order sequence in the outline — see `~/.anything-ppt/styles/<active-style>/outline_template.md` *Before showing the user* |
| Passing emoji (🙅 🤝 ❌ ✅ 🎭 ✨ etc.) into pill labels / titles / captions | Emoji render as flat OS glyphs, photobomb the watercolor deck | Zero emoji in text slots. Use color-coded pills + plain text, or describe the motif as "a watercolor brush-stroke tick mark" — see `~/.anything-ppt/styles/<active-style>/style_guide.md` § 12 |
| Delivering a base64-embedded HTML (`build-html-ppt.py`) by default | 3k PNGs base64-encoded inflate ~33%; a 2-slide deck is ~38 MB, a 5-slide deck is ~70+ MB. Takes several seconds to open every time, feels broken, gets closed. User in this project has explicitly flagged this as "太重打开很慢". | Default to `tools/build-html-ppt-external.py` (external WebP refs, q=95, ~3 KB HTML + 2-3 MB per slide). Only use the base64 version when the user explicitly needs a single-file deliverable (WeChat/email attachment, air-gapped share). |
| Keeping 3k PNGs alongside the WebPs in the final deck folder | Doubles folder size for no reason — HTML references .webp, PNGs are dead weight | `build-html-ppt-external.py` deletes source PNGs by default after successful compression. Only pass `--keep-png` if the user asked to keep originals. |
| Running `build-html-ppt-external.py` without `cwebp` installed | Script exits with "cwebp not found" and the user has to install + re-run | Before first use on a fresh machine: `brew install webp` (macOS) / `apt install webp` (debian). Verify with `command -v cwebp`. |
