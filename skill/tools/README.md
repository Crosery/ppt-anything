# tools/ — skill 内置工具

| 工具 | 用途 |
|---|---|
| `generate-image.py` | 生图客户端。支持 google (默认, 官方 Gemini) / nanobanana (第三方 Gemini 桥接) / seedream / xais 四个 provider。**从 `~/.ppt-anything/providers/<name>.toml` 读 api_key + base_url + auth_style**。 |
| `build-html-ppt-external.py` | 把 PNG 序列压成 WebP 外链 HTML (默认, 推荐)。HTML ~3KB + 图片几 MB. |
| `build-html-ppt.py` | 把 PNG 序列 base64 嵌入单文件 HTML (备用, 文件大但便于分享). |

---

## generate-image.py

### 配置来源 (按优先级)

1. **`~/.ppt-anything/providers/<provider>.toml`** 的 `[auth].api_key` 和 `[auth].base_url`  ← 默认走这里
2. `~/.claude/skills/ppt-anything/tools/.env`  ← 兼容老用户的 fallback (没有 .env 就跳过)
3. `os.environ` 里的环境变量 (NANOBANANA_API_KEY / ARK_API_KEY / XAIS_API_KEY)

env -> provider 映射:

| 环境变量 | provider toml 文件 |
|---|---|
| `GOOGLE_API_KEY` | `google.toml` |
| `NANOBANANA_API_KEY` | `nanobanana.toml`  (legacy alias for any third-party Gemini bridge) |
| `ARK_API_KEY` | `seedream.toml` |
| `XAIS_API_KEY` | `xais.toml` |

如果 toml 字段是空字符串 / `<...>` 占位符 / `PLACEHOLDER`, 视为未配置, fallback 到下一个来源。

### 使用

```bash
# google pro 4K, 16:9 (默认 provider)
~/.claude/skills/ppt-anything/tools/generate-image.py "夕阳下的金门大桥, 油画风格"

# 指定模型 + 比例 + 输出
cat /tmp/my_prompt.txt | ~/.claude/skills/ppt-anything/tools/generate-image.py \
  --provider google \
  -m gemini-3-pro-image-preview \
  --size 4K \
  -r 16:9 \
  -o ./assets \
  -n my_image \
  --no-preview

# image-to-image (传 ref)
~/.claude/skills/ppt-anything/tools/generate-image.py \
  --ref characters/<slug>/<slug>.png \
  "<prompt>"

# 看完整帮助
~/.claude/skills/ppt-anything/tools/generate-image.py --help
```

### 注意

- Gemini-shape providers (google / nanobanana) **失败也扣费**, 禁止盲重试. 脚本只对 4K -> 2K 做一次 fallback (pro 模型).
- gpt-image-2 在某些第三方桥接下偶尔返回 `finishReason=STOP` + 空 parts (provider 侧不稳). 出现时停下, 别盲重试.
- 默认输出目录是 `~/Pictures/<provider>/`. 用 `-o` 指定其他目录.
- 默认 provider 是 `google`. 想用第三方桥接, `cp google.toml my-bridge.toml`, 改 `base_url` + `auth_style="bearer"` + `api_key`.

---

## build-html-ppt-external.py / build-html-ppt.py

### 默认走 external-ref 版

```bash
~/.claude/skills/ppt-anything/tools/build-html-ppt-external.py \
  --dir ~/.ppt-anything/demo/<my-deck>/ \
  --pattern '<slug>_s*.png' \
  -t '<title>'
```

输出: `<dir>/index.html` (壳 ~3KB) + `<dir>/*.webp` (压缩后图片).
默认 q=95, 拷贝完后 PNG 源文件**会被删除** (省空间). 想保留加 `--keep-png`.

### 何时用 base64 单文件版

只在用户**明确需要单文件交付** (微信 / 邮件附件 / air-gap 分享) 时:

```bash
~/.claude/skills/ppt-anything/tools/build-html-ppt.py \
  --dir <out> --pattern '<slug>_s*.png' \
  -o <out>/<slug>.html -t '<title>'
```

base64 把 PNG 膨胀 ~33%, 5 张 4K deck ~70+MB, 打开慢. 默认不要走它.

### 依赖

- `cwebp` (macOS: `brew install webp`, debian: `apt install webp`)
- python 3.9+ (打包脚本本身)
