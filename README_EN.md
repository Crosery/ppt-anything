<div align="center">

<img src="assets/logo.jpg" alt="ppt-anything" width="320" />

# ppt-anything

### AI story-deck generation for any AI CLI

<p>Give it a topic. Get back a coherent illustrated presentation with recurring characters, visual taste, and a story you can actually present.</p>

<p>
  <a href="README.md"><b>中文</b></a>
  &nbsp;|&nbsp;
  <a href="README_EN.md"><b>English</b></a>
</p>

<p>
  <a href="#quick-start"><b>Quick start</b></a>
  &nbsp;·&nbsp;
  <a href="#library-system"><b>Library system</b></a>
  &nbsp;·&nbsp;
  <a href="#what-it-solves"><b>What it solves</b></a>
  &nbsp;·&nbsp;
  <a href="AGENT.md"><b>Agent entry</b></a>
</p>

<sub>Cross-AI-CLI skill · Claude Code / Gemini CLI / Codex CLI / Cursor · Bring your own image-generation key</sub>

</div>

---

<div align="center">

## Architecture at a glance

<img src="assets/architecture.jpg" alt="ppt-anything architecture" width="100%" />

</div>

---

## What it is

`ppt-anything` is a cross-AI-CLI skill for generating illustrated story decks. It breaks the job into three reusable libraries:
**characters + style packs + image-generation providers**.

It is not a slide-template filler. Every slide is designed around the hierarchy: content first, characters support emotion, decorations support atmosphere.

The default README is intentionally Chinese-first because the current workflow, default characters, and examples are maintained in Chinese. This English page is the GitHub-facing introduction for English readers.

---

## What it solves

| Pain point | How ppt-anything handles it |
|---|---|
| Characters drift across images | Requires reference images and an outline approval gate before image generation |
| Prompt style is hard to reuse | Uses a style-pack library; the default pack is anime chibi watercolor |
| Image provider setup is messy | Uses provider profiles so each API can be configured once and reused |
| Chinese text often fails in images | Defaults to Chinese-aware font and high-resolution prompts |
| One-shot generation wastes money | The outline must be reviewed before any image-generation call runs |

---

## Core features

- **Extensible libraries** — `characters`, `styles`, and `providers` live under `~/.ppt-anything/`.
- **Outline gate** — image generation does not start until the story outline is approved.
- **Reference-image discipline** — every slide uses the original character references plus the previous slide as anchors.
- **Layout × beat method** — slide layout is selected by story beat instead of blindly filling templates.
- **Content-first visuals** — content must read before characters and decorations.
- **Lightweight delivery** — the final deck is an HTML shell with external WebP assets.
- **No emoji in outputs** — generated decks, illustrations, UI labels, docs, and commit messages avoid emoji.

---

## Quick start

### 1. Clone and install

```bash
git clone git@github.com:Crosery/ppt-anything.git ~/work_file/ppt-anything
cd ~/work_file/ppt-anything
bash scripts/install.sh
```

`install.sh` will:

- copy `skill/` to `~/.claude/skills/ppt-anything/`, backing up any existing copy first;
- copy the default library assets from `defaults/` to `~/.ppt-anything/` on first install;
- check for `cwebp` and Python support;
- never write or manage your API key.

### 2. Configure an image-generation provider

The installer creates a provider profile under `~/.ppt-anything/providers/`. The default profile points to the official Google Gemini Image API and leaves the API key for you to fill in.

```bash
vim ~/.ppt-anything/providers/google.toml
```

Security rule: the AI agent should not read provider TOML files, because they contain API keys. Configure keys yourself whenever possible.

If you use a custom bridge or another provider, create a new provider profile instead of overwriting the default one.

### 3. Run it from your AI CLI

Claude Code:

```text
/ppt-anything Make a deck explaining how strong RL goes from zero to a competitive agent
```

Other AI CLIs should start from [`AGENT.md`](AGENT.md), which describes the project workflow shared by Claude Code, Gemini CLI, Codex CLI, Cursor, and similar tools.

---

## Library system

All reusable runtime assets live outside the repository, under `~/.ppt-anything/`:

```text
~/.ppt-anything/
├── characters/    character library
├── styles/        style-pack library
├── providers/     image-generation provider profiles
└── demo/          generated deck archive
```

The defaults are:

- characters: `chengcheng` and `lanlan`, a paired AI mascot duo;
- style: `anime-chibi-default`, an anime chibi watercolor style pack;
- provider: `google`, pointing to the official Gemini Image API profile with the key left empty.

You can add a new character, style, or provider without changing the repository itself. See [`docs/library-management.md`](docs/library-management.md) for the Chinese full guide.

---

## Repository layout

```text
ppt-anything/
├── README.md                    Chinese-first GitHub README
├── README_EN.md                 English GitHub introduction
├── AGENT.md                     shared entry point for AI CLIs
├── CLAUDE.md / GEMINI.md / ...  small stubs pointing to AGENT.md
├── skill/                       skill implementation copied into ~/.claude/skills/ppt-anything/
├── defaults/                    default assets copied into ~/.ppt-anything/ on first install
├── docs/                        advanced Chinese documentation
├── scripts/install.sh
└── assets/                      logo and architecture images
```

---

## Design principles

1. **Content first** — characters, poses, scenes, and decorations serve the slide content.
2. **Outline before generation** — no approved outline, no image-generation spend.
3. **Reference images are required** — text-only character descriptions drift too easily.
4. **Sequential generation by default** — safer for rate limits and character consistency.
5. **Extensible libraries** — users should not be locked into default characters, styles, or providers.

---

## Credits

Created from Crosery's private `ppt-anything` skill and extracted into a reusable open-source AI-CLI workflow.

<div align="center">
<sub>Made with watercolor anime by the Chengcheng + Lanlan mascot duo</sub>
</div>
