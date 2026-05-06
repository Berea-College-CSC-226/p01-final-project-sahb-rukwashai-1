"""
Tower classes for the tower defense game.
Includes base Tower and subclasses: ArrowTower, BombTower, FreezeTower.
Each tower type has a unique visual design.

Authors: Bhushan Sah, Daniel Rukwasha
"""

import math
import pygame
from game_object import GameObject


class Tower(GameObject):
    """
    Base tower class. Subclasses set their own stats and override render
    for unique visuals.
    """

    tower_name = "Tower"
    damage = 0
    tower_range = 0
    fire_rate = 1.0
    cost = 0
    color = (128, 128, 128)
    outline_color = (200, 200, 200)

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
        Draw the tower. Base version draws a simple square.
        Subclasses override for unique designs.

        :param screen: Pygame surface to draw on
        """
        rect = pygame.Rect(
            self.x - self.size, self.y - self.size,
            self.size * 2, self.size * 2
        )
        pygame.draw.rect(screen, self.color, rect, border_radius=4)
        pygame.draw.rect(screen, self.outline_color, rect, 2, border_radius=4)

    def draw_range(self, screen):
        """
        Draw a translucent circle showing this tower's attack range.

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
    """Fast-firing single target tower. Drawn as a pointed turret shape."""

    tower_name = "Arrow"
    damage = 25
    tower_range = 150
    fire_rate = 1.0
    cost = 50
    color = (74, 140, 74)
    outline_color = (100, 200, 100)

    def render(self, screen):
        """
        Draw the ArrowTower as a green base with a pointed turret.

        :param screen: Pygame surface to draw on
        """
        cx, cy = int(self.x), int(self.y)
        s = self.size

        # Base platform (dark circle)
        pygame.draw.circle(screen, (50, 90, 50), (cx, cy), s)
        pygame.draw.circle(screen, (30, 60, 30), (cx, cy), s, 2)

        # Inner tower body (lighter square)
        inner = pygame.Rect(cx - s // 2, cy - s // 2, s, s)
        pygame.draw.rect(screen, self.color, inner, border_radius=3)
        pygame.draw.rect(screen, self.outline_color, inner, 2, border_radius=3)

        # Arrow tip pointing up (triangle)
        tip_points = [
            (cx, cy - s - 4),       # top point
            (cx - s // 2, cy - 4),  # bottom left
            (cx + s // 2, cy - 4),  # bottom right
        ]
        pygame.draw.polygon(screen, (140, 220, 140), tip_points)
        pygame.draw.polygon(screen, self.outline_color, tip_points, 2)

        # Center dot
        pygame.draw.circle(screen, (200, 255, 200), (cx, cy), 4)
        pygame.draw.circle(screen, self.outline_color, (cx, cy), 4, 1)

        # Barrel line pointing at target if one exists
        if self.target is not None and self.target.alive:
            dx = self.target.x - self.x
            dy = self.target.y - self.y
            dist = math.sqrt(dx * dx + dy * dy)
            if dist > 0:
                end_x = cx + int((dx / dist) * (s + 6))
                end_y = cy + int((dy / dist) * (s + 6))
                pygame.draw.line(screen, (200, 255, 200),
                                 (cx, cy), (end_x, end_y), 3)


class BombTower(Tower):
    """Slow-firing area damage tower. Drawn as a stocky red turret."""

    tower_name = "Bomb"
    damage = 40
    tower_range = 100
    fire_rate = 2.0
    cost = 100
    color = (160, 50, 50)
    outline_color = (220, 100, 100)
    blast_radius = 60

    def render(self, screen):
        """
        Draw the BombTower as a red base with a wide cannon.

        :param screen: Pygame surface to draw on
        """
        cx, cy = int(self.x), int(self.y)
        s = self.size

        # Base platform (dark circle)
        pygame.draw.circle(screen, (90, 30, 30), (cx, cy), s)
        pygame.draw.circle(screen, (60, 20, 20), (cx, cy), s, 2)

        # Inner tower body (octagon-like shape using a thick rect)
        body = pygame.Rect(cx - s // 2 - 2, cy - s // 2 - 2, s + 4, s + 4)
        pygame.draw.rect(screen, self.color, body, border_radius=6)
        pygame.draw.rect(screen, self.outline_color, body, 2, border_radius=6)

        # Bomb symbol (small circle with a fuse line)
        pygame.draw.circle(screen, (40, 40, 40), (cx, cy), 7)
        pygame.draw.circle(screen, (255, 200, 50), (cx, cy), 7, 2)

        # Fuse spark
        pygame.draw.circle(screen, (255, 255, 100), (cx + 5, cy - 6), 3)

        # Warning stripes on corners
        for dx_off, dy_off in [(-s + 3, -s + 3), (s - 6, -s + 3),
                                (-s + 3, s - 6), (s - 6, s - 6)]:
            stripe_rect = pygame.Rect(cx + dx_off, cy + dy_off, 4, 4)
            pygame.draw.rect(screen, (255, 200, 50), stripe_rect)


class FreezeTower(Tower):
    """Slows enemies within range. Drawn as a blue crystal tower."""

    tower_name = "Freeze"
    damage = 0
    tower_range = 120
    fire_rate = 0.0
    cost = 75
    color = (50, 100, 160)
    outline_color = (100, 180, 230)
    slow_amount = 0.5

    def apply_slow(self, enemies):
        """
        Slow every enemy currently within range by the slow_amount multiplier.

        :param enemies: list of Enemy objects
        """
        for enemy in enemies:
            if self.distance_to(enemy) <= self.tower_range:
                enemy.speed *= self.slow_amount

    def render(self, screen):
        """
        Draw the FreezeTower as a blue crystal with ice spikes.

        :param screen: Pygame surface to draw on
        """
        cx, cy = int(self.x), int(self.y)
        s = self.size

        # Frost aura (pulsing circle effect)
        aura_surface = pygame.Surface((s * 4, s * 4), pygame.SRCALPHA)
        pygame.draw.circle(aura_surface, (100, 180, 255, 30),
                           (s * 2, s * 2), s + 8)
        screen.blit(aura_surface, (cx - s * 2, cy - s * 2))

        # Base platform (icy blue circle)
        pygame.draw.circle(screen, (40, 80, 130), (cx, cy), s)
        pygame.draw.circle(screen, (30, 60, 100), (cx, cy), s, 2)

        # Diamond/crystal shape in the center
        diamond_points = [
            (cx, cy - s + 2),    # top
            (cx + s - 4, cy),    # right
            (cx, cy + s - 2),    # bottom
            (cx - s + 4, cy),    # left
        ]
        pygame.draw.polygon(screen, self.color, diamond_points)
        pygame.draw.polygon(screen, self.outline_color, diamond_points, 2)

        # Inner crystal highlight
        inner_diamond = [
            (cx, cy - 6),
            (cx + 6, cy),
            (cx, cy + 6),
            (cx - 6, cy),
        ]
        pygame.draw.polygon(screen, (120, 200, 255), inner_diamond)
        pygame.draw.polygon(screen, (180, 230, 255), inner_diamond, 1)

        # Ice spike lines radiating out
        spike_length = 6
        for angle in [0, 60, 120, 180, 240, 300]:
            rad = math.radians(angle)
            start_x = cx + int(math.cos(rad) * (s - 4))
            start_y = cy + int(math.sin(rad) * (s - 4))
            end_x = cx + int(math.cos(rad) * (s + spike_length))
            end_y = cy + int(math.sin(rad) * (s + spike_length))
            pygame.draw.line(screen, (180, 220, 255),
                             (start_x, start_y), (end_x, end_y), 2)

    def draw_range(self, screen):
        """
        Draw range with a frosty blue tint instead of the default blue.

        :param screen: Pygame surface to draw on
        """
        range_surface = pygame.Surface(
            (self.tower_range * 2, self.tower_range * 2), pygame.SRCALPHA
        )
        pygame.draw.circle(
            range_surface, (100, 200, 255, 35),
            (self.tower_range, self.tower_range), self.tower_range
        )
        pygame.draw.circle(
            range_surface, (150, 220, 255, 80),
            (self.tower_range, self.tower_range), self.tower_range, 2
        )
        screen.blit(range_surface,
                     (self.x - self.tower_range, self.y - self.tower_range))


# Map tower name strings to their classes (used by the UI)
TOWER_TYPES = {
    "Arrow": ArrowTower,
    "Bomb": BombTower,
    "Freeze": FreezeTower,
}