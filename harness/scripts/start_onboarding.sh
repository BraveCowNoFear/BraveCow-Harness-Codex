#!/bin/sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
RUNTIME=
WORKSPACE=$(pwd)
SKILL_PATH=
RECEIPT=
LANGUAGE=auto
TIMEOUT=300
while [ "$#" -gt 0 ]; do
  case "$1" in
    --runtime) RUNTIME=$2; shift 2 ;;
    --workspace) WORKSPACE=$2; shift 2 ;;
    --skill-path) SKILL_PATH=$2; shift 2 ;;
    --receipt) RECEIPT=$2; shift 2 ;;
    --language) LANGUAGE=$2; shift 2 ;;
    --timeout) TIMEOUT=$2; shift 2 ;;
    *) printf 'Unknown option: %s\n' "$1" >&2; exit 2 ;;
  esac
done
[ -n "$RUNTIME" ] && [ -n "$SKILL_PATH" ] && [ -n "$RECEIPT" ] || { printf 'Missing launcher arguments.\n' >&2; exit 2; }
mkdir -p "$(dirname "$RECEIPT")"

if [ "$RUNTIME" = codex ]; then
  command -v python3 >/dev/null 2>&1 || { printf 'Python 3 is required for the Codex App Server launcher.\n' >&2; exit 1; }
  exec python3 "$SCRIPT_DIR/start_onboarding.py" --workspace "$WORKSPACE" --skill-path "$SKILL_PATH" --receipt "$RECEIPT" --language "$LANGUAGE" --timeout "$TIMEOUT"
fi

[ "$RUNTIME" = zcode ] || { printf 'Unsupported runtime: %s\n' "$RUNTIME" >&2; exit 2; }
command -v osascript >/dev/null 2>&1 || { printf 'ZCode automatic task creation requires macOS osascript.\n' >&2; exit 1; }
if [ "$LANGUAGE" = en ]; then
  PROMPT='$bravecow-onboarding Start the adaptive course as Brave Cow (勇敢牛牛). First ask what I study or do, my goal, and my experience. Generate the route from my answer. Match technical depth to my background, but always teach real mechanisms rather than only analogies.'
else
  PROMPT='$bravecow-onboarding 请以“勇敢牛牛”的身份开始自适应课程。第一条回复先问我的专业或工作、目标和经验，再根据回答现场生成课程。技术背景讲工程机制；非技术背景也讲真实原理，不要只用生活比喻。'
fi
if ! osascript - "$PROMPT" <<'APPLESCRIPT'
on run argv
  set onboardingPrompt to item 1 of argv
  tell application "ZCode" to activate
  delay 1
  set the clipboard to onboardingPrompt
  tell application "System Events"
    tell process "ZCode"
      keystroke "n" using command down
      delay 1
      keystroke "v" using command down
      delay 0.2
      key code 36
    end tell
  end tell
end run
APPLESCRIPT
then
  printf '{"status":"failed","runtime":"ZCode","method":"keyboard-shortcut","error":"ZCode activation or macOS Accessibility permission failed"}\n' > "$RECEIPT"
  printf 'Could not automate ZCode. Grant Accessibility permission, then open a new task and run /bravecow-onboarding.\n' >&2
  exit 1
fi
printf '{"status":"started","runtime":"ZCode","method":"keyboard-shortcut","shortcut":"Command+N"}\n' > "$RECEIPT"
printf 'Started ZCode onboarding task.\n'
