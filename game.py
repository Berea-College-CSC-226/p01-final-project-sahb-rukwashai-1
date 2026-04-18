"""
Path of No Return: A Tower Defense Game

Authors: Bhushan Sah, Daniel Rukwasha
"""

import pygame
import sys
from path_data import WAYPOINTS, SPAWN_POINT, EXIT_POINT, PATH_WIDTH


SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
GAME_AREA_WIDTH = 750
SIDE_PANEL_WIDTH = SCREEN_WIDTH - GAME_AREA_WIDTH
FPS = 60

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


class Game:
    """
    Main game class. Handles window setup, map rendering,
    and the side panel display.
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

        # Path data
        self.waypoints = WAYPOINTS
        self.spawn_point = SPAWN_POINT
        self.exit_point = EXIT_POINT

        # Fonts
        self.font_large = pygame.font.SysFont("Arial", 28, bold=True)
        self.font_medium = pygame.font.SysFont("Arial", 20)
        self.font_small = pygame.font.SysFont("Arial", 16)

    def draw_map(self):
        """
        Draw the game background and the enemy path.
        """
        game_area = pygame.Rect(0, 0, GAME_AREA_WIDTH, SCREEN_HEIGHT)
        pygame.draw.rect(self.screen, GRASS_GREEN, game_area)

        # Draw some grass texture (darker patches)
        for x in range(0, GAME_AREA_WIDTH, 40):
            for y in range(0, SCREEN_HEIGHT, 40):
                if (x + y) % 80 == 0:
                    patch = pygame.Rect(x, y, 20, 20)
                    pygame.draw.rect(self.screen, DARK_GREEN, patch)

        # Draw the path border
        if len(self.waypoints) > 1:
            pygame.draw.lines(self.screen, PATH_BORDER_COLOR, False, self.waypoints, PATH_WIDTH + 6)

        # Draw the main path
        if len(self.waypoints) > 1:
            pygame.draw.lines(self.screen, PATH_COLOR, False, self.waypoints, PATH_WIDTH)

        # Draw circles at each waypoint to smooth the corners
        for wp in self.waypoints:
            pygame.draw.circle(self.screen, PATH_COLOR, wp, PATH_WIDTH // 2)
            pygame.draw.circle(self.screen, PATH_BORDER_COLOR, wp, PATH_WIDTH // 2 + 3, 3)

        # Draw spawn and exit markers
        pygame.draw.circle(self.screen, RED, (self.waypoints[1][0], self.waypoints[1][1]), 10)
        spawn_label = self.font_small.render("SPAWN", True, WHITE)
        self.screen.blit(spawn_label, (self.waypoints[1][0] - 25, self.waypoints[1][1] - 25))

        exit_wp = self.waypoints[-2]
        pygame.draw.circle(self.screen, GOLD, (exit_wp[0], exit_wp[1]), 10)
        exit_label = self.font_small.render("EXIT", True, WHITE)
        self.screen.blit(exit_label, (exit_wp[0] - 15, exit_wp[1] - 25))

    def draw_side_panel(self):
        """
        Draw the side panel with player stats and tower selection buttons.
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

        # Divider line
        pygame.draw.line(self.screen, PANEL_BORDER, (x, y), (SCREEN_WIDTH - 15, y), 2)
        y += 15

        # Player stats
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

        wave_text = self.font_medium.render(f"Wave: {self.current_wave}/{self.total_waves}", True, WHITE)
        self.screen.blit(wave_text, (x, y))
        y += 40

        # Divider line
        pygame.draw.line(self.screen, PANEL_BORDER, (x, y), (SCREEN_WIDTH - 15, y), 2)
        y += 15

        # Tower selection header
        tower_label = self.font_medium.render("--- TOWERS ---", True, LIGHT_GRAY)
        self.screen.blit(tower_label, (x + 25, y))
        y += 35

        # Tower buttons (placeholders, will be interactive later)
        tower_info = [
            ("Arrow Tower", "$50", (100, 200, 100)),
            ("Bomb Tower", "$100", (200, 100, 100)),
            ("Freeze Tower", "$75", (100, 150, 200)),
        ]

        for tower_name, cost, color in tower_info:
            btn_rect = pygame.Rect(x, y, SIDE_PANEL_WIDTH - 30, 50)
            pygame.draw.rect(self.screen, color, btn_rect, border_radius=5)
            pygame.draw.rect(self.screen, WHITE, btn_rect, 2, border_radius=5)

            name_text = self.font_small.render(tower_name, True, WHITE)
            cost_text = self.font_small.render(cost, True, GOLD)
            self.screen.blit(name_text, (x + 10, y + 8))
            self.screen.blit(cost_text, (x + 10, y + 28))

            y += 60

        y += 20

        # Divider line
        pygame.draw.line(self.screen, PANEL_BORDER, (x, y), (SCREEN_WIDTH - 15, y), 2)
        y += 15

        # Instructions
        instructions = [
            "Click map to place tower",
            "Press SPACE to start wave",
            "Press P to pause",
            "Press Q to quit",
        ]
        inst_label = self.font_medium.render("--- CONTROLS ---", True, LIGHT_GRAY)
        self.screen.blit(inst_label, (x + 15, y))
        y += 30

        for line in instructions:
            inst_text = self.font_small.render(line, True, GRAY)
            self.screen.blit(inst_text, (x, y))
            y += 22

    def handle_events(self):
        """
        Handle Pygame events like quitting.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    self.running = False

    def update(self):
        """
        Update game state each frame.
        Will be expanded as we add enemies, towers, and projectiles.
        """
        pass

    def draw(self):
        """
        Draw everything to the screen.
        """
        self.draw_map()
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