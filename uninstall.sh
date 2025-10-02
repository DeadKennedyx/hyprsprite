#!/usr/bin/env bash
set -eEo pipefail
SRVDIR="$HOME/.config/systemd/user"
APPDIR="$HOME/.local/share/hyprsprite"

systemctl --user disable --now hyprsprite-watcher.service 2>/dev/null || true
rm -f "$SRVDIR/hyprsprite-watcher.service"
systemctl --user daemon-reload

rm -f "$APPDIR/hyprsprite.py" "$APPDIR/hyprsprite-watcher.py" "$APPDIR/hyprsprite-watcher.sh"

echo "✓ HyprSprite uninstalled (service removed). Frames left in $APPDIR/frames"
