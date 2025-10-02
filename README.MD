# HyprSprite (Omarchy/Hyprland)

Tiny desktop sprite for Wayland/Hyprland. **One sprite per workspace**, spawns when you first visit a workspace.  
- fully **transparent**, **draggable**.
- Drop your frames (`.png/.webp/.jpg`) in `~/.local/share/hyprsprite/frames`.

### Quick install (Omarchy/Arch)
```bash
git clone https://github.com/deadkennedyx/HyprSprite.git
cd HyprSprite
Place your own sprites on frames/ or keep the default ones.
chmod +x install.sh
./install.sh
cd ..
rm -rf HyprSprite

To merge frames: ./install.sh --merge-frames

To overwrite frames: ./install.sh --force-frames

### Update

git clone https://github.com/deadkennedyx/HyprSprite.git && cd HyprSprite && ./install.sh

### Uninstall (keeps your frames in ~/.local/share/hyprsprite/frames)
./uninstall.sh

![Logo](https://raw.githubusercontent.com/DeadKennedyx/hyprsprite/refs/heads/master/assets/gh.png?token=GHSAT0AAAAAADJ4ZSCOEVQFETUWYIS2VYZG2G6XFOQ)
