#!/usr/bin/env python3
import os, sys, math, random, time, signal
from PySide6 import QtCore, QtGui, QtWidgets

DEFAULT_CORNER     = "bottom-right"
CORNER_WANDER_BOX  = 0
MARGIN, FRAME_MS, STEP_MS = 24, 60, 16
SCALE, STRICT_HITTEST, ALPHA_THRESH = 1.0, False, 10

def load_frames(folder):
    names = sorted(n for n in os.listdir(folder) if n.lower().endswith((".png",".webp",".jpg",".jpeg")))
    out=[]
    for n in names:
        img = QtGui.QImage(os.path.join(folder,n))
        if img.isNull(): continue
        if SCALE != 1.0:
            w,h = int(round(img.width()*SCALE)), int(round(img.height()*SCALE))
            img = img.scaled(w,h, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        out.append(img.convertToFormat(QtGui.QImage.Format_ARGB32))
    return out

def normalize_frames_same_size(frames, align="center"):
    if not frames: return frames
    W = max(i.width() for i in frames); H = max(i.height() for i in frames)
    out=[]
    for img in frames:
        if img.width()==W and img.height()==H: out.append(img); continue
        canvas = QtGui.QImage(W,H,QtGui.QImage.Format_ARGB32); canvas.fill(QtCore.Qt.transparent)
        p = QtGui.QPainter(canvas)
        x = (W-img.width())//2 if align=="center" else 0
        y = (H-img.height())//2 if align=="center" else 0
        p.drawImage(x,y,img); p.end()
        out.append(canvas.convertToFormat(QtGui.QImage.Format_ARGB32))
    return out

def placeholder():
    s=120; img = QtGui.QImage(s,s,QtGui.QImage.Format_ARGB32); img.fill(QtCore.Qt.transparent)
    p=QtGui.QPainter(img); p.setRenderHint(QtGui.QPainter.Antialiasing, True)
    p.setPen(QtGui.QPen(QtGui.QColor("#222"),3)); p.setBrush(QtGui.QBrush(QtGui.QColor(255,255,255,230)))
    p.drawEllipse(6,6,s-12,s-12); p.end(); return img

class HyprSprite(QtWidgets.QWidget):
    def __init__(self, frames):
        super().__init__(None, QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.Window)
        self.setWindowTitle("HyprSprite")
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)
        self.setAttribute(QtCore.Qt.WA_NoSystemBackground, True)
        self.setFocusPolicy(QtCore.Qt.ClickFocus)

        self.frames = frames if frames else [placeholder()]
        self.idx=0; self.setFixedSize(self.frames[0].size()); self._update_mask()
        self.mode="idle"; self.dragging=False; self.user_moved=False
        self.drag_off=QtCore.QPoint(); self.tx=self.ty=0; self.last_wander=time.time()
        self._first_paint=False

        self.anim=QtCore.QTimer(self); self.anim.timeout.connect(self._next_frame); self.anim.start(FRAME_MS)
        self.tick=QtCore.QTimer(self); self.tick.timeout.connect(self._step); self.tick.start(STEP_MS)
        self.menu=QtWidgets.QMenu(); self.menu.addAction("Quit", QtWidgets.QApplication.quit)

        self.show()
        for d in (60,160,320,640,1200,2000):
            QtCore.QTimer.singleShot(d, self._place_initial)

    def _update_mask(self):
        self.setMask(QtGui.QBitmap.fromImage(self.frames[self.idx].createAlphaMask()))
    def paintEvent(self, _):
        p=QtGui.QPainter(self); p.setRenderHint(QtGui.QPainter.SmoothPixmapTransform, True)
        p.drawImage(0,0,self.frames[self.idx])
        if not self._first_paint:
            self._first_paint=True
            QtCore.QTimer.singleShot(0, self._place_initial)
    def _next_frame(self):
        self.idx=(self.idx+1)%len(self.frames); self._update_mask(); self.update()

    def _active_rect(self):
        scr = QtGui.QGuiApplication.screenAt(QtGui.QCursor.pos())
        return (scr or QtGui.QGuiApplication.primaryScreen()).availableGeometry()
    def _bounds_full(self):
        r=self._active_rect()
        return QtCore.QRect(r.x()+MARGIN, r.y()+MARGIN, r.width()-2*MARGIN, r.height()-2*MARGIN)
    def _place_to_corner(self, corner):
        r=self._active_rect()
        corners={
            "top-left":     (r.left()+MARGIN, r.top()+MARGIN),
            "top-right":    (r.right()-self.width()-MARGIN, r.top()+MARGIN),
            "bottom-left":  (r.left()+MARGIN, r.bottom()-self.height()-MARGIN),
            "bottom-right": (r.right()-self.width()-MARGIN, r.bottom()-self.height()-MARGIN),
            "center":       (r.center().x()-self.width()//2, r.center().y()-self.height()//2),
        }
        x,y=corners.get(corner, corners["bottom-right"]); self.move(x,y)
    def _place_initial(self):
        if not self.user_moved: self._place_to_corner(DEFAULT_CORNER)

    def _corner_bounds(self):
        if CORNER_WANDER_BOX<=0: return None
        r=self._active_rect()
        if DEFAULT_CORNER=="top-left":         left,top = r.left()+MARGIN, r.top()+MARGIN
        elif DEFAULT_CORNER=="top-right":      left,top = r.right()-MARGIN-CORNER_WANDER_BOX, r.top()+MARGIN
        elif DEFAULT_CORNER=="bottom-left":    left,top = r.left()+MARGIN, r.bottom()-MARGIN-CORNER_WANDER_BOX
        else:                                  left,top = r.right()-MARGIN-CORNER_WANDER_BOX, r.bottom()-MARGIN-CORNER_WANDER_BOX
        return QtCore.QRect(left, top, CORNER_WANDER_BOX, CORNER_WANDER_BOX)

    def _pick_target(self):
        b=self._corner_bounds() or self._bounds_full()
        self.tx=random.randint(b.left(), max(b.left(), b.right()-1))
        self.ty=random.randint(b.top(),  max(b.top(),  b.bottom()-1))
    def _step(self):
        if CORNER_WANDER_BOX>0 and not self.dragging:
            now=time.time()
            if now-self.last_wander>random.uniform(2.5,5.0):
                self.mode="wander"; self.last_wander=now; self._pick_target()
            if self.mode=="wander":
                dx,dy=self.tx-self.x(), self.ty-self.y(); dist=math.hypot(dx,dy)
                if dist>2:
                    spd=min(12.0, 2.0+dist/40.0)
                    self.move(self.x()+int(dx/dist*spd), self.y()+int(dy/dist*spd))
                else:
                    self.mode="idle"
        b=self._bounds_full()
        nx=min(max(self.x(), b.left()),  b.right()-self.width())
        ny=min(max(self.y(), b.top()),   b.bottom()-self.height())
        if nx!=self.x() or ny!=self.y(): self.move(nx,ny)

    def _alpha_at(self, pos):
        if not (0<=pos.x()<self.width() and 0<=pos.y()<self.height()): return 0
        return QtGui.qAlpha(self.frames[self.idx].pixel(pos))
    def _hit_ok(self, pt): return (self._alpha_at(pt)>ALPHA_THRESH) if STRICT_HITTEST else True
    def mousePressEvent(self, ev):
        pt=ev.position().toPoint()
        if ev.button()==QtCore.Qt.RightButton and self._hit_ok(pt):
            self.menu.popup(ev.globalPosition().toPoint()); return
        if ev.button()==QtCore.Qt.LeftButton and self._hit_ok(pt):
            self.mode="drag"; self.dragging=True; self.user_moved=True
            self.drag_off = ev.globalPosition().toPoint() - self.frameGeometry().topLeft(); ev.accept()
        else: ev.ignore()
    def mouseMoveEvent(self, ev):
        if self.dragging: self.move(ev.globalPosition().toPoint() - self.drag_off); ev.accept()
        else: ev.ignore()
    def mouseReleaseEvent(self, ev):
        if ev.button()==QtCore.Qt.LeftButton: self.dragging=False; self.mode="idle"

def main():
    QtGui.QGuiApplication.setDesktopFileName("hyprsprite")
    QtWidgets.QApplication.setApplicationName("HyprSprite")
    app = QtWidgets.QApplication(sys.argv)
    signal.signal(signal.SIGINT, lambda *_: QtWidgets.QApplication.quit())
    t=QtCore.QTimer(); t.start(200); t.timeout.connect(lambda: None)
    frames = load_frames(os.path.join(os.path.dirname(__file__),"frames"))
    frames = normalize_frames_same_size(frames)
    _ = HyprSprite(frames)
    sys.exit(app.exec())

if __name__=="__main__": main()
