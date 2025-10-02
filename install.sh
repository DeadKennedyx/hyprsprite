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
