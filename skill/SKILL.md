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
| `~/.claude/skills/ppt-anything/tools/generate-image.py` | Image client. Supports `google` (default, official Gemini) / `nanobanana` (third-party Gemini bridge) / `seedream` / `xais`. |
| `~/.ppt-anything/providers/<name>.toml` | API credentials (`[auth].api_key` + `[auth].base_url` + `[auth].docs_url` + `[auth].auth_style`). **Source of truth for keys. The agent never reads this file directly — `generate-image.py` does.** |
| `~/.ppt-anything/characters/<slug>/<slug>.{md,png}` | Character library. Skill reads from here at runtime. |
| `~/.ppt-anything/styles/<style-name>/` | Style packs. Default `anime-chibi-default/` ships with the skill. |
| `~/.ppt-anything/demo/<YYYY-MM-DD>-<slug>/` | Auto-archive of every generated deck (outline + slides + html + meta). |
| `~/.claude/skills/ppt-anything/tools/build-html-ppt-external.py` | Default HTML packager (WebP external refs, ~3KB shell). |
| `~/.claude/skills/ppt-anything/tools/build-html-ppt.py` | Single-file HTML packager (base64, only for WeChat/email use cases). |

### Provider iron rules (read before first run)

1. **Agent does NOT read provider toml files.** The toml stores `api_key`. Reading it = pulling the key into the agent's conversation context (cached, persisted in memory systems, replayed across turns, leaked between agents). To check whether config is ready, call `generate-image.py` and let it fail with a clear status — its error messages tell you which field is missing without exposing the key. **Never `cat` / `Read` any `*.toml` file body.** `ls` of the filenames is fine; contents are not.

2. **Handing api_key / base_url to the agent is a risk operation.** When the user's path is "I'll edit the toml myself", the agent sees zero key bytes — safe. When the user's path is "agent, please write the toml for me", the agent must explicitly warn ("your key will enter my context, the recommended path is option A") and require a second confirmation before touching the key string.

3. **Agents that register a new provider MUST verify connectivity.** Writing the toml is not enough — call `tools/register-provider.py` which uses the cheapest model + smallest prompt to actually round-trip one image, and only marks `verified=true` when that succeeds. A failed verify means the toml goes back to `verified=false` and the user is told what to check.

### First-run wizard (no provider configured yet)

**Trigger (mandatory, BEFORE asking the user any briefing question):** The agent runs `~/.claude/skills/ppt-anything/tools/check-providers.py`. The script reads provider tomls internally and outputs a key-free summary on stdout:

  - Exit `0` + `READY: <names>` → at least one provider is configured. Note the names; surface them in Step 2 as the choices for "which provider".
  - Exit `1` + `NEED-CONFIG: ...` → STOP. Open the conversation below before doing anything else.

The agent does NOT cat / Read any toml. `check-providers.py` does the reading; agent only sees ok/incomplete summaries.

> "I notice ppt-anything has no usable provider configured yet. Two paths:
>
> **Path 1 — Google official (recommended)**
> The shipped `~/.ppt-anything/providers/google.toml` already has `base_url` / `docs_url` / `auth_style` filled with the official values. You only need to:
>   1. Get a Gemini API key from <https://aistudio.google.com/app/apikey>
>   2. Open `google.toml` in your editor and paste it into `[auth].api_key`
>
> **Strongly recommended.** I never touch your key bytes.
>
> **Path 2 — Third-party bridge (risky)**
> If you've subscribed to some third-party Gemini-shape or OpenAI-image-compatible bridge, I can write the toml for you. You'd give me:
>   - `base_url` (gateway URL)
>   - `api_key` (giving this to me means it enters my context — caching / memory / multi-agent transcript leakage are all on the table)
>   - `docs_url` (I'll WebFetch it to confirm request/response shape)
>   - `auth_style` (`google` for X-Goog-Api-Key, `bearer` for OpenAI-style Authorization)
>
> **Reconfirm**: if you go Path 2, I will see your key. If you'd rather I never see it, switch to Path 1 — `cp google.toml my-bridge.toml`, edit it yourself.
>
> Which path? (1 / 2 / something I haven't listed)"

If the user picks Path 2, the agent runs the connectivity self-test via `tools/register-provider.py` (which writes the toml AND verifies it round-trips one image before returning). See § Setup tool below.

`generate-image.py` reads credentials from `~/.ppt-anything/providers/<name>.toml` itself (lookup table: `GOOGLE_API_KEY` → `google.toml`, `NANOBANANA_API_KEY` → `nanobanana.toml`, `ARK_API_KEY` → `seedream.toml`, `XAIS_API_KEY` → `xais.toml`). The agent does not need to involve itself — call the script and let it handle the secret.

### Setup tool — `register-provider.py`

The agent uses this when registering ANY non-default provider. It:

1. Writes `~/.ppt-anything/providers/<name>.toml` from the user-supplied fields.
2. Generates one tiny image via `gemini-2.5-flash-image` (~$0.04, ~10s) to verify base_url + api_key + auth_style actually work end-to-end.
3. Marks `[provider].verified = true` only on success. On failure, the toml is left with `verified = false` and the script exits non-zero so the agent flags the user to check the offending field.

**Invocation pattern (agent-side; key never goes on the command line — pipe via stdin):**

```bash
echo "$USER_KEY" | ~/.claude/skills/ppt-anything/tools/register-provider.py \
  --name my-bridge \
  --base-url https://example.com \
  --auth-style bearer \
  --docs-url https://example.com/docs \
  --key-stdin
```

If the user prefers Path 1 (Google official, fill the key themselves), the agent does NOT run register-provider.py — it tells them to edit `google.toml` directly, then they re-invoke the skill and the agent verifies on first generation.

## When to use

- User asks for a story-telling illustrated slide deck / 故事 PPT / 萌系分享图 / 绘本 slide
- Topic needs multiple slides to walk through (onboarding, tech talk, concept recap, workflow explanation)
- User wants anime-chibi aesthetic combined with Chinese text

## When NOT to use

- Single standalone picture with no slide context → use `generate-image` directly
- Realistic / photographic / non-anime style → wrong skill
- Only a cover image needed → `generate-image` with one prompt is faster

## Workflow

0. **Provider readiness gate (run BEFORE everything else, including library snapshot).** Run `~/.claude/skills/ppt-anything/tools/check-providers.py`. Read the stdout summary:

   - Exit 0 → at least one provider is `READY` or `verified`. Remember the list; you'll surface it as Step 2's provider-choice options. Proceed to Step 1.
   - Exit 1 → no provider usable. **DO NOT proceed to briefing.** Surface the problem to the user and run the first-run wizard (§ First-run wizard above): walk them through Path 1 (self-fill `google.toml`) or Path 2 (`tools/register-provider.py` for a bridge). Resume Step 1 only after the user has finished setup AND a re-run of `check-providers.py` exits 0.

   **Anti-pattern (do NOT do this):** don't proceed to briefing/outline/generation when the gate fails — you'll waste user time + collect a brief that can't be executed because the rail isn't ready. The gate is the FIRST thing in this skill, not an afterthought triggered by a 401 mid-flow.

1. **Library snapshot, briefing second.** Before asking the user any open-ended brief questions (audience / register / slide count / character preference / etc.), do these reads in parallel:

   - `ls ~/.ppt-anything/characters/` — list available character slugs
   - `ls ~/.ppt-anything/styles/` — list available style packs
   - `ls ~/.ppt-anything/providers/` — list provider toml files (filenames only; **do NOT cat them — agent never reads provider toml**)

   For each character slug, `Read` the character's `<slug>.md` profile to know what it looks like (you'll need this to judge fit). For each style, glance at `<style>/manifest.md` if it exists.

   **Then** open the briefing with the user — **lead with what's actually in the library**, not a generic 5-question form. Example shape:

   > "库里现在有：橙橙(暖橙水滴 · 冲劲) + 蓝蓝(深蓝水滴 · 稳健搭子)、anime-chibi-default 风格、google + nanobanana provider。
   >
   > 你想做的是 [回放用户主题]。这俩水滴吉祥物天然配 [topic-fit 评估]。
   >
   > 我需要你定的：[只问 1-2 个 truly missing 的关键点 — 例如基调、张数、是否要新建角色]"

   **Anti-pattern (do NOT do this):** Send a 5-question form (视角 / 切片 / 基调 / 角色 / 张数) without first surfacing what's available. The library constrains feasibility; ignoring it makes briefing rounds blow up.

   **Topic-character fit judgment:** if the user's topic obviously needs a kind of character the library can't serve (e.g. user wants a 写实校园怀旧, library only has abstract OC water droplets), proactively flag that mismatch in the briefing — offer two paths: (a) accept abstract symbolic handling with the existing characters, (b) add a new character now (Branch B/C of step 2). Don't proceed with a topic that can't work and discover it 3 rounds later.

   **Style-library miss judgment (mirror of the character rule above):** if the user's prompt names a style direction the library doesn't have (e.g. user says "科技风" / "复古风" / "商务风" / "赛博朋克" but `styles/` only has `anime-chibi-default`), **the correct response is to BUILD a new style pack — not to relay confusion back as "我对你的话有 N 种理解"**. Library miss IS the signal to build, not a license to ask "which of my interpretations did you mean?". Lead with the build framing:

   > "库里现在只有 [既有 style], 没有 [用户说的 style] — 我去建一个新 pack。在 [用户说的 style] 内部你拍方向: A 硬路线 / B 折中 / C 跟既有 style 混搭 + 该方向 motif。"

   Then once the user picks A/B/C, build the new pack (`manifest.md` + `style_guide.md` + `prompt_template.md` + `outline_template.md` mirroring `anime-chibi-default/`'s structure) and proceed. Building a new style pack is a normal workflow branch, not an exception path. **Anti-pattern**: responding with "我对你说的 X 风格有 2-3 种理解，是哪种？" — that puts the inferential burden back on the user; they already named the style, the missing piece is direction within it.

2. **Clarify what's still missing — including provider choice and generation mode.** After the library snapshot you know what's available, BUT YOU STILL ASK USER A FEW DECISIONS BEFORE TOUCHING `generate-image.py`:

   - **Topic-side**: register (serious/playful) if ambiguous from topic, slide count if user didn't say, any new-character/new-style needs that the snapshot revealed.
   - **Provider choice — MANDATORY when more than one provider toml exists.** Do NOT silently default. If `ls ~/.ppt-anything/providers/` shows multiple `.toml` files (e.g. `google.toml` + `nanobanana.toml` + bridges), explicitly ask: `"providers/ 里有 [list]，这次用哪个？"`. Only auto-select when there's exactly ONE configured provider on disk. (Reason: the user pays per call, may want different model/quality, may have one provider keyed and one not — choosing for them costs them money on the wrong rail.)

   - **Model + 分辨率默认 — 永远 provider 顶配, 不许"安全的中间值".** 用户为某个 provider 付了钱, 默认就要用满它能给的最强配置; "2K 对水彩够用" / "默认中间值更稳" 都是把 AI 偏好包装成默认, 实际是吃用户预算。各 provider 顶配 (查 `generate-image.py --help` 确认):

     | Provider | 默认 model | 默认 `--size` | 备注 |
     |---|---|---|---|
     | `google` / `nanobanana` (Gemini-shape) | `gemini-3-pro-image-preview` | `4K` | `gemini-2.5-flash-image` 只用于注册校验或用户主动说"省钱/草稿" |
     | `seedream` | `doubao-seedream-5-0-260128` (单模型) | `3k` | `2k` 是降配 |
     | `xais` | **必须先跑** `generate-image.py --provider xais --list-models` 看动态 catalog, 取最新最强 | `--size` 对 xais 无效, 跳过 | xais 模型池会变, 不查就用旧默认 = 用户付了升级钱没拿到 |

     告诉用户你的选择 + 留降配出口:

     > "默认 [provider] + [模型] + [分辨率] (provider 范围内最强配置)。想省钱可以降到 [备选模型] 或 [次级分辨率], 你说。"

     **降配只在用户明示"省钱/草稿/不敏感"时才触发**, AI 不许替用户拿这个决定。
   - **Generation mode — MANDATORY ASK, no silent default.** This is a **质量 vs 速度** tradeoff (not just 串/并行的技术选择); both axes must be on the table for the user:
     - **高质量模式 (顺序生成 + AI 中途看图复盘)**: 一张生成完, AI 立刻 `Read` 那张图, 验证角色 IP 没崩 / style 一致 / 中文字串没乱码, 再开下一张。慢, 但每张都过审, 出问题早期就抓到。**适合**: 第一次跑某个 style / 用户对 IP 还原度高敏感 / 重要交付。
     - **快速模式 (批量并发 + AI 不中途看图)**: 多张并发出货, AI 不审中间结果, 直接拿全部回包打包成 deck。**速度起飞但放弃中间复盘**, 如果某张崩了要等到末尾看 deck 才发现, 重生成的成本也是用户出。**适合**: style 和 character 已经在之前的 deck 里走通过 / 用户赶时间 / 草稿迭代版 / 用户明说"先批一版看看效果"。
     - **并发上限**: 默认 3 (跨 provider 都安全的上限)。如果用户对自己 provider 的 RPM 有把握, 可以指定到 5 或 8 — 但**先问** "你 provider 的限频是多少 RPM?"。第三方 bridge **永远 ≤3**, 不接受用户上调。
     - **风控提醒（用户选快速时, 必须复述）**: "批量会撞 provider 风控, 可能限频或临时封号; 失败也扣费, 由你承担。确认要快速模式 + N 并发?" 第一次 429 自动降回顺序模式, 把这点也提前讲明白。
     - **铁律 — 不许默认**: 用户没明说模式 = **必须问**。"我 default 顺序" / "用户没说我猜要稳" / "outline 已经过了模式不重要" 全是违规借口 —— 这是一笔钱 + 一段时间的 tradeoff, 不该 AI 替用户拍。

   **提问示范 — provider + mode 一次问完, 用户只停一次:**

   > "默认 [provider X] + [N 张] + [基调]。还要你拍:
   >  · provider 选 google / nanobanana / [其他]?
   >  · 模式: **高质量 (顺序+我每张看图复盘, 慢但稳)** / **快速 (批量+不看图直接出货, 快但中间出问题要末尾才发现)**? 选快速的话默认 3 并发, 你 provider 限频高可以指定到 5/8。"
3. **Resolve characters — and ALWAYS anchor with a real reference image.** Text description alone is never enough; the model will drift toward its training-data bias (e.g. a 2012 version of a character that's been redesigned in 2024). Every character used in the deck must end this step with BOTH (a) a profile file `~/.ppt-anything/characters/<slug>/<slug>.md` AND (b) a local reference image `~/.ppt-anything/characters/<slug>/<slug>.<ext>` that Claude has Read (vision input) at least once this session.

   Three branches:

   - **Branch A — character already in library**: check `~/.ppt-anything/characters/<slug>/<slug>.md`. If the profile exists AND `~/.ppt-anything/characters/<slug>/<slug>.<ext>` exists on disk, `Read` both. Done.
   - **Branch B — public character, not yet in library**: `WebSearch` + `curl` the canonical image into `~/.ppt-anything/characters/<slug>/<slug>.<ext>` → `Read` it with vision → write the profile file from WHAT YOU SAW, not from text summaries. If multiple canonical versions exist (old vs redesign), confirm with the user which version to use, and record the choice in `version_note`.
   - **Branch C — user-provided image** (character can't be found online / OC / obscure): ask the user for the image path/URL if not given → copy into `~/.ppt-anything/characters/<slug>/<slug>.<ext>` (never leave in `/tmp`) → `Read` it → write the profile with `image_provenance: user-provided`, leaning more on explicit feature description since the model has no latent memory to summon.

   See `~/.ppt-anything/characters/README.md` for the full schema, two-branch workflow details, and the real failure this rule was written to prevent. **Skipping the Read step is the #1 source of character drift. Do not skip it even if the name feels famous.**
4. **Plan the story arc — think, don't fill a form.** Decide slide count based on what the topic needs. For each slide, you are designing a beat in a story — think through it, don't fill a checklist:
   - What is the ONE core message of this slide? What emotion should the viewer feel?
   - Which layout (A–H from `~/.ppt-anything/styles/<active-style>/style_guide.md` § Layout variation) best fits that message — OR does this beat earn a **custom scene** (scrapbook, corkboard, chat window, recipe card, desk workspace...) per § Scene-ify? Scene-ify for memory / emotion / lived-experience; A–H for teaching / reference / taxonomy. **Before committing**: run § Scene-ify's modifier check (POV / tense / register / simultaneity). If a vocabulary row fits 1:1 after the check, trust it — don't drift to look creative. If no row holds your modifiers, invent.
   - How much copy does this beat need? A big emotional moment might be three bold words; a teaching beat may need a paragraph. **Let the content drive density, not a rule.**
   - Which characters serve this beat, in what pose? Pick poses that amplify the emotion, not to fill a slot.
   - Which decorations reinforce the beat without stealing focus? Could be 2, could be 10 — context decides. **Less is often more when the copy is already information-rich; more welcome when the copy is sparse and the story leans visual.**
   - **Hard constraint (not a quantity rule, a variety rule)**: adjacent slides MUST use different layouts AND different character poses. This is about rhythm, not quota.
   - **Anti-rule**: never pad a slide with decorations / characters / copy just because some template said to. If an element doesn't earn its place, drop it.

   Use `~/.ppt-anything/styles/<active-style>/outline_template.md` as a thinking scaffold — articulate your design intent in your own words, not by filling blanks.

5. **Gate: share the outline, wait for approval.** Write out your design intent for every slide (using `~/.ppt-anything/styles/<active-style>/outline_template.md` as a thinking scaffold) and show it to the user. Include enough so the user can tell: is each slide purposeful? Do layouts and poses vary? Does any slide feel over/under-filled? Do NOT call `generate.py` yet. Wait for explicit approval.
6. **Generate slides — execute the mode the user picked in Step 2, not a default.** For each slide: fill every `<<SLOT>>` in `~/.ppt-anything/styles/<active-style>/prompt_template.md`, invoke `generate.py`.

   - **高质量模式 (顺序 + 看图)**: 一张生成完, 立即 `Read` 那张 PNG/WebP, 复盘 — 角色 IP 没崩? Style 一致? 中文字串没乱码? 任一不过, 跟用户讲 + 决定是重生成还是接受, 然后再开下一张。每张都是一个 RED→GREEN cycle, 不许跳过 Read。
   - **快速模式 (批量 + 不看图)**: 用 N 路并发 (Step 2 拍的并发数, 默认 3, 第三方 bridge ≤3) 同时跑全部 slide。**AI 不中途 Read 中间产物**, 直接等所有回包后一次打包。第一次 429/throttle → 立即降回顺序模式, 把剩余未完成 slide 串行跑完, 并通知用户 "撞限频降回顺序"。
   - **不许混淆**: 用户选高质量你私自批量 = 违规; 用户选快速你磨磨蹭蹭一张张看图 = 浪费用户时间也是违规。Mode 是用户的拍板, 不是 AI 的灵活区。

   **`--ref` discipline (load-bearing for character fidelity):**
   - EVERY slide passes the character reference image(s) `~/.ppt-anything/characters/<slug>/<slug>.<ext>` as `--ref`. These are the ground truth; they anchor signature details across the whole deck.
   - From slide 2 onward, ALSO pass the previous slide's PNG as `--ref` for style continuity (watercolor tone, decoration style).
   - Seedream supports multiple `--ref` flags — pass all relevant ones. Typical slide 2+ invocation: `--ref ~/.ppt-anything/characters/chengcheng/chengcheng.png --ref ~/.ppt-anything/characters/lanlan/lanlan.png --ref <previous_slide>.png`.
   - Daisy-chaining ONLY the previous slide (without re-anchoring to the original character image) accumulates drift across 5–6 slides. Always re-anchor every slide.
   - Resolution: 用 Step 2 拍的 provider 顶配 (Gemini-shape pro = `--size 4K`, seedream = `--size 3k`, xais 无 size 概念)。**不许**生图阶段私自降到 2K 理由是"水彩够用 / 省时"——降配只在 Step 2 用户明示触发。Chinese 文本多的 deck 顶配本就是必要项, 不是 nice-to-have。

   **⚠️ Parallelization is gated on user-picked mode.** 高质量模式下永远不并发, 一张接一张; 快速模式下按用户拍的并发数并发 (默认 3, 第三方 bridge ≤3 硬上限)。Xais / Seedream / 第三方 bridge 都做 RPM 风控, 越界扣费且可能临时封号 — 所以**并发数永远不超过用户在 Step 2 明确确认过的值**, 不许 AI 自己加码。
7. **Package & deliver.**

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
- [ ] **T2b**: Every character in the deck has a local reference image on disk (`~/.ppt-anything/characters/<slug>/<slug>.<ext>`) AND Claude has Read it (vision input) at least once this session. No text-only character goes into generation.
- [ ] **T3**: Full outline approved by user before the first `generate.py` call
- [ ] **T4**: EVERY `generate.py` call passes the character reference image(s) as `--ref`; slides 2+ ALSO pass the previous slide as `--ref`. No slide relies on daisy-chained previous slides alone.
- [ ] **T5**: Each slide uses a DIFFERENT layout from the previous slide (no 5× identical ribbon-banner template)
- [ ] **T6**: Each slide uses a DIFFERENT character pose from the previous slide
- [ ] **T7**: 生成模式被**显式问过** — 高质量(顺序+每张看图复盘) vs 快速(批量+不看图直接出货)。没有静默默认。并发上限默认 3, 用户确认 provider RPM 后可放宽到 5-8, 第三方 bridge 永远 ≤3。第一次 429 自动降回顺序。高质量模式下每张生成完 AI 都 `Read` 过该图; 快速模式下不中途 Read。
- [ ] **T11**: provider 选定后, model + 分辨率都用了 provider 范围内的**顶配** — Gemini-shape (google/nanobanana) = `gemini-3-pro-image-preview` + `--size 4K`; seedream = `--size 3k`; xais 跑过 `--list-models` 后取最新最强。没有静默退到 `2K` / `gemini-2.5-flash-image` / xais 旧默认。降配只在用户明示"省钱/草稿/不敏感"时触发。
- [ ] **T8**: Every element on every slide earns its place — no filler character / decoration / sentence added to meet a quota. If asked "why is this here?" you can answer with a story reason, not a rule reason.
- [ ] **T9**: Design intent was articulated per slide and shown to the user BEFORE any generation — covering beat, layout choice, pose choice, copy, decorations (with reasoning)
- [ ] **T10 (content-first sanity check)**: On each finished slide, the viewer's eye lands on the title/copy first, then the character, then the decorations. If a character or decoration is stealing the scene, shrink or reposition — characters serve the content, not the other way around.

Failing any gate = restart from the failing step. Do not patch on top of a broken gate.

## Style rules

See `~/.ppt-anything/styles/<active-style>/style_guide.md`. Default aesthetic: SD chibi 2.5-head-body characters, hand-painted watercolor finish, clean pastel infographic layout, LXGW WenKai Chinese font, content-first hierarchy. Key sub-sections to consult:

- § 3 **Character pose vocabulary** — pick a fresh pose each slide; avoid mid-action poses and abstract props (§ 3 *Pose traps*)
- § 4 **Layout variation** — pick a different layout each slide; match layout to beat shape (§ 4 *Layout × beat fit*); for memory / emotion / lived-experience beats, consider a **custom scene** over A–H (§ 4 *Scene-ify*)
- § 6 **Background** — clean, restrained, no "magical forest" filler
- § 7 **Decoration density** — context decides, not a number; flow/timeline slides = near-zero extras
- § 12 **No emoji, ever** (hard rule) — zero Unicode emoji in any text slot; describe marks as painted motifs
- § 13 **Chinese glyph clarity** (soft hint) — keep lines short, split long phrases across two lines

Deviate only when the user explicitly requests a different style. Drift within a single deck is the #1 failure mode.

## Prompt template

See `~/.ppt-anything/styles/<active-style>/prompt_template.md`. All slots are `<<ALL_CAPS>>`. Never ship to `generate.py` with a slot still in place.

## Character library

See `~/.ppt-anything/characters/README.md` for profile schema, the mandatory reference-image rule, and the two branches (public vs user-provided). Every new character — whether researched online or given to you by the user — must be persisted as **BOTH** a profile `.md` AND a local image file. Text description without a verified image = character drift in production.

## Common mistakes

| Mistake | Why bad | Fix |
|---|---|---|
| Generating images before showing outline | Burns money on wrong direction | Gate T3 is mandatory |
| Forgetting `--ref` from slide 2 onward | Characters drift between slides | Check Gate T4 before each call |
| Auto-running parallel `generate.py` calls without asking the user first | API risk-control throttles or bans + spends user money on the wrong rail | Default sequential; batch only after asking + warning + re-confirm; cap at 3 concurrent; fall back to sequential on first 429 (T7) |
| 没问用户模式 (高质量/快速) 直接开始生成 — 即使是"安全的"顺序也违规 | 把 钱 + 时间 的 tradeoff 从用户手里拿走。用户想快你给慢, 用户想稳你给快批崩了。"顺序很安全所以不用问"是最危险的借口, 因为它把 AI 的偏好包装成默认 | T7 + Step 2 *Generation mode*: 模式问询是 slide 1 之前的硬门, 必须问。"我 default 顺序" / "用户没说我猜稳" / "outline 已经过了" 全部不算。问的时候必须把"高质量=顺序+我看图"和"快速=批量+不看图"都摆上, 让用户拍 |
| 用户说一个 style 方向 (科技风/复古风/商务风/赛博朋克), 库里没有该 pack, AI 回 "我对你的话有 2/3 种理解, 是哪个?" | 把推断成本甩回给用户 — 用户已经说清楚他要那个 style 了。库 miss = 该 BUILD 新 pack 的信号, 不是该让用户解释一遍他刚说过的话。"我有 N 种理解" 框架在装认真, 实际是把决策推给用户 | Step 1 *Style-library miss judgment*: 直接说 "库里没这个 style, 我去建新 pack — 在这个 style 内部你拍方向 A/B/C?" 框架是 "我在建, 给我方向", 不是 "我搞不懂你说啥"。建 pack (manifest+style_guide+prompt_template+outline_template) 是正常分支不是异常 |
| 注册 / 选定 provider 后用 generate-image.py 的硬编码默认 (`--size 2K` / `gemini-2.5-flash-image` / xais 旧 model), 没用 provider 顶配 | 用户为顶配 provider 付了钱却只拿中等画质。"水彩 2K 够用" / "我不知道 max 是多少所以 2K 安全" / "flash 便宜先试试" 都是把 AI 偏好包装成谨慎默认, 实际吃用户预算 | T11 + Step 2 *Model + 分辨率默认*: Gemini-shape → `gemini-3-pro-image-preview` + `--size 4K`; seedream → `--size 3k`; xais → 必须先 `--list-models` 看动态 catalog 再取最新最强。降配只在用户明示触发 |
| Auto-picking a provider when multiple toml exist | User pays for the wrong rail / wrong quality / wrong key | If `ls ~/.ppt-anything/providers/*.toml` shows >1 entry, ASK the user which to use — do not silently default |
| Same layout on every slide | Monotonous deck, reader disengages | Vary layouts per `~/.ppt-anything/styles/<active-style>/style_guide.md` § Layout variation (T5) |
| Same character pose every slide (e.g. "holding notebook") | Dead deck, no motion | Pick fresh pose from vocabulary per slide (T6) |
| Padding a slide with filler (extra characters / decorations / copy) to "look rich" | Dilutes the main message; filler ≠ richness | Every element earns its place or gets dropped (T8) |
| Character in the visual center with content pushed to the side | Character steals focus from the message | Characters serve the story — place content at the visual anchor, characters frame/support |
| Copy-pasting the previous slide's design with different words | Deck feels flat and machine-made | Each slide is a distinct beat — think it through, don't template it |
| Researching a character but skipping the profile write | Defeats the library's purpose | Write first, then generate |
| Writing a character profile from a text description WITHOUT reading an actual image | Model drifts to the training-data default version (e.g. 2012 老版 when you wanted 2024 redesign); by slide 3 the character is unrecognizable | Branch A/C: always download or receive a real image, `Read` it as vision input, then write the profile from what you saw. Gate T2b. |
| Passing only the previous slide as `--ref` for slides 2+ (daisy-chain) | Character features drift a little each hop; by slide 5 the accumulated drift is visible | Every slide passes the ORIGINAL `~/.ppt-anything/characters/<slug>/<slug>.<ext>` as `--ref` in addition to the previous slide. Gate T4. |
| User says "this character can't be found online, here's a picture" and you ignore the picture, reasoning from their verbal description | Their words miss 3/5 visual details that matter for consistent regeneration (eye shape, prop texture, exact hair part) | Branch C: copy the provided image to `~/.ppt-anything/characters/<slug>/<slug>.<ext>`, `Read` it, let the image drive the profile. |
| Passing vague English gloss for Chinese text | Model hallucinates characters | Pass exact Chinese string in quotes, demand accuracy explicitly |
| Asking model to "be creative with font" | Chinese glyphs break | Always specify LXGW WenKai (霞鹜文楷) style |
| Picking Layout D for a mindset-flip beat (e.g. 破除共识 / 用户≠上帝) | Didactic layout neutralizes the punch — message reads like a manual page | Use Layout G (split) or B (hero) — see `~/.ppt-anything/styles/<active-style>/style_guide.md` § 4 *Layout × beat fit* |
| Defaulting to Layout D + bullet list for an emotional / memory / lived-experience beat (e.g. 回忆录 / 情怀 / 复盘 / "这周我们经历了…") | Turns a story moment into a manual recap — the feeling doesn't land; user reads bullets, not the memory | Consider a custom scene (scrapbook, corkboard, chat window, recipe card...) where content lives inside the metaphor and characters act it out — see `~/.ppt-anything/styles/<active-style>/style_guide.md` § 4 *Scene-ify* |
| Grabbing the nearest § Scene-ify vocabulary row without checking the beat's hidden modifiers (POV / tense / register / simultaneity) | Container holds the topic but not the shape — the slide "looks right" but the emotion doesn't land | Run the modifier check first — see `~/.ppt-anything/styles/<active-style>/style_guide.md` § 4 *Before picking — ask the beat's hidden modifiers* |
| Departing from a § Scene-ify vocabulary row that was already 1:1 right, to "avoid looking table-dependent" or "show creativity" | Overcorrection — the easy answer was correct; you picked a worse scene to perform thinking | If the modifier check comes back clean, trust the row — see `~/.ppt-anything/styles/<active-style>/style_guide.md` § 4 *If a row fits 1:1 after the modifier check, trust it* |
| Writing UI-design words (`icon`, `card`, `drop-shadow`, `badge`) into a watercolor deck | Triggers flat-vector Material Design style, clashes with the rest of the deck | Use watercolor vocabulary — see `~/.ppt-anything/styles/<active-style>/prompt_template.md` top-level rule 6 |
| Dynamic mid-action chibi poses ("about to press stamp", "mid-swing") + abstract digital props (`.md file`, `code file`) | Model freezes mid-action as awkward, and abstract props render as generic rectangles | Use terminal-state poses + concrete iconic substitutes (gift box, scroll, target) — see `~/.ppt-anything/styles/<active-style>/style_guide.md` § 3 *Pose traps* |
| Outline shows per-slide design but buries the slide ORDER inside prose | User spots order problems only after generation — reframing finished beats is expensive | Separate a glanceable one-line order sequence in the outline — see `~/.ppt-anything/styles/<active-style>/outline_template.md` *Before showing the user* |
| Passing emoji (🙅 🤝 ❌ ✅ 🎭 ✨ etc.) into pill labels / titles / captions | Emoji render as flat OS glyphs, photobomb the watercolor deck | Zero emoji in text slots. Use color-coded pills + plain text, or describe the motif as "a watercolor brush-stroke tick mark" — see `~/.ppt-anything/styles/<active-style>/style_guide.md` § 12 |
| Delivering a base64-embedded HTML (`build-html-ppt.py`) by default | 3k PNGs base64-encoded inflate ~33%; a 2-slide deck is ~38 MB, a 5-slide deck is ~70+ MB. Takes several seconds to open every time, feels broken, gets closed. User in this project has explicitly flagged this as "太重打开很慢". | Default to `tools/build-html-ppt-external.py` (external WebP refs, q=95, ~3 KB HTML + 2-3 MB per slide). Only use the base64 version when the user explicitly needs a single-file deliverable (WeChat/email attachment, air-gapped share). |
| Keeping 3k PNGs alongside the WebPs in the final deck folder | Doubles folder size for no reason — HTML references .webp, PNGs are dead weight | `build-html-ppt-external.py` deletes source PNGs by default after successful compression. Only pass `--keep-png` if the user asked to keep originals. |
| Running `build-html-ppt-external.py` without `cwebp` installed | Script exits with "cwebp not found" and the user has to install + re-run | Before first use on a fresh machine: `brew install webp` (macOS) / `apt install webp` (debian). Verify with `command -v cwebp`. |
