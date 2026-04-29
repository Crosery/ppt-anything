# 安装指南

## 一句话

```bash
git clone <repo-url> ~/work_file/ppt-anything
cd ~/work_file/ppt-anything
bash scripts/install.sh
```

## 它做了什么

| 步骤 | 动作 | 安全性 |
|---|---|---|
| 1 | `cp -R skill/` 到 `~/.claude/skills/ppt-anything/` | 已存在则备份到 `.bak.<时间戳>/` 再覆盖 |
| 2 | 拷贝 `defaults/characters/*` 到 `~/.ppt-anything/characters/`  | 仅在目标不存在时拷贝 |
| 3 | 拷贝 `defaults/styles/*` 到 `~/.ppt-anything/styles/` | 仅在目标不存在时拷贝 |
| 4 | 拷贝 `defaults/providers/*.toml.example` 到 `~/.ppt-anything/providers/` | 仅在目标不存在时拷贝 |
| 5 | 检查 `cwebp` 是否安装 | 仅检查，不自动装 |

**install.sh 不会**:
- 改你已有的 `~/.ppt-anything/` 数据
- 替你写 API key
- 安装系统级依赖
- 推任何东西到远端

## 系统依赖

| 依赖 | 用途 | 安装 |
|---|---|---|
| `bash` >= 4 | 跑 install.sh | macOS / Linux 自带 |
| `cwebp` | HTML 打包时 PNG → WebP 压缩 | macOS: `brew install webp` / Debian: `sudo apt install webp` |
| `python3` >= 3.9 | HTML 打包脚本 | macOS / Linux 自带 |
| 一个生图 API key | 实际生图 | 见下文 |

## 生图 API key 配置

`install.sh` 出厂只装 `nanobanana` 一个 provider 模板, `[auth]` 下三个字段全部留空。你必须自己填齐三项才能生图:

```bash
vim ~/.ppt-anything/providers/nanobanana.toml
```

把 `[auth]` 段里这三个字段都改成你申请到的真实值:

```toml
[auth]
api_key  = "<你申请到的 key>"
base_url = "<官方网关地址>"
docs_url = "<官方 API 文档地址>"
```

**AI 不会替你猜任何字段**——包括官网公开的 base_url 也要你自己填, 这是为了避免它在你不知情时把请求发去错地方。

**想用其他渠道** (gpt-image-2 / Replicate / Fal / 自建网关 / 任何 OpenAI-compatible 端点):

### 方案 A - 自己加 (推荐, 安全)

```bash
cp docs/provider-examples/gpt-image-2.toml.example ~/.ppt-anything/providers/gpt-image-2.toml
vim ~/.ppt-anything/providers/gpt-image-2.toml
# 按 schema 填 api_key / base_url / models / docs_url
chmod 600 ~/.ppt-anything/providers/gpt-image-2.toml   # 防止旁人偷看
```

### 方案 B - 让 AI 帮加 (危险操作)

在 AI CLI 里说"帮我加 <provider 名>"。AI 会按规范向你要 4 样东西:

| 你要给的 | AI 怎么用 |
|---|---|
| api_key | 写到 `~/.ppt-anything/providers/<name>.toml` 里, 不上传任何地方 |
| base_url | 写进 `[auth].base_url`。AI 不替你猜, 必须你提供 |
| docs_url | 写进 `[auth].docs_url`。AI 会 WebFetch 读它确认请求 schema |
| 模型清单 | 写进 `[models]` |

**警告**: AI 不替你生成 api_key, 也不替你保管 key。建议你自己 vim 填 key 字符串, 不要让 AI 经手。

### 启动自检

skill 每次启动会扫 `~/.ppt-anything/providers/*.toml`, 检查每个 provider 的 `[auth]` 段:
- `api_key` / `base_url` / `docs_url` 任一为空 / `<...>` 占位符 / `PLACEHOLDER` → 该 provider 视为未配置
- 零 provider 字段全齐 → 拒绝生图, 给你两条路 (自己填 / 让 AI 帮加, 后者带危险警告)

## 在不同 AI CLI 里调用

### Claude Code

skill 已经被 `install.sh` 软链到 `~/.claude/skills/ppt-anything/`，直接：

```
/ppt-anything 做一套 PPT 讲 RL 怎么从 0 入门到上分
```

### 其他 AI CLI (Gemini / Codex / Cursor 等)

进入项目目录 → AI 会自动读 `AGENT.md`（或对应的 `GEMINI.md`/`CODEX.md`/`.cursorrules`，都指向 `AGENT.md`）→ 按里面写的工作流执行。

## 卸载

```bash
# 移除 skill 软链
rm ~/.claude/skills/ppt-anything

# 想完全清理全局库 (会丢掉你扩展的角色/风格/配置, 谨慎)
rm -rf ~/.ppt-anything
```

不会留任何系统服务、cron、登录项。
