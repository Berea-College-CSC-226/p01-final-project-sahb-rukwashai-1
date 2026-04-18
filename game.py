"""
Path of No Return: A Tower Defense Game

Authors: Bhushan Sah, Daniel Rukwasha
"""

import pygame
import sys
import math
from path_data import WAYPOINTS, SPAWN_POINT, EXIT_POINT, PATH_WIDTH, GAME_AREA_WIDTH
from game_object import GameObject
from towers import ArrowTower, BombTower, FreezeTower, TOWER_TYPES


SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
SIDE_PANEL_WIDTH = SCREEN_WIDTH - GAME_AREA_WIDTH
FPS = 60

# Path collision buffer
PATH_BUFFER = 30

# Colors
GRASS_GREEN = (34, 139, 34)
PATH_COLOR = (139, 119, 101)
PATH_BORDER_COLOR = (100, 80, 60)
PANEL_BG = (40, 40, 50)
PANEL_BORDER = (80, 80, 100)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GOLD = (255, 215, 0)
RED = (220, 50, 50)
GRAY = (150, 150, 150)
LIGHT_GRAY = (200, 200, 200)
DARK_GREEN = (20, 100, 20)
SELECTED_BORDER = (255, 221, 87)


# ---------------------------------------------------------------------------
# PATH HELPERS (used by placement validation)
# ---------------------------------------------------------------------------
def _point_segment_distance(px, py, ax, ay, bx, by):
    """
    Calculate shortest distance from point (px, py) to line segment
    (ax, ay)-(bx, by).

    :param px: point x
    :param py: point y
    :param ax: segment start x
    :param ay: segment start y
    :param bx: segment end x
    :param by: segment end y
    :return: float distance
    """
    dx, dy = bx - ax, by - ay
    if dx == 0 and dy == 0:
        return math.sqrt((px - ax) ** 2 + (py - ay) ** 2)
    t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)))
    nearest_x = ax + t * dx
    nearest_y = ay + t * dy
    return math.sqrt((px - nearest_x) ** 2 + (py - nearest_y) ** 2)


def is_on_path(x, y):
    """
    Check if a point (x, y) is too close to any path segment.

    :param x: x-coordinate to check
    :param y: y-coordinate to check
    :return: True if point is on the path
    """
    half_width = PATH_WIDTH / 2 + PATH_BUFFER
    for i in range(len(WAYPOINTS) - 1):
        ax, ay = WAYPOINTS[i]
        bx, by = WAYPOINTS[i + 1]
        if _point_segment_distance(x, y, ax, ay, bx, by) < half_width:
            return True
    return False


class Game:
    """
    Main game class. Handles window setup, map rendering,
    side panel, tower selection and placement, and the game loop.
    """

    def __init__(self):
        """
        Initialize Pygame, create the game window, and set up initial game state.
        """
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Path of No Return: A Tower Defense Game")
        self.clock = pygame.time.Clock()
        self.running = True

        # Game state
        self.money = 200
        self.lives = 20
        self.score = 0
        self.current_wave = 0
        self.total_waves = 5

        # Lists to track game objects
        self.towers = []
        self.enemies = []
        self.projectiles = []

        # Tower selection state
        self.selected_tower_name = None
        self.selected_tower_class = None

        # Status message for the side panel
        self.status_message = "Select a tower to place."

        # Path data
        self.waypoints = WAYPOINTS
        self.spawn_point = SPAWN_POINT
        self.exit_point = EXIT_POINT

        # Fonts
        self.font_large = pygame.font.SysFont("Arial", 28, bold=True)
        self.font_medium = pygame.font.SysFont("Arial", 20)
        self.font_small = pygame.font.SysFont("Arial", 16)
        self.font_tiny = pygame.font.SysFont("Arial", 13)

        # Build tower button rects for click detection
        self._build_tower_buttons()

    def _build_tower_buttons(self):
        """
        Create clickable button rectangles for each tower type.
        Called once during init.
        """
        self.tower_buttons = []
        x = GAME_AREA_WIDTH + 15
        y = 305
        btn_w = SIDE_PANEL_WIDTH - 30
        btn_h = 50

        tower_info = [
            ("Arrow", ArrowTower, (100, 200, 100)),
            ("Bomb", BombTower, (200, 100, 100)),
            ("Freeze", FreezeTower, (100, 150, 200)),
        ]

        for name, cls, color in tower_info:
            rect = pygame.Rect(x, y, btn_w, btn_h)
            self.tower_buttons.append({
                "name": name,
                "class": cls,
                "color": color,
                "rect": rect,
            })
            y += btn_h + 10

        # Cancel button rect
        self.cancel_rect = pygame.Rect(x, y + 5, btn_w, 30)

    def draw_map(self):
        """
        Draw the game background and the enemy path.
        """
        game_area = pygame.Rect(0, 0, GAME_AREA_WIDTH, SCREEN_HEIGHT)
        pygame.draw.rect(self.screen, GRASS_GREEN, game_area)

        # Grass texture
        for x in range(0, GAME_AREA_WIDTH, 40):
            for y in range(0, SCREEN_HEIGHT, 40):
                if (x + y) % 80 == 0:
                    patch = pygame.Rect(x, y, 20, 20)
                    pygame.draw.rect(self.screen, DARK_GREEN, patch)

        # Path border
        if len(self.waypoints) > 1:
            pygame.draw.lines(self.screen, PATH_BORDER_COLOR, False,
                              self.waypoints, PATH_WIDTH + 6)

        # Main path
        if len(self.waypoints) > 1:
            pygame.draw.lines(self.screen, PATH_COLOR, False,
                              self.waypoints, PATH_WIDTH)

        # Smooth corners
        for wp in self.waypoints:
            pygame.draw.circle(self.screen, PATH_COLOR, wp, PATH_WIDTH // 2)
            pygame.draw.circle(self.screen, PATH_BORDER_COLOR, wp,
                               PATH_WIDTH // 2 + 3, 3)

        # Spawn marker
        pygame.draw.circle(self.screen, RED,
                           (self.waypoints[1][0], self.waypoints[1][1]), 10)
        spawn_label = self.font_small.render("SPAWN", True, WHITE)
        self.screen.blit(spawn_label,
                         (self.waypoints[1][0] - 25, self.waypoints[1][1] - 25))

        # Exit marker
        exit_wp = self.waypoints[-2]
        pygame.draw.circle(self.screen, GOLD, (exit_wp[0], exit_wp[1]), 10)
        exit_label = self.font_small.render("EXIT", True, WHITE)
        self.screen.blit(exit_label, (exit_wp[0] - 15, exit_wp[1] - 25))

    def draw_towers(self):
        """
        Draw all placed towers on the map.
        If a tower type is selected, show range circles on hover.
        """
        for tower in self.towers:
            tower.render(self.screen)

        # Show range preview where the mouse is if a tower is selected
        if self.selected_tower_class is not None:
            mx, my = pygame.mouse.get_pos()
            if mx < GAME_AREA_WIDTH:
                cls = self.selected_tower_class
                range_surface = pygame.Surface(
                    (cls.tower_range * 2, cls.tower_range * 2), pygame.SRCALPHA
                )
                pygame.draw.circle(
                    range_surface, (100, 200, 255, 40),
                    (cls.tower_range, cls.tower_range), cls.tower_range
                )
                pygame.draw.circle(
                    range_surface, (100, 200, 255, 100),
                    (cls.tower_range, cls.tower_range), cls.tower_range, 2
                )
                self.screen.blit(range_surface,
                                 (mx - cls.tower_range, my - cls.tower_range))

    def draw_side_panel(self):
        """
        Draw the side panel with player stats, tower buttons, and status.
        """
        # Panel background
        panel_rect = pygame.Rect(GAME_AREA_WIDTH, 0, SIDE_PANEL_WIDTH, SCREEN_HEIGHT)
        pygame.draw.rect(self.screen, PANEL_BG, panel_rect)
        pygame.draw.line(self.screen, PANEL_BORDER, (GAME_AREA_WIDTH, 0),
                         (GAME_AREA_WIDTH, SCREEN_HEIGHT), 3)

        x = GAME_AREA_WIDTH + 15
        y = 20

        # Title
        title = self.font_large.render("TOWER DEFENSE", True, GOLD)
        self.screen.blit(title, (x, y))
        y += 45

        # Divider
        pygame.draw.line(self.screen, PANEL_BORDER, (x, y),
                         (SCREEN_WIDTH - 15, y), 2)
        y += 15

        # Stats
        stats_label = self.font_medium.render("--- STATS ---", True, LIGHT_GRAY)
        self.screen.blit(stats_label, (x + 30, y))
        y += 30

        money_text = self.font_medium.render(f"Money: ${self.money}", True, GOLD)
        self.screen.blit(money_text, (x, y))
        y += 28

        lives_text = self.font_medium.render(f"Lives: {self.lives}", True, RED)
        self.screen.blit(lives_text, (x, y))
        y += 28

        score_text = self.font_medium.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (x, y))
        y += 28

        wave_text = self.font_medium.render(
            f"Wave: {self.current_wave}/{self.total_waves}", True, WHITE)
        self.screen.blit(wave_text, (x, y))
        y += 40

        # Divider
        pygame.draw.line(self.screen, PANEL_BORDER, (x, y),
                         (SCREEN_WIDTH - 15, y), 2)
        y += 15

        # Tower header
        tower_label = self.font_medium.render("--- TOWERS ---", True, LIGHT_GRAY)
        self.screen.blit(tower_label, (x + 25, y))
        y += 35

        # Tower buttons
        mouse_pos = pygame.mouse.get_pos()

        for btn in self.tower_buttons:
            rect = btn["rect"]
            is_selected = (btn["name"] == self.selected_tower_name)
            is_hovered = rect.collidepoint(mouse_pos)

            # Button color (lighten on hover)
            bg_color = btn["color"]
            if is_hovered:
                bg_color = tuple(min(c + 30, 255) for c in bg_color)

            pygame.draw.rect(self.screen, bg_color, rect, border_radius=5)

            # Border (gold if selected, white otherwise)
            if is_selected:
                pygame.draw.rect(self.screen, SELECTED_BORDER, rect, 3,
                                 border_radius=5)
            else:
                pygame.draw.rect(self.screen, WHITE, rect, 2, border_radius=5)

            # Button text
            name_text = self.font_small.render(
                f"{btn['name']} Tower", True, WHITE)
            cost_text = self.font_small.render(
                f"${btn['class'].cost}", True, GOLD)
            self.screen.blit(name_text, (rect.x + 10, rect.y + 8))
            self.screen.blit(cost_text, (rect.x + 10, rect.y + 28))

        # Cancel button
        cancel_hovered = self.cancel_rect.collidepoint(mouse_pos)
        cancel_color = (100, 100, 100) if cancel_hovered else (70, 70, 70)
        pygame.draw.rect(self.screen, cancel_color, self.cancel_rect,
                         border_radius=4)
        cancel_text = self.font_tiny.render("Cancel selection", True, WHITE)
        cancel_text_rect = cancel_text.get_rect(center=self.cancel_rect.center)
        self.screen.blit(cancel_text, cancel_text_rect)

        # Divider
        div_y = self.cancel_rect.bottom + 15
        pygame.draw.line(self.screen, PANEL_BORDER, (x, div_y),
                         (SCREEN_WIDTH - 15, div_y), 2)

        # Status message
        status_y = div_y + 10
        for line in self.status_message.split("\n"):
            status_text = self.font_tiny.render(line, True, SELECTED_BORDER)
            self.screen.blit(status_text, (x, status_y))
            status_y += 18

        # Controls
        controls_y = SCREEN_HEIGHT - 100
        pygame.draw.line(self.screen, PANEL_BORDER, (x, controls_y - 10),
                         (SCREEN_WIDTH - 15, controls_y - 10), 2)

        ctrl_label = self.font_medium.render("--- CONTROLS ---", True, LIGHT_GRAY)
        self.screen.blit(ctrl_label, (x + 15, controls_y))
        controls_y += 25

        controls = [
            "Click map to place tower",
            "Press SPACE to start wave",
            "Press P to pause",
            "Press Q to quit",
        ]
        for line in controls:
            ctrl_text = self.font_tiny.render(line, True, GRAY)
            self.screen.blit(ctrl_text, (x, controls_y))
            controls_y += 16

    # -----------------------------------------------------------------------
    # TOWER SELECTION (Issue II.A)
    # -----------------------------------------------------------------------
    def _select_tower(self, name):
        """
        Select a tower type for placement.

        :param name: string name of the tower type
        """
        cls = TOWER_TYPES[name]
        if self.money >= cls.cost:
            self.selected_tower_name = name
            self.selected_tower_class = cls
            self.status_message = (f"{name} Tower selected (${cls.cost}).\n"
                                   f"Click the map to place.")
        else:
            self.status_message = (f"Not enough money for {name} Tower!\n"
                                   f"Need ${cls.cost}, have ${self.money}.")
            self.selected_tower_name = None
            self.selected_tower_class = None

    def _deselect_tower(self):
        """Clear the current tower selection."""
        self.selected_tower_name = None
        self.selected_tower_class = None
        self.status_message = "Select a tower to place."

    # -----------------------------------------------------------------------
    # PLACEMENT VALIDATION (Issue II.C)
    # -----------------------------------------------------------------------
    def _placement_is_valid(self, x, y, cls):
        """
        Check if a tower can be placed at (x, y).

        :param x: x-coordinate
        :param y: y-coordinate
        :param cls: tower class to place
        :return: tuple (bool valid, string reason)
        """
        # Check money
        if self.money < cls.cost:
            return False, f"Not enough money! Need ${cls.cost}, have ${self.money}."

        # Check path collision
        if is_on_path(x, y):
            return False, "Can't place on the path!"

        # Check existing tower collision
        temp = GameObject(x, y, size=18)
        for t in self.towers:
            tower_obj = GameObject(t.x, t.y, size=18)
            if temp.collides_with(tower_obj):
                return False, "A tower is already there!"

        # Check map bounds
        if not (20 < x < GAME_AREA_WIDTH - 20 and 20 < y < SCREEN_HEIGHT - 20):
            return False, "That's outside the map!"

        return True, ""

    # -----------------------------------------------------------------------
    # PLACE TOWER (Issue II.D)
    # -----------------------------------------------------------------------
    def _try_place_tower(self, x, y):
        """
        Validate and place a tower at (x, y).

        :param x: click x-coordinate
        :param y: click y-coordinate
        """
        cls = self.selected_tower_class
        valid, reason = self._placement_is_valid(x, y, cls)

        if not valid:
            self.status_message = reason
            return

        # Place the tower
        tower = cls(x, y)
        self.towers.append(tower)

        # Subtract cost
        self.money -= cls.cost

        self.status_message = (f"{cls.tower_name} Tower placed!\n"
                               f"${cls.cost} spent. ${self.money} remaining.")

        # Check if player can still afford this tower type
        if self.money < cls.cost:
            self.status_message += (f"\nCan't afford another {cls.tower_name}.")
            self._deselect_tower()

    # -----------------------------------------------------------------------
    # CLICK HANDLING (Issue II.B)
    # -----------------------------------------------------------------------
    def _handle_click(self, mx, my):
        """
        Route a mouse click to the correct handler.

        :param mx: mouse x-coordinate
        :param my: mouse y-coordinate
        """
        # Check tower buttons
        for btn in self.tower_buttons:
            if btn["rect"].collidepoint(mx, my):
                self._select_tower(btn["name"])
                return

        # Check cancel button
        if self.cancel_rect.collidepoint(mx, my):
            self._deselect_tower()
            return

        # Check game area (tower placement)
        if mx < GAME_AREA_WIDTH:
            if self.selected_tower_class is None:
                self.status_message = "Select a tower first!"
            else:
                self._try_place_tower(mx, my)

    def handle_events(self):
        """
        Handle Pygame events: quit, key presses, mouse clicks.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    self.running = False

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self._handle_click(*event.pos)

    def update(self):
        """
        Update game state each frame.
        Will be expanded with enemies, projectiles, etc.
        """
        pass

    def draw(self):
        """
        Draw everything to the screen.
        """
        self.draw_map()
        self.draw_towers()
        self.draw_side_panel()
        pygame.display.flip()

    def run(self):
        """
        Main game loop. Handles events, updates state, and draws each frame.
        """
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()


def main():
    """
    Entry point for the game.
    """
    game = Game()
    game.run()


if __name__ == "__main__":
    main()