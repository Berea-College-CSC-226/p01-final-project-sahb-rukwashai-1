"""
Tower classes for the tower defense game.
Includes base Tower and subclasses: ArrowTower, BombTower, FreezeTower.

Authors: Bhushan Sah, Daniel Rukwasha
"""

import math
import pygame
from game_object import GameObject


class Tower(GameObject):
    """
    Base tower class. Draws as a colored square on the map.
    Subclasses set their own damage, range, fire_rate, and cost.
    """

    tower_name = "Tower"
    damage = 0
    tower_range = 0
    fire_rate = 1.0
    cost = 0
    color = (128, 128, 128)         # fill color
    outline_color = (200, 200, 200) # border color

    def __init__(self, x, y):
        """
        Initialize a tower at the given position.

        :param x: x-coordinate on screen
        :param y: y-coordinate on screen
        """
        super().__init__(x, y, size=18)
        self.target = None
        self._fire_timer = 0.0

    def find_target(self, enemies):
        """
        Find the closest enemy within range.

        :param enemies: list of Enemy objects currently on the map
        :return: closest Enemy in range, or None
        """
        closest = None
        closest_dist = float("inf")

        for enemy in enemies:
            dist = self.distance_to(enemy)
            if dist <= self.tower_range and dist < closest_dist:
                closest = enemy
                closest_dist = dist

        self.target = closest
        return closest

    def can_fire(self):
        """
        Check if enough time has passed since the last shot.

        :return: True if the tower is ready to fire
        """
        return self._fire_timer <= 0

    def update_timer(self, dt):
        """
        Decrease the fire cooldown timer by dt seconds.

        :param dt: time elapsed since last frame in seconds
        """
        if self._fire_timer > 0:
            self._fire_timer -= dt

    def reset_timer(self):
        """Reset the fire cooldown after shooting."""
        self._fire_timer = self.fire_rate

    def render(self, screen):
        """
        Draw the tower as a colored square with its first letter in the center.

        :param screen: Pygame surface to draw on
        """
        # Tower body
        rect = pygame.Rect(
            self.x - self.size, self.y - self.size,
            self.size * 2, self.size * 2
        )
        pygame.draw.rect(screen, self.color, rect, border_radius=4)
        pygame.draw.rect(screen, self.outline_color, rect, 2, border_radius=4)

        # First letter label
        font = pygame.font.SysFont("Arial", 14, bold=True)
        label = font.render(self.tower_name[0], True, (255, 255, 255))
        label_rect = label.get_rect(center=(self.x, self.y))
        screen.blit(label, label_rect)

    def draw_range(self, screen):
        """
        Draw a translucent circle showing this tower's attack range.
        Useful for showing the player where a tower can reach.

        :param screen: Pygame surface to draw on
        """
        range_surface = pygame.Surface(
            (self.tower_range * 2, self.tower_range * 2), pygame.SRCALPHA
        )
        pygame.draw.circle(
            range_surface, (100, 200, 255, 50),
            (self.tower_range, self.tower_range), self.tower_range
        )
        pygame.draw.circle(
            range_surface, (100, 200, 255, 120),
            (self.tower_range, self.tower_range), self.tower_range, 2
        )
        screen.blit(range_surface,
                     (self.x - self.tower_range, self.y - self.tower_range))

    def __repr__(self):
        return f"{self.tower_name}({self.x:.0f}, {self.y:.0f})"


class ArrowTower(Tower):
    """Fast-firing single target tower. Cheap and reliable."""

    tower_name = "Arrow"
    damage = 25
    tower_range = 150
    fire_rate = 1.0
    cost = 50
    color = (100, 200, 100)         # matches the green button in game.py
    outline_color = (140, 230, 140)


class BombTower(Tower):
    """Slow-firing area damage tower. Expensive but hits multiple enemies."""

    tower_name = "Bomb"
    damage = 40
    tower_range = 100
    fire_rate = 2.0
    cost = 100
    color = (200, 100, 100)         # matches the red button in game.py
    outline_color = (230, 140, 140)
    blast_radius = 60


class FreezeTower(Tower):
    """Slows enemies within range. Deals no damage."""

    tower_name = "Freeze"
    damage = 0
    tower_range = 120
    fire_rate = 0.0
    cost = 75
    color = (100, 150, 200)         # matches the blue button in game.py
    outline_color = (140, 190, 230)
    slow_amount = 0.5

    def apply_slow(self, enemies):
        """
        Slow every enemy currently within range by the slow_amount multiplier.

        :param enemies: list of Enemy objects
        """
        for enemy in enemies:
            if self.distance_to(enemy) <= self.tower_range:
                enemy.speed *= self.slow_amount


# Map tower name strings to their classes (used by the UI)
TOWER_TYPES = {
    "Arrow": ArrowTower,
    "Bomb": BombTower,
    "Freeze": FreezeTower,
}