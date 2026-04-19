"""
Wave system for the tower defense game.
Defines wave data and handles spawning enemies with delays.

Authors: Bhushan Sah, Daniel Rukwasha
"""

import pygame
from enemies import Enemy, FastEnemy, TankEnemy


# Map enemy type strings to their classes
ENEMY_TYPES = {
    "normal": Enemy,
    "fast": FastEnemy,
    "tank": TankEnemy,
}

# ---------------------------------------------------------------------------
# III.A - WAVE DEFINITIONS
# ---------------------------------------------------------------------------
# Each wave is a list of tuples: (enemy_type_string, delay_in_ms)
# delay_in_ms is how long to wait BEFORE spawning that enemy.
WAVE_DATA = [
    # Wave 1: easy intro, just normal enemies
    [
        ("normal", 1000),
        ("normal", 1000),
        ("normal", 1000),
        ("normal", 1000),
        ("normal", 1000),
    ],
    # Wave 2: mix of normal and fast
    [
        ("normal", 800),
        ("fast", 600),
        ("normal", 800),
        ("fast", 600),
        ("fast", 600),
        ("normal", 800),
    ],
    # Wave 3: first tank appears
    [
        ("fast", 500),
        ("fast", 500),
        ("normal", 700),
        ("tank", 1500),
        ("fast", 500),
        ("normal", 700),
        ("fast", 500),
    ],
    # Wave 4: heavier mix
    [
        ("tank", 1200),
        ("fast", 400),
        ("fast", 400),
        ("normal", 600),
        ("tank", 1200),
        ("fast", 400),
        ("normal", 600),
        ("fast", 400),
        ("fast", 400),
    ],
    # Wave 5: final wave, everything at once
    [
        ("tank", 1000),
        ("fast", 300),
        ("fast", 300),
        ("tank", 1000),
        ("normal", 500),
        ("fast", 300),
        ("fast", 300),
        ("normal", 500),
        ("tank", 800),
        ("fast", 300),
        ("fast", 300),
        ("tank", 800),
    ],
]


class Wave:
    """
    Manages spawning enemies for a single wave.
    Pops enemies from the wave data one at a time with delays between them.
    """

    def __init__(self, wave_number, waypoints):
        """
        Initialize a wave from the WAVE_DATA list.

        :param wave_number: which wave this is (0-indexed)
        :param waypoints: list of (x, y) path waypoints for enemy movement
        """
        self.wave_number = wave_number
        self.waypoints = waypoints

        # Copy the wave data so we can pop from it without modifying the original
        if wave_number < len(WAVE_DATA):
            self.spawn_queue = list(WAVE_DATA[wave_number])
        else:
            self.spawn_queue = []

        self.spawn_timer = 0        # time until next enemy spawns (in ms)
        self.waiting = True         # waiting for the first delay before spawning
        self.started = False        # has the wave begun spawning
        self.all_spawned = False    # have all enemies been pushed out

        # Load the first delay
        if len(self.spawn_queue) > 0:
            self.spawn_timer = self.spawn_queue[0][1]
            self.started = True
        else:
            self.all_spawned = True

    def update(self, dt_ms):
        """
        Update the spawn timer. Returns a new Enemy if one should spawn
        this frame, otherwise returns None.

        :param dt_ms: time elapsed since last frame in milliseconds
        :return: Enemy object or None
        """
        if self.all_spawned or not self.started:
            return None

        self.spawn_timer -= dt_ms

        if self.spawn_timer <= 0:
            # Time to spawn the next enemy
            enemy_type_str, _ = self.spawn_queue.pop(0)
            enemy_class = ENEMY_TYPES.get(enemy_type_str, Enemy)
            new_enemy = enemy_class(self.waypoints)

            # Load the next delay, or mark wave as fully spawned
            if len(self.spawn_queue) > 0:
                self.spawn_timer = self.spawn_queue[0][1]
            else:
                self.all_spawned = True

            return new_enemy

        return None

    def is_complete(self):
        """
        Check if all enemies in this wave have been spawned.

        :return: True if no more enemies to spawn
        """
        return self.all_spawned

    def __repr__(self):
        remaining = len(self.spawn_queue)
        return f"Wave {self.wave_number + 1} ({remaining} enemies remaining)"