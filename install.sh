#!/bin/sh
set -eu

REPO_ROOT=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
BRAVECOW_HOME=${BRAVECOW_HOME:-"$HOME/.bravecow"}
CODEX_HOME=${CODEX_HOME:-"$HOME/.codex"}
ZCODE_HOME=${ZCODE_HOME:-"$HOME/.zcode"}
SHARED_SKILLS_HOME=${SHARED_SKILLS_HOME:-"$HOME/.agents/skills"}
OPENCLAW_HOME=${OPENCLAW_HOME:-"$HOME/.openclaw"}
WORKSPACE=$(pwd)
TARGETS=all
ONBOARDING_RUNTIME=auto
ONBOARDING_LANGUAGE=auto
ONBOARDING_TIMEOUT=300
UPDATE_RUNTIME=0
MIGRATE_CONFIG=0
INITIALIZE_MEMORY=0
REPLACE_USER_DATA=0
DRY_RUN=0
SKIP_ONBOARDING=0
NO_WORKSPACE_AGENTS=0
NO_LINKS=0
SKIP_AUDIT=0
RUN_STAMP=$(date '+%Y%m%d-%H%M%S')
BACKUP_ROOT=

usage() {
  printf '%s\n' "Usage: ./install.sh [--targets all|codex|zcode] [options]"
  printf '%s\n' "  --bravecow-home PATH       Shared Harness and memory root"
  printf '%s\n' "  --codex-home PATH          Codex home (default: ~/.codex)"
  printf '%s\n' "  --zcode-home PATH          ZCode home (default: ~/.zcode)"
  printf '%s\n' "  --workspace PATH           Workspace receiving the managed AGENTS block"
  printf '%s\n' "  --update-runtime           Update managed scripts and skills"
  printf '%s\n' "  --migrate-config           Update managed runtime configuration"
  printf '%s\n' "  --initialize-memory        Create missing memory files"
  printf '%s\n' "  --replace-user-data        Replace memory templates after backup"
  printf '%s\n' "  --skip-onboarding          Do not create the post-install task"
  printf '%s\n' "  --dry-run                  Show actions without changing files"
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --bravecow-home) BRAVECOW_HOME=$2; shift 2 ;;
    --codex-home) CODEX_HOME=$2; shift 2 ;;
    --zcode-home) ZCODE_HOME=$2; shift 2 ;;
    --shared-skills-home) SHARED_SKILLS_HOME=$2; shift 2 ;;
    --openclaw-home) OPENCLAW_HOME=$2; shift 2 ;;
    --workspace) WORKSPACE=$2; shift 2 ;;
    --targets) TARGETS=$(printf '%s' "$2" | tr '[:upper:]' '[:lower:]'); shift 2 ;;
    --onboarding-runtime) ONBOARDING_RUNTIME=$(printf '%s' "$2" | tr '[:upper:]' '[:lower:]'); shift 2 ;;
    --onboarding-language) ONBOARDING_LANGUAGE=$2; shift 2 ;;
    --onboarding-timeout) ONBOARDING_TIMEOUT=$2; shift 2 ;;
    --backup-root) BACKUP_ROOT=$2; shift 2 ;;
    --update-runtime) UPDATE_RUNTIME=1; shift ;;
    --migrate-config) MIGRATE_CONFIG=1; shift ;;
    --initialize-memory) INITIALIZE_MEMORY=1; shift ;;
    --replace-user-data) REPLACE_USER_DATA=1; INITIALIZE_MEMORY=1; shift ;;
    --dry-run) DRY_RUN=1; shift ;;
    --skip-onboarding) SKIP_ONBOARDING=1; shift ;;
    --no-workspace-agents) NO_WORKSPACE_AGENTS=1; shift ;;
    --no-links) NO_LINKS=1; shift ;;
    --skip-audit) SKIP_AUDIT=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) printf 'Unknown option: %s\n' "$1" >&2; usage >&2; exit 2 ;;
  esac
done

case "$TARGETS" in all|codex|zcode) ;; *) printf 'Invalid --targets: %s\n' "$TARGETS" >&2; exit 2 ;; esac
case "$ONBOARDING_RUNTIME" in auto|codex|zcode) ;; *) printf 'Invalid --onboarding-runtime: %s\n' "$ONBOARDING_RUNTIME" >&2; exit 2 ;; esac
case "$ONBOARDING_LANGUAGE" in auto|zh-CN|en) ;; *) printf 'Invalid --onboarding-language: %s\n' "$ONBOARDING_LANGUAGE" >&2; exit 2 ;; esac

HARNESS_HOME="$BRAVECOW_HOME/harness"
MEMORY_HOME="$BRAVECOW_HOME/memories"
[ -n "$BACKUP_ROOT" ] || BACKUP_ROOT="$HARNESS_HOME/backups/$RUN_STAMP"
if [ "$UPDATE_RUNTIME$MIGRATE_CONFIG$INITIALIZE_MEMORY$REPLACE_USER_DATA" = 0000 ]; then
  UPDATE_RUNTIME=1
  MIGRATE_CONFIG=1
  INITIALIZE_MEMORY=1
fi

plan() { if [ "$DRY_RUN" -eq 1 ]; then printf 'DRY-RUN: %s\n' "$*"; else printf '%s\n' "$*"; fi; }
ensure_dir() { [ -d "$1" ] || { plan "Create directory: $1"; [ "$DRY_RUN" -eq 1 ] || mkdir -p "$1"; }; }

backup_file() {
  local relative destination
  [ -f "$1" ] || return 0
  relative=$(printf '%s' "$1" | sed 's#^/##')
  destination="$BACKUP_ROOT/$relative"
  plan "Backup file: $1 -> $destination"
  if [ "$DRY_RUN" -eq 0 ]; then mkdir -p "$(dirname "$destination")"; cp "$1" "$destination"; fi
}

copy_file() {
  local source_file destination_file allow_overwrite category
  source_file=$1 destination_file=$2 allow_overwrite=$3 category=$4
  [ -f "$source_file" ] || { printf 'Missing source file: %s\n' "$source_file" >&2; exit 1; }
  if [ -f "$destination_file" ] && cmp -s "$source_file" "$destination_file"; then
    printf 'Up to date [%s]: %s\n' "$category" "$destination_file"; return
  fi
  if [ -f "$destination_file" ] && [ "$allow_overwrite" -eq 0 ]; then
    printf 'Keep existing [%s]: %s\n' "$category" "$destination_file"; return
  fi
  ensure_dir "$(dirname "$destination_file")"
  [ -f "$destination_file" ] && backup_file "$destination_file"
  plan "Write [$category]: $destination_file"
  [ "$DRY_RUN" -eq 1 ] || cp "$source_file" "$destination_file"
}

copy_tree() {
  local source_tree destination_tree allow_overwrite category source_file relative
  source_tree=$1 destination_tree=$2 allow_overwrite=$3 category=$4
  [ -d "$source_tree" ] || return 0
  ensure_dir "$destination_tree"
  find "$source_tree" -type f ! -name '*.pyc' ! -path '*/__pycache__/*' | while IFS= read -r source_file; do
    relative=${source_file#"$source_tree"/}
    copy_file "$source_file" "$destination_tree/$relative" "$allow_overwrite" "$category"
  done
}

ensure_link() {
  local alias_path target_path
  alias_path=$1 target_path=$2
  if [ -e "$alias_path" ] || [ -L "$alias_path" ]; then printf 'Keep existing runtime path: %s\n' "$alias_path"; return; fi
  ensure_dir "$(dirname "$alias_path")"
  if [ "$NO_LINKS" -eq 1 ]; then printf 'Skip symbolic link because --no-links is set: %s\n' "$alias_path"; return; fi
  plan "Create symbolic link: $alias_path -> $target_path"
  [ "$DRY_RUN" -eq 1 ] || ln -s "$target_path" "$alias_path"
}

ensure_neutral_root() {
  local neutral legacy label
  neutral=$1 legacy=$2 label=$3
  if [ -e "$neutral" ] || [ -L "$neutral" ]; then return 0; fi
  ensure_dir "$(dirname "$neutral")"
  if [ -d "$legacy" ] && [ "$NO_LINKS" -eq 0 ]; then
    plan "Adopt existing Codex data [$label]: $neutral -> $legacy"
    [ "$DRY_RUN" -eq 1 ] || ln -s "$legacy" "$neutral"
  else
    ensure_dir "$neutral"
    if [ -d "$legacy" ]; then copy_tree "$legacy" "$neutral" 0 "legacy-$label"; fi
  fi
}

install_skill_entry() {
  local skill_name runtime_home shared_target runtime_target
  skill_name=$1 runtime_home=$2 shared_target=$3
  runtime_target="$runtime_home/$skill_name"
  if [ -e "$runtime_target" ] || [ -L "$runtime_target" ]; then
    if [ -L "$runtime_target" ]; then printf 'Keep existing runtime skill link: %s\n' "$runtime_target"
    elif [ "$UPDATE_RUNTIME" -eq 1 ]; then copy_tree "$shared_target" "$runtime_target" 1 runtime
    else printf 'Keep existing runtime skill: %s\n' "$runtime_target"; fi
    return
  fi
  ensure_dir "$runtime_home"
  if [ "$NO_LINKS" -eq 1 ]; then copy_tree "$shared_target" "$runtime_target" 1 runtime
  else plan "Create symbolic link: $runtime_target -> $shared_target"; [ "$DRY_RUN" -eq 1 ] || ln -s "$shared_target" "$runtime_target"; fi
}

update_agents() {
  local destination snippet start end temporary
  destination=$1 snippet="$REPO_ROOT/templates/AGENTS.snippet.md"
  ensure_dir "$(dirname "$destination")"
  if [ ! -f "$destination" ]; then copy_file "$snippet" "$destination" 1 config; return; fi
  if grep -q '<!-- BraveCow Harness: start -->' "$destination"; then start='<!-- BraveCow Harness: start -->'; end='<!-- BraveCow Harness: end -->'
  elif grep -q '<!-- BraveCow Harness Codex: start -->' "$destination"; then start='<!-- BraveCow Harness Codex: start -->'; end='<!-- BraveCow Harness Codex: end -->'
  else
    backup_file "$destination"; plan "Append managed AGENTS block: $destination"
    [ "$DRY_RUN" -eq 1 ] || { printf '\n\n' >> "$destination"; cat "$snippet" >> "$destination"; }
    return
  fi
  temporary="${destination}.bravecow.$$"
  awk -v start="$start" -v end="$end" -v snippet="$snippet" '
    $0 == start { while ((getline line < snippet) > 0) print line; close(snippet); skipping=1; next }
    skipping && $0 == end { skipping=0; next }
    !skipping { print }
  ' "$destination" > "$temporary"
  if cmp -s "$destination" "$temporary"; then rm -f "$temporary"; printf 'Up to date [config]: %s\n' "$destination"; return; fi
  backup_file "$destination"; plan "Update managed AGENTS block: $destination"
  if [ "$DRY_RUN" -eq 1 ]; then rm -f "$temporary"; else mv "$temporary" "$destination"; fi
}

ensure_neutral_root "$HARNESS_HOME" "$CODEX_HOME/harness" harness
ensure_neutral_root "$MEMORY_HOME" "$CODEX_HOME/memories" memory
for directory in "$BRAVECOW_HOME" "$HARNESS_HOME" "$HARNESS_HOME/catalog" "$HARNESS_HOME/reports" "$HARNESS_HOME/vendor" "$HARNESS_HOME/onboarding" "$MEMORY_HOME" "$SHARED_SKILLS_HOME"; do ensure_dir "$directory"; done

copy_file "$REPO_ROOT/harness/README.md" "$HARNESS_HOME/README.md" "$UPDATE_RUNTIME" runtime
copy_tree "$REPO_ROOT/harness/scripts" "$HARNESS_HOME/scripts" "$UPDATE_RUNTIME" runtime
for source_file in "$REPO_ROOT"/harness/catalog/*.example.*; do [ -f "$source_file" ] && copy_file "$source_file" "$HARNESS_HOME/catalog/$(basename "$source_file")" "$UPDATE_RUNTIME" runtime; done

for skill_dir in "$REPO_ROOT"/skills/*; do
  [ -d "$skill_dir" ] || continue
  skill_name=$(basename "$skill_dir") shared_target="$SHARED_SKILLS_HOME/$skill_name"
  copy_tree "$skill_dir" "$shared_target" "$UPDATE_RUNTIME" runtime
  case "$TARGETS" in all|codex) install_skill_entry "$skill_name" "$CODEX_HOME/skills" "$shared_target" ;; esac
  case "$TARGETS" in all|zcode) install_skill_entry "$skill_name" "$ZCODE_HOME/skills" "$shared_target" ;; esac
done

for source_file in "$REPO_ROOT"/templates/memories/*.md; do
  destination="$MEMORY_HOME/$(basename "$source_file")"
  if [ -f "$destination" ] || [ "$INITIALIZE_MEMORY" -eq 1 ]; then copy_file "$source_file" "$destination" "$REPLACE_USER_DATA" memory
  else printf 'Skip missing memory (use --initialize-memory): %s\n' "$destination"; fi
done

case "$TARGETS" in
  all|codex)
    ensure_dir "$CODEX_HOME"; ensure_link "$CODEX_HOME/harness" "$HARNESS_HOME"; ensure_link "$CODEX_HOME/memories" "$MEMORY_HOME"
    for source_file in "$REPO_ROOT"/templates/agents/*.toml; do [ -f "$source_file" ] && copy_file "$source_file" "$CODEX_HOME/agents/$(basename "$source_file")" "$MIGRATE_CONFIG" config; done
    update_agents "$CODEX_HOME/AGENTS.md"
    ;;
esac
case "$TARGETS" in
  all|zcode)
    ensure_dir "$ZCODE_HOME"; ensure_link "$ZCODE_HOME/harness" "$HARNESS_HOME"; ensure_link "$ZCODE_HOME/memories" "$MEMORY_HOME"
    copy_file "$REPO_ROOT/templates/zcode/commands/bravecow-onboarding.md" "$ZCODE_HOME/commands/bravecow-onboarding.md" 1 zcode-command
    update_agents "$ZCODE_HOME/AGENTS.md"
    ;;
esac
[ "$NO_WORKSPACE_AGENTS" -eq 1 ] || update_agents "$WORKSPACE/AGENTS.md"

if [ "$SKIP_AUDIT" -eq 0 ] && [ "$DRY_RUN" -eq 0 ]; then
  if command -v python3 >/dev/null 2>&1; then
    BRAVECOW_HOME="$BRAVECOW_HOME" BRAVECOW_HARNESS_HOME="$HARNESS_HOME" BRAVECOW_MEMORY_HOME="$MEMORY_HOME" CODEX_HOME="$CODEX_HOME" ZCODE_HOME="$ZCODE_HOME" SHARED_SKILLS_HOME="$SHARED_SKILLS_HOME" OPENCLAW_HOME="$OPENCLAW_HOME" python3 "$HARNESS_HOME/scripts/build_skill_inventory.py"
    BRAVECOW_HOME="$BRAVECOW_HOME" BRAVECOW_HARNESS_HOME="$HARNESS_HOME" BRAVECOW_MEMORY_HOME="$MEMORY_HOME" CODEX_HOME="$CODEX_HOME" ZCODE_HOME="$ZCODE_HOME" SHARED_SKILLS_HOME="$SHARED_SKILLS_HOME" OPENCLAW_HOME="$OPENCLAW_HOME" python3 "$HARNESS_HOME/scripts/harness_audit.py"
  else printf 'Python 3 was not found; inventory and audit were skipped.\n' >&2; fi
fi

if [ "$ONBOARDING_RUNTIME" = auto ]; then
  case "${BRAVECOW_CALLER_RUNTIME:-}" in
    [Zz][Cc]ode) ONBOARDING_RUNTIME=zcode ;;
    [Cc]odex) ONBOARDING_RUNTIME=codex ;;
    *)
      caller_pid=$PPID
      caller_runtime=
      caller_depth=0
      while [ "$caller_depth" -lt 8 ] && [ -n "$caller_pid" ] && [ "$caller_pid" -gt 1 ] 2>/dev/null; do
        caller_record=$(ps -p "$caller_pid" -o ppid= -o comm= 2>/dev/null || true)
        caller_name=$(printf '%s' "$caller_record" | tr '[:upper:]' '[:lower:]')
        case "$caller_name" in *zcode*) caller_runtime=zcode; break ;; *codex*|*chatgpt*) caller_runtime=codex; break ;; esac
        caller_pid=$(printf '%s' "$caller_record" | awk '{print $1}')
        caller_depth=$((caller_depth + 1))
      done
      if [ -n "$caller_runtime" ]; then ONBOARDING_RUNTIME=$caller_runtime
      elif [ "$TARGETS" = zcode ]; then ONBOARDING_RUNTIME=zcode
      else ONBOARDING_RUNTIME=codex; fi
      ;;
  esac
fi
if [ "$SKIP_ONBOARDING" -eq 1 ]; then printf 'Onboarding: skipped by --skip-onboarding\n'
elif [ "$DRY_RUN" -eq 1 ]; then plan "Create a new $ONBOARDING_RUNTIME task and start the 12-lesson BraveCow onboarding course"
elif [ "$TARGETS" != all ] && [ "$TARGETS" != "$ONBOARDING_RUNTIME" ]; then printf 'Onboarding runtime was not installed; task launch skipped.\n' >&2
else
  "$HARNESS_HOME/scripts/start_onboarding.sh" --runtime "$ONBOARDING_RUNTIME" --workspace "$WORKSPACE" --skill-path "$SHARED_SKILLS_HOME/bravecow-onboarding/SKILL.md" --receipt "$HARNESS_HOME/onboarding/last-launch.json" --language "$ONBOARDING_LANGUAGE" --timeout "$ONBOARDING_TIMEOUT"
fi

printf '\nBraveCow Harness install/update completed.\n'
printf 'Shared home: %s\nTargets: %s\nShared skills: %s\n' "$BRAVECOW_HOME" "$TARGETS" "$SHARED_SKILLS_HOME"
if [ "$DRY_RUN" -eq 1 ]; then printf 'Mode: dry-run (no files or tasks changed)\n'
elif [ "$SKIP_AUDIT" -eq 1 ]; then printf 'Harness audit: skipped\n'
else printf 'Harness audit: %s\n' "$HARNESS_HOME/reports/agent-harness-audit.md"; fi
