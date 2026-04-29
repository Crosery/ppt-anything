---
name: anime-chibi-default
display_name: 萌系日漫水彩 (默认风格)
language: zh-CN, en-US
font_preference: LXGW WenKai (霞鹜文楷)
created: 2026-04-29
provenance: ppt-anything 项目出厂默认风格
---

# 风格: 萌系日漫水彩 (anime-chibi-default)

`ppt-anything` 出厂默认风格，源自 Crosery 私人 skill 的方法论沉淀。

## 一句话定位

SD chibi 2.5 头身 anime 角色 + 手绘水彩质感 + 干净的 pastel infographic 排版 + 中文 LXGW 文楷。
内容是主角，人物服务情绪，装饰服务氛围。

## 这个 style pack 包含什么 (self-contained)

| 文件 | 用途 |
|---|---|
| `manifest.md` | 你正在读的这份 — 风格元信息 + 入口 |
| `style_guide.md` | 完整风格规范 (content-first / layout A-H / scene-ify / pose vocab / decoration density / 12 条铁律) |
| `prompt_template.md` | 带 `<<SLOT>>` 的 prompt 模板 (主用，nanobanana / seedream / xais 等通路) |
| `prompt_template_gpt_image.md` | gpt-image-1 专用 prompt 模板 (海外通路, M2 启用) |
| `outline_template.md` | outline 思考脚手架 (gate 用户审之前先填这个) |

`install.sh` 会把整包拷到 `~/.ppt-anything/styles/anime-chibi-default/`，AI 直接从全局库读，不依赖 skill 仓库内任何文件。

## 关键铁律 (摘自 style_guide.md)

1. **内容是主角** — 视觉读取顺序: 内容 > 人物 > 装饰
2. **每张 slide 必须不同 layout** — A-H 八种基础 + scene-ify 自定义
3. **每张 slide 必须不同人物姿势** — 姿势词典见 style_guide § 3
4. **零 emoji** — 所有文本插槽 (title / 正文 / pill / caption) 都不能有
5. **中文 LXGW** — 默认字体 LXGW WenKai (霞鹜文楷)，长句拆两行避免单字过密

## 怎么换风格 / 加新 style pack

不要改 `anime-chibi-default`。在 `~/.ppt-anything/styles/<你的风格名>/` 新建目录，至少包含:

```
styles/<你的风格名>/
├── manifest.md         # 元信息 + 这个风格的一句话定位
├── style_guide.md      # 风格规范 (可参考 anime-chibi-default 的结构)
└── prompt_template.md  # 带 <<SLOT>> 的 prompt 模板
```

AI 启动 skill 时会列出 `~/.ppt-anything/styles/` 下所有 manifest，问你用哪个。
