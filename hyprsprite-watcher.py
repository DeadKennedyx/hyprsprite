#!/usr/bin/env python3
import json, os, subprocess, sys, time
APP = os.path.expanduser("~/.local/share/hyprsprite")
PY  = os.environ.get("HYPRSPRITE_PY_BIN", sys.executable)

def j(cmd):
    out = subprocess.check_output(["hyprctl","-j"]+cmd.split(), text=True)
    return json.loads(out)

def active_ws():
    try:    return int(j("activeworkspace").get("id",-1))
    except: return -1

def sprite_ws_set():
    try:
        return { int(c.get("workspace",{}).get("id")) for c in j("clients") if c.get("title")=="HyprSprite" }
    except:
        return set()

def launch():
    subprocess.Popen([PY, os.path.join(APP,"hyprsprite.py")], cwd=APP)

def tick():
    wid = active_ws()
    if wid >= 0 and wid not in sprite_ws_set():
        launch()

def main():
    tick()
    while True:
        time.sleep(1.0)
        tick()

if __name__=="__main__":
    if not os.path.isfile(os.path.join(APP,"hyprsprite.py")): sys.exit(1)
    main()
