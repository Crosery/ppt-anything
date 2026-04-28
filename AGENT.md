# AGENT.md — `ppt-anything` 项目操作总入口

> 这份文档面向 AI CLI（Claude Code / Gemini CLI / Codex CLI / Cursor / Cline / 任何 MCP host）。
> 所有 CLI 专属配置文件（`CLAUDE.md` / `GEMINI.md` / `CODEX.md` / `.cursorrules` 等）都应一行指向这里。
> 给人看的项目说明在 [`README.md`](README.md)。

---

## 你在哪 / 这是什么

你正在 `ppt-anything` 项目根目录。这个仓库的目标：把"用 AI 做一套讲故事的插画 PPT"打包成一个跨 CLI 的 skill。

仓库本体不存运行时数据，运行时全部住在用户的全局目录 **`~/.anything-ppt/`**。

---

## 安装（首次进入此项目时检查）

如果用户问"怎么装"或这是新克隆的仓库，按下面顺序：

```bash
bash scripts/install.sh
```

它会：
1. `cp -R skill/` → `~/.claude/skills/ppt-anything/`（已存在则备份到 `.bak.<时间戳>/`）
2. 把 `defaults/characters/`、`defaults/styles/`、`defaults/providers/` 拷到 `~/.anything-ppt/` 下对应位置（**仅在目标不存在时拷贝，绝不覆盖用户已有数据**）
3. 检查 `cwebp` 是否在 PATH（用于 HTML 打包），缺失则提示 `brew install webp` / `apt install webp`
4. 不会替用户写 API key，会提示进 `~/.anything-ppt/providers/` 自己填

非 Claude Code 用户（Gemini CLI、Codex CLI 等）skill 本体的工作流文档仍在 `~/.anything-ppt/skill/` 的副本里（install.sh 也会拷一份），你按里面的 SKILL.md 流程跑即可。

---

## 用户全局库结构（必须熟悉）

```
~/.anything-ppt/
├── characters/                         人物库
│   ├── chengcheng/                     默认人物之一: 橙橙 (搭子 AI OC 双核「冲」)
│   │   ├── chengcheng.md               profile (含 prompt 锚点 / drift risk / pairing)
│   │   └── chengcheng.png              reference image (必须有)
│   ├── lanlan/                         默认人物之二: 蓝蓝 (搭子 AI OC 双核「稳」)
│   │   ├── lanlan.md
│   │   └── lanlan.png
│   └── <slug>/                         其他用户/AI 添加的角色 (单角色或新双核)
├── styles/                             风格模板库
│   ├── anime-chibi-default/            默认风格（当前的萌系日漫水彩）
│   │   ├── style.md                    风格特性 + content-first 原则 + layout 表 + scene-ify
│   │   └── prompt_template.md          带 <<SLOT>> 的 prompt 模板
│   └── <slug>/                         其他风格包
├── providers/                          生图 API 库 (出厂只装 nanobanana, 其他靠扩展)
│   └── nanobanana.toml                 base_url / api_key (默认空) / models[] / how_to_use
└── demo/                               每次成品归档
    └── YYYY-MM-DD-<slug>/
        ├── outline.md                  本次的 outline（用户审过的版本）
        ├── slides/                     生图原文件
        ├── deck.html                   最终 HTML 交付物
        └── meta.toml                   用了哪个 character / style / provider，便于复盘
```

**铁律**：所有库都可读、可写、可扩展。AI 在用户许可后可以新增条目，但**绝不修改用户已有条目**——如果要换风格就建新 style pack，不要去改 `anime-chibi-default`。

---

## 工作流（生成一套 PPT 时）

### 0. 启动前 provider 自检 (强制, 最先做)

进入 skill 第一件事就扫 `~/.anything-ppt/providers/*.toml`，对每个 .toml 检查 `[auth]` 下**三个字段全部要齐**:
- `api_key`
- `base_url`
- `docs_url`

任一为空字符串 `""` / `<...>` 占位符 / 包含 `PLACEHOLDER` → 视为未配置。AI **不替用户猜任何字段**, 包括 base_url 和 docs_url——哪怕官网是众所周知的也要等用户自己填。

**没有任何 provider 字段填齐**: 立即停下来告诉用户，给两条路:

> "当前 `~/.anything-ppt/providers/` 下没有任何 provider 字段填齐 (需要 `api_key` + `base_url` + `docs_url` 三项), 我没法生图。你有两个选项:
>
> **方案 A — 你自己加 (推荐, 安全)**: 打开 `~/.anything-ppt/providers/nanobanana.toml`, 把 `[auth]` 下三个字段都填上你申请到的真实值。改完告诉我, 我重扫。
>
> **方案 B — 我帮你加 (危险操作)**: 你需要给我 4 样东西:
>   1. **api_key** (我会写到本地 .toml, 不上传, 但我**强烈建议你自己用 vim 填**, 不要让我经手 key 字符串)
>   2. **base_url** (网关地址, 你提供, 我不猜)
>   3. **docs_url** (官方 API 文档地址, 我会 WebFetch 读它确认请求 schema)
>   4. **模型清单** (默认模型 + 可选模型 ID)
>
>   我会按 schema 写一份 .toml 到 `~/.anything-ppt/providers/<name>.toml`, 但**不会替你生成 key, 也不会保管 key**。
>
> 你选 A 还是 B?"

**等用户明确选**, 不要自作主张走 B, 也不要因为"这个 provider 我知道官网"就替用户填 base_url / docs_url。

### 1-N. 正式生成

1. **澄清 brief** — 主题、受众、语气、张数偏好。模糊就追问，别猜。
2. **声明默认值** — 一句话告诉用户："这次默认用 `characters/chengcheng + lanlan`(搭子双核) + `styles/anime-chibi-default` + `providers/nanobanana`，要换吗？"。等用户确认或换。

   橙橙 + 蓝蓝是「搭子」AI OC 双核 mascot，几乎所有场景成对出现：橙橙负责冲（行动/抛想法/庆祝），蓝蓝负责稳（分析/把关/复盘）。这是 OC，模型没有训练记忆，**必须每张都传 ref 图 + 显式 feature 一句话**（profile 里的 one-liner 字段）。
3. **解析人物/风格/provider**:
   - 用户指定的角色不在 `~/.anything-ppt/characters/`：先 WebSearch 找官方图，下到 `~/.anything-ppt/characters/<slug>/`，写 profile，**Read 图（视觉输入）确认特征**，再用。
   - 用户指定的风格不在 `~/.anything-ppt/styles/`：让用户描述或给参考图，建新 style pack。
   - 用户指定的 provider 不在 `~/.anything-ppt/providers/`：让用户给 base_url + api_key + 模型清单，建新 toml。
4. **设计 outline**（按 skill 的 `outline_template.md` 思考脚手架，不是填表）。
5. **GATE**: outline 给用户过审。**没过审禁止生图**。
6. **顺序生成**: 严格串行，每张 slide 都把原始角色 ref + 上一张 slide ref 一起传给 provider。绝不并行（API 风控）。
7. **打包**: `tools/build-html-ppt-external.py`（默认 WebP 外链，HTML 壳 ~3KB）。
8. **归档**: 把 outline + slides + html + meta 写到 `~/.anything-ppt/demo/<date>-<slug>/`。
9. **报告**: 给用户 demo 路径 + 总大小 + 一段 story recap。

---

## 核心铁律（不许违反）

| 铁律 | 触发后果 |
|---|---|
| Outline 不过审禁止生图 | 浪费用户钱 |
| 每张 slide 必须传原始角色 ref + 上一张 slide ref | 主角会逐步漂移 |
| 严格串行，禁止并行 / 后台 / subagent fanout 调 generate.py | API 风控直接封号 |
| 所有产出物（PPT/插画/文档/UI/commit message）禁用 emoji | 用户铁律 |
| 内容是主角，人物服务情绪，装饰服务氛围 | 视觉读取顺序倒置就是失败 |
| 每张 slide 必须不同 layout + 不同人物姿势 | 模板化 = 死板 |
| 找不到用户指定的东西时，停下来问，不替换 | 替换 = 在猜 |

---

## 关键文件位置

| 用途 | 路径 |
|---|---|
| Skill 本体（工作流 + style guide + prompt 模板 + tools） | `skill/`（被 install.sh `cp -R` 全量更新到 `~/.claude/skills/ppt-anything/`） |
| 默认库（首次安装来源） | `defaults/` |
| 全局运行时库 | `~/.anything-ppt/` |
| HTML 打包脚本 | `.claude/skills/ppt-anything/tools/build-html-ppt-external.py` |
| 生图依赖（Crosery 私人版本） | `~/.claude/skills/generate-image/generate.py`，参数走 `~/.anything-ppt/providers/*.toml` 配置 |

---

## 扩展库（自动 + 手动）

**用户说"用 Pikachu 当人物"**：
1. 检查 `~/.anything-ppt/characters/pikachu/` 是否存在
2. 不存在 → WebSearch 找官方图 → `curl` 到 `~/.anything-ppt/characters/pikachu/pikachu.png` → Read（视觉确认）→ 写 `pikachu.md` profile
3. 写完后向用户确认："找到了 pikachu，用 2024 redesign 还是经典版？"
4. 这次 deck 用 + 留库下次复用

**用户说"用赛博朋克风格"**：
1. 检查 `~/.anything-ppt/styles/cyberpunk/` 是否存在
2. 不存在 → 让用户给参考图 / 描述关键词 → 仿照 `anime-chibi-default/style.md` 结构写新 style pack
3. 必须包含: content-first 原则、layout 表、prompt 模板、字体偏好

**用户说"用 OpenAI gpt-image-1"**：
1. 检查 `~/.anything-ppt/providers/openai-image.toml` 是否存在 + api_key 是否填
2. 不存在 → 创建 toml 模板，让用户填 key
3. 永远不替用户填 key

---

## 当前关注 / 项目状态

正在从 Crosery 私人 skill 解耦走向通用版。M1 目标：让任何 Claude Code 用户能 git clone 后跑通。M2 目标：独立 CLI（不依赖 Claude Code）。

当前阶段：M1 骨架搭建中。
