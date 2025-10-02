#!/usr/bin/env bash
set -eEo pipefail

APPDIR="$HOME/.local/share/hyprsprite"
SRVDIR="$HOME/.config/systemd/user"
HYPRDIR="$HOME/.config/hypr"
HYPRMAIN="$HYPRDIR/hyprland.conf"

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "[HyprSprite] Installing (per-workspace watcher)…"
mkdir -p "$APPDIR/frames" "$SRVDIR" "$HYPRDIR"

sudo pacman -S --needed --noconfirm python qt6-wayland >/dev/null 2>&1 || true

PY_SYS="$(command -v python3 || command -v python || echo python)"
if ! "$PY_SYS" -c "import PySide6" >/dev/null 2>&1; then
  echo "[HyprSprite] Creating venv and installing PySide6…"
  "$PY_SYS" -m venv "$APPDIR/.venv"
  "$APPDIR/.venv/bin/pip" install --upgrade pip >/dev/null
  "$APPDIR/.venv/bin/pip" install --no-input PySide6 >/dev/null
  PY_BIN="$APPDIR/.venv/bin/python"
else
  PY_BIN="$PY_SYS"
fi

install -Dm755 "$REPO_DIR/hyprsprite.py" "$APPDIR/hyprsprite.py"
install -Dm755 "$REPO_DIR/hyprsprite-watcher.py" "$APPDIR/hyprsprite-watcher.py"
install -Dm755 "$REPO_DIR/hyprsprite-watcher.sh" "$APPDIR/hyprsprite-watcher.sh"

REPO_FRAMES="$REPO_DIR/frames"
APP_FRAMES="$APPDIR/frames"
MODE="${1:-auto}"
shopt -s nullglob
mapfile -t SRC_FRAMES < <(find "$REPO_FRAMES" -maxdepth 1 -type f \
  \( -iname '*.png' -o -iname '*.webp' -o -iname '*.jpg' -o -iname '*.jpeg' \) 2>/dev/null)

target_empty() { [[ -z "$(find "$APP_FRAMES" -maxdepth 1 -type f -print -quit 2>/dev/null)" ]]; }

if ((${#SRC_FRAMES[@]})); then
  case "$MODE" in
  --force-frames)
    echo "[HyprSprite] Copying frames (overwrite) from repo → $APP_FRAMES"
    cp -f "${SRC_FRAMES[@]}" "$APP_FRAMES/"
    ;;
  --merge-frames)
    echo "[HyprSprite] Merging frames (no overwrite) from repo → $APP_FRAMES"
    for f in "${SRC_FRAMES[@]}"; do
      b="$(basename "$f")"
      [[ -e "$APP_FRAMES/$b" ]] || cp "$f" "$APP_FRAMES/"
    done
    ;;
  auto | *)
    if target_empty; then
      echo "[HyprSprite] Frames folder empty → copying repo frames to $APP_FRAMES"
      cp "${SRC_FRAMES[@]}" "$APP_FRAMES/"
    else
      echo "[HyprSprite] Frames folder not empty → leaving existing frames untouched."
      echo "            (Use --merge-frames or --force-frames to change this behavior.)"
    fi
    ;;
  esac
fi
shopt -u nullglob

cat >"$HYPRDIR/hyprsprite.conf" <<'EOF'
# HyprSprite rules
windowrulev2 = float,     title:^(HyprSprite)$
windowrulev2 = noblur,    title:^(HyprSprite)$
windowrulev2 = noborder,  title:^(HyprSprite)$
windowrulev2 = noanim,    title:^(HyprSprite)$
EOF

grep -q 'hyprsprite.conf' "$HYPRMAIN" 2>/dev/null ||
  printf '\n# HyprSprite rules\nsource = ~/.config/hypr/hyprsprite.conf\n' >>"$HYPRMAIN"

cat >"$SRVDIR/hyprsprite-watcher.service" <<'UNIT'
[Unit]
Description=HyprSprite watcher (per-workspace)
After=graphical-session.target

[Service]
Type=simple
ExecStart=%h/.local/share/hyprsprite/hyprsprite-watcher.sh
Restart=always
RestartSec=1

[Install]
WantedBy=graphical-session.target
UNIT

systemctl --user daemon-reload
systemctl --user enable --now hyprsprite-watcher.service

command -v hyprctl >/dev/null 2>&1 && hyprctl reload >/dev/null 2>&1 || true

echo "✓ HyprSprite installed."
echo "   Put your PNG/WebP frames in: $APPDIR/frames"
echo "   A sprite spawns the first time you visit a workspace (bottom-right, no border, draggable)."
