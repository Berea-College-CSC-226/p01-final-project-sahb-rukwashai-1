# CSC226 Final Project

## Instructions

❗️Exclamation Marks ❗️indicate action items; you should remove these emoji as you complete/update the items which 
  they accompany. (This means that your final README should have no ❗️in it!)

**Author(s)**: Bhushan Sah & Daniel Rukwasha

**Google Doc Link**: https://docs.google.com/document/d/1lKuOB9pPnH6yuEsixRnpE7bPGq9S8JdDnZPzu4O5a8s/edit?usp=sharing
**GitHub Link**: https://github.com/Berea-College-CSC-226/p01-final-project-sahb-rukwashai-1

---

## Milestone 1: Setup, Planning, Design

**Title**: `Path of No Return: A Tower Defense Game`

**Purpose**: `A tower defense game where the player places different types of towers along a winding path to stop waves
 of enemies from reaching the exit, built with Turtle graphics and a Tkinter control panel.`

**Source Assignment(s)**: `T02 (Exploring Turtles), HW02 (Loopy Turtles), HW09 (UPC Barcodes), HW10 (Caesar Cipher), T10 (Pet Adoption Center),
   T11 (The Legend of Tuna)`

**CRC Card(s)**:
    # CRC Cards

---
## Class name: GameObject

| Class Attributes: | Class Collaborations (other classes): |
|---|---|
| x, y (position coordinates) | |
| size (for collision detection) | |

| Class Methods: | Class Collaborations (other classes): |
|---|---|
| render(): draw itself on screen | Pygame |
| distance_to(other): calculate distance to another object | GameObject |
| collides_with(other): check collision with another object | GameObject |

---

## Class name: Tower (inherits GameObject)

| Class Attributes: | Class Collaborations (other classes): |
|---|---|
| tower_range (how far it can shoot) | |
| damage (how much damage per shot) | |
| fire_rate (time between shots) | |
| cost (price to place the tower) | |
| target (the enemy currently aimed at) | Enemy |
| _fire_timer (cooldown tracker) | |

| Class Methods: | Class Collaborations (other classes): |
|---|---|
| find_target(enemies): find nearest enemy in range | Enemy |
| can_fire(): check if cooldown is ready | |
| update_timer(dt): decrease fire cooldown | |
| reset_timer(): reset cooldown after firing | |
| render(): draw the tower on the map | Pygame |
| draw_range(): show attack range circle | Pygame |

---

## Class name: ArrowTower (inherits Tower)

| Class Attributes: | Class Collaborations (other classes): |
|---|---|
| damage = 25 | |
| tower_range = 150 | |
| fire_rate = 1.0 | |
| cost = 50 | |

| Class Methods: | Class Collaborations (other classes): |
|---|---|
| Inherits all methods from Tower | |

---

## Class name: BombTower (inherits Tower)

| Class Attributes: | Class Collaborations (other classes): |
|---|---|
| damage = 40 | |
| tower_range = 100 | |
| fire_rate = 2.0 | |
| cost = 100 | |
| blast_radius (area of explosion) | |

| Class Methods: | Class Collaborations (other classes): |
|---|---|
| Inherits all methods from Tower | |

---

## Class name: FreezeTower (inherits Tower)

| Class Attributes: | Class Collaborations (other classes): |
|---|---|
| tower_range = 120 | |
| slow_amount (speed multiplier) | |
| cost = 75 | |

| Class Methods: | Class Collaborations (other classes): |
|---|---|
| apply_slow(enemies): slow all enemies within range | Enemy |

---

## Class name: Enemy (inherits GameObject)

| Class Attributes: | Class Collaborations (other classes): |
|---|---|
| health (current hit points) | |
| max_health (starting hit points) | |
| speed (how fast it moves per frame) | |
| original_speed (stored for freeze restore) | |
| reward (money given when destroyed) | |
| current_waypoint_index (next waypoint to reach) | |
| alive (whether the enemy is still active) | |
| reached_end (whether it passed the last waypoint) | |

| Class Methods: | Class Collaborations (other classes): |
|---|---|
| move(): step toward the next waypoint | |
| take_damage(amount): reduce health by amount | |
| is_dead(): check if health is zero or below | |
| render(): draw itself and its health bar | Pygame |

---

## Class name: FastEnemy (inherits Enemy)

| Class Attributes: | Class Collaborations (other classes): |
|---|---|
| max_health = 50 (low) | |
| speed = 4 (high) | |
| reward = 10 | |

| Class Methods: | Class Collaborations (other classes): |
|---|---|
| Inherits all methods from Enemy | |

---

## Class name: TankEnemy (inherits Enemy)

| Class Attributes: | Class Collaborations (other classes): |
|---|---|
| max_health = 200 (high) | |
| speed = 1 (low) | |
| reward = 30 | |

| Class Methods: | Class Collaborations (other classes): |
|---|---|
| Inherits all methods from Enemy | |

---

## Class name: Projectile (inherits GameObject)

| Class Attributes: | Class Collaborations (other classes): |
|---|---|
| damage (how much damage on hit) | |
| speed (how fast it travels) | |
| target (reference to the enemy it tracks) | Enemy |
| alive (whether projectile is still active) | |

| Class Methods: | Class Collaborations (other classes): |
|---|---|
| move(): step toward the target's current position | Enemy |
| hit(): deal damage to target and mark as dead | Enemy |
| render(): draw itself on screen | Pygame |

---

## Class name: BombProjectile (inherits Projectile)

| Class Attributes: | Class Collaborations (other classes): |
|---|---|
| blast_radius (area of explosion) | |
| enemies_list (reference to all enemies for splash) | Enemy |

| Class Methods: | Class Collaborations (other classes): |
|---|---|
| hit(): deal splash damage to all enemies in blast radius | Enemy |

---

## Class name: Wave

| Class Attributes: | Class Collaborations (other classes): |
|---|---|
| wave_number (which wave this is) | |
| spawn_queue (list of enemy types and delays) | |
| spawn_timer (time until next spawn in ms) | |
| started (whether wave has begun) | |
| all_spawned (whether all enemies pushed out) | |

| Class Methods: | Class Collaborations (other classes): |
|---|---|
| update(dt_ms): spawn next enemy if delay passed | Enemy, FastEnemy, TankEnemy |
| is_complete(): check if all enemies have been spawned | |

---

## Class name: Game

| Class Attributes: | Class Collaborations (other classes): |
|---|---|
| towers (list of all placed towers) | Tower |
| enemies (list of all active enemies) | Enemy |
| projectiles (list of all active projectiles) | Projectile |
| wave (current Wave object) | Wave |
| money (player's current money) | |
| lives (player's remaining lives) | |
| score (player's current score) | |
| selected_tower_class (tower type chosen for placement) | Tower |
| game_over, game_won (win/lose state) | |

| Class Methods: | Class Collaborations (other classes): |
|---|---|
| _build_window(): initialize Pygame window | Pygame |
| draw_map(): draw background and path | Pygame |
| draw_side_panel(): draw stats and tower buttons | Pygame |
| _handle_click(mx, my): route clicks to buttons or map | Tower |
| _select_tower(name): choose a tower type to place | Tower |
| _placement_is_valid(x, y, cls): check if spot is valid | GameObject |
| _try_place_tower(x, y): subtract cost and place tower | Tower |
| _start_wave(): begin spawning the next wave | Wave |
| _update_towers(dt): targeting and firing logic | Tower, Enemy, Projectile |
| _update_projectiles(): move projectiles, remove dead | Projectile |
| update(): run one frame of game logic | Tower, Enemy, Projectile, Wave |
| draw(): render everything to screen | Pygame |
| run(): main game loop | Pygame |
  - **Branches**: This project will **require** effective use of git. 

 Each partner should create a branch at the beginning of the project, and stay on this branch (or branches of their 
branch) as they work. When you need to bring each others branches together, do so by merging each other's branches 
into your own, following the process we've discussed in previous assignments, then re-branching out from the merged code.  

```
    Branch 1 starting name: sahb
    Branch 2 starting name: Rukwashai
    
    ### Task Delegation
  - Sahb: Game class, Tower classes (ArrowTower, BombTower, FreezeTower), tower placement logic, Tkinter side panel
  - Rukwashai: Enemy classes (FastEnemy, TankEnemy), Projectile class, Wave system, enemy pathfinding
  - Shared: GameObject base class, testing, README updates, bug fixes
```

### References 

Throughout this project, you will likely use outside resources. Reference all ideas which are not your own, 
and describe how you integrated the ideas or code into your program. This includes online sources, people who have 
helped you, AI tools you've used, and any other resources that are not solely your own contribution. Update this 
section as you go. DO NOT forget about it!
    
- Claude AI -helping write game logic for tower placement, enemy movement, wave spawning,
  and projectile systems.
- Pygame documentation (https://www.pygame.org/docs/) - Referenced for drawing functions,
  event handling, and surface/alpha blending.
- T11: The Legend of Tuna - Used as reference for Pygame game loop structure, sprite
  movement, and collision detection patterns.
- T10: Pet Adoption Center - Used as reference for class inheritance structure.
- Stack Overflow (https://stackoverflow.com/) - Referenced for point-to-line-segment
  distance formula used in tower placement validation.
- GeeksforGeeks (https://www.geeksforgeeks.org/) - Referenced for understanding
  Euclidean distance calculation and circle-based collision detection.
- Real Python Pygame tutorial (https://realpython.com/pygame-a-primer/) - Referenced
  for game loop structure and frame rate management with pygame.time.Clock.
- Python docs (https://docs.python.org/3/) - Referenced for math module functions
  (sqrt, atan2) and list comprehension patterns used for filtering enemies and projectiles.
---

## Milestone 2: Code Setup and Issue Queue

Most importantly, keep your issue queue up to date, and focus on your code. 🙃

Reflect on what you’ve done so far. How’s it going? Are you feeling behind/ahead? What are you worried about? 
What has surprised you so far? Describe your general feelings. Be honest with yourself; this section is for you, not me.

```
    This project has been going well. We got the core game loop working faster than I expected.
    Towers place correctly, enemies walk the path, projectiles track and hit targets. Seeing it
    all come together was satisfying.
    
    I think we're in a good spot for the timeline. The main gameplay is done so now it's about
    testing, cleaning up, and fixing edge cases. The issue queue helped a lot with staying on
    track and splitting work between us.
    
    What surprised me was how much thought went into the small stuff. Tower placement validation
    and projectile tracking took longer than I assumed they would. Getting the freeze tower to
    slow enemies without stacking permanently was a fun problem to solve.
    
    My biggest concern right now is the test suite. Most of our code is visual so I need to
    figure out how to test the logic (damage, distance, path collision) without spinning up a
    Pygame window.
    
    Overall feeling good. The game is playable and we've been committing steadily.
```

---

## Milestone 3: Virtual Check-In
Indicate what percentage of the project you have left to complete and how confident you feel. 

**Completion Percentage**: `0 - 100%`

**Confidence**: Describe how confident you feel about completing this project, and why. Then, describe some 
  strategies you can employ to increase the likelihood that you'll be successful in completing this project 
  before the deadline.

```
    Completion Percentage: 90%

The core game is fully functional. Towers place and shoot, enemies walk the path and take
damage, waves spawn with increasing difficulty, freeze tower slows enemies, bomb tower does
splash damage, there's a pause system, restart button, floating damage numbers, death
particles, and a polished UI with stat bars and a pre-rendered map with trees and flowers.
The test suite covers all the logic classes. The main things left are final code cleanup,
finishing the README, and making sure the issue queue is in good shape for submission.

We feel confident about finishing on time. The hard parts (game loop, targeting, projectiles,
wave system) are done and tested. What's left is mostly writing and cleanup, not coding. The
biggest risk would be finding a last-minute bug during the demo, but the test suite should
catch most logic issues before that happens. Our strategy for the final stretch is to play
through the game a few times to catch edge cases, have each other review the code for
anything we missed, and write the README sections incrementally instead of leaving them all
for the last night.
```

---

## Milestone 4: Final Code, Presentation, Demo

### User Instructions

When you run the program, a game window opens with a green map on the left and a dark control panel on the right. The map 
shows a winding dirt path with a red pulsing SPAWN marker and a gold pulsing EXIT marker. To start playing, press SPACE
to launch the first wave of enemies. Enemies will appear at the spawn point and walk along the path toward the exit. 
Before or during a wave, click one of the three tower buttons on the side panel (Arrow, Bomb, or Freeze)to select a tower 
type. Then click anywhere on the green grass to place it. A blue range preview follows your cursor showing where the tower
can reach, and the square turns green if the spot is valid or red if it is not. Towers automatically detect and shoot at
enemies within range. Arrow towers fire fast single shots, bomb towers fire slow area-damage explosions, and freeze towers 
slow all enemies nearby without dealing damage. You earn money for each enemy killed which you can spend on more towers. 
If an enemy reaches the exit you lose a life. Lose all 20 lives and the game is over. Clear all 5 waves and you win. Press
P to pause, R to restart after a game over, and Q to quit.


### Errors and Constraints

All known bugs and limitations are documented in the GitHub issue queue. The key ones are:

- Freeze tower slow does not stack with multiple freeze towers. Two freeze towers next to each other slow enemies the 
  same amount as one.
- Projectiles can briefly render off-screen if an enemy dies right at the map edge .
- Placing towers very close together sometimes overlaps visually even though the collision check passes.
- Wave cleared banner sometimes overlaps with floating damage text.
- Towers cannot be sold or moved after placement.
- No sound effects or music.
- No difficulty selection. Waves are hardcoded.
- No start menu screen. The game loads directly into gameplay.
- Window size is fixed and cannot be resized.
- No save system for high scores.

### Reflection

 Each partner should write three to four well-written paragraphs address the following (at a minimum):
- Why did you select the project that you did?
- How closely did your final project reflect your initial design?
- What did you learn from this process?
- What was the hardest part of the final project?
- What would you do differently next time, knowing what you know now?
- How well did you work with your partner? What made it go well? What made it challenging?

```
    Partner 1: Bhushan Sah 
   We picked the tower defense game because it covered basically everything from this course in one project. We needed 
   classes and inheritance for the tower and enemy types,lists to manage all the game objects, dictionaries for mapping 
   tower names to their classes, file I/O patterns from earlier assignments, exception handling concepts, and Pygame for 
   the GUI. It was one of those ideas where every chapter had a clear place in the code, which made it feel like a real 
   capstone project rather than something that only used a few topics. 
   
   The final version ended up pretty close to what we designed in Milestone 1. The six main subtasks from our top-down
   design all made it into the game. We actually added more than we planned. Floating damage numbers, death particles, 
   the wave cleared banner, pause and restart systems, and the pre-rendered map with trees and flowers were all things
   we came up with while building. The only feature we cut was tower selling because the UI for selecting an already-placed
   tower got complicated and we decided our time was better spent polishing what we had.
   
   We learned a lot about how important design is before writing code. The top-down design from HW11 felt tedious at the 
   time but it gave us a clear roadmap for what to build and in what order. We also learned how to split a large program 
   across multiple files and have them work together through imports, which is something we never did in earlier assignments. 
   Working with Git branches and merging taught us how real collaboration works. On the technical side, we got a much deeper
   understanding of how game loops work, how to separate game logic from rendering, and how to test code that has a visual 
   component by isolating the logic into testable functions.
   
   The hardest part was the projectile and targeting system. Each tower has to scan all enemies every frame, pick the
   closest one in range, check its fire cooldown, then create a projectile that recalculates its direction every frame 
   because the target is moving. Bomb projectiles made it worse because they deal splash damage on impact, so we had to 
   loop through all enemies again at the hit location. The trickiest bug was enemies being removed from the list while we 
   were still iterating over it, which we fixed by iterating over a copy of the list with the slice notation.
   
   Next time we would write the test suite alongside the code instead of after. We caught a couple of issues late that we 
   could have found earlier with tests in place from the start. Working with Daniel went smoothly for the most part. Splitting
   tasks clearly in the design phase meant we could work on separate branches without conflicts. The only friction was when
   we both needed to edit game.py at the same time, but we handled it by communicating before pushing and merging frequently 
   instead of waiting until the end.
```

```
    Partner 2: Here's your reflection, written in your own voice but polished into proper paragraphs:

---

**Partner 2:**

I supported this project idea from the start even though it came from my partner. I was genuinely curious to see what 
we could build together and whether the final product would be something enjoyable, especially for younger players. 
Tower defense games have a simple enough concept that kids can pick them up quickly, but they also require real strategy,
 so I wanted to see if we could pull that balance off. That curiosity ended up being enough motivation to push through 
 the harder parts of the project.

Our starting plan was more of a rough picture than a detailed blueprint. We had a general vision but not all the pieces 
figured out yet, and we discovered what we actually needed as we built. Many things changed along the way. 
We wanted to add more features and make the game as interactive and user-friendly as possible, but we had to make 
realistic decisions about what we could actually finish in time. That process of adjusting our expectations taught 
me that planning and building are two very different skills, and you need both.

What surprised me most about what I learned was personal as much as technical. I am not someone who plays video games, 
but working on this project made me genuinely excited to play something I helped create. That was a feeling I did not 
expect. On the technical side, I got hands-on experience with game-related libraries I had never used before and 
developed a real appreciation for how much logic goes into something that looks simple on the surface.

The hardest part for me was the moments when my partner and I had to agree on a specific feature, 
especially when we each had a different picture of how it should look or work. Talking through those disagreements 
took time and patience. Bhushan was a great teammate throughout the process. He is patient, thoughtful, 
and genuinely invested in doing the work well, which made it easier to work through those moments and keep moving forward.

---