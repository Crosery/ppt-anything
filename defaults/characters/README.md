# Character Library — `~/.ppt-anything/characters/`

Each character used by ppt-anything lives here as a **directory** containing one profile `.md` AND one local reference image (jpg/png/webp).

**Iron rule**: text description alone is NOT enough. The model may know an older version, a different redesign, or hallucinate features. Always persist a real image and pass it as `--ref` to `tools/generate-image.py`.

## Layout

```
~/.ppt-anything/characters/
  <slug>/
    <slug>.md           profile (frontmatter + visual features + prompt anchors)
    <slug>.<ext>        the actual reference image — jpg / png / webp
```

`<slug>` is `<firstname>_<lastname>` all lowercase (e.g. `mahiro_oyama`). Single-name characters: `<name>` (e.g. `dimo`, `chengcheng`). Hiragana-to-romaji for Japanese names.

## Default characters (shipped by `install.sh`)

| slug | role |
|---|---|
| `chengcheng` (橙橙) | 「搭子」AI OC double-act, action-driver. Warm peach-orange watercolor droplet mascot. |
| `lanlan` (蓝蓝) | 「搭子」AI OC double-act, stabilizer. Deep dusk-blue watercolor droplet mascot, transparent belly window with 3 droplets. |

These two are paired CP — almost always appear together. Skill auto-suggests them as the default character pair on every new deck.

## Schema (frontmatter)

```markdown
---
name: <English or romaji name>
name_zh: <Chinese name if known>
name_jp: <Japanese name in kanji/kana>
source_work: <Anime / manga / game / OC / ...>
role_archetype: <mentor | protagonist | novice | mascot | ...>
source_urls:
  - <wiki / fandom URL or empty if OC>
reference_image: characters/<slug>/<slug>.<ext>   # REQUIRED, relative to ~/.ppt-anything/
image_provenance: <web | user-provided | project-default>
verified_date: <YYYY-MM-DD>
version_note: |
  (Optional, REQUIRED when multiple canonical versions exist.) Which version this profile covers and which to NOT draw.
---
```

## Adding a new character (3 branches)

### Branch A — already in library
Check `~/.ppt-anything/characters/<slug>/`. If profile + image both exist, `Read` both (vision input mandatory). Done.

### Branch B — public character, not yet here
`WebSearch` the canonical image, `curl` it to `~/.ppt-anything/characters/<slug>/<slug>.<ext>`, **`Read` it with vision**, then write the profile from WHAT YOU SAW (not text summaries). If multiple canonical versions exist (old vs redesign), confirm with the user and record in `version_note`.

### Branch C — user-provided image (OC / obscure)
Ask the user for the image path/URL. Copy into `~/.ppt-anything/characters/<slug>/<slug>.<ext>` (never leave in `/tmp`). `Read` it. Write profile with `image_provenance: user-provided`, leaning on explicit feature description (the model has no latent memory of OCs).

**Skipping the Read step is the #1 source of character drift. Do not skip it even if the name feels famous.**
