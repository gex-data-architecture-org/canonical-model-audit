#!/usr/bin/env bash
# build.sh — Regenerates all agent-platform wrappers from the canonical source.
#
# Canonical source: skills/<skill>/content.md  (pure markdown, no YAML frontmatter)
#
# Generated wrappers:
#   Hermes Agent  → skills/<skill>/SKILL.md   (YAML frontmatter + content)
#   Claude Code   → CLAUDE.md                 (root)
#   Codex CLI      → AGENTS.md                 (root)
#   Gemini CLI     → GEMINI.md                 (root)
#   Cursor         → .cursor/rules/<skill>.mdc
#   GitHub Copilot → .github/copilot-instructions.md
#
# Usage:
#   bash skills/dors-loopcraft/build.sh          # regenerate all wrappers
#   bash skills/dors-loopcraft/build.sh --dry-run  # show what would change

set -euo pipefail
cd "$(dirname "$0")/../.."   # repo root

SKILL_NAME="dors-loopcraft"
CANONICAL="skills/${SKILL_NAME}/content.md"
SKILL_MD="skills/${SKILL_NAME}/SKILL.md"

DRY_RUN=false
if [[ "${1:-}" == "--dry-run" ]]; then
    DRY_RUN=true
fi

if [[ ! -f "$CANONICAL" ]]; then
    echo "ERROR: canonical source not found: $CANONICAL"
    exit 1
fi

BODY=$(cat "$CANONICAL")

# YAML frontmatter for Hermes (read from current SKILL.md)
YAML=$(sed -n '/^---$/,/^---$/p' "$SKILL_MD" | head -n -1 | tail -n +2)

HEADER=$(cat <<HEADEOF
<!--
  GENERATED from $CANONICAL
  Do not edit directly — edit the canonical source and regenerate.
  Run: bash skills/${SKILL_NAME}/build.sh
-->

HEADEOF
)

write_if_changed() {
    local file="$1" content="$2" label="$3"
    if $DRY_RUN; then
        if [[ -f "$file" ]]; then
            if ! diff -q <(echo "$content") "$file" &>/dev/null; then
                echo "[dry-run] would update: $file ($label)"
            fi
        else
            echo "[dry-run] would create: $file ($label)"
        fi
        return
    fi

    mkdir -p "$(dirname "$file")"
    echo "$content" > "$file"
    echo "✓ $file ($label)"
}

# Hermes: YAML frontmatter + content
write_if_changed "$SKILL_MD" "---
${YAML}
---
${BODY}" "Hermes Agent"

# Root wrappers (markdown + auto-gen header)
# $() strips trailing newlines from HEADER; add back the blank line separator
SEP=$'\n\n'
write_if_changed "CLAUDE.md"  "${HEADER}${SEP}${BODY}" "Claude Code"
write_if_changed "AGENTS.md"  "${HEADER}${SEP}${BODY}" "Codex CLI"
write_if_changed "GEMINI.md"  "${HEADER}${SEP}${BODY}" "Gemini CLI"

# Editor/IDE wrappers
write_if_changed ".cursor/rules/${SKILL_NAME}.mdc" "${HEADER}${SEP}${BODY}" "Cursor"
write_if_changed ".github/copilot-instructions.md"  "${HEADER}${SEP}${BODY}" "GitHub Copilot"

echo ""
echo "All wrappers regenerated from $CANONICAL"
