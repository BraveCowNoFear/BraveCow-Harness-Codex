#!/bin/sh
set -eu

REPO_ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
TEMP_ROOT=$(mktemp -d "${TMPDIR:-/tmp}/bravecow-harness-smoke.XXXXXX")
cleanup() { case "$TEMP_ROOT" in "${TMPDIR:-/tmp}"/bravecow-harness-smoke.*) rm -rf "$TEMP_ROOT" ;; *) printf 'Refusing unsafe cleanup: %s\n' "$TEMP_ROOT" >&2 ;; esac; }
trap cleanup EXIT INT TERM

BRAVECOW_HOME="$TEMP_ROOT/.bravecow"
CODEX_HOME="$TEMP_ROOT/.codex"
ZCODE_HOME="$TEMP_ROOT/.zcode"
SHARED_SKILLS_HOME="$TEMP_ROOT/.agents/skills"
WORKSPACE="$TEMP_ROOT/workspace"
mkdir -p "$BRAVECOW_HOME/memories" "$CODEX_HOME"
printf 'USER-SENTINEL\n' > "$BRAVECOW_HOME/memories/PROFILE.md"
printf 'User preface.\n\n<!-- BraveCow Harness Codex: start -->\nold managed block\n<!-- BraveCow Harness Codex: end -->\n' > "$CODEX_HOME/AGENTS.md"

EXTRA_OPTION=
case "$(uname -s)" in MINGW*|MSYS*) EXTRA_OPTION=--skip-audit ;; esac
sh "$REPO_ROOT/install.sh" --bravecow-home "$BRAVECOW_HOME" --codex-home "$CODEX_HOME" --zcode-home "$ZCODE_HOME" --shared-skills-home "$SHARED_SKILLS_HOME" --workspace "$WORKSPACE" --targets all --update-runtime --migrate-config --initialize-memory --no-links --skip-onboarding $EXTRA_OPTION

test -f "$BRAVECOW_HOME/harness/scripts/harness_audit.py"
if [ -z "$EXTRA_OPTION" ]; then
  test -f "$BRAVECOW_HOME/harness/catalog/skill-inventory.json"
  test -f "$BRAVECOW_HOME/harness/reports/agent-harness-audit.md"
fi
test -f "$CODEX_HOME/skills/bravecow-onboarding/SKILL.md"
test -f "$ZCODE_HOME/skills/bravecow-onboarding/SKILL.md"
test -f "$ZCODE_HOME/commands/bravecow-onboarding.md"
test "$(tr -d '\r\n' < "$BRAVECOW_HOME/memories/PROFILE.md")" = USER-SENTINEL
grep -q '~/.bravecow/memories' "$CODEX_HOME/AGENTS.md"
! grep -q 'old managed block' "$CODEX_HOME/AGENTS.md"
printf 'OK: isolated macOS Codex + ZCode install smoke test passed\n'
