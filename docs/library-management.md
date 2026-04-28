# 库管理指南

`ppt-anything` 的所有可扩展资产都住在 `~/.anything-ppt/`，分三个库 + 一个归档目录:

```
~/.anything-ppt/
├── characters/    人物库
├── styles/        风格模板库
├── providers/     生图 API 库
└── demo/          每次生成的成品归档
```

每个库都遵循同一原则: **默认条目不要改，新增就建新目录/新文件**。

---

## 1. characters/ — 人物库

### 默认条目

| 名字 | slug | 是什么 |
|---|---|---|
| 橙橙 | `chengcheng` | 「搭子」AI OC 双核之「冲」: 暖橙水滴形 mascot，行动派，抛想法/出发/庆祝 |
| 蓝蓝 | `lanlan` | 「搭子」AI OC 双核之「稳」: 深暮蓝水滴形 mascot，腹部透明水仓 + 3 颗小蓝水滴是 KO 辨识点；负责分析/把关/复盘 |

两者几乎所有场景成对出现，组成「搭子」CP。
**关键**: 模型对这两个 OC 零训练记忆，每次生图必须 `--ref` 传图 + 在 prompt 里显式贴 profile 里的 one-liner 段落（含水滴形 / 颜色 / 关键特征 / 否定项）。

### 文件结构

```
characters/<slug>/
├── <slug>.md         profile (frontmatter + 视觉特征 + 性格 + prompt 锚点)
└── <slug>.<ext>      reference image (.png / .jpg / .webp)
```

**铁律**: profile 和 image 必须配对存在。AI 在生图前会强制 Read 这张 image (vision input)，没有就拒绝。

### 怎么扩展

#### A. 用户主动加

```bash
mkdir ~/.anything-ppt/characters/<slug>
# 把参考图放进去
cp ~/Downloads/my_char.png ~/.anything-ppt/characters/<slug>/<slug>.png
# 写 profile (照 chengcheng/chengcheng.md 模板)
vim ~/.anything-ppt/characters/<slug>/<slug>.md
```

#### B. AI 自动加 (用户口头要求时)

用户说"用 Pikachu 当人物"，AI 工作流:

1. 检查 `~/.anything-ppt/characters/pikachu/` 是否存在 → 不存在
2. 用 WebSearch 找 Pikachu 官方图 (确认是哪个 era 的版本)
3. `curl` 下载到 `~/.anything-ppt/characters/pikachu/pikachu.png`
4. **Read 这张图** (视觉确认特征)
5. 按 `chengcheng/chengcheng.md` 模板写 `pikachu/pikachu.md`，重点描述视觉特征 (不靠模型记忆) + 显式 prompt 锚点 + drift risk 否定项
6. 向用户确认: "找到了 Pikachu，用 2024 redesign 还是经典版？" 等回答
7. 这次 deck 用 + 留库下次复用

### 修改 / 删除

- 改默认 `chengcheng` / `lanlan`: 直接编辑 `~/.anything-ppt/characters/<slug>/` 下的文件 (项目自带的副本仍在 `defaults/`，下次重装可恢复)
- 删: `rm -rf ~/.anything-ppt/characters/<slug>/`，下次 install.sh 不会自动恢复非默认条目 (默认的橙橙/蓝蓝若被删，重跑 install.sh 会按"目标不存在则拷贝"恢复)

---

## 2. styles/ — 风格模板库

### 默认条目

| 名字 | slug | 是什么 |
|---|---|---|
| 萌系日漫水彩 (默认) | `anime-chibi-default` | 当前 skill 的默认风格，SD chibi + 水彩 + LXGW 文楷中文 |

### 文件结构

```
styles/<slug>/
├── manifest.md         元信息 + 一句话定位 + 入口
├── style_guide.md      完整风格规范 (content-first / layout / scene-ify / pose / decoration / 字体)
└── prompt_template.md  带 <<SLOT>> 的 prompt 模板
```

> 默认风格 `anime-chibi-default` 的 `style_guide.md` 和 `prompt_template.md` 实际由 skill 维护 (`~/.claude/skills/ppt-anything/`)，manifest 指向 skill 内文件。
> 用户新增 style pack 必须把这两份文件实装在 style 目录下，不依赖 skill。

### 怎么扩展

#### A. 用户主动加新风格

```bash
mkdir ~/.anything-ppt/styles/<新风格名>
cd ~/.anything-ppt/styles/<新风格名>
# 写三份文件
vim manifest.md          # 抄 anime-chibi-default/manifest.md 模板
vim style_guide.md       # 风格规范
vim prompt_template.md   # 带 <<SLOT>> 的 prompt 模板
```

#### B. AI 自动加 (用户给关键词或参考图)

用户说"我想要一个赛博朋克风格"，AI 工作流:

1. 检查 `~/.anything-ppt/styles/cyberpunk/` 是否存在 → 不存在
2. 问用户: "给我 1-3 张参考图 (路径或 URL)，或描述关键词"
3. 收到参考图 → Read (视觉确认风格特征)
4. 按 `anime-chibi-default` 结构生成新 style pack:
   - `manifest.md`: 元信息 + 一句话
   - `style_guide.md`: 写视觉特征 / 配色 / 字体 / layout 偏好 / 装饰风格
   - `prompt_template.md`: 在 anime-chibi-default 模板基础上替换风格关键词
5. 向用户确认整体方向 → 生 1 张测试 slide → 用户拍板
6. 留库下次复用

### 强烈建议保留的内容

不管什么风格，新 style pack 都应保留这些铁律 (现有 style_guide.md 里的核心方法论):

- Content-first hierarchy (内容 > 人物 > 装饰)
- Layout × beat fit (按情绪选版式，不照模板填)
- 同一 deck 内每张 slide 不同 layout + 不同人物姿势
- 零 emoji
- 顺序生成

---

## 3. providers/ — 生图 API 库

### 默认条目

| name | 区域 | 状态 |
|---|---|---|
| `nanobanana` | 国内 | 出厂默认且**唯一自动安装**的 provider，api_key 留空待用户填 |

`docs/provider-examples/` 下还有一份 `gpt-image-2.toml.example` 作为 schema 参考 (海外通路 / OpenAI-compatible 自建网关)。**它不会被 install.sh 自动安装**，需要用户手动拷或让 AI 帮加。

其他渠道 (Seedream / Xais / Replicate / Fal / 任何自建网关) 全部按"自定义渠道"流程走，不预置模板。

### 文件结构

每个 provider 一个 `<name>.toml`，包含:

```toml
[provider]      # 元信息
[auth]          # api_key + base_url
[models]        # 默认模型 + 可选模型清单
[defaults]      # 默认 size / aspect_ratio / quality
[capabilities]  # 是否支持 i2i / 多 ref / ref 上限 / 失败是否扣费
[how_to_use]    # AI 怎么调用 (invoke 模板 + notes 提醒)
```

### 怎么扩展

#### A. 用户主动加新 provider

```bash
cd ~/.anything-ppt/providers/
# 抄一份现有 toml 当模板
cp nanobanana.toml.example my-new-provider.toml
vim my-new-provider.toml
```

填好后还需要改 `~/.claude/skills/generate-image/generate.py` 让它识别新 provider，或者在 M2 之后用 generic-http 适配层无需改代码就能接入。M1 阶段需要手动改 generate.py。

#### B. AI 自动加 (用户给材料)

用户说"我想加 Replicate flux / gpt-image-2 / 自建网关 ..."，AI 工作流 (危险操作, 必须先警告):

1. **警告用户这是危险操作**, 解释清楚下面要用户给 4 样东西
2. 问用户要:
   - **api_key** (建议用户自己 vim 填到生成的 .toml 里, 不要让 AI 经手 key 字符串本身)
   - **base_url** (例: `https://api.openai.com/v1` / 自建网关地址)
   - **官方文档链接** (AI 会用 WebFetch 去读, 确认 API 形状)
   - **模型清单** (默认模型 + 可选模型 ID)
3. WebFetch 读文档, 确认 POST/GET / body 格式 / 鉴权方式
4. 参照 `docs/provider-examples/gpt-image-2.toml.example` schema, 写 `~/.anything-ppt/providers/<name>.toml`
5. **永不替用户生成 key, 永不替用户保管 key**
6. 写完后用 `head -20` 给用户看一眼内容
7. 提醒用户 `chmod 600 ~/.anything-ppt/providers/<name>.toml`
8. 当前 generate-image skill 集成是 M2 路线图。在那之前, AI 会按 [how_to_use].invoke 模板生成 curl 调用作为 fallback

### AI 怎么选 provider (启动自检 + 默认值声明)

skill 启动时强制扫 `~/.anything-ppt/providers/*.toml`:

1. **检查每个 .toml 的 `[auth].api_key`** — 空 / `<...>` / `PLACEHOLDER` 视为未配置
2. **零 provider 配好 key** → 立即停下, 给用户两条路 (自己 vim 填 / 让 AI 帮加, 后者带危险警告)
3. **有配好的** → 找 `default = true` 的作为这次的出厂默认
4. 告诉用户: "这次默认用 [nanobanana / pro / 4K], 要换吗?"
5. 用户说换 → 列出所有已配置好的 provider 让选
6. 风格/角色/provider 三者 AI 在生图前都会一并向用户确认

---

## 4. demo/ — 成品归档

每次成功生成一套 PPT，AI 会自动把成品写到:

```
~/.anything-ppt/demo/YYYY-MM-DD-<slug>/
├── outline.md          用户审过的 outline
├── slides/             所有原始生图 (PNG)
├── deck.html           最终 HTML 交付物
├── deck.html-assets/   WebP 图片 (HTML 引用)
└── meta.toml           本次用了哪个 character / style / provider，便于复盘
```

`<slug>` 是 AI 根据主题生成的 kebab-case (例如 `rl-quickstart-from-zero`)。

**这个目录不会被 install.sh 动**，安全可以攒成历史档。
**也不会被自动清理**，磁盘要紧自己删。

可以浏览历史:

```bash
ls -lt ~/.anything-ppt/demo/ | head
open ~/.anything-ppt/demo/2026-04-29-rl-quickstart/deck.html
```

---

## 备份建议

`~/.anything-ppt/` 整个目录就是你的所有可扩展资产 (人物/风格/配置/历史)。
建议:

- 加进个人 dotfiles 仓库 (注意 providers/*.toml 含 api_key，需 .gitignore 或加密)
- 或者定期 tar 备份: `tar -czf anything-ppt-$(date +%F).tar.gz -C ~ .anything-ppt`
