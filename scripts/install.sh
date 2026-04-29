#!/usr/bin/env bash
# ppt-anything installer
#
# 安装动作 (按顺序):
#   1. 全量覆盖更新 ~/.claude/skills/ppt-anything/ <- .claude/skills/ppt-anything/
#      (cp -R, 不再用软链。已存在则先备份到 .bak.<timestamp>/)
#   2. defaults/* -> ~/.anything-ppt/* (仅在目标不存在时拷贝, 不覆盖用户数据)
#   3. 检查 cwebp + tomllib (Python 3.11+)
#   4. 扫 ~/.anything-ppt/providers/ 报告未配置的 provider

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
GLOBAL_LIB="$HOME/.anything-ppt"
CLAUDE_SKILLS="$HOME/.claude/skills"
SKILL_NAME="ppt-anything"
TIMESTAMP="$(date +%Y%m%d-%H%M%S)"
# 备份必须放 CLAUDE_SKILLS 之外。否则 .bak.<TS>/ 也会被 Claude Code 当 skill 扫描进来制造噪声。
SKILL_BACKUP_DIR="$GLOBAL_LIB/.skill-backups"

bold() { printf "\033[1m%s\033[0m\n" "$*"; }
info() { printf "  %s\n" "$*"; }
warn() { printf "  [warn] %s\n" "$*"; }
ok()   { printf "  [ok]   %s\n" "$*"; }

bold "ppt-anything installer"
echo ""
info "项目根目录:   $PROJECT_ROOT"
info "全局库目录:   $GLOBAL_LIB"
info "Claude skill: $CLAUDE_SKILLS/$SKILL_NAME"
echo ""

# ---------- step 1: skill 全量更新 (cp -R, 不软链) ----------
bold "1. 全量更新 Claude Code skill (cp -R 覆盖)"
mkdir -p "$CLAUDE_SKILLS"
SKILL_SRC="$PROJECT_ROOT/skill"
SKILL_DST="$CLAUDE_SKILLS/$SKILL_NAME"

if [[ -L "$SKILL_DST" ]]; then
    target="$(readlink "$SKILL_DST")"
    warn "$SKILL_DST 之前是软链 -> $target"
    warn "现在改用 cp -R 覆盖式安装。先把软链移除..."
    rm "$SKILL_DST"
elif [[ -d "$SKILL_DST" ]]; then
    mkdir -p "$SKILL_BACKUP_DIR"
    backup="$SKILL_BACKUP_DIR/${SKILL_NAME}.${TIMESTAMP}"
    info "已存在 $SKILL_DST, 备份到 $backup (放 skills 目录外, 避免被识别为新 skill)"
    mv "$SKILL_DST" "$backup"
    ok "已备份"
fi

cp -R "$SKILL_SRC" "$SKILL_DST"
ok "skill 已安装到 $SKILL_DST"

# 确保 tools/*.py 可执行
chmod +x "$SKILL_DST"/tools/*.py 2>/dev/null || true
echo ""

# ---------- step 2: 全局库 (不覆盖用户数据) ----------
bold "2. 初始化全局库 $GLOBAL_LIB"
mkdir -p "$GLOBAL_LIB"/{characters,styles,providers,demo}

copy_default() {
    local src="$1" dst="$2" label="$3"
    if [[ -e "$dst" ]]; then
        ok "$label 已存在, 跳过 (不覆盖用户数据)"
    else
        cp -R "$src" "$dst"
        ok "$label 已安装到 $dst"
    fi
}

for char_dir in "$PROJECT_ROOT"/defaults/characters/*/; do
    [[ -d "$char_dir" ]] || continue
    name="$(basename "$char_dir")"
    copy_default "$char_dir" "$GLOBAL_LIB/characters/$name" "character: $name"
done

for style_dir in "$PROJECT_ROOT"/defaults/styles/*/; do
    [[ -d "$style_dir" ]] || continue
    name="$(basename "$style_dir")"
    copy_default "$style_dir" "$GLOBAL_LIB/styles/$name" "style: $name"
done

# providers: 把 .toml.example 平铺为 .toml (仅在用户没建 .toml 时), 字段全空
for tmpl in "$PROJECT_ROOT"/defaults/providers/*.toml.example; do
    [[ -f "$tmpl" ]] || continue
    base="$(basename "$tmpl" .toml.example)"
    real="$GLOBAL_LIB/providers/$base.toml"
    if [[ -e "$real" ]]; then
        ok "provider: $base.toml 已存在, 跳过"
    else
        cp "$tmpl" "$real"
        ok "provider: $base.toml 已生成 (api_key/base_url/docs_url 都留空, 待填)"
    fi
done
echo ""

# ---------- step 3: 依赖检查 ----------
bold "3. 检查依赖"
if command -v cwebp >/dev/null 2>&1; then
    ok "cwebp 已安装 ($(cwebp -version 2>&1 | head -1))"
else
    warn "cwebp 未安装 -- HTML 打包(WebP 压缩)会失败"
    warn "  macOS:  brew install webp"
    warn "  debian: sudo apt install webp"
fi
if python3 -c "import tomllib" 2>/dev/null; then
    ok "Python 3.11+ tomllib 可用 (provider toml 解析)"
else
    warn "Python tomllib 不可用 -- 需要 Python 3.11+. 当前版本: $(python3 --version 2>&1)"
    warn "Provider 配置将无法读取 .toml, 退化到环境变量。建议升级 Python。"
fi
echo ""

# ---------- step 4: provider 状态扫描 ----------
bold "4. 扫描 provider 配置状态"

field_val() {
    local file="$1" field="$2"
    grep -E "^[[:space:]]*${field}[[:space:]]*=" "$file" | head -1 \
        | sed -E 's/^[^=]*=[[:space:]]*"?([^"]*)"?.*/\1/'
}
is_empty_or_placeholder() {
    local v="$1"
    [[ -z "$v" || "$v" == "<"* || "$v" == "PLACEHOLDER"* ]]
}

configured=0
unconfigured=()
shopt -s nullglob
for cfg in "$GLOBAL_LIB"/providers/*.toml; do
    [[ -f "$cfg" ]] || continue
    name="$(basename "$cfg" .toml)"
    api_val="$(field_val "$cfg" api_key)"
    base_val="$(field_val "$cfg" base_url)"
    docs_val="$(field_val "$cfg" docs_url)"
    missing=()
    is_empty_or_placeholder "$api_val"  && missing+=("api_key")
    is_empty_or_placeholder "$base_val" && missing+=("base_url")
    is_empty_or_placeholder "$docs_val" && missing+=("docs_url")
    if (( ${#missing[@]} > 0 )); then
        unconfigured+=("$name (缺: ${missing[*]})")
    else
        configured=$((configured + 1))
        ok "$name: 字段齐全"
    fi
done

if (( configured == 0 )); then
    warn "没有任何 provider 配置完整"
    warn "skill 启动时会启动首跑向导询问你怎么配 (详见 AGENT.md §0)"
fi
if (( ${#unconfigured[@]} > 0 )); then
    warn "未配置完整的 provider:"
    for u in "${unconfigured[@]}"; do warn "  - $u"; done
fi
echo ""

# ---------- step 5: 后续指引 ----------
bold "5. 接下来你需要做"
echo ""
info "a) 给默认 provider 填 api_key (其余字段已预填好官方值):"
info "     vim $GLOBAL_LIB/providers/google.toml"
info "     # 去 https://aistudio.google.com/app/apikey 申请 Gemini API key"
info "     # 推荐自己填; 让 AI agent 帮填属于风险操作 (key 会进 agent 上下文)"
info ""
info "b) 想接入第三方桥接 (任何 OpenAI-compatible 或 Gemini-shape 网关):"
info "     方案 A - 自己加: cp google.toml google-bridge-x.toml, 改 base_url + auth_style + key"
info "     方案 B - 让 AI 加: 准备好 api_key + base_url + 文档链接 告诉 agent"
info "             (有风险: agent 会经手你的 key 字符串)"
info ""
info "c) 在 AI CLI 里调用 skill:"
info "     Claude Code:  /ppt-anything 做一套 PPT 讲 <主题>"
info "     其他 CLI:    见项目 AGENT.md"
info ""
info "d) 想再次更新 skill (比如本仓库有更新):"
info "     重新跑 bash scripts/install.sh"
info "     已存在的 skill 会被备份到 $SKILL_BACKUP_DIR/$SKILL_NAME.<时间戳>/, 然后覆盖"
echo ""
bold "安装完成"
