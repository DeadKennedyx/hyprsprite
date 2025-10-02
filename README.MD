# HyprSprite (Omarchy/Hyprland)

![sprite](/assets/gh.gif)

Tiny animated desktop sprite for Wayland/Hyprland. **One sprite per workspace**, spawns when you first visit a workspace.  
- fully **transparent**, **draggable**.

### Quick install (Omarchy/Arch)
note: Place your own sprites on frames/ or keep the default ones.

```bash
cd HyprSprite
chmod +x install.sh
./install.sh
cd ..
rm -rf HyprSprite
```

To merge frames:
```bash
./install.sh --merge-frames
```

To overwrite frames: 
```bash
./install.sh --force-frames
```

### Update
```bash
git clone https://github.com/deadkennedyx/HyprSprite.git && cd HyprSprite && ./install.sh
```

### Uninstall (keeps your frames in ~/.local/share/hyprsprite/frames)
```bash
./uninstall.sh
```

