# ArcadeActions Framework Documentation

## 🚀 Quick Start

**Getting started with ArcadeActions?** Start here: **[API Usage Guide](api_usage_guide.md)**

ArcadeActions is a **conditional action system** for Arcade 3.x that enables declarative game behaviors through condition-based actions rather than fixed durations.

## 📚 Documentation Overview

### Essential Reading
1. **[API Usage Guide](api_usage_guide.md)** - **START HERE** - Complete guide to using the framework
2. **[Testing Guide](testing_guide.md)** - **Testing patterns and best practices**
3. **[PRD](prd.md)** - Project requirements and architecture decisions
4. **[Boundary Events](boundary_event.md)** - BoundedMove and WrappedMove patterns

## 🎯 Key Concepts

### Core Philosophy: Condition-Based Actions
Actions run until conditions are met, not for fixed time periods:

```python
from actions.conditional import MoveUntil, RotateUntil, FadeUntil

# Move until reaching a position
move_action = MoveUntil((100, 0), lambda: sprite.center_x > 700)

# Rotate until reaching an angle  
rotate_action = RotateUntil(90, lambda: sprite.angle >= 45)

# Fade until reaching transparency
fade_action = FadeUntil(-50, lambda: sprite.alpha <= 50)
```

### Global Action Management
No manual action tracking - everything is handled globally:

```python
from actions.base import Action

# Apply actions directly to any arcade.Sprite or arcade.SpriteList
action.apply(sprite, tag="movement")
action.apply(sprite_list, tag="formation")

# Single global update in your game loop
def on_update(self, delta_time):
    Action.update_all(delta_time)  # Handles all active actions
```

### Operator-Based Composition
Use mathematical operators to create complex behaviors:

```python
# Sequential actions with +
sequence = delay + move + fade

# Parallel actions with |  
parallel = move | rotate | scale

# Nested combinations
complex = delay + (move | fade) + final_action
```

## 🎮 Example: Space Invaders Pattern

```python
import arcade
from actions.base import Action
from actions.conditional import MoveUntil, DelayUntil, duration
from actions.pattern import AttackGroup
from actions.move import BoundedMove

class SpaceInvadersGame(arcade.Window):
    def __init__(self):
        super().__init__(800, 600, "Space Invaders")
        
        # Create enemy formation using standard arcade.SpriteList
        enemies = arcade.SpriteList()
        for row in range(5):
            for col in range(10):
                enemy = arcade.Sprite(":resources:images/enemy.png")
                enemy.center_x = 100 + col * 60
                enemy.center_y = 500 - row * 40
                enemies.append(enemy)
        
        # Use AttackGroup for high-level game management
        self.formation = AttackGroup(enemies, name="invaders")
        self._setup_movement_pattern()
    
    def _setup_movement_pattern(self):
        # Create formation movement with boundary bouncing
        def on_boundary_hit(sprite, axis):
            if axis == 'x':
                # Move entire formation down and change direction
                drop_action = MoveUntil((0, -30), duration(0.3))
                self.formation.apply(drop_action, tag="drop")
        
        # Set up boundary detection
        bounds = lambda: (50, 0, 750, 600)
        bouncer = BoundedMove(bounds, on_bounce=on_boundary_hit)
        
        # Create continuous horizontal movement
        move_action = MoveUntil((50, 0), lambda: False)  # Move indefinitely
        bouncer.wrap_action(move_action)
        
        # Apply to formation with global management
        bouncer.apply(self.formation.sprites, tag="formation_movement")
    
    def on_update(self, delta_time):
        # Single line handles all action updates
        Action.update_all(delta_time)
```

## 🔧 Core Components

### ✅ Implementation

#### Base Action System (actions/base.py)
- **Action** - Core action class with global management
- **CompositeAction** - Base for sequential and parallel actions
- **Global management** - Automatic action tracking and updates
- **Operator overloads** - `+` for sequences, `|` for parallel

#### Conditional Actions (actions/conditional.py)
- **MoveUntil** - Velocity-based movement until condition met
- **RotateUntil** - Angular velocity rotation
- **ScaleUntil** - Scale velocity changes  
- **FadeUntil** - Alpha velocity changes
- **DelayUntil** - Wait for condition to be met

#### Composite Actions (actions/composite.py)
- **Sequential actions** - Run actions one after another (use `+` operator)
- **Parallel actions** - Run actions in parallel (use `|` operator)

#### Boundary Actions (actions/move.py)
- **BoundedMove** - Bounce off boundaries with callbacks
- **WrappedMove** - Wrap around screen edges

#### Game Management (actions/pattern.py)
- **AttackGroup** - High-level sprite group lifecycle management
- **GridPattern** - Formation positioning patterns

## 📋 Decision Matrix

| Scenario | Use | Example |
|----------|-----|---------|
| Single sprite behavior | Direct action application | `action.apply(sprite, tag="move")` |
| Group coordination | Action on SpriteList | `action.apply(enemies, tag="formation")` |
| Sequential behavior | `+` operator | `delay + move + fade` |
| Parallel behavior | `\|` operator | `move \| rotate \| scale` |
| Game lifecycle management | AttackGroup | `formation.apply(pattern, tag="attack")` |
| Boundary detection | BoundedMove wrapper | `bouncer.wrap_action(movement)` |
| Standard sprites (no actions) | arcade.Sprite + arcade.SpriteList | Regular Arcade usage |

## 🎯 API Patterns

### ✅ Correct Usage
```python
# Works with any arcade.Sprite or arcade.SpriteList
player = arcade.Sprite("player.png")
enemies = arcade.SpriteList([enemy1, enemy2, enemy3])

# Apply actions directly
move_action = MoveUntil((100, 0), duration(2.0))
move_action.apply(player, tag="movement")
move_action.apply(enemies, tag="formation")

# Compose with operators
complex = delay + (move | fade) + final_action
complex.apply(sprite, tag="complex")

# High-level management
formation = AttackGroup(enemies)
formation.apply(pattern, tag="attack")
formation.schedule(3.0, retreat_pattern, tag="retreat")

# Global update handles everything
Action.update_all(delta_time)
```

## 🧪 Testing Patterns

### Individual Actions
```python
def test_move_until_condition():
    sprite = arcade.Sprite(":resources:images/test.png")
    sprite.center_x = 0
    
    # Apply action
    action = MoveUntil((100, 0), lambda: sprite.center_x >= 100)
    action.apply(sprite, tag="test")
    
    # Test with global update
    Action.update_all(1.0)
    assert sprite.center_x == 100
```

### Group Actions
```python
def test_group_coordination():
    enemies = arcade.SpriteList()
    for i in range(3):
        enemy = arcade.Sprite(":resources:images/enemy.png")
        enemies.append(enemy)
    
    # Apply to entire group
    action = MoveUntil((0, -50), duration(1.0))
    action.apply(enemies, tag="formation")
    
    # Test coordinated movement
    Action.update_all(1.0)
    for enemy in enemies:
        assert enemy.center_y == -50
```

### AttackGroup Management
```python
def test_attack_group():
    enemies = arcade.SpriteList([enemy1, enemy2])
    formation = AttackGroup(enemies, auto_destroy_when_empty=True)
    
    # Test high-level patterns
    pattern = delay + move + fade
    formation.apply(pattern, tag="test")
    
    # Test lifecycle management
    assert not formation.is_destroyed
```

## 📖 Documentation Structure

```
docs/
├── README.md                 # This file - overview and quick start
├── api_usage_guide.md       # Complete API usage patterns (START HERE)
├── boundary_event.md        # Boundary callback patterns
└── prd.md                   # Requirements and architecture
```

## 🚀 Getting Started

1. **Read the [API Usage Guide](api_usage_guide.md)** to understand the framework
2. **Study the Space Invaders example** above for a complete pattern
3. **Start with simple conditional actions** and build up to complex compositions
4. **Use AttackGroup** for game-level sprite management and lifecycle

The ArcadeActions framework transforms Arcade game development with declarative, condition-based behaviors! 

# Individual sprite control
sprite = arcade.Sprite("image.png")
action = MoveUntil((100, 0), lambda: sprite.center_x > 700)
action.apply(sprite, tag="movement")

# Group management  
enemies = arcade.SpriteList()  # Use standard arcade.SpriteList
action = MoveUntil((50, 0), duration(2.0))
action.apply(enemies, tag="formation") 