---
name: Chengcheng
name_zh: 橙橙
name_jp: —
source_work: 搭子 AI 智能组织系统 (original IP / OC mascot)
role_archetype: mascot / action-driver / cheerleader
source_urls:
  - (none — original IP, no canonical online source)
reference_image: characters/chengcheng/chengcheng.png
image_provenance: user-provided
verified_date: 2026-04-25
version_note: |
  Original IP, no public reference. The model has zero training memory of this character — name-invocation alone WILL fail. Every prompt MUST include the explicit feature one-liner AND `--ref characters/chengcheng/chengcheng.png`.
  Paired duo with 蓝蓝 (lanlan) — they almost always appear together as "搭子".
---

## Prompt call-keywords
- **Primary (explicit feature phrase, since OC has no name-summon)**: `a small chibi watercolor mascot shaped like a rounded orange water droplet, with a warm peach-orange body, big round shiny eyes, pink circular blush, tiny stub arms and feet`
- **Alt (Chinese tag, mostly for human readability)**: `橙橙 (Chengcheng) — 搭子 AI 系统的橙色水滴吉祥物`

## One-liner (paste-ready prompt fragment)
`橙橙 (Chengcheng), a small chibi watercolor mascot from the 搭子 AI IP — a rounded teardrop / water-droplet body in warm peach-orange (#F4A460), <POSE>, <EXPRESSION>, preserving its big round dark-brown shiny eyes with single white highlight, soft pink circular watercolor blush on both cheeks, tiny upturned closed-mouth smile, two short stubby orange arms and two tiny stub feet, soft watercolor wash texture with gentle dark-orange line-art outline. NO clothing, NO accessories, NO ears, NO hair — just the droplet body.`

---

(sections below are internal reference — do NOT paste into prompts)

## Identity
搭子 AI 智能组织系统的「行动派」吉祥物。永远第一个举手、第一个出发、第一个把想法变成行动。情绪稳定的乐观派，不说"不行 / 太难了 / 算了"。常用语："来了来了！" / "这个可以搞！" / "冲就完了~" / "好耶！"。和「蓝蓝」是一对平等双核搭子，自己负责冲、蓝蓝负责稳。

## Appearance (reference only — verified from characters/chengcheng/chengcheng.png)
- **Body shape**: 圆润饱满的水滴形 / 雨滴形，顶部尖、底部圆，弹性饱满；约 2.5 头身比例（头大身小一体）
- **Body palette**: 暖橙色水彩晕染主体，主调接近 `#F4A460`（沙橙 / 桃橙），不是亮红、不是芒果黄
- **Outline**: 比身体略深的橙棕色细线手绘描边
- **Eyes**: 两颗大圆眼，深棕色虹膜，单点白色高光（位置偏左上），无睫毛、无瞳仁分层
- **Cheeks**: 圆形粉色腮红，水彩晕染软边，不是红色、不是橙色
- **Mouth**: 极小的微笑曲线，闭嘴（无牙、无舌、无表情夸张）
- **Arms**: 两条短粗橙色小胳膊从身体两侧伸出，无手指 / 无关节，像小肉粒；常做「搭在蓝蓝身上」「举手」「张开拥抱」等姿势
- **Feet**: 两只极小的橙色椭圆短脚露在身体下方
- **Texture**: 水彩纸晕染质感、轻微纸纹、柔软边缘，NOT flat vector / NOT digital cel-shading
- **Background interaction**: 身下有一抹淡橙灰色软投影
- **Signature details (must preserve in every render)**: 暖橙水滴身 / 大圆深棕眼 + 单白点高光 / 粉腮红 / 短胳膊小脚 / 水彩纸晕染笔触

## Chibi drawing notes (reference only)
本身就是 SD 极简水滴造型，画的时候核心就是：
- **身体必须是「水滴形」整体**，不是球 + 头 + 四肢的那种 anthropomorphic mascot 结构。整个角色 = 一颗会动的橙色水滴
- 水彩感 > 矢量感。任何"图标化 / 卡通厚描边 / Adobe Illustrator 风"都跑偏
- 表情主要靠眼睛 + 嘴角微动，不要画夸张表情纹（不要汗滴、不要 anger mark、不要爆炸星）
- 姿势可以多用：举手、伸手指方向、跳起来、张臂、撑腰、和蓝蓝相靠
- 不画衣服、不画头发、不画耳朵 —— 加任何一样都会破坏 IP 形象

## Recommended pairings
- **Companion characters**: 蓝蓝（lanlan） —— 几乎所有场景都成对出现，「搭子」CP
- **Story themes**: AI 协作 / 团队启动 / 创意头脑风暴 / 项目鼓劲 / 行动派文化 / 双核分工（橙=冲，蓝=稳）
- **Best beats for 橙橙 solo focus**: 出场宣布、抛想法、庆祝任务完成、提议换路、用户提需求时的"我能做"

## Drift risk (critical — model defaults will betray this OC)
- ❗ 模型**完全没有这个角色的训练记忆** → 必须 `--ref characters/chengcheng/chengcheng.png` 每次每张
- ❗ 容易画成「橙色小人 / 橙色 mascot 小球 / 橙色精灵」而不是「橙色水滴」 → prompt 必须显式写 `teardrop / water-droplet body shape`
- 容易给加帽子 / 围巾 / 蝴蝶结 / 小翅膀 → 显式写 `NO clothing, NO accessories, NO hair, NO ears`
- 颜色容易漂成芒果黄、亮红或荧光橙 → 显式写 `warm peach-orange #F4A460, soft watercolor wash, NOT bright red, NOT mango yellow`
- 描边容易变成黑色硬线 → `gentle dark-orange line-art, watercolor not vector`
- 腮红容易丢或变成红圈 → `soft pink watercolor blush circles on cheeks`
- 容易被画成 4 头身或 3 头身比例 → `chibi 2.5 head-body, head IS the body (single droplet form)`
- 和蓝蓝同框时，容易被画成「橙橙比蓝蓝矮一截」→ 实际两者基本等高（蓝蓝略高/略宽 ~5%）
