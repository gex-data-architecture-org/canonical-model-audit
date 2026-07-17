#!/usr/bin/env bash
# build.sh — Syncs canonical skills to all Agent Skills-compatible platforms.
#
# Canonical source: skills/<name>/SKILL.md  (Agent Skills open standard)
#
# Platform targets:
#   Claude Code   → .claude/skills/<name>/   (full copy)
#   Gemini CLI     → .gemini/skills/<name>/   (full copy)
#   Hermes Agent  → skills/<name>/           (IS the canonical)
#   Codex CLI      → AGENTS.md               (root wrapper)
#   Cursor         → .cursor/rules/<name>.mdc
#   GitHub Copilot → .github/copilot-instructions.md
#
# Usage:
#   bash skills/dors-loopcraft/build.sh              # sync all
#   bash skills/dors-loopcraft/build.sh --dry-run    # show changes

set -euo pipefail
cd "$(dirname "$0")/../.."   # repo root

SKILL_NAME="dors-loopcraft"
CANONICAL_DIR="skills/${SKILL_NAME}"
SKILL_MD="${CANONICAL_DIR}/SKILL.md"

DRY_RUN=false
[[ "${1:-}" == "--dry-run" ]] && DRY_RUN=true

if [[ ! -f "$SKILL_MD" ]]; then
    echo "ERROR: canonical skill not found: $SKILL_MD"
    exit 1
fi

# ---- helpers ----
sync_dir() {
    local src="$1" dst="$2" label="$3"
    if $DRY_RUN; then
        echo "[dry-run] would sync: $src → $dst ($label)"
        return
    fi
    rm -rf "$dst"
    cp -r "$src" "$dst"
    echo "✓ $dst ($label)"
}

write_if_changed() {
    local file="$1" content="$2" label="$3"
    if $DRY_RUN; then
        if [[ -f "$file" ]]; then
            diff -q <(printf '%s' "$content") "$file" &>/dev/null || \
                echo "[dry-run] would update: $file ($label)"
        else
            echo "[dry-run] would create: $file ($label)"
        fi
        return
    fi
    mkdir -p "$(dirname "$file")"
    printf '%s' "$content" > "$file"
    echo "✓ $file ($label)"
}

# ---- 1. Sync skill dirs to Claude Code + Gemini CLI ----
sync_dir "$CANONICAL_DIR" ".claude/skills/${SKILL_NAME}" "Claude Code"
sync_dir "$CANONICAL_DIR" ".gemini/skills/${SKILL_NAME}" "Gemini CLI"

# ---- 2. Generate root wrappers (thin — reference the skill, don't duplicate) ----
DESCRIPTION=$(sed -n '/^description:/s/^description:[[:space:]]*//p' "$SKILL_MD" | head -1)

ROOT_WRAPPER=$(cat <<EOF
<!--
  GENERATED — do not edit directly.
  Canonical source: ${CANONICAL_DIR}/SKILL.md
  This project follows the Agent Skills open standard (agentskills.io).
-->

# ${SKILL_NAME}

${DESCRIPTION}

## How to use

- **Claude Code**: \`/dors-loopcraft\` (skill auto-loaded from \`.claude/skills/\`)
- **Gemini CLI**: skill auto-loaded from \`.gemini/skills/\`
- **Hermes Agent**: skill auto-loaded from \`skills/\`
- **Codex CLI**: reads this file as project context
- **Cursor**: reads \`.cursor/rules/${SKILL_NAME}.mdc\`
- **GitHub Copilot**: reads \`.github/copilot-instructions.md\`

Full skill: [${CANONICAL_DIR}/SKILL.md](${CANONICAL_DIR}/SKILL.md)
EOF
)

for target in AGENTS.md CLAUDE.md GEMINI.md; do
    write_if_changed "$target" "$ROOT_WRAPPER" "${target%.md} wrapper"
done

# ---- 3. IDE wrappers (same thin reference) ----
write_if_changed ".cursor/rules/${SKILL_NAME}.mdc" "$ROOT_WRAPPER" "Cursor"
write_if_changed ".github/copilot-instructions.md" "$ROOT_WRAPPER" "GitHub Copilot"

echo ""
echo "All platforms synced from ${CANONICAL_DIR}/SKILL.md"
