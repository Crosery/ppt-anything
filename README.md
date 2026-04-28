<p align="center">
  <img src="assets/logo.webp" alt="ppt-anything" width="320">
</p>

# ppt-anything

> 任何人都能用的 AI 故事 PPT 生成器。
> 给一个主题，吐回一套连贯、有人物、有审美、能直接讲的插画 PPT。

---

## 架构一览

<p align="center">
  <img src="assets/architecture.webp" alt="ppt-anything architecture" width="100%">
</p>

---

## 一句话

`ppt-anything` 是一个跨 AI CLI 的 skill，把"做一套讲故事的 PPT"这件事拆成了：
**人物库 + 风格模板库 + 生图 Provider 库**，三个库都可以挑、可以扩，AI 也能自动去网上找资料更新。
默认配置开箱即用，进阶用户可以替换任意一层。

不是模板填空。每张 slide 都按"内容是主角，人物服务情绪，装饰服务氛围"的层级被设计过。

---

## 解决的痛点

| 你以前的痛点 | ppt-anything 怎么解 |
|---|---|
| 用 LLM 一次生成一组图，人物每张都漂 | 强制 reference image + outline gate，5 张 deck 主角能稳得住 |
| 风格随便挑一个，不知道怎么写 prompt | 风格模板库，默认一套萌系日漫水彩，可换可加 |
| 不知道用哪个生图 API | Provider 库统一抽象，AI 自动选最合适的 |
| 中文字一模糊就废 | 默认走 LXGW 文楷 + 高分辨率 + 中文词级精确 prompt |
| 一键生成最后是文字墙 PPT | outline 必须经你过目，没拍板不烧钱 |

---

## 核心特性

- **三库可扩展**: characters / styles / providers，全部住在 `~/.anything-ppt/`
- **Outline gate**: 任何生图前必须先把故事大纲拿给你过，杜绝烧钱试错
- **Reference image 纪律**: 每张 slide 都用原始角色图 + 上一张 slide 双重 anchor，主角不漂
- **Layout × Beat 方法论**: A-H 布局 + scene-ify 自定义场景，按情绪选版式不靠模板
- **Content-first**: 视觉读取顺序强制 内容 > 人物 > 装饰，杜绝喧宾夺主
- **轻量交付**: 默认 WebP 外链 HTML（~3KB 壳 + 几 MB 图），秒开
- **零 emoji**: 所有产出物（PPT/插画/文档/UI label/commit message）禁用 emoji

---

## 快速开始

### 1. 克隆 + 安装

```bash
git clone <repo-url> ~/work_file/ppt-anything
cd ~/work_file/ppt-anything
bash scripts/install.sh
```

`install.sh` 做的事：
- 把 `.claude/skills/ppt-anything/` 软链到 `~/.claude/skills/ppt-anything/`（Claude Code 用户）
- 把 `defaults/` 拷到 `~/.anything-ppt/`（首次安装，已存在则跳过）
- 检查 `cwebp` 是否安装（HTML 打包需要）

### 2. 配一个生图 provider

`install.sh` 会自动把 `nanobanana.toml.example` 平铺成 `nanobanana.toml`，但 `api_key` 留空。
你需要去填:

```bash
vim ~/.anything-ppt/providers/nanobanana.toml
# 把 api_key = "" 改成你从 https://nn.147ai.com 申请的真实 key
```

**想加别的渠道** (gpt-image-2 / Replicate / 自建网关 / 任何 OpenAI-compatible 端点):
- 自己加: 拷 `docs/provider-examples/gpt-image-2.toml.example` 到 `~/.anything-ppt/providers/`，按 schema 填
- 让 AI 加: 在 AI CLI 里说"帮我加 <provider 名>"，准备好 api_key + base_url + 文档链接 + 模型清单

AI 启动 skill 时会扫 `~/.anything-ppt/providers/`，对没填 key 的 provider 给警告并问你怎么处理。
**AI 永远不替你生成或保管 api_key**——这是铁律。

### 3. 在你的 AI CLI 里调用

**Claude Code**:

```
/ppt-anything 做一套 PPT 讲 strong-rl 怎么从 0 到峡谷段位
```

**其他 CLI**: 见 [`AGENT.md`](AGENT.md)，里面写了 Claude / Gemini CLI / Codex CLI / Cursor 怎么各自接入这个项目。

---

## 库系统

所有可扩展的资产都住在 **`~/.anything-ppt/`**（不在项目仓库里），方便跨 CLI、跨项目复用：

```
~/.anything-ppt/
├── characters/    人物库  (默认: 橙橙 chengcheng + 蓝蓝 lanlan, 「搭子」AI OC 双核 mascot)
├── styles/        风格模板库  (默认: anime-chibi-default 萌系日漫水彩)
├── providers/     生图 API 库  (默认只装 nanobanana 模板, api_key 留空待填; 其他渠道靠扩展)
└── demo/          每次生成的成品归档 (按日期 + 主题命名)
```

**默认值**: 启动 skill 时会告诉你"这次默认用 [橙橙 + 蓝蓝 搭子双核] 角色 + [萌系日漫] 风格 + [nanobanana] provider，要换吗？"。
**自动扩展**: 你说"用某某动漫角色"或"用某某风格"，AI 没有的话会去网上搜，下载、写 profile、塞进库，下次直接用。

详见 [`docs/library-management.md`](docs/library-management.md)。

---

## 项目结构

```
ppt-anything/
├── README.md                    给人看
├── AGENT.md                     给 AI CLI 看的总入口
├── CLAUDE.md / GEMINI.md / ...  桩文件，指向 AGENT.md
├── skill/                       skill 本体 (SKILL.md / style_guide / prompt_template / tools/...)
│                                被 install.sh cp -R 到 ~/.claude/skills/ppt-anything/
├── defaults/                    首次安装时拷到 ~/.anything-ppt/ 的默认库
│   ├── characters/chengcheng/   橙橙 (搭子双核之「冲」)
│   ├── characters/lanlan/       蓝蓝 (搭子双核之「稳」)
│   ├── styles/anime-chibi-default/
│   └── providers/nanobanana.toml.example   出厂只装它一个, 其他渠道在 docs/provider-examples/ 留 schema
├── docs/                        进阶文档
├── scripts/install.sh
└── assets/                      项目本身的 logo / 架构图
```

---

## 设计原则

1. **内容是主角** — 人物、姿势、场景、装饰都为内容服务，让位给标题和正文
2. **Outline 先于生图** — 大纲不过审，一张图都不画
3. **Reference image 是铁律** — 文字描述模型会自由发挥，必须给图
4. **顺序生成** — 串行，不并行，避免 API 风控
5. **库可扩展** — 用户不该被默认值绑死

---

## 致谢与出处

源自 [`~/.claude/skills/ppt-anything`](https://github.com/Crosery)（@Crosery 私人 skill），
解耦 + 抽象 + 库化后开放给所有人。
