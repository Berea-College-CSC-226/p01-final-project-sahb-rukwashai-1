"""
Test suite for Path of No Return: A Tower Defense Game
Tests game logic: distance, collision, path validation, towers, enemies, waves, projectiles.

Authors: Bhushan Sah, Daniel Rukwasha
"""

import sys
import math
from inspect import getframeinfo, stack
import pygame
pygame.init()
pygame.display.set_mode((1, 1))  # minimal display so pygame doesn't crash

from game_object import GameObject
from towers import Tower, ArrowTower, BombTower, FreezeTower, TOWER_TYPES
from enemies import Enemy, FastEnemy, TankEnemy
from waves import Wave, WAVE_DATA
from projectiles import Projectile, BombProjectile
from path_data import WAYPOINTS, PATH_WIDTH
from game import is_on_path, _point_seg_dist


# TEST HELPER

def unittest(did_pass):
    """
    Print the result of a unit test.

    :param did_pass: a boolean representing the test
    :return: None
    """
    caller = getframeinfo(stack()[1][0])
    linenum = caller.lineno
    if did_pass:
        msg = "Test at line {0} ok.".format(linenum)
    else:
        msg = "Test at line {0} FAILED.".format(linenum)
    print(msg)


# GAMEOBJECT TESTS
def test_game_object():
    """Test GameObject position, distance, and collision."""
    print("\n--- Testing GameObject ---")

    # Test initialization
    obj1 = GameObject(100, 200, size=20)
    unittest(obj1.x == 100)
    unittest(obj1.y == 200)
    unittest(obj1.size == 20)

    # Test default size
    obj2 = GameObject(0, 0)
    unittest(obj2.size == 20)

    # Test distance_to with known values
    obj_a = GameObject(0, 0)
    obj_b = GameObject(3, 4)
    unittest(obj_a.distance_to(obj_b) == 5.0)

    # Test distance_to with same position
    obj_c = GameObject(50, 50)
    obj_d = GameObject(50, 50)
    unittest(obj_c.distance_to(obj_d) == 0.0)

    # Test collides_with (overlapping)
    obj_e = GameObject(100, 100, size=20)
    obj_f = GameObject(110, 100, size=20)  # 10 apart, sizes total 40
    unittest(obj_e.collides_with(obj_f) == True)

    # Test collides_with (not overlapping)
    obj_g = GameObject(100, 100, size=10)
    obj_h = GameObject(200, 200, size=10)  # far apart
    unittest(obj_g.collides_with(obj_h) == False)

    # Test collides_with (exactly touching)
    obj_i = GameObject(0, 0, size=10)
    obj_j = GameObject(20, 0, size=10)  # distance = 20, sizes total = 20
    unittest(obj_i.collides_with(obj_j) == False)  # not less than, equal

# TOWER TESTS
def test_towers():
    """Test tower attributes, targeting, and fire timer."""
    print("\n--- Testing Towers ---")

    # Test ArrowTower attributes
    arrow = ArrowTower(100, 100)
    unittest(arrow.tower_name == "Arrow")
    unittest(arrow.damage == 25)
    unittest(arrow.tower_range == 150)
    unittest(arrow.fire_rate == 1.0)
    unittest(arrow.cost == 50)
    unittest(arrow.x == 100)
    unittest(arrow.y == 100)

    # Test BombTower attributes
    bomb = BombTower(200, 200)
    unittest(bomb.tower_name == "Bomb")
    unittest(bomb.damage == 40)
    unittest(bomb.cost == 100)
    unittest(bomb.blast_radius == 60)

    # Test FreezeTower attributes
    freeze = FreezeTower(300, 300)
    unittest(freeze.tower_name == "Freeze")
    unittest(freeze.damage == 0)
    unittest(freeze.cost == 75)
    unittest(freeze.slow_amount == 0.5)

    # Test TOWER_TYPES dictionary
    unittest("Arrow" in TOWER_TYPES)
    unittest("Bomb" in TOWER_TYPES)
    unittest("Freeze" in TOWER_TYPES)
    unittest(TOWER_TYPES["Arrow"] == ArrowTower)

    # Test fire timer
    arrow2 = ArrowTower(0, 0)
    unittest(arrow2.can_fire() == True)

    arrow2.reset_timer()
    unittest(arrow2.can_fire() == False)

    arrow2.update_timer(0.5)
    unittest(arrow2.can_fire() == False)

    arrow2.update_timer(0.6)
    unittest(arrow2.can_fire() == True)

    # Test find_target with no enemies
    arrow3 = ArrowTower(100, 100)
    result = arrow3.find_target([])
    unittest(result is None)

    # Test find_target with enemy in range
    arrow4 = ArrowTower(100, 100)
    enemy_near = Enemy([(100, 200), (100, 300)])
    result = arrow4.find_target([enemy_near])
    unittest(result == enemy_near)

    # Test find_target with enemy out of range
    arrow5 = ArrowTower(100, 100)
    enemy_far = Enemy([(500, 500), (600, 600)])
    result = arrow5.find_target([enemy_far])
    unittest(result is None)

    # Test find_target picks closest enemy
    arrow6 = ArrowTower(100, 100)
    enemy_close = Enemy([(120, 100), (200, 100)])
    enemy_medium = Enemy([(200, 100), (300, 100)])
    result = arrow6.find_target([enemy_medium, enemy_close])
    unittest(result == enemy_close)


# ENEMY TESTS
def test_enemies():
    """Test enemy attributes, movement, and damage."""
    print("\n--- Testing Enemies ---")

    # Test basic enemy initialization
    waypoints = [(0, 0), (100, 0), (100, 100)]
    enemy = Enemy(waypoints)
    unittest(enemy.x == 0)
    unittest(enemy.y == 0)
    unittest(enemy.health == 100)
    unittest(enemy.alive == True)
    unittest(enemy.reached_end == False)
    unittest(enemy.current_waypoint_index == 1)

    # Test FastEnemy attributes
    fast = FastEnemy(waypoints)
    unittest(fast.max_health == 50)
    unittest(fast.speed == 4.0)
    unittest(fast.reward == 10)

    # Test TankEnemy attributes
    tank = TankEnemy(waypoints)
    unittest(tank.max_health == 200)
    unittest(tank.speed == 1.0)
    unittest(tank.reward == 30)

    # Test take_damage
    enemy2 = Enemy([(0, 0), (100, 0)])
    enemy2.take_damage(30)
    unittest(enemy2.health == 70)
    unittest(enemy2.alive == True)

    # Test take_damage kills enemy
    enemy3 = Enemy([(0, 0), (100, 0)])
    enemy3.take_damage(100)
    unittest(enemy3.health == 0)
    unittest(enemy3.alive == False)
    unittest(enemy3.is_dead() == True)

    # Test overkill damage
    enemy4 = Enemy([(0, 0), (100, 0)])
    enemy4.take_damage(999)
    unittest(enemy4.health == 0)
    unittest(enemy4.is_dead() == True)

    # Test movement toward waypoint
    simple_path = [(0, 0), (100, 0)]
    enemy5 = Enemy(simple_path)
    enemy5.speed = 10
    old_x = enemy5.x
    enemy5.move()
    unittest(enemy5.x > old_x)
    unittest(enemy5.y == 0)

    # Test enemy reaches end
    short_path = [(0, 0), (5, 0)]
    enemy6 = Enemy(short_path)
    enemy6.speed = 10
    enemy6.move()
    unittest(enemy6.reached_end == True)

    # Test dead enemy does not move
    enemy7 = Enemy([(0, 0), (100, 0)])
    enemy7.take_damage(100)
    old_x = enemy7.x
    enemy7.move()
    unittest(enemy7.x == old_x)

# WAVE TESTS
def test_waves():
    """Test wave data and spawning logic."""
    print("\n--- Testing Waves ---")

    # Test WAVE_DATA exists and has waves
    unittest(len(WAVE_DATA) > 0)
    unittest(len(WAVE_DATA) == 5)

    # Test wave 1 has enemies
    unittest(len(WAVE_DATA[0]) > 0)

    # Test wave data format (each entry is a tuple of string and int)
    for enemy_type, delay in WAVE_DATA[0]:
        unittest(isinstance(enemy_type, str))
        unittest(isinstance(delay, int))

    # Test Wave initialization
    wave = Wave(0, WAYPOINTS)
    unittest(wave.wave_number == 0)
    unittest(wave.started == True)
    unittest(wave.all_spawned == False)
    unittest(wave.is_complete() == False)

    # Test spawning with enough time passed
    wave2 = Wave(0, WAYPOINTS)
    result = wave2.update(2000)
    unittest(result is not None)
    unittest(isinstance(result, Enemy))

    # Test spawning with not enough time
    wave3 = Wave(0, WAYPOINTS)
    result = wave3.update(100)
    unittest(result is None)

    # Test wave completes after all enemies spawned
    wave4 = Wave(0, WAYPOINTS)
    spawned_count = 0
    for _ in range(100):  # run many updates
        result = wave4.update(500)
        if result is not None:
            spawned_count += 1
        if wave4.is_complete():
            break
    unittest(wave4.is_complete() == True)
    unittest(spawned_count == len(WAVE_DATA[0]))

    # Test invalid wave number
    wave5 = Wave(999, WAYPOINTS)
    unittest(wave5.is_complete() == True)

# PROJECTILE TESTS
def test_projectiles():
    """Test projectile movement and damage."""
    print("\n--- Testing Projectiles ---")

    # Create a target enemy
    target = Enemy([(200, 0), (300, 0)])

    # Test projectile initialization
    proj = Projectile(0, 0, target, damage=25, speed=8)
    unittest(proj.x == 0)
    unittest(proj.y == 0)
    unittest(proj.damage == 25)
    unittest(proj.alive == True)
    unittest(proj.target == target)

    # Test projectile moves toward target
    proj2 = Projectile(0, 0, target, damage=25, speed=10)
    old_x = proj2.x
    proj2.move()
    unittest(proj2.x > old_x)

    # Test projectile hits target when close enough
    close_target = Enemy([(10, 0), (100, 0)])
    proj3 = Projectile(0, 0, close_target, damage=25, speed=50)
    proj3.move()
    unittest(proj3.alive == False)
    unittest(close_target.health < close_target.max_health)

    # Test projectile dies if target is dead
    dead_target = Enemy([(200, 0), (300, 0)])
    dead_target.take_damage(999)
    proj4 = Projectile(0, 0, dead_target, damage=25)
    proj4.move()
    unittest(proj4.alive == False)

    # Test projectile dies if target reached end
    end_target = Enemy([(5, 0), (6, 0)])
    end_target.speed = 100
    end_target.move()
    proj5 = Projectile(0, 0, end_target, damage=25)
    proj5.move()
    unittest(proj5.alive == False)

    # Test BombProjectile splash damage
    enemy_a = Enemy([(100, 0), (200, 0)])
    enemy_b = Enemy([(120, 0), (200, 0)])
    enemy_c = Enemy([(500, 0), (600, 0)])
    enemies = [enemy_a, enemy_b, enemy_c]

    bomb = BombProjectile(95, 0, enemy_a, damage=40, blast_radius=60,
                          enemies_list=enemies, speed=100)
    bomb.move()

    unittest(enemy_a.health < enemy_a.max_health)
    unittest(enemy_b.health < enemy_b.max_health)
    unittest(enemy_c.health == enemy_c.max_health)

# PATH VALIDATION TESTS
def test_path_validation():
    """Test path collision detection for tower placement."""
    print("\n--- Testing Path Validation ---")

    # Test point directly on a waypoint
    wp = WAYPOINTS[1]  # first visible waypoint
    unittest(is_on_path(wp[0], wp[1]) == True)

    # Test point on the path between two waypoints
    mid_x = (WAYPOINTS[1][0] + WAYPOINTS[2][0]) / 2
    mid_y = (WAYPOINTS[1][1] + WAYPOINTS[2][1]) / 2
    unittest(is_on_path(mid_x, mid_y) == True)

    # Test point far from the path
    unittest(is_on_path(700, 650) == False)

    unittest(is_on_path(100 + 60, 150) == False)

    # Test _point_segment_distance with simple cases
    # Point directly on the segment
    dist = _point_seg_dist(5, 0, 0, 0, 10, 0)
    unittest(dist == 0.0)

    # Point perpendicular to segment
    dist = _point_seg_dist(5, 3, 0, 0, 10, 0)
    unittest(dist == 3.0)

    # Point at segment endpoint
    dist = _point_seg_dist(0, 0, 0, 0, 10, 0)
    unittest(dist == 0.0)

    # Point beyond segment end
    dist = _point_seg_dist(15, 0, 0, 0, 10, 0)
    unittest(dist == 5.0)

# FREEZE TOWER TESTS
def test_freeze_tower():
    """Test freeze tower slow effect."""
    print("\n--- Testing Freeze Tower ---")

    freeze = FreezeTower(100, 100)

    # Enemy within range
    enemy_near = Enemy([(150, 100), (200, 100)])  # 50 away, within 120 range
    original_speed = enemy_near.speed

    freeze.apply_slow([enemy_near])
    unittest(enemy_near.speed < original_speed)
    unittest(enemy_near.speed == original_speed * 0.5)

    # Enemy outside range
    enemy_far = Enemy([(500, 500), (600, 600)])  # way outside range
    original_speed_far = enemy_far.speed

    freeze.apply_slow([enemy_far])
    unittest(enemy_far.speed == original_speed_far)  # should not be slowed

# RUN ALL TESTS
def run_all_tests():
    """Run every test suite."""
    print("=" * 50)
    print("TOWER DEFENSE GAME - TEST SUITE")
    print("=" * 50)

    test_game_object()
    test_towers()
    test_enemies()
    test_waves()
    test_projectiles()
    test_path_validation()
    test_freeze_tower()

    print("\n" + "=" * 50)
    print("ALL TESTS COMPLETE")
    print("=" * 50)


if __name__ == "__main__":
    run_all_tests()