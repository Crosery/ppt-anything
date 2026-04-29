# AGENT.md — `ppt-anything` 项目操作总入口

> 这份文档面向 AI CLI（Claude Code / Gemini CLI / Codex CLI / Cursor / Cline / 任何 MCP host）。
> 所有 CLI 专属配置文件（`CLAUDE.md` / `GEMINI.md` / `CODEX.md` / `.cursorrules` 等）都应一行指向这里。
> 给人看的项目说明在 [`README.md`](README.md)。

---

## 你在哪 / 这是什么

你正在 `ppt-anything` 项目根目录。这个仓库的目标：把"用 AI 做一套讲故事的插画 PPT"打包成一个跨 CLI 的 skill。

仓库本体不存运行时数据，运行时全部住在用户的全局目录 **`~/.ppt-anything/`**。

---

## 安装（首次进入此项目时检查）

如果用户问"怎么装"或这是新克隆的仓库，按下面顺序：

```bash
bash scripts/install.sh
```

它会：
1. `cp -R skill/` → `~/.claude/skills/ppt-anything/`（已存在则备份到 `.bak.<时间戳>/`）
2. 把 `defaults/characters/`、`defaults/styles/`、`defaults/providers/` 拷到 `~/.ppt-anything/` 下对应位置（**仅在目标不存在时拷贝，绝不覆盖用户已有数据**）
3. 检查 `cwebp` 是否在 PATH（用于 HTML 打包），缺失则提示 `brew install webp` / `apt install webp`
4. 不会替用户写 API key，会提示进 `~/.ppt-anything/providers/` 自己填

非 Claude Code 用户（Gemini CLI、Codex CLI 等）skill 本体的工作流文档仍在 `~/.ppt-anything/skill/` 的副本里（install.sh 也会拷一份），你按里面的 SKILL.md 流程跑即可。

---

## 用户全局库结构（必须熟悉）

```
~/.ppt-anything/
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
├── providers/                          生图 API 库 (出厂只装 google.toml, 其他靠扩展)
│   └── google.toml                     默认指向 Google Gemini Image 官方 API
│                                       base_url / docs_url 已预填官方值; api_key 待用户填
│                                       auth_style = "google" (X-Goog-Api-Key)
│                                       想接桥接? cp 一份成 my-bridge.toml, 改 auth_style="bearer"
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

### 0. Provider 配置 — 首跑向导 (重要, 先读铁律再看流程)

#### 三条铁律

1. **agent 不读 provider toml 文件**。toml 里有 api_key, agent 不该把 key 字符串读进对话上下文 (会被缓存 / 记忆系统持久化 / 多轮复述 / 多 agent transcript 流转)。需要判断"配置是否就绪"时, 直接调 `tools/generate-image.py` 让脚本去读, 由脚本输出 ok/need-config 状态。**绝不 cat / Read 任何 *.toml 文件本体。** ls 文件名是允许的, 内容不行。

2. **把 api_key/base_url 给 agent 是风险操作**。若用户选择"自己填 toml"路径, agent 一字不经手 — 安全。若用户选择"agent 帮填"路径, agent 必须显式警告 + 二次确认才能落笔。

3. **agent 注册新 provider 后必须验通**。写完 toml 不算完, 必须用最便宜模型 + 最小 prompt 跑一发图, 确认 base_url + key + auth_style 三件套实际能通, 才算注册成功。这套流程已经封装进 `tools/register-provider.py`: 它写完 toml 自动跑 `gemini-2.5-flash-image` 出 1 张图 (~$0.04), 验通才标 `[provider].verified=true`, 失败留 `verified=false` + 非零退出。

#### 首跑向导 (没任何 provider 配置好时触发)

agent 不主动扫 toml。当 generate-image.py 第一次调用因 401/缺字段失败时, 或用户明显第一次跑 skill 时, agent 启动这个对话:

> "我注意到 ppt-anything 还没有可用的 provider 配置。你想用哪条路?
>
> **路径 1 — Google 官方 (推荐)**
> 出厂自带的 `~/.ppt-anything/providers/google.toml` 已经把 base_url / docs_url / auth_style 都预填好了, 你只需要:
>   1. 去 https://aistudio.google.com/app/apikey 申请一个 Gemini API key
>   2. 用 vim / 任意编辑器, 自己把 key 粘进 google.toml 的 `[auth].api_key`
>
> **强烈推荐这条路** — 我永远不经手你的 key 字符串。
>
> **路径 2 — 第三方桥接 (有风险)**
> 如果你接入了某个第三方 Gemini-shape 或 OpenAI-image-compatible 桥接服务, 我可以帮你建一份新 toml。你需要给我:
>   - `base_url` (网关地址)
>   - `api_key` (这一项给我意味着 key 会进我的对话上下文 - 风险面: 缓存 / 记忆 / 多 agent 流转)
>   - `docs_url` (我会 WebFetch 读它对齐请求 schema)
>   - `auth_style` ("google" 走 X-Goog-Api-Key / "bearer" 走 Authorization: Bearer)
>
> **再次确认**: 如果你选路径 2, 我会动你的 key 字符串。如果你不放心, 改走路径 1, 自己 cp google.toml 一份, 改 base_url + auth_style + key, 我永远不看 key。
>
> 你选哪条? (路径 1 / 路径 2 / 用别的我没列的方式)"

agent 等用户明确选, 不自作主张, 不因为"这个 provider 我知道官网"就替用户填字段。

如果走路径 2, agent 写完 toml 后**必须**调 register-provider.py(或同等流程)跑一发连通性自检, 确认通了才算注册完成。

### 1-N. 正式生成

1. **库快照先于追问 (强制)** — 在问用户"主题/受众/张数/角色"之前，并行 ls 三个库目录:
   - `~/.ppt-anything/characters/` — 看有哪些角色 slug + Read 每个 slug 的 .md 看长相 / 性格
   - `~/.ppt-anything/styles/` — 看有哪些风格包
   - `~/.ppt-anything/providers/` — 只 ls 文件名 (不 cat！key 不进 agent context)

   然后开口的第一句**必须**亮库存："库里有 [角色列表] + [风格列表] + provider [谁]，你要做的 [回放主题] 跟它们的契合度是 [评估]"。**禁止**直接抛一个 5 问题表单 (视角/切片/基调/角色/张数) — 上下文不报库存的话用户每答一轮你要 round-trip 验证可行性，浪费几轮。

   契合度判断: 用户主题需要库里没有的角色类型 (如想要写实校园 + 库里只有抽象 OC 水滴) → 主动告知错配，给两条路: (a) 接受抽象/符号化处理用现有角色, (b) 现在加新角色 (走 §扩展库流程)。**不许装作能搭后面才发现搭不上**。
2. **声明默认值 + 提缺什么** — 库快照之后, 你已经知道默认值。剩下追问的只剩用户没说清的那 1-2 个 (张数 / 基调如果模糊 / 是否要新角色)。一句话："默认 `橙橙 + 蓝蓝 + anime-chibi-default + providers/google`，你只要补 [缺的字段]"。等用户确认或换。

   橙橙 + 蓝蓝是「搭子」AI OC 双核 mascot，几乎所有场景成对出现：橙橙负责冲（行动/抛想法/庆祝），蓝蓝负责稳（分析/把关/复盘）。这是 OC，模型没有训练记忆，**必须每张都传 ref 图 + 显式 feature 一句话**（profile 里的 one-liner 字段）。
3. **解析人物/风格/provider**:
   - 用户指定的角色不在 `~/.ppt-anything/characters/`：先 WebSearch 找官方图，下到 `~/.ppt-anything/characters/<slug>/`，写 profile，**Read 图（视觉输入）确认特征**，再用。
   - 用户指定的风格不在 `~/.ppt-anything/styles/`：让用户描述或给参考图，建新 style pack。
   - 用户指定的 provider 不在 `~/.ppt-anything/providers/`：让用户给 base_url + api_key + 模型清单，建新 toml。
4. **设计 outline**（按 skill 的 `outline_template.md` 思考脚手架，不是填表）。
5. **GATE**: outline 给用户过审。**没过审禁止生图**。
6. **顺序生成**: 严格串行，每张 slide 都把原始角色 ref + 上一张 slide ref 一起传给 provider。绝不并行（API 风控）。
7. **打包**: `tools/build-html-ppt-external.py`（默认 WebP 外链，HTML 壳 ~3KB）。
8. **归档**: 把 outline + slides + html + meta 写到 `~/.ppt-anything/demo/<date>-<slug>/`。
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
| 全局运行时库 | `~/.ppt-anything/` |
| HTML 打包脚本 | `.claude/skills/ppt-anything/tools/build-html-ppt-external.py` |
| 生图依赖（Crosery 私人版本） | `~/.claude/skills/generate-image/generate.py`，参数走 `~/.ppt-anything/providers/*.toml` 配置 |

---

## 扩展库（自动 + 手动）

**用户说"用 Pikachu 当人物"**：
1. 检查 `~/.ppt-anything/characters/pikachu/` 是否存在
2. 不存在 → WebSearch 找官方图 → `curl` 到 `~/.ppt-anything/characters/pikachu/pikachu.png` → Read（视觉确认）→ 写 `pikachu.md` profile
3. 写完后向用户确认："找到了 pikachu，用 2024 redesign 还是经典版？"
4. 这次 deck 用 + 留库下次复用

**用户说"用赛博朋克风格"**：
1. 检查 `~/.ppt-anything/styles/cyberpunk/` 是否存在
2. 不存在 → 让用户给参考图 / 描述关键词 → 仿照 `anime-chibi-default/style.md` 结构写新 style pack
3. 必须包含: content-first 原则、layout 表、prompt 模板、字体偏好

**用户说"用 OpenAI gpt-image-1"** (或任何第三方桥接):
1. 检查 `~/.ppt-anything/providers/` 目录里有哪些 toml — **只看文件名 ls**, 不 cat 内容 (key 不许进 agent context)。
2. 没有合适 provider → 启动 §0 首跑向导, 走"路径 2"流程, 同时显式警告"key 给 agent 是风险操作"。
3. 永远不替用户填 key — 用户不允许 agent 经手 key 字符串时, 引导用户自己 cp + vim。
4. 用户允许 agent 帮填 → 调 `tools/register-provider.py --name X --base-url Y --auth-style Z --key-stdin`, 工具内部会写 toml + 自动跑 flash 模型生 1 张图验通连通性, 验通才算注册完成。

---

## Git 工作流（项目级 override 全局 CLAUDE.md）

全局 CLAUDE.md 默认要求"合入 main 必须走 MR"。本项目作为个人维护的开源 skill 仓库，规则按改动重量分级：

| 改动类型 | 流程 |
|---|---|
| **小改动**（typo / 文档措辞 / README 渲染修复 / 单文件 < 30 行 diff） | 直接在 main 上 commit + `git push origin main`，不走分支不走 MR |
| **中等改动**（新增功能 / 改库结构 / 多文件协调） | 走 `feat/<slug>` 或 `fix/<slug>` 分支 + MR + 自审 |
| **大改动**（架构重写 / 删默认资产 / 不可逆操作） | 必须 MR + commit message 含 rationale |

### Commit 格式（仍按全局规范）

```
[<type>][提交人] 具体内容：位置 + 更改
```

type 9 类：`feat / fix / refactor / docs / test / chore / release / dev` —— 详见全局 CLAUDE.md。

### Hook 注意

`~/.claude/bin/hook-commit-discipline.py` 是全局保险（任何项目里 main 上动代码都会拦）。本项目允许小改动直接动 main，所以遇到 hook 拦截时按它自己提示的方法临时关：

```bash
chmod -x ~/.claude/bin/hook-commit-discipline.py
# ...小改动 commit + push...
chmod +x ~/.claude/bin/hook-commit-discipline.py
```

中等 / 大改动**不要**关 hook，按 main → 切分支 → MR 流程走。

---

## 当前关注 / 项目状态

正在从 Crosery 私人 skill 解耦走向通用版。M1 目标：让任何 Claude Code 用户能 git clone 后跑通。M2 目标：独立 CLI（不依赖 Claude Code）。

当前阶段：M1 骨架搭建中。
