"""
Projectile class for the tower defense game.
Projectiles are created by towers and travel toward enemy targets.

Authors: Bhushan Sah, Daniel Rukwasha
"""

import math
import pygame
from game_object import GameObject


class Projectile(GameObject):
    """
    A projectile fired by a tower at an enemy.
    Moves toward its target each frame and deals damage on hit.
    """

    def __init__(self, x, y, target, damage, speed=8, color=(255, 255, 100)):
        """
        Initialize a projectile at the tower's position aimed at a target.

        :param x: starting x-coordinate (tower position)
        :param y: starting y-coordinate (tower position)
        :param target: the Enemy object this projectile is tracking
        :param damage: how much damage to deal on hit
        :param speed: how fast the projectile moves per frame
        :param color: RGB tuple for the projectile color
        """
        super().__init__(x, y, size=5)
        self.target = target
        self.damage = damage
        self.speed = speed
        self.color = color
        self.alive = True

    def move(self):
        """
        Move the projectile toward the target's current position.
        If the target is dead or gone, mark this projectile as dead.
        """
        if not self.alive:
            return

        # If target is already dead or reached the end, remove projectile
        if self.target is None or not self.target.alive or self.target.reached_end:
            self.alive = False
            return

        # Calculate direction toward the target
        dx = self.target.x - self.x
        dy = self.target.y - self.y
        dist = math.sqrt(dx * dx + dy * dy)

        # Check if projectile has reached the target
        if dist <= self.speed + self.target.size:
            self.hit()
            return

        # Move toward the target
        self.x += (dx / dist) * self.speed
        self.y += (dy / dist) * self.speed

    def hit(self):
        """
        Deal damage to the target and mark this projectile as dead.
        """
        if self.target is not None and self.target.alive:
            self.target.take_damage(self.damage)
        self.alive = False

    def render(self, screen):
        """
        Draw the projectile as a small colored circle.

        :param screen: Pygame surface to draw on
        """
        if not self.alive:
            return

        pygame.draw.circle(screen, self.color,
                           (int(self.x), int(self.y)), self.size)
        pygame.draw.circle(screen, (255, 255, 255),
                           (int(self.x), int(self.y)), self.size, 1)

    def __repr__(self):
        return f"Projectile(pos=({self.x:.0f},{self.y:.0f}), dmg={self.damage})"


class BombProjectile(Projectile):
    """
    A projectile fired by BombTower. On hit, deals area damage
    to all enemies within the blast radius.
    """

    def __init__(self, x, y, target, damage, blast_radius, enemies_list,
                 speed=6, color=(255, 100, 50)):
        """
        Initialize a bomb projectile.

        :param x: starting x-coordinate
        :param y: starting y-coordinate
        :param target: the Enemy this projectile is aimed at
        :param damage: damage dealt to each enemy in blast radius
        :param blast_radius: how far the explosion reaches
        :param enemies_list: reference to the game's enemy list for splash damage
        :param speed: how fast the projectile moves
        :param color: RGB tuple for the projectile color
        """
        super().__init__(x, y, target, damage, speed, color)
        self.blast_radius = blast_radius
        self.enemies_list = enemies_list
        self.size = 7  # slightly bigger than normal projectile

    def hit(self):
        """
        Explode on impact. Deal damage to all enemies within blast_radius
        of the target's position.
        """
        if self.target is None:
            self.alive = False
            return

        # Deal splash damage to all enemies near the impact point
        impact_x = self.target.x
        impact_y = self.target.y

        for enemy in self.enemies_list:
            if not enemy.alive:
                continue
            dist = math.sqrt((enemy.x - impact_x) ** 2 +
                             (enemy.y - impact_y) ** 2)
            if dist <= self.blast_radius:
                enemy.take_damage(self.damage)

        self.alive = False