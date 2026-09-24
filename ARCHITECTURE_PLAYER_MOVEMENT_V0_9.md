# Player Movement / Camera Architecture v0.9

## Goal
Add a second outer-world gameplay view without coupling movement or camera logic to magic physics.

## Modes
- **Third Person** — existing character/camera remains untouched and is the precision-casting view.
- **Top Down** — activated with **Shift**.
  - Hold **Right Mouse Button**: move toward cursor position.
  - Hold **Left Mouse Button + drag**: orbit camera around the character; vertical drag adjusts elevation.
  - **Mouse Wheel Up**: sprint speed.
  - **Mouse Wheel Down**: return to walk speed.
  - **Shift**: return to Third Person.

## Ownership
### PlayerViewModes
Owns only:
- Third-person/top-down switching.
- Top-down orbit camera.
- Cursor-based movement.
- Top-down sprint state.
- A generic player-based aim ray for systems that need to cast toward the cursor.

It does **not** know about Earth, materials, impact calculations, spell definitions, or generated spell bodies.

### InnerRealm
Still exclusively owns TAB meditation/realm switching. While meditation is active, PlayerViewModes does nothing and preserves the chosen outer-world mode.

### EarthTestHarness
Still owns the disposable `E` test cast. It consumes the generic top-down aim ray when top-down is active so Earth spells launch from the player toward the cursor instead of from the aerial camera.

## Dependency direction
```
InnerRealm       PlayerViewModes
     ^                 ^
     |                 |
     +---- gameplay ---+
                       |
               EarthTestHarness
                       |
                   EarthMagic
```

PlayerViewModes depends on InnerRealm only to respect its higher-priority view/input state.
EarthTestHarness may query PlayerViewModes for an aim ray, but PlayerViewModes never imports spell or Earth systems.

## World Partition
The top-down camera actor follows the player's world position and uses a spring arm, keeping it in the same streaming region rather than teleporting to a remote camera location.
