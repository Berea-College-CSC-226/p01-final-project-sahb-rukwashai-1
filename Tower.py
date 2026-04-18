"""
Path of No Return: A Tower Defense Game
CSC226 Final Project

Authors: Bhushan Sah, Daniel Rukwasha

This file implements:
  II.A  - Tower selection buttons in the Tkinter side panel
  II.B  - Click listener on the map canvas after selecting a tower
  II.C  - Valid placement check (not on path, not on tower, enough money)
  II.D  - Subtract cost and place the tower on a valid click
"""

import turtle
import tkinter as tk
import math


# ---------------------------------------------------------------------------
# PATH DEFINITION
# ---------------------------------------------------------------------------
# Waypoints are (x, y) coordinates in Turtle space.
# The path goes: left edge → across → down → across → down → right edge
# Feel free to adjust these to reshape the winding path.
PATH_WAYPOINTS = [
    (-380, 200),
    (-150, 200),
    (-150,  50),
    ( 100,  50),
    ( 100, -150),
    ( 350, -150),
]

PATH_WIDTH = 40          # visual width of the drawn path (pixels)
PATH_BUFFER = 30         # extra collision margin so towers can't sit on the edge


# ---------------------------------------------------------------------------
# BASE CLASS
# ---------------------------------------------------------------------------
class GameObject:
    """Base class for every object that lives on the game map."""

    def __init__(self, x: float, y: float, size: float = 20):
        self.x = x
        self.y = y
        self.size = size

    def distance_to(self, other: "GameObject") -> float:
        """Euclidean distance to another GameObject."""
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)

    def collides_with(self, other: "GameObject") -> bool:
        """True if the two objects overlap (circle collision)."""
        return self.distance_to(other) < (self.size + other.size)

    def render(self, pen: turtle.Turtle):
        """Subclasses override this to draw themselves."""
        raise NotImplementedError


# ---------------------------------------------------------------------------
# TOWER HIERARCHY  (II.A data – types, costs, colours)
# ---------------------------------------------------------------------------
class Tower(GameObject):
    """Abstract tower. Subclasses set damage, range, fire_rate, cost."""

    # Subclasses fill these in
    tower_name  = "Tower"
    damage      = 0
    tower_range = 0
    fire_rate   = 1.0
    cost        = 0
    color       = "gray"

    def __init__(self, x: float, y: float):
        super().__init__(x, y, size=18)
        self.target     = None
        self._fire_timer = 0.0

    # -- rendering -----------------------------------------------------------
    def render(self, pen: turtle.Turtle):
        """Draw a coloured square with the tower initial centred on (x, y)."""
        pen.penup()
        pen.goto(self.x - self.size, self.y - self.size)
        pen.pendown()
        pen.fillcolor(self.color)
        pen.begin_fill()
        for _ in range(4):
            pen.forward(self.size * 2)
            pen.left(90)
        pen.end_fill()
        pen.penup()

        # Tower label
        pen.goto(self.x, self.y - 6)
        pen.color("white")
        pen.write(self.tower_name[0], align="center",
                  font=("Arial", 10, "bold"))
        pen.color("black")

    # -- range circle (drawn when selected) ----------------------------------
    def draw_range(self, pen: turtle.Turtle):
        pen.penup()
        pen.goto(self.x, self.y - self.tower_range)
        pen.pendown()
        pen.pencolor("lightblue")
        pen.circle(self.tower_range)
        pen.penup()
        pen.pencolor("black")

    def __repr__(self):
        return f"{self.tower_name}({self.x:.0f}, {self.y:.0f})"


class ArrowTower(Tower):
    tower_name  = "Arrow"
    damage      = 25
    tower_range = 150
    fire_rate   = 1.0
    cost        = 50
    color       = "forest green"


class BombTower(Tower):
    tower_name   = "Bomb"
    damage       = 40
    tower_range  = 100
    fire_rate    = 2.0
    cost         = 100
    color        = "firebrick"
    blast_radius = 60


class FreezeTower(Tower):
    tower_name   = "Freeze"
    damage       = 0
    tower_range  = 120
    fire_rate    = 0.0
    cost         = 75
    color        = "steel blue"
    slow_amount  = 0.5          # multiplier applied to enemy speed

    def apply_slow(self, enemies):
        """Slow every enemy currently within range."""
        for enemy in enemies:
            dist = math.sqrt((self.x - enemy.x) ** 2 + (self.y - enemy.y) ** 2)
            if dist <= self.tower_range:
                enemy.speed *= self.slow_amount   # caller should restore later


# Map tower-type strings to their classes (used by the UI buttons)
TOWER_TYPES = {
    "Arrow":  ArrowTower,
    "Bomb":   BombTower,
    "Freeze": FreezeTower,
}


# ---------------------------------------------------------------------------
# PATH HELPERS  (used by II.C validation)
# ---------------------------------------------------------------------------
def _point_segment_distance(px, py, ax, ay, bx, by) -> float:
    """Shortest distance from point (px,py) to line segment (ax,ay)-(bx,by)."""
    dx, dy = bx - ax, by - ay
    if dx == 0 and dy == 0:
        return math.sqrt((px - ax) ** 2 + (py - ay) ** 2)
    t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)))
    nearest_x = ax + t * dx
    nearest_y = ay + t * dy
    return math.sqrt((px - nearest_x) ** 2 + (py - nearest_y) ** 2)


def is_on_path(x: float, y: float, waypoints=PATH_WAYPOINTS,
               half_width: float = PATH_WIDTH / 2 + PATH_BUFFER) -> bool:
    """Return True if (x, y) is too close to any path segment."""
    for i in range(len(waypoints) - 1):
        ax, ay = waypoints[i]
        bx, by = waypoints[i + 1]
        if _point_segment_distance(x, y, ax, ay, bx, by) < half_width:
            return True
    return False


# ---------------------------------------------------------------------------
# GAME  – main controller
# ---------------------------------------------------------------------------
class Game:
    """
    Sets up the Turtle window + Tkinter side panel, wires up all
    interaction, and owns the game state.
    """

    STARTING_MONEY = 300
    STARTING_LIVES = 20
    MAP_WIDTH      = 800
    MAP_HEIGHT     = 500
    PANEL_WIDTH    = 220

    def __init__(self):
        # ---- game state ----------------------------------------------------
        self.money            = self.STARTING_MONEY
        self.lives            = self.STARTING_LIVES
        self.score            = 0
        self.towers: list[Tower]   = []
        self.selected_tower_type   = None   # class (ArrowTower etc.) or None

        # ---- build UI -------------------------------------------------------
        self._build_window()
        self._build_side_panel()
        self._draw_map()

        # ---- II.B: bind canvas click ONCE; handler decides what to do ------
        self.screen.onclick(self._on_map_click)

    # -----------------------------------------------------------------------
    # WINDOW + TURTLE SETUP
    # -----------------------------------------------------------------------
    def _build_window(self):
        """Create the root Tk window, embed a Turtle canvas on the left."""
        self.root = tk.Tk()
        self.root.title("Path of No Return – Tower Defense")
        self.root.resizable(False, False)

        # Left frame: Turtle canvas
        canvas_frame = tk.Frame(self.root)
        canvas_frame.pack(side=tk.LEFT)

        self.canvas = tk.Canvas(canvas_frame,
                                width=self.MAP_WIDTH,
                                height=self.MAP_HEIGHT)
        self.canvas.pack()

        # Wire turtle into our canvas
        self.screen = turtle.TurtleScreen(self.canvas)
        self.screen.bgcolor("darkgreen")
        self.screen.tracer(0)   # manual updates only

        # Drawing pen
        self.pen = turtle.RawTurtle(self.screen)
        self.pen.hideturtle()
        self.pen.speed(0)
        self.pen.penup()

    # -----------------------------------------------------------------------
    # II.A – SIDE PANEL WITH TOWER BUTTONS
    # -----------------------------------------------------------------------
    def _build_side_panel(self):
        """Build the right-hand Tkinter panel with stats and tower buttons."""
        panel = tk.Frame(self.root, width=self.PANEL_WIDTH,
                         bg="#2b2b2b", padx=10, pady=10)
        panel.pack(side=tk.RIGHT, fill=tk.Y)
        panel.pack_propagate(False)

        # ---- Stats display -------------------------------------------------
        tk.Label(panel, text="PATH OF NO RETURN", bg="#2b2b2b",
                 fg="gold", font=("Arial", 13, "bold"),
                 wraplength=200).pack(pady=(0, 10))

        stats_frame = tk.Frame(panel, bg="#2b2b2b")
        stats_frame.pack(fill=tk.X, pady=5)

        self.money_var = tk.StringVar(value=f"💰 Money: ${self.money}")
        self.lives_var = tk.StringVar(value=f"❤️  Lives: {self.lives}")
        self.score_var = tk.StringVar(value=f"⭐ Score: {self.score}")

        for var in (self.money_var, self.lives_var, self.score_var):
            tk.Label(stats_frame, textvariable=var, bg="#2b2b2b",
                     fg="white", font=("Arial", 11), anchor="w").pack(
                fill=tk.X, pady=2)

        tk.Frame(panel, bg="#555", height=1).pack(fill=tk.X, pady=8)

        # ---- Tower buttons (II.A) -----------------------------------------
        tk.Label(panel, text="Select a Tower", bg="#2b2b2b",
                 fg="lightgray", font=("Arial", 10, "italic")).pack(pady=(0, 6))

        self._tower_buttons: dict[str, tk.Button] = {}

        tower_info = [
            ("Arrow",  ArrowTower,  "#4a7c59", "Single target\nFast fire rate"),
            ("Bomb",   BombTower,   "#8b3a3a", "Area splash\nSlow fire rate"),
            ("Freeze", FreezeTower, "#3a6b8b", "Slows enemies\nNo damage"),
        ]

        for name, cls, bg_color, description in tower_info:
            frame = tk.Frame(panel, bg="#3c3c3c", bd=1, relief=tk.RAISED)
            frame.pack(fill=tk.X, pady=4)

            btn = tk.Button(
                frame,
                text=f"{name} Tower  ${cls.cost}",
                bg=bg_color, fg="white",
                font=("Arial", 11, "bold"),
                activebackground="#ffdd57",
                activeforeground="black",
                relief=tk.FLAT,
                cursor="hand2",
                command=lambda n=name: self._select_tower(n),
            )
            btn.pack(fill=tk.X, ipady=4)

            tk.Label(frame, text=description, bg="#3c3c3c", fg="#aaa",
                     font=("Arial", 8), justify=tk.LEFT).pack(
                anchor="w", padx=6, pady=2)

            self._tower_buttons[name] = btn

        # ---- Cancel / deselect button --------------------------------------
        tk.Button(panel, text="✕  Cancel selection",
                  bg="#555", fg="white", font=("Arial", 9),
                  relief=tk.FLAT, cursor="hand2",
                  command=self._deselect_tower).pack(fill=tk.X, pady=(8, 0))

        # ---- Status message ------------------------------------------------
        tk.Frame(panel, bg="#555", height=1).pack(fill=tk.X, pady=8)
        self.status_var = tk.StringVar(value="Select a tower to place.")
        tk.Label(panel, textvariable=self.status_var, bg="#2b2b2b",
                 fg="#ffdd57", font=("Arial", 9, "italic"),
                 wraplength=190, justify=tk.LEFT).pack(anchor="w")

    # -----------------------------------------------------------------------
    # MAP DRAWING
    # -----------------------------------------------------------------------
    def _draw_map(self):
        """Draw the background path using the global waypoints list."""
        p = self.pen

        # Draw path segments
        p.pensize(PATH_WIDTH)
        p.pencolor("#c8a96e")   # sandy/dirt colour
        p.penup()
        p.goto(PATH_WAYPOINTS[0])
        p.pendown()
        for wx, wy in PATH_WAYPOINTS[1:]:
            p.goto(wx, wy)
        p.penup()

        # Draw start/end markers
        for label, (wx, wy), col in [
            ("START", PATH_WAYPOINTS[0],  "limegreen"),
            ("END",   PATH_WAYPOINTS[-1], "red"),
        ]:
            p.goto(wx, wy)
            p.pencolor(col)
            p.dot(30)
            p.pencolor("white")
            p.goto(wx, wy - 5)
            p.write(label, align="center", font=("Arial", 8, "bold"))
            p.pencolor("black")

        self.screen.update()

    # -----------------------------------------------------------------------
    # II.A helper – highlight selected button
    # -----------------------------------------------------------------------
    def _select_tower(self, name: str):
        """Mark name as selected; highlight its button, dim the others."""
        self.selected_tower_type = TOWER_TYPES[name]

        for btn_name, btn in self._tower_buttons.items():
            if btn_name == name:
                btn.config(relief=tk.SUNKEN, bd=3,
                           highlightbackground="gold",
                           highlightthickness=2)
            else:
                btn.config(relief=tk.FLAT, bd=0)

        cls = TOWER_TYPES[name]
        if self.money >= cls.cost:
            self.status_var.set(
                f"{name} Tower selected (${cls.cost}).\nClick the map to place.")
        else:
            self.status_var.set(
                f"Not enough money for {name} Tower (${cls.cost})!")
            self.selected_tower_type = None   # can't afford it – don't select

    def _deselect_tower(self):
        """Clear the current selection."""
        self.selected_tower_type = None
        for btn in self._tower_buttons.values():
            btn.config(relief=tk.FLAT, bd=0)
        self.status_var.set("Select a tower to place.")

    # -----------------------------------------------------------------------
    # II.B – MAP CLICK LISTENER
    # -----------------------------------------------------------------------
    def _on_map_click(self, x: float, y: float):
        """
        Called by turtle whenever the player clicks the canvas.
        Only acts if a tower type is currently selected.
        """
        if self.selected_tower_type is None:
            self.status_var.set("Select a tower first!")
            return

        self._try_place_tower(x, y)

    # -----------------------------------------------------------------------
    # II.C – VALIDATION
    # -----------------------------------------------------------------------
    def _placement_is_valid(self, x: float, y: float, cls) -> tuple[bool, str]:
        """
        Return (True, "") if the spot is valid, or (False, reason) if not.

        Checks:
          1. Player has enough money.
          2. Click is not on the path.
          3. Click is not on top of an existing tower.
          4. Click is within the map bounds (with a small margin).
        """
        # 1 – money check
        if self.money < cls.cost:
            return False, f"Not enough money! Need ${cls.cost}, have ${self.money}."

        # 2 – path collision
        if is_on_path(x, y):
            return False, "Can't place a tower on the path!"

        # 3 – existing tower collision
        temp = GameObject(x, y, size=18)
        for t in self.towers:
            tower_obj = GameObject(t.x, t.y, size=18)
            if temp.collides_with(tower_obj):
                return False, "A tower is already there!"

        # 4 – map bounds  (Turtle coords: ±MAP/2 roughly, with margin)
        half_w = self.MAP_WIDTH  / 2 - 20
        half_h = self.MAP_HEIGHT / 2 - 20
        if not (-half_w < x < half_w and -half_h < y < half_h):
            return False, "That's outside the map!"

        return True, ""

    # -----------------------------------------------------------------------
    # II.D – PLACE THE TOWER
    # -----------------------------------------------------------------------
    def _try_place_tower(self, x: float, y: float):
        """Validate the click; if valid, subtract cost and place the tower."""
        cls = self.selected_tower_type
        valid, reason = self._placement_is_valid(x, y, cls)

        if not valid:
            self.status_var.set(f"❌ {reason}")
            return

        # --- place it -------------------------------------------------------
        tower = cls(x, y)
        self.towers.append(tower)

        # II.D – subtract cost
        self.money -= cls.cost
        self._update_stats()

        # Render the new tower immediately
        tower.render(self.pen)
        self.screen.update()

        self.status_var.set(
            f"✅ {cls.tower_name} Tower placed! "
            f"${cls.cost} spent. ${self.money} remaining.")

        # Keep the same tower type selected so the player can place more,
        # but re-check affordability.
        if self.money < cls.cost:
            self.status_var.set(
                self.status_var.get() +
                f"\n(Can't afford another {cls.tower_name} Tower.)")
            self._deselect_tower()

    # -----------------------------------------------------------------------
    # STATS REFRESH
    # -----------------------------------------------------------------------
    def _update_stats(self):
        self.money_var.set(f"💰 Money: ${self.money}")
        self.lives_var.set(f"❤️  Lives: {self.lives}")
        self.score_var.set(f"⭐ Score: {self.score}")

    # -----------------------------------------------------------------------
    # MAIN LOOP
    # -----------------------------------------------------------------------
    def run(self):
        """Hand control to Tkinter's event loop."""
        self.root.mainloop()


# ---------------------------------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    game = Game()
    game.run()