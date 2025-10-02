#!/usr/bin/env bash
set -eEo pipefail
shopt -s nullglob
export PATH="/usr/local/bin:/usr/bin:/bin:$PATH"

APP="$HOME/.local/share/hyprsprite"
PY_BIN="$APP/.venv/bin/python"
[[ -x "$PY_BIN" ]] || PY_BIN="$(command -v python3 || command -v python)"

check_hypr() { hyprctl -j activeworkspace >/dev/null 2>&1; }

if ! check_hypr; then
  try_sig() {
    export HYPRLAND_INSTANCE_SIGNATURE="$1"
    check_hypr
  }
  [[ -n "${HYPRLAND_INSTANCE_SIGNATURE:-}" ]] && try_sig "$HYPRLAND_INSTANCE_SIGNATURE" || true
  XR="${XDG_RUNTIME_DIR:-/run/user/$UID}/hypr"
  for d in "$XR" "/run/user/$UID/hypr" "/tmp/hypr"; do
    [[ -d "$d" ]] || continue
    for f in "$d"/*/HYPRLAND_INSTANCE_SIGNATURE; do
      sig="$(cat "$f" 2>/dev/null || true)"
      [[ -n "$sig" ]] || continue
      try_sig "$sig" && break 2
    done
  done
fi

exec "$PY_BIN" -u "$APP/hyprsprite-watcher.py"
