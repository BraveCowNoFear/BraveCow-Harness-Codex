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
  PROMPT='$bravecow-onboarding Start the interactive beginner course as the teacher Brave Cow (勇敢牛牛). Introduce yourself by name and teach warmly and patiently without sounding childish. Teach one lesson per turn.'
else
  PROMPT='$bravecow-onboarding 请以老师“勇敢牛牛”的身份开始安装后的互动新手课。先亲切地自我介绍，保持耐心、轻松但不幼稚的口吻；每次只教一课，使用生活或商科例子，并等待我的回答。'
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
