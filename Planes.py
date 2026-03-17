"""
✈ Plane Game — натискай Пробіл або ЛКМ щоб летіти
"""
import tkinter as tk
import random, math

W, H = 520, 680

# ── кольори ──────────────────────────────────────────────────────────────────
SKY_TOP    = (30,  120, 210)
SKY_BOT    = (90,  180, 255)
TOWER_COL  = (160, 160, 165)
TOWER_DARK = (100, 100, 105)
CITY_COL   = (40,  55,  80)

def rgb(r,g,b): return f"#{int(r):02x}{int(g):02x}{int(b):02x}"
def lerp(a,b,t): return a+(b-a)*t
def lc(c1,c2,t): return tuple(int(lerp(a,b,t)) for a,b in zip(c1,c2))

# ── хмарки ───────────────────────────────────────────────────────────────────
class Cloud:
    def __init__(self, x=None):
        self.x  = x if x else random.randint(W, W+200)
        self.y  = random.randint(40, int(H*0.55))
        self.w  = random.randint(55, 110)
        self.h  = random.randint(18, 32)
        self.sp = random.uniform(0.4, 0.9)

    def update(self, speed):
        self.x -= self.sp * speed / 3

    def draw(self, cv):
        x,y,w,h = self.x, self.y, self.w, self.h
        for dx,dy,rw,rh in [(0,0,w,h),(w*.25,-h*.4,w*.5,h*.7),(w*.55,-h*.25,w*.45,h*.6)]:
            cv.create_oval(x+dx,y+dy,x+dx+rw,y+dy+rh,
                           fill="#ddeeff", outline="")

# ── гравець (літак) ───────────────────────────────────────────────────────────
class Plane:
    W, H = 70, 28

    def __init__(self):
        self.x  = 100
        self.y  = H // 2
        self.vy = 0
        self.alive = True

    def flap(self):
        self.vy = -7

    def update(self):
        self.vy += 0.38          # гравітація
        self.vy  = max(-9, min(self.vy, 12))
        self.y  += self.vy

    def draw(self, cv):
        x, y = self.x, self.y
        angle = max(-25, min(self.vy * 3, 35))
        rad   = math.radians(-angle)
        cos_a, sin_a = math.cos(rad), math.sin(rad)

        def rot(px, py):
            return (x + px*cos_a - py*sin_a,
                    y + px*sin_a + py*cos_a)

        # фюзеляж
        body = [rot(-34,  -5), rot( 34, -5),
                rot( 34,   5), rot(-34,  5)]
        cv.create_polygon(body, fill="#e8e0d0", outline="#999")

        # ніс (конус)
        nose = [rot(28, -4), rot(28,  4), rot(38, 0)]
        cv.create_polygon(nose, fill="#cc5500", outline="")

        # хвіст
        tail = [rot(-34, -5), rot(-34, -17), rot(-24, -5)]
        cv.create_polygon(tail, fill="#cc5500", outline="")

        # крило
        wing = [rot(-8, 3), rot(20, 3), rot(12, 18), rot(-14, 18)]
        cv.create_polygon(wing, fill="#cc5500", outline="")

        # маленьке крило
        swng = [rot(-22, -5), rot(-10, -5), rot(-14,-14), rot(-26,-14)]
        cv.create_polygon(swng, fill="#cc5500", outline="")

        # ілюмінатори
        for px in [14, 4, -6, -16]:
            wx, wy = rot(px, -2)
            cv.create_oval(wx-4, wy-4, wx+4, wy+4, fill="#aaddff", outline="#888", width=1)

        # двигун
        ex, ey = rot(5, 10)
        cv.create_oval(ex-7, ey-5, ex+7, ey+5, fill="#555", outline="")
        cv.create_oval(ex-5, ey-3, ex+5, ey+3, fill="#333", outline="")

    def rect(self):
        """Хітбокс (менший за малюнок)"""
        return (self.x-28, self.y-8, self.x+30, self.y+10)

# ── башня ─────────────────────────────────────────────────────────────────────
GAP    = 200     # проміжок між баштами
PIPE_W = 72

class Tower:
    def __init__(self, x):
        self.x    = x
        self.gap_y = random.randint(130, H - 180)   # центр проміжку
        self.passed = False
        self.w    = PIPE_W

    def update(self, speed):
        self.x -= speed

    def top_rect(self):
        return (self.x, 0, self.x+self.w, self.gap_y - GAP//2)

    def bot_rect(self):
        return (self.x, self.gap_y + GAP//2, self.x+self.w, H)

    def draw(self, cv, ground_y):
        x, w = self.x, self.w
        top_h = self.gap_y - GAP//2
        bot_y = self.gap_y + GAP//2

        for rect_y1, rect_y2 in [(0, top_h), (bot_y, ground_y)]:
            if rect_y2 <= rect_y1: continue
            rh = rect_y2 - rect_y1

            # основний прямокутник башні
            cv.create_rectangle(x, rect_y1, x+w, rect_y2,
                                 fill=rgb(*TOWER_COL), outline="")

            # темна права грань (3D ефект)
            cv.create_rectangle(x+w-10, rect_y1, x+w, rect_y2,
                                 fill=rgb(*TOWER_DARK), outline="")

            # вікна
            win_cols = 4; win_rows = max(1, rh // 28)
            for row in range(win_rows):
                for col in range(win_cols):
                    wx = x + 6 + col * 15
                    wy = rect_y1 + 8 + row * 28
                    if wy + 10 < rect_y2 - 4:
                        lit = random.random() > 0.3
                        wc  = "#ffffcc" if lit else "#334455"
                        cv.create_rectangle(wx, wy, wx+9, wy+14,
                                             fill=wc, outline="#222", width=1)

            # антена на верхній башні
            if rect_y1 == 0 and top_h > 20:
                cv.create_line(x+w//2, 0, x+w//2, rect_y1-18,
                               fill="#888", width=3)
                cv.create_oval(x+w//2-4, rect_y1-22, x+w//2+4, rect_y1-14,
                               fill="red", outline="")

# ── місто на горизонті ────────────────────────────────────────────────────────
CITY_BUILDINGS = []
def gen_city():
    global CITY_BUILDINGS
    CITY_BUILDINGS = []
    x = 0
    while x < W + 60:
        bw = random.randint(20, 50)
        bh = random.randint(30, 90)
        CITY_BUILDINGS.append((x, bw, bh))
        x += bw + random.randint(2, 8)

gen_city()

def draw_city(cv, ground_y, offset):
    for bx, bw, bh in CITY_BUILDINGS:
        rx = (bx - offset * 0.15) % (W + 120) - 60
        cv.create_rectangle(rx, ground_y - bh, rx+bw, ground_y,
                             fill=rgb(*CITY_COL), outline="")
        # вікна
        for wy in range(int(ground_y-bh+5), int(ground_y-5), 14):
            for wx in range(int(rx+4), int(rx+bw-4), 10):
                c = "#ffee88" if random.random()>0.4 else "#223344"
                cv.create_rectangle(wx, wy, wx+6, wy+8, fill=c, outline="")

# ═════════════════════════════════════════════════════════════════════════════
#  ГОЛОВНА ГРА
# ═════════════════════════════════════════════════════════════════════════════
class Game(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Сімулятор Алах акбар")
        self.resizable(False, False)
        self.configure(bg="#000")

        self.cv = tk.Canvas(self, width=W, height=H,
                            highlightthickness=0, bg="#1e78d2")
        self.cv.pack()

        self.bind("<space>",          lambda e: self._flap())
        self.bind("<Button-1>",       lambda e: self._flap())
        self.bind("<Up>",             lambda e: self._flap())
        self.cv.bind("<Button-1>",    lambda e: self._flap())

        self._init_game()
        self._tick()

    # ── ініціалізація ─────────────────────────────────────────────────────────
    def _init_game(self):
        self.plane     = Plane()
        self.towers    = [Tower(W + i*280) for i in range(3)]
        self.clouds    = [Cloud(random.randint(0, W)) for _ in range(5)]
        self.score     = 0
        self.speed     = 3.2
        self.state     = "playing"   # playing | dead
        self.ground_y  = H - 70
        self.offset    = 0           # для міста
        self.phase     = 0.0
        self.particles = []          # вибух

    # ── флеп ──────────────────────────────────────────────────────────────────
    def _flap(self):
        if self.state == "dead":
            self._init_game()
            return
        self.plane.flap()

    # ── вибух ─────────────────────────────────────────────────────────────────
    def _spawn_particles(self):
        x, y = self.plane.x, self.plane.y
        for _ in range(30):
            self.particles.append({
                "x": x, "y": y,
                "vx": random.uniform(-5, 5),
                "vy": random.uniform(-6, 2),
                "life": random.randint(18, 35),
                "col": random.choice([(255,80,0),(255,200,0),(200,50,0),(255,255,100)])
            })

    def _update_particles(self):
        for p in self.particles:
            p["x"] += p["vx"]; p["y"] += p["vy"]
            p["vy"] += 0.3; p["life"] -= 1
        self.particles = [p for p in self.particles if p["life"] > 0]

    def _draw_particles(self):
        for p in self.particles:
            a = p["life"] / 35
            r,g,b = p["col"]
            col = rgb(int(r*a), int(g*a), int(b*a))
            sz  = max(1, int(a*8))
            self.cv.create_oval(p["x"]-sz, p["y"]-sz,
                                 p["x"]+sz, p["y"]+sz,
                                 fill=col, outline="")

    # ── колізія ───────────────────────────────────────────────────────────────
    def _collides(self, r1, r2):
        return not (r1[2]<r2[0] or r1[0]>r2[2] or r1[3]<r2[1] or r1[1]>r2[3])

    def _check_collisions(self):
        pr = self.plane.rect()
        # земля / стеля
        if self.plane.y > self.ground_y - 10 or self.plane.y < 15:
            return True
        # башти
        for t in self.towers:
            if self._collides(pr, t.top_rect()) or self._collides(pr, t.bot_rect()):
                return True
        return False

    # ── фон (небо з градієнтом) ───────────────────────────────────────────────
    def _draw_sky(self):
        cv = self.cv
        step = 20
        for i in range(0, self.ground_y, step):
            t   = i / self.ground_y
            col = lc(SKY_TOP, SKY_BOT, t)
            cv.create_rectangle(0, i, W, i+step+1, fill=rgb(*col), outline="")

    # ── земля ─────────────────────────────────────────────────────────────────
    def _draw_ground(self):
        cv = self.cv; gy = self.ground_y
        cv.create_rectangle(0, gy,   W, gy+4,  fill="#a0784a", outline="")
        cv.create_rectangle(0, gy+4, W, H,     fill="#7a5c38", outline="")
        # смуги
        for x in range(0, W, 30):
            xo = (x - int(self.offset*0.8)) % W
            cv.create_line(xo, gy+2, xo+20, gy+2, fill="#b08858", width=2)

    # ── HUD ───────────────────────────────────────────────────────────────────
    def _draw_hud(self):
        cv = self.cv
        # score
        for off,col in [(2,"#000"),(0,"#fff")]:
            cv.create_text(W//2+off, 28+off, text=str(self.score),
                           font=("Arial",34,"bold"), fill=col, anchor="center")
        # підказка на старті (перші 2 очки)
        if self.score == 0 and self.state == "playing":
            cv.create_text(W//2, 90, text="ПРОБІЛ або ЛКМ — летіти",
                           font=("Arial",13,"bold"), fill="#d2e4f6", anchor="center")

    # ── екран смерті ──────────────────────────────────────────────────────────
    def _draw_death_screen(self):
        cv = self.cv
        # напівпрозорий оверлей
        for i in range(6):
            cv.create_rectangle(i,i,W-i,H-i, outline=rgb(200,50,0), width=1)
        cv.create_rectangle(80, H//2-110, W-80, H//2+110,
                             fill="#0a0a0a", outline=rgb(200,50,0), width=3)

        cv.create_text(W//2, H//2-72, text=" МОЛОДЕЦЬ! ",
                       font=("Arial",32,"bold"), fill=rgb(220,60,0), anchor="center")
        cv.create_text(W//2, H//2-28, text=f"Рахунок:  {self.score}",
                       font=("Arial",18), fill="white", anchor="center")

        best = getattr(self, 'best_score', 0)
        if self.score > best:
            self.best_score = self.score
            cv.create_text(W//2, H//2+10, text="🏆  Новий рекорд!",
                           font=("Arial",14,"bold"), fill="#ffdd00", anchor="center")
        else:
            cv.create_text(W//2, H//2+10, text=f"Рекорд:  {self.best_score}",
                           font=("Arial",14), fill="#aaaaaa", anchor="center")

        # кнопка RESTART
        bx1,by1,bx2,by2 = W//2-85, H//2+42, W//2+85, H//2+88
        hov = self._hover_restart
        bcol = (60,160,80) if hov else (40,120,55)
        self.cv.create_rectangle(bx1,by1,bx2,by2,
                                  fill=rgb(*bcol), outline="#aaffaa", width=2)
        self.cv.create_text(W//2,(by1+by2)//2, text="↺   RESTART",
                            font=("Arial",18,"bold"), fill="white", anchor="center")

        self.cv.tag_bind("restart_btn", "<Enter>",    lambda e: setattr(self,'_hover_restart',True))
        self.cv.tag_bind("restart_btn", "<Leave>",    lambda e: setattr(self,'_hover_restart',False))
        self.cv.tag_bind("restart_btn", "<Button-1>", lambda e: self._init_game())

        hit = self.cv.create_rectangle(bx1,by1,bx2,by2,
                                        fill="", outline="", tags="restart_btn")

    # ── головний цикл ─────────────────────────────────────────────────────────
    def _tick(self):
        self.phase += 0.02
        cv = self.cv
        cv.delete("all")

        if self.state == "playing":
            # оновлення
            self.plane.update()
            self.offset += self.speed
            for c in self.clouds: c.update(self.speed)
            if any(c.x < -130 for c in self.clouds):
                self.clouds = [c for c in self.clouds if c.x > -130]
                self.clouds.append(Cloud())

            for t in self.towers:
                t.update(self.speed)
            # рециклінг башт
            self.towers = [t for t in self.towers if t.x > -PIPE_W-10]
            if not self.towers or self.towers[-1].x < W - 260:
                last_x = max(t.x for t in self.towers) if self.towers else W
                self.towers.append(Tower(last_x + random.randint(230, 300)))

            # рахунок
            for t in self.towers:
                if not t.passed and t.x + t.w < self.plane.x:
                    t.passed = True
                    self.score += 1
                    self.speed = min(3.2 + self.score * 0.08, 7.0)

            # колізія
            if self._check_collisions():
                self.state = "dead"
                self._spawn_particles()

        self._update_particles()

        # малювання
        self._draw_sky()
        for c in self.clouds: c.draw(cv)
        draw_city(cv, self.ground_y, self.offset)
        for t in self.towers: t.draw(cv, self.ground_y)
        self._draw_ground()

        if self.state == "playing":
            self.plane.draw(cv)

        self._draw_particles()
        self._draw_hud()

        if self.state == "dead":
            self._draw_death_screen()

        self.after(16, self._tick)

    # hover state
    _hover_restart = False
    best_score     = 0


if __name__ == "__main__":
    Game().mainloop()
