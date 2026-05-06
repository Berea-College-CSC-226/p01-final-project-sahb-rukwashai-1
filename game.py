"""
Path of No Return: A Tower Defense Game
Authors: Bhushan Sah, Daniel Rukwasha
"""
import pygame, sys, math, random
from path_data import WAYPOINTS, SPAWN_POINT, EXIT_POINT, PATH_WIDTH, GAME_AREA_WIDTH
from game_object import GameObject
from towers import ArrowTower, BombTower, FreezeTower, TOWER_TYPES
from enemies import Enemy
from waves import Wave, WAVE_DATA
from projectiles import Projectile, BombProjectile

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 650
SIDE_PANEL_WIDTH = SCREEN_WIDTH - GAME_AREA_WIDTH
FPS = 60
PATH_BUFFER = 30

# Colors
GRASS_GREEN = (34, 139, 34)
PATH_COLOR = (139, 119, 101)
PANEL_BG = (30, 30, 38)
PANEL_HEADER = (40, 42, 54)
PANEL_BORDER = (60, 62, 80)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GOLD = (255, 215, 0)
RED = (220, 50, 50)
GRAY = (150, 150, 150)
LIGHT_GRAY = (200, 200, 200)
DARK_GREEN = (20, 100, 20)
SELECTED_BORDER = (255, 221, 87)
MONEY_GREEN = (100, 220, 100)


class FloatingText:
    """Small text that floats upward and fades out."""
    def __init__(self, x, y, text, color, size=16, duration=1.0):
        self.x, self.y = x, y
        self.text, self.color, self.duration = text, color, duration
        self.timer = duration
        self.alive = True
        self.font = pygame.font.SysFont("Arial", size, bold=True)

    def update(self, dt):
        self.y -= 30 * dt
        self.timer -= dt
        if self.timer <= 0:
            self.alive = False

    def render(self, screen):
        if not self.alive:
            return
        alpha = max(0, min(255, int(255 * (self.timer / self.duration))))
        surf = self.font.render(self.text, True, self.color)
        surf.set_alpha(alpha)
        screen.blit(surf, (int(self.x), int(self.y)))


class Particle:
    """Small particle for death effects."""
    def __init__(self, x, y, color):
        self.x, self.y = x, y
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(30, 120)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.color = color
        self.size = random.randint(2, 5)
        self.timer = random.uniform(0.3, 0.7)
        self.alive = True

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.timer -= dt
        self.size = max(0, self.size - 4 * dt)
        if self.timer <= 0:
            self.alive = False

    def render(self, screen):
        if self.alive and self.size >= 1:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), int(self.size))


# Path helpers
def _point_seg_dist(px, py, ax, ay, bx, by):
    """Shortest distance from point to line segment."""
    dx, dy = bx - ax, by - ay
    if dx == 0 and dy == 0:
        return math.sqrt((px - ax)**2 + (py - ay)**2)
    t = max(0.0, min(1.0, ((px-ax)*dx + (py-ay)*dy) / (dx*dx + dy*dy)))
    return math.sqrt((px - ax - t*dx)**2 + (py - ay - t*dy)**2)

def is_on_path(x, y):
    """Check if (x, y) is too close to any path segment."""
    hw = PATH_WIDTH / 2 + PATH_BUFFER
    for i in range(len(WAYPOINTS) - 1):
        ax, ay = WAYPOINTS[i]
        bx, by = WAYPOINTS[i + 1]
        if _point_seg_dist(x, y, ax, ay, bx, by) < hw:
            return True
    return False


class Game:
    """Main game class. Manages all game state, rendering, and logic."""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Path of No Return: A Tower Defense Game")
        self.clock = pygame.time.Clock()
        self.running = True

        # State
        self.money, self.lives, self.score, self.kills = 200, 20, 0, 0
        self.current_wave, self.total_waves = 0, len(WAVE_DATA)
        self.game_over = self.game_won = self.wave_active = self.paused = False
        self.wave_cleared = False
        self.wave_cleared_timer = 0
        self.towers, self.enemies, self.projectiles = [], [], []
        self.floating_texts, self.particles = [], []
        self.wave = None
        self.selected_tower_name = self.selected_tower_class = None
        self.status_message = "Press SPACE to start wave 1."
        self.waypoints = WAYPOINTS
        self.frame_count = 0

        # Fonts
        self.font_title = pygame.font.SysFont("Arial", 22, bold=True)
        self.font_large = pygame.font.SysFont("Arial", 28, bold=True)
        self.font_med = pygame.font.SysFont("Arial", 17)
        self.font_sm = pygame.font.SysFont("Arial", 14)
        self.font_xs = pygame.font.SysFont("Arial", 12)
        self.font_huge = pygame.font.SysFont("Arial", 48, bold=True)
        self.font_stat = pygame.font.SysFont("Arial", 15, bold=True)

        self.map_surface = self._build_map()
        self._build_buttons()

    # --- MAP PRE-RENDER ---
    def _build_map(self):
        """Pre-render static map: grass, trees, rocks, flowers, path."""
        s = pygame.Surface((GAME_AREA_WIDTH, SCREEN_HEIGHT))
        random.seed(42)

        # Rich grass gradient with noise
        for y in range(SCREEN_HEIGHT):
            base_g = max(90, 145 - int(y * 0.04))
            for x in range(0, GAME_AREA_WIDTH, 4):
                noise = random.randint(-8, 8)
                c = (22 + int(y*0.01), max(0, min(255, base_g + noise)), 22 + int(y*0.01))
                pygame.draw.rect(s, c, (x, y, 4, 1))

        # Large soft grass patches (varied shades)
        for _ in range(80):
            gx, gy = random.randint(0, GAME_AREA_WIDTH), random.randint(0, SCREEN_HEIGHT)
            gr = random.randint(15, 40)
            shade = random.randint(0, 30)
            patch_surf = pygame.Surface((gr*2, gr*2), pygame.SRCALPHA)
            pygame.draw.circle(patch_surf, (20+shade, 100+random.randint(0,35), 20+shade, 60), (gr,gr), gr)
            s.blit(patch_surf, (gx-gr, gy-gr))

        # Grass blade clusters
        for _ in range(500):
            bx, by = random.randint(0, GAME_AREA_WIDTH), random.randint(0, SCREEN_HEIGHT)
            blade_count = random.randint(2, 5)
            for _ in range(blade_count):
                bh = random.randint(5, 14)
                boff = random.randint(-4, 4)
                blade_c = (25+random.randint(0,20), 90+random.randint(0,60), 20+random.randint(0,15))
                pygame.draw.line(s, blade_c, (bx+boff, by), (bx+boff+random.randint(-3,3), by-bh), 1)

        # Tree shadows (drawn before trees)
        tree_positions = []
        for _ in range(30):
            tx, ty = random.randint(40, GAME_AREA_WIDTH-40), random.randint(40, SCREEN_HEIGHT-40)
            if not is_on_path(tx, ty):
                tree_positions.append((tx, ty))
                shadow_surf = pygame.Surface((40, 20), pygame.SRCALPHA)
                pygame.draw.ellipse(shadow_surf, (0, 0, 0, 40), (0, 0, 40, 20))
                s.blit(shadow_surf, (tx-20, ty+8))

        # Trees with more detail
        for tx, ty in tree_positions:
            cs = random.randint(12, 22)
            # Trunk
            trunk_w = max(3, cs // 4)
            trunk_c = (65+random.randint(0,30), 40+random.randint(0,20), 15+random.randint(0,10))
            pygame.draw.rect(s, trunk_c, (tx-trunk_w//2, ty-2, trunk_w, cs//2+4))
            # Dark canopy layer
            dark_c = (10+random.randint(0,15), 65+random.randint(0,30), 10+random.randint(0,15))
            pygame.draw.circle(s, dark_c, (tx+2, ty), cs)
            # Mid canopy
            mid_c = (20+random.randint(0,20), 95+random.randint(0,35), 20+random.randint(0,15))
            pygame.draw.circle(s, mid_c, (tx-2, ty-3), cs-2)
            # Light highlight
            light_c = (45+random.randint(0,20), 135+random.randint(0,30), 40+random.randint(0,15))
            pygame.draw.circle(s, light_c, (tx-4, ty-6), cs//2)
            # Tiny top highlight
            pygame.draw.circle(s, (80, 180, 70), (tx-5, ty-8), cs//4)

        # Bushes (smaller, rounder, placed near path edges)
        for _ in range(20):
            bx, by = random.randint(30, GAME_AREA_WIDTH-30), random.randint(30, SCREEN_HEIGHT-30)
            if not is_on_path(bx, by):
                bs = random.randint(6, 12)
                bush_dark = (15+random.randint(0,15), 70+random.randint(0,25), 15)
                bush_light = (30+random.randint(0,15), 110+random.randint(0,25), 30)
                pygame.draw.circle(s, bush_dark, (bx, by), bs)
                pygame.draw.circle(s, bush_light, (bx-2, by-2), bs-2)
                pygame.draw.circle(s, (50, 140, 50), (bx-3, by-3), bs//3)

        # Rocks with highlights
        for _ in range(20):
            rx, ry = random.randint(30, GAME_AREA_WIDTH-30), random.randint(30, SCREEN_HEIGHT-30)
            if not is_on_path(rx, ry):
                rsz = random.randint(3, 8)
                base = 90+random.randint(0,40)
                pygame.draw.circle(s, (base-20, base-25, base-35), (rx, ry), rsz)
                pygame.draw.circle(s, (base, base-5, base-15), (rx, ry), rsz-1)
                pygame.draw.circle(s, (base+30, base+25, base+15), (rx-1, ry-2), max(1, rsz//3))

        # Flowers with petals
        for _ in range(50):
            fx, fy = random.randint(10, GAME_AREA_WIDTH-10), random.randint(10, SCREEN_HEIGHT-10)
            if not is_on_path(fx, fy):
                fc = random.choice([(255,90,90),(255,240,80),(220,100,255),(255,170,80),(255,255,240)])
                # Petals
                for angle in range(0, 360, 72):
                    rad = math.radians(angle)
                    px = fx + int(math.cos(rad) * 3)
                    py = fy + int(math.sin(rad) * 3)
                    pygame.draw.circle(s, fc, (px, py), 2)
                # Center
                pygame.draw.circle(s, (255, 220, 50), (fx, fy), 2)
                # Stem
                pygame.draw.line(s, (30, 90, 25), (fx, fy+2), (fx, fy+7), 1)

        # Mushrooms (rare, fun detail)
        for _ in range(6):
            mx, my = random.randint(40, GAME_AREA_WIDTH-40), random.randint(40, SCREEN_HEIGHT-40)
            if not is_on_path(mx, my):
                # Stem
                pygame.draw.rect(s, (220, 210, 190), (mx-2, my, 4, 6))
                # Cap
                cap_c = random.choice([(200,50,50), (180,120,50), (220,180,80)])
                pygame.draw.circle(s, cap_c, (mx, my), 6)
                pygame.draw.circle(s, (min(255,cap_c[0]+40), min(255,cap_c[1]+40), min(255,cap_c[2]+40)),
                                   (mx-2, my-2), 2)

        # --- PATH ---
        # Outer worn edge
        if len(WAYPOINTS) > 1:
            pygame.draw.lines(s, (55,42,28), False, WAYPOINTS, PATH_WIDTH+14)
            pygame.draw.lines(s, (75,60,40), False, WAYPOINTS, PATH_WIDTH+8)
            pygame.draw.lines(s, PATH_COLOR, False, WAYPOINTS, PATH_WIDTH)
            pygame.draw.lines(s, (155,135,110), False, WAYPOINTS, PATH_WIDTH-12)
            pygame.draw.lines(s, (165,148,125), False, WAYPOINTS, PATH_WIDTH-20)

        # Smooth waypoint corners with multiple layers
        for wp in WAYPOINTS:
            pygame.draw.circle(s, (55,42,28), wp, PATH_WIDTH//2+7)
            pygame.draw.circle(s, (75,60,40), wp, PATH_WIDTH//2+4)
            pygame.draw.circle(s, PATH_COLOR, wp, PATH_WIDTH//2)
            pygame.draw.circle(s, (155,135,110), wp, PATH_WIDTH//2-6)
            pygame.draw.circle(s, (165,148,125), wp, PATH_WIDTH//2-10)

        # Path pebbles and dirt texture
        for i in range(len(WAYPOINTS)-1):
            ax,ay = WAYPOINTS[i]; bx,by = WAYPOINTS[i+1]
            sl = math.sqrt((bx-ax)**2 + (by-ay)**2)
            for j in range(int(sl/6)):
                t = j / max(int(sl/6), 1)
                px = int(ax+(bx-ax)*t+random.randint(-14,14))
                py = int(ay+(by-ay)*t+random.randint(-14,14))
                ps = random.randint(105,155)
                sz = random.randint(1, 3)
                pygame.draw.circle(s, (ps, ps-12, ps-28), (px,py), sz)

        # Path edge grass (grass growing over path edges)
        for i in range(len(WAYPOINTS)-1):
            ax,ay = WAYPOINTS[i]; bx,by = WAYPOINTS[i+1]
            sl = math.sqrt((bx-ax)**2 + (by-ay)**2)
            dx, dy = bx-ax, by-ay
            if sl == 0: continue
            nx, ny = -dy/sl, dx/sl
            for j in range(int(sl/10)):
                t = j / max(int(sl/10), 1)
                for side in [1, -1]:
                    ex = int(ax + dx*t + nx*(PATH_WIDTH//2+3)*side + random.randint(-3,3))
                    ey = int(ay + dy*t + ny*(PATH_WIDTH//2+3)*side + random.randint(-3,3))
                    gc = (25+random.randint(0,15), 95+random.randint(0,40), 20)
                    bh = random.randint(3, 8)
                    pygame.draw.line(s, gc, (ex, ey), (ex+random.randint(-2,2), ey-bh*side*0.3-bh*0.7), 1)

        random.seed()
        return s

    # --- BUTTON SETUP ---
    def _build_buttons(self):
        """Create tower button rects."""
        self.tower_buttons = []
        x, y = GAME_AREA_WIDTH + 8, 260
        bw, bh = SIDE_PANEL_WIDTH - 16, 50
        info = [
            ("Arrow", ArrowTower, (55,110,55), (80,160,80), "DMG:25 | RNG:150"),
            ("Bomb", BombTower, (130,45,45), (180,80,80), "DMG:40 | Splash"),
            ("Freeze", FreezeTower, (45,85,130), (80,130,180), "SLW:50% | RNG:120"),
        ]
        for name, cls, col, hcol, desc in info:
            r = pygame.Rect(x, y, bw, bh)
            self.tower_buttons.append({"name":name,"class":cls,"color":col,"hover":hcol,"desc":desc,"rect":r})
            y += bh + 6
        self.cancel_rect = pygame.Rect(x, y+2, bw, 24)

    # --- DRAWING ---
    def draw_map(self):
        """Blit pre-rendered map and draw animated markers."""
        self.screen.blit(self.map_surface, (0, 0))
        # Pulsing spawn
        p = int(3 * math.sin(self.frame_count * 0.08)) + 12
        sp = (self.waypoints[1][0], self.waypoints[1][1])
        pygame.draw.circle(self.screen, (255,80,80), sp, p)
        pygame.draw.circle(self.screen, RED, sp, 8)
        pygame.draw.circle(self.screen, (255,150,150), sp, 4)
        self.screen.blit(self.font_xs.render("SPAWN", True, WHITE), (sp[0]-20, sp[1]-22))
        # Pulsing exit
        ep = self.waypoints[-2]
        p2 = int(3 * math.sin(self.frame_count * 0.08 + 1.5)) + 12
        pygame.draw.circle(self.screen, (255,235,100), ep, p2)
        pygame.draw.circle(self.screen, GOLD, ep, 8)
        pygame.draw.circle(self.screen, (255,255,200), ep, 4)
        self.screen.blit(self.font_xs.render("EXIT", True, WHITE), (ep[0]-12, ep[1]-22))

    def draw_towers(self):
        for t in self.towers:
            t.render(self.screen)
        if self.selected_tower_class and pygame.mouse.get_pos()[0] < GAME_AREA_WIDTH:
            mx, my = pygame.mouse.get_pos()
            cls = self.selected_tower_class
            rs = pygame.Surface((cls.tower_range*2, cls.tower_range*2), pygame.SRCALPHA)
            pygame.draw.circle(rs, (100,200,255,40), (cls.tower_range, cls.tower_range), cls.tower_range)
            pygame.draw.circle(rs, (100,200,255,100), (cls.tower_range, cls.tower_range), cls.tower_range, 2)
            self.screen.blit(rs, (mx-cls.tower_range, my-cls.tower_range))
            valid, _ = self._placement_is_valid(mx, my, cls)
            gc = (100,255,100,80) if valid else (255,100,100,80)
            gs = pygame.Surface((36,36), pygame.SRCALPHA)
            pygame.draw.rect(gs, gc, (0,0,36,36), border_radius=4)
            self.screen.blit(gs, (mx-18, my-18))

    def draw_enemies(self):
        for e in self.enemies: e.render(self.screen)

    def draw_projectiles(self):
        for p in self.projectiles: p.render(self.screen)

    def draw_effects(self):
        for ft in self.floating_texts: ft.render(self.screen)
        for p in self.particles: p.render(self.screen)

    def _draw_stat_bar(self, x, y, label, value, color, ratio):
        """Draw a stat label, value, and thin progress bar."""
        bw = SIDE_PANEL_WIDTH - 16
        self.screen.blit(self.font_xs.render(label, True, GRAY), (x, y))
        vt = self.font_stat.render(value, True, color)
        self.screen.blit(vt, (x + bw - vt.get_width(), y))
        bar_y = y + 18
        ratio = max(0, min(1, ratio))
        pygame.draw.rect(self.screen, (50,50,60), (x, bar_y, bw, 5), border_radius=2)
        if ratio > 0:
            pygame.draw.rect(self.screen, color, (x, bar_y, int(bw*ratio), 5), border_radius=2)

    def draw_side_panel(self):
        """Draw compact side panel with stats, buttons, status, controls."""
        pygame.draw.rect(self.screen, PANEL_BG, (GAME_AREA_WIDTH, 0, SIDE_PANEL_WIDTH, SCREEN_HEIGHT))
        pygame.draw.rect(self.screen, PANEL_HEADER, (GAME_AREA_WIDTH, 0, SIDE_PANEL_WIDTH, 40))
        pygame.draw.line(self.screen, GOLD, (GAME_AREA_WIDTH,40), (SCREEN_WIDTH,40), 2)
        t = self.font_stat.render("PATH OF NO RETURN", True, GOLD)
        self.screen.blit(t, t.get_rect(center=(GAME_AREA_WIDTH + SIDE_PANEL_WIDTH//2, 20)))

        x, y = GAME_AREA_WIDTH + 8, 50
        self._draw_stat_bar(x, y, "MONEY", f"${self.money}", GOLD, self.money/500); y+=32
        self._draw_stat_bar(x, y, "LIVES", str(self.lives), RED, self.lives/20); y+=32
        self._draw_stat_bar(x, y, "SCORE", str(self.score), WHITE, min(self.score/500,1)); y+=32
        self._draw_stat_bar(x, y, "KILLS", str(self.kills), (200,150,255), min(self.kills/50,1)); y+=32
        self._draw_stat_bar(x, y, "WAVE", f"{self.current_wave}/{self.total_waves}", (100,200,255),
                           self.current_wave/max(self.total_waves,1)); y+=35

        pygame.draw.line(self.screen, PANEL_BORDER, (x,y), (SCREEN_WIDTH-8,y), 1); y+=6
        h = self.font_xs.render("SELECT TOWER", True, LIGHT_GRAY)
        self.screen.blit(h, h.get_rect(center=(GAME_AREA_WIDTH+SIDE_PANEL_WIDTH//2, y+4))); y+=14

        mp = pygame.mouse.get_pos()
        for btn in self.tower_buttons:
            r = btn["rect"]
            sel = btn["name"] == self.selected_tower_name
            hov = r.collidepoint(mp)
            afford = self.money >= btn["class"].cost
            bg = btn["hover"] if (sel or (hov and afford)) else (50,50,50) if not afford else btn["color"]
            pygame.draw.rect(self.screen, bg, r, border_radius=5)
            bdr = SELECTED_BORDER if sel else (80,80,80) if not afford else (100,100,120)
            pygame.draw.rect(self.screen, bdr, r, 3 if sel else 1, border_radius=5)
            nc = WHITE if afford else GRAY
            self.screen.blit(self.font_xs.render(f"{btn['name']} ${btn['class'].cost}", True, nc), (r.x+8, r.y+5))
            dc = LIGHT_GRAY if afford else (80,80,80)
            self.screen.blit(self.font_xs.render(btn["desc"], True, dc), (r.x+8, r.y+22))
            if not afford:
                self.screen.blit(self.font_xs.render("NO $", True, (180,80,80)), (r.right-35, r.y+5))

        ch = self.cancel_rect.collidepoint(mp)
        pygame.draw.rect(self.screen, (80,80,90) if ch else (55,55,65), self.cancel_rect, border_radius=3)
        ct = self.font_xs.render("Cancel", True, GRAY)
        self.screen.blit(ct, ct.get_rect(center=self.cancel_rect.center))

        dy = self.cancel_rect.bottom + 8
        pygame.draw.line(self.screen, PANEL_BORDER, (x,dy), (SCREEN_WIDTH-8,dy), 1)
        sy = dy + 6
        sb = pygame.Rect(x, sy, SIDE_PANEL_WIDTH-16, 45)
        pygame.draw.rect(self.screen, (35,35,45), sb, border_radius=4)
        pygame.draw.rect(self.screen, PANEL_BORDER, sb, 1, border_radius=4)
        ty = sy + 5
        for line in self.status_message.split("\n"):
            self.screen.blit(self.font_xs.render(line, True, SELECTED_BORDER), (x+6, ty)); ty+=14

        cy = SCREEN_HEIGHT - 70
        pygame.draw.line(self.screen, PANEL_BORDER, (x,cy-6), (SCREEN_WIDTH-8,cy-6), 1)
        ch = self.font_xs.render("CONTROLS", True, LIGHT_GRAY)
        self.screen.blit(ch, ch.get_rect(center=(GAME_AREA_WIDTH+SIDE_PANEL_WIDTH//2, cy+2))); cy+=14
        for key, act in [("SPACE","Start wave"),("P","Pause"),("R","Restart"),("Q","Quit"),("CLICK","Place tower")]:
            self.screen.blit(self.font_xs.render(f"{key} {act}", True, GRAY), (x+4, cy)); cy+=13

    def draw_game_over(self):
        ov = pygame.Surface((GAME_AREA_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        ov.fill((0,0,0,160)); self.screen.blit(ov, (0,0))
        cx = GAME_AREA_WIDTH // 2
        msg, col = ("VICTORY!", GOLD) if self.game_won else ("GAME OVER", RED)
        t = self.font_huge.render(msg, True, col)
        self.screen.blit(t, t.get_rect(center=(cx, SCREEN_HEIGHT//2-50)))
        stats = [f"Score: {self.score}", f"Kills: {self.kills}",
                 f"Waves: {self.current_wave}", f"Towers: {len(self.towers)}"]
        sy = SCREEN_HEIGHT//2
        for s in stats:
            st = self.font_med.render(s, True, WHITE)
            self.screen.blit(st, st.get_rect(center=(cx, sy))); sy+=25
        qt = self.font_sm.render("Press R to restart  |  Press Q to quit", True, GRAY)
        self.screen.blit(qt, qt.get_rect(center=(cx, sy+20)))

        # Restart button
        self.restart_rect = pygame.Rect(cx - 80, sy + 45, 160, 40)
        mp = pygame.mouse.get_pos()
        hov = self.restart_rect.collidepoint(mp)
        btn_col = (80, 180, 80) if hov else (60, 140, 60)
        pygame.draw.rect(self.screen, btn_col, self.restart_rect, border_radius=6)
        pygame.draw.rect(self.screen, WHITE, self.restart_rect, 2, border_radius=6)
        rt = self.font_stat.render("PLAY AGAIN", True, WHITE)
        self.screen.blit(rt, rt.get_rect(center=self.restart_rect.center))

    def draw_paused(self):
        ov = pygame.Surface((GAME_AREA_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        ov.fill((0,0,0,100)); self.screen.blit(ov, (0,0))
        t = self.font_huge.render("PAUSED", True, WHITE)
        self.screen.blit(t, t.get_rect(center=(GAME_AREA_WIDTH//2, SCREEN_HEIGHT//2-20)))
        r = self.font_med.render("Press P to resume", True, GRAY)
        self.screen.blit(r, r.get_rect(center=(GAME_AREA_WIDTH//2, SCREEN_HEIGHT//2+30)))

    # --- TOWER SELECTION AND PLACEMENT ---
    def _select_tower(self, name):
        cls = TOWER_TYPES[name]
        if self.money >= cls.cost:
            self.selected_tower_name, self.selected_tower_class = name, cls
            self.status_message = f"{name} Tower selected (${cls.cost}).\nClick the map to place."
        else:
            self.status_message = f"Not enough money for {name}!\nNeed ${cls.cost}, have ${self.money}."
            self.selected_tower_name = self.selected_tower_class = None

    def _deselect_tower(self):
        self.selected_tower_name = self.selected_tower_class = None
        self.status_message = "Select a tower to place."

    def _restart(self):
        """Reset all game state for a new game."""
        self.money, self.lives, self.score, self.kills = 200, 20, 0, 0
        self.current_wave = 0
        self.game_over = self.game_won = self.wave_active = self.paused = False
        self.wave_cleared = False
        self.wave_cleared_timer = 0
        self.towers, self.enemies, self.projectiles = [], [], []
        self.floating_texts, self.particles = [], []
        self.wave = None
        self.selected_tower_name = self.selected_tower_class = None
        self.status_message = "Press SPACE to start wave 1."

    def _placement_is_valid(self, x, y, cls):
        if self.money < cls.cost:
            return False, f"Need ${cls.cost}, have ${self.money}."
        if is_on_path(x, y):
            return False, "Can't place on the path!"
        temp = GameObject(x, y, size=18)
        for t in self.towers:
            if temp.collides_with(GameObject(t.x, t.y, size=18)):
                return False, "A tower is already there!"
        if not (20 < x < GAME_AREA_WIDTH-20 and 20 < y < SCREEN_HEIGHT-20):
            return False, "Outside the map!"
        return True, ""

    def _try_place_tower(self, x, y):
        cls = self.selected_tower_class
        valid, reason = self._placement_is_valid(x, y, cls)
        if not valid:
            self.status_message = reason; return
        self.towers.append(cls(x, y))
        self.money -= cls.cost
        self.floating_texts.append(FloatingText(x, y-20, f"-${cls.cost}", (255,150,150), 14))
        self.status_message = f"{cls.tower_name} Tower placed!\n${self.money} remaining."
        if self.money < cls.cost:
            self._deselect_tower()

    def _start_wave(self):
        if self.wave_active:
            self.status_message = "Wave already in progress!"; return
        if self.current_wave >= self.total_waves:
            self.status_message = "All waves completed!"; return
        self.wave = Wave(self.current_wave, WAYPOINTS)
        self.current_wave += 1
        self.wave_active = True
        self.status_message = f"Wave {self.current_wave} incoming!"

    # --- TOWER AND PROJECTILE LOGIC ---
    def _update_towers(self, dt):
        for tower in self.towers:
            tower.update_timer(dt)
            if isinstance(tower, FreezeTower):
                tower.apply_slow(self.enemies); continue
            target = tower.find_target(self.enemies)
            if target is None: continue
            if tower.can_fire():
                if isinstance(tower, BombTower):
                    p = BombProjectile(tower.x, tower.y, target, tower.damage,
                                       tower.blast_radius, self.enemies, speed=6, color=(255,100,50))
                else:
                    p = Projectile(tower.x, tower.y, target, tower.damage, speed=8, color=(255,255,100))
                self.projectiles.append(p)
                tower.reset_timer()

    def _update_projectiles(self):
        for p in self.projectiles: p.move()
        self.projectiles = [p for p in self.projectiles if p.alive]

    def _update_effects(self, dt):
        for ft in self.floating_texts: ft.update(dt)
        self.floating_texts = [ft for ft in self.floating_texts if ft.alive]
        for p in self.particles: p.update(dt)
        self.particles = [p for p in self.particles if p.alive]

    # --- EVENTS ---
    def _handle_click(self, mx, my):
        if self.game_over: return
        for btn in self.tower_buttons:
            if btn["rect"].collidepoint(mx, my):
                self._select_tower(btn["name"]); return
        if self.cancel_rect.collidepoint(mx, my):
            self._deselect_tower(); return
        if mx < GAME_AREA_WIDTH:
            if self.selected_tower_class is None:
                self.status_message = "Select a tower first!"
            else:
                self._try_place_tower(mx, my)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT: self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q: self.running = False
                if event.key == pygame.K_r and self.game_over:
                    self._restart()
                if event.key == pygame.K_p and not self.game_over:
                    self.paused = not self.paused
                    self.status_message = "PAUSED. Press P to resume." if self.paused else "Resumed!"
                if event.key == pygame.K_SPACE and not self.game_over and not self.paused:
                    self.wave_cleared = False
                    self._start_wave()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.game_over and hasattr(self, 'restart_rect') and self.restart_rect.collidepoint(event.pos):
                    self._restart()
                else:
                    self._handle_click(*event.pos)

    # --- UPDATE ---
    def update(self):
        dt_ms = self.clock.get_time()
        dt = dt_ms / 1000.0
        self._update_effects(dt)
        self.frame_count += 1

        # Tick down the wave cleared banner timer
        if self.wave_cleared:
            self.wave_cleared_timer -= dt
            if self.wave_cleared_timer <= 0:
                self.wave_cleared = False

        if self.game_over or self.paused: return

        # Spawn enemies
        if self.wave and not self.wave.is_complete():
            e = self.wave.update(dt_ms)
            if e: self.enemies.append(e)

        # Restore speeds, update towers, move enemies and projectiles
        for e in self.enemies: e.speed = e.original_speed
        self._update_towers(dt)
        for e in self.enemies: e.move()
        self._update_projectiles()

        # Enemies reaching exit
        for e in self.enemies[:]:
            if e.reached_end:
                self.lives -= 1; self.enemies.remove(e)
                self.floating_texts.append(FloatingText(e.x-30, e.y, "-1 LIFE", (255,80,80), 16))

        # Dead enemies
        for e in self.enemies[:]:
            if e.is_dead():
                self.money += e.reward; self.score += e.reward; self.kills += 1
                self.enemies.remove(e)
                self.floating_texts.append(FloatingText(e.x, e.y-15, f"+${e.reward}", MONEY_GREEN, 15))
                for _ in range(8):
                    self.particles.append(Particle(e.x, e.y, e.color))

        # Wave complete check
        if self.wave_active and self.wave and self.wave.is_complete() and not self.enemies:
            self.wave_active = False
            if self.current_wave >= self.total_waves:
                self.status_message = "All waves cleared! You win!"
                self.game_over = self.game_won = True
            else:
                self.wave_cleared = True
                self.wave_cleared_timer = 3.0
                self.status_message = f"Wave {self.current_wave} cleared!\nPress SPACE for wave {self.current_wave+1}."

        # Lose check
        if self.lives <= 0:
            self.lives = 0; self.game_over = True; self.game_won = False
            self.status_message = "Game Over! You ran out of lives."

    def draw_wave_cleared(self):
        """Draw a banner showing the wave was cleared."""
        cx = GAME_AREA_WIDTH // 2
        cy = SCREEN_HEIGHT // 2

        # Semi-transparent banner background
        banner_w, banner_h = 400, 150
        banner = pygame.Surface((banner_w, banner_h), pygame.SRCALPHA)
        banner.fill((0, 0, 0, 160))
        pygame.draw.rect(banner, GOLD, (0, 0, banner_w, banner_h), 3, border_radius=10)
        self.screen.blit(banner, (cx - banner_w//2, cy - banner_h//2))

        # Wave cleared text
        t1 = self.font_large.render(f"WAVE {self.current_wave} CLEARED!", True, GOLD)
        self.screen.blit(t1, t1.get_rect(center=(cx, cy - 35)))

        # Stats for this wave
        t2 = self.font_med.render(f"Score: {self.score}  |  Kills: {self.kills}", True, WHITE)
        self.screen.blit(t2, t2.get_rect(center=(cx, cy + 5)))

        # Next wave prompt (blinking)
        if int(self.frame_count * 0.05) % 2 == 0:
            t3 = self.font_sm.render(f"Press SPACE to start wave {self.current_wave + 1}", True, LIGHT_GRAY)
            self.screen.blit(t3, t3.get_rect(center=(cx, cy + 40)))

    # --- DRAW ---
    def draw(self):
        self.draw_map()
        self.draw_towers()
        self.draw_enemies()
        self.draw_projectiles()
        self.draw_effects()
        self.draw_side_panel()
        if self.wave_cleared: self.draw_wave_cleared()
        if self.game_over: self.draw_game_over()
        if self.paused: self.draw_paused()
        pygame.display.flip()

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        pygame.quit()
        sys.exit()


def main():
    game = Game()
    game.run()

if __name__ == "__main__":
    main()