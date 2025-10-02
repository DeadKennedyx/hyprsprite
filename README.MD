# HyprSprite (Omarchy/Hyprland)

Tiny desktop sprite for Wayland/Hyprland. **One sprite per workspace**, spawns when you first visit a workspace.  
- fully **transparent**, **draggable**.
- Drop your frames (`.png/.webp/.jpg`) in `~/.local/share/hyprsprite/frames`.

### Quick install (Omarchy/Arch)
```bash
git clone https://github.com/deadkennedyx/HyprSprite.git
cd HyprSprite
chmod +x install.sh
./install.sh
cd ..
rm -rf HyprSprite

### Update
git clone https://github.com/<you>/HyprSprite.git && cd HyprSprite && ./install.sh

### Uninstall (keeps your frames)
./uninstall.sh

