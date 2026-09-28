# POWR SCALE

## Game concept and systems design

**Version 1.0 · 28 September 2026**

**Purpose:** Define the game idea, its player experience, and the system relationships needed to support it.

**Status:** Design document. Existing project foundations and proposed additions are distinguished in [Project alignment](#17-project-alignment).

> One world. Shared laws. Different ways to play. Understanding opens possibilities; the player chooses how much to manage.

Dungeon floors reveal dimensions that change the whole gameplay experience. First person, third person, top down, and the Inner Realm offer different controls, activities, and degrees of direct manipulation within one connected world.

Statements labeled **Proposed default** resolve details that have not yet been explicitly chosen. They make the design concrete and reviewable without treating every suggested mechanic as a settled requirement.

## Contents

1. [Vision and design principles](#1-vision-and-design-principles)
2. [World, floors, dimensions, and scale](#2-world-floors-dimensions-and-scale)
3. [Gameplay dimensions](#3-gameplay-dimensions)
4. [Controls and dimension transitions](#4-controls-and-dimension-transitions)
5. [Player loops and freedom of play](#5-player-loops-and-freedom-of-play)
6. [Knowledge, gates, and progression](#6-knowledge-gates-and-progression)
7. [Elements, spells, and construction](#7-elements-spells-and-construction)
8. [Equipment and persistent rewards](#8-equipment-and-persistent-rewards)
9. [Mana, analysis, and puzzle rewards](#9-mana-analysis-and-puzzle-rewards)
10. [The phone and Inner Module](#10-the-phone-and-inner-module)
11. [Shared world state and time](#11-shared-world-state-and-time)
12. [Core architecture and ownership](#12-core-architecture-and-ownership)
13. [Nodes, classification, and relationships](#13-nodes-classification-and-relationships)
14. [Functions, contracts, and data flow](#14-functions-contracts-and-data-flow)
15. [A connected gameplay example](#15-a-connected-gameplay-example)
16. [Readability, balance, and accessibility](#16-readability-balance-and-accessibility)
17. [Project alignment](#17-project-alignment)
18. [Development slices and verification](#18-development-slices-and-verification)
19. [Decision register and concept coverage](#19-decision-register-and-concept-coverage)

## 1. Vision and design principles

The player begins inside a dungeon, experiencing the world through direct, first-person interaction. Exploration reveals that its floors are entrances into different dimensions of that same world. Entering a new dimension changes how the player moves, perceives, constructs actions, and manages power.

Third-person play introduces primitive elemental magic and prepared spells. Top-down play gives movement to the mouse and makes the keyboard available as a live spell table. The Inner Realm provides space for understanding and experimentation; a phone can become another entrance into that space.

Learning more can increase the number of elements, relationships, and effects the player can manipulate. The player remains free to enjoy a simpler style, specialize in a small set of actions, or return to a familiar dimension after discovering more complex ones.

| Principle | Design consequence |
| --- | --- |
| One shared world | Dimensions share character identity, objects, discoveries, equipment, resources, and world consequences. |
| Dimensions change gameplay | Each dimension defines movement, input, targeting, available operations, and casting workflow together. |
| Shared laws | The same valid action produces the same result under the same conditions, regardless of which interface requested it. |
| Understanding expands possibilities | Discoveries open tools, combinations, routes, and scales of control. |
| Complexity is a choice | Enjoyable exploration and combat remain available without live spell construction or comprehensive theory. |
| Every dimension has lasting value | Earlier styles receive meaningful encounters, equipment uses, and opportunities for improvement. |
| Preparation reduces effort | A useful construction can become a prepared action, subject to its execution requirements. |
| Connected devices contribute to the world | Phone activities produce usable knowledge, spell drafts, or resources connected to the same player. |
| Clear ownership supports expansion | Each system owns a specific responsibility and communicates through explicit data and actions. |

The main balance test is simple: learning a complicated system should feel rewarding, while declining it should still leave a satisfying game.

## 2. World, floors, dimensions, and scale

### 2.1 Terms

| Term | Meaning in POWR SCALE |
| --- | --- |
| World | The shared reality containing characters, places, objects, resources, and consequences. |
| Location | A physical place with a position and persistent identity. |
| Floor | The dungeon's spatial and narrative expression of progression. A floor may introduce a dimensional gate. |
| Dimension | A playable state that changes perception, control, and the operations available to the player. |
| Gameplay profile | The complete configuration that implements a dimension's movement, controls, targeting, interface, and action access. |
| Gate | A world interaction whose explicit conditions open a route or dimension. |
| Knowledge | Player-specific discoveries and understanding of the world's concepts and relationships. |
| Capability | A specific supported operation, such as shaping earth or composing a pattern during combat. |
| Scale | The scope of effects and relationships a player can coordinate. It includes breadth, complexity, and reach as well as strength. |

A dungeon floor and a dimension are linked concepts, but their identifiers remain separate. This allows one dimension to be used in several locations and one location to support several dimensions.

**Proposed default:** A gate is discovered at a meaningful floor or location. Once its dimension is unlocked, the player can use that dimension in compatible explored areas. Authored transition zones can temporarily limit access for a clear gameplay reason. A new camera does not create a second copy of the location.

A location declares its supported profiles and a readable reason for any restriction. An interactable declares its available actions and presentation in each supported profile while retaining one canonical identity and state. Profile restrictions on optional areas may be specialized; the principal route follows the preferred-style commitment in [Player freedom](#55-content-commitments).

### 2.2 The scale of understanding

The initial direction is:

**Physical interaction → elemental manipulation → live composition and coordination → optional wider systems.**

These are entry points into new activities, rather than a ranking of player worth or enjoyment. A player can deepen their skill within any one of them.

Future scales could include coordinating persistent constructs, environmental processes, or several linked effects. These are expansion possibilities. Their introduction depends on a distinct, intuitive interaction model and the same shared-world contracts defined in [Core architecture](#12-core-architecture-and-ownership).

## 3. Gameplay dimensions

The labels below describe their functions. Final fictional names can be developed separately.

### 3.1 First person: physical discovery

**Role:** Establish presence, curiosity, and a readable world before asking the player to manage magic.

The player explores through their own eyes, moves directly, interacts with objects, uses equipment, encounters danger, and notices unexplained phenomena. A moving stone, a reacting material, or an unusual structure can introduce a future concept through an observable event.

**Proposed default:** Start with familiar direct movement and mouse look. Initial actions are physical interaction, a small set of tools, and simple combat where appropriate. Elemental construction becomes available through later discovery rather than being required at the start.

Long-term value comes from close observation, movement skill, environmental interaction, exploration, and suitable equipment. The dimension needs its own ongoing rewards and activities after other dimensions open.

**Proposed default:** Learned knowledge persists on return, but usable abilities are explicitly listed by the first-person profile. Returning does not automatically grant every third-person or top-down operation. Selected tools or prepared effects may be made available when they fit this style.

### 3.2 Third person: embodied elemental magic

**Role:** Combine direct character movement with intuitive magic and preparation.

The player controls movement with **WASD**. The mouse supports looking, aiming, and interaction. Because movement occupies important keyboard inputs, combat emphasizes **predefined, constructed spells** selected from a manageable loadout.

Primitive magic introduces a few understandable operations at a time: select an available element, apply a supported transformation, choose a target, and release the effect. Examples include lifting a small earth fragment, shaping a barrier, or directing a simple projectile. Other elements need their own valid operations rather than inheriting earth's behavior.

The player constructs or edits spells in the Inner Realm, equips them, and uses them through simple inputs in the outer world. Combat depth comes from movement, aim, timing, positioning, spell choice, and the environment.

Prepared spells can become sophisticated. Their complexity was handled during preparation; casting them remains readable. Any effect that genuinely requires ongoing manual control must state that requirement and may be unavailable in this profile.

### 3.3 Top down: live construction and coordination

**Role:** Make composition itself part of active gameplay.

The player directs movement with the **mouse**. The keyboard becomes a **spell table** for selecting concepts, combining operations, setting parameters, and committing casts during an encounter.

The table represents actions and concepts, such as element, form, pattern, motion, target, confirm, and cancel. It must show the current construction and which next operations are valid. Exact key assignments are remappable interface choices.

The player may build a spell live, start from a prepared spell, or use a prepared spell unchanged. This allows gradual learning within top-down play instead of requiring full keyboard fluency immediately.

Complexity comes from coordinating effects, reacting through composition, and managing spatial relationships. The dimension can support more direct manipulation without receiving an unexplained damage multiplier.

**Proposed default:** Mouse movement and ground targeting use explicit, distinct input actions. The interface makes the current mouse role visible so choosing a spell target does not accidentally issue a movement command. The keyboard still reserves essential system and accessibility controls; “spell table” means substantially expanded casting access.

**Proposed default:** The world continues in real time while the spell table is used. Readable previews, a small initial operation set, and prepared spells make the introduction manageable. Safe practice happens in the Inner Realm. Any later time-slowing assistance must follow the shared session time policy and be presented explicitly.

### 3.4 Inner Realm: understanding and preparation

**Role:** Let the player study, experiment, organize, and prepare at a comfortable pace.

The Inner Realm contains the Codex, spell workbench, experiments, loadouts, and optional world-logic puzzles. It is accessible through the main game, with appropriate functions also available through the phone's Inner Module.

The Inner Realm is a gameplay domain with its own preparation profile. The phone is an optional companion surface into selected actions in that domain, with its own touch-based puzzle gameplay. The physical device is not a Dimension node or a target of `RequestDimensionTransition`; opening it never switches the character's active profile.

It operates on the same knowledge and spell definitions as combat. A preview is a safe experiment with clearly identified assumptions; it cannot silently change the live world or grant resources.

Its different time and body-control rules are specified in [Shared world state and time](#11-shared-world-state-and-time). Its phone interface is specified in [The phone and Inner Module](#10-the-phone-and-inner-module).

### 3.5 Dimension comparison

| Property | First person | Third person | Top down | Inner Realm (phone companion) |
| --- | --- | --- | --- | --- |
| Main interaction | Physical exploration | Direct movement and prepared magic | Tactical movement and live composition | Study, construction, experiments, puzzles |
| Movement | Direct character control | WASD | Mouse-directed | No outer-world movement by default |
| Magic access | Explicit supported subset | Equipped prepared spells | Prepared spells plus live spell table | Author and inspect valid constructions |
| Main demand | Observation and immediate action | Movement, aim, timing | Composition and coordination | Optional curiosity and experimentation |
| Comfortable path | Familiar tools and actions | Small dependable loadout | Prepared casts with a limited table | Short untimed activities and saved recipes |
| Shared consequence | Changes the same world | Changes the same world | Changes the same world | Supplies validated definitions, discoveries, and rewards |

## 4. Controls and dimension transitions

### 4.1 A complete gameplay profile

Each dimension references a profile containing:

- Camera and perception presentation.
- Movement controller and input bindings.
- Target selection and aiming behavior.
- Available action capabilities.
- Spell preparation or live-construction interface.
- Loadout presentation and supported equipment actions.
- Transition eligibility and any explicit world restrictions.
- Accessibility settings compatible with the dimension's actions.

Unlocking a dimension grants access to this complete profile. Changing only a camera does not unlock its capabilities.

### 4.2 Transition contract

**Proposed default:** Transitions are explicit player actions. They are available between committed actions, with a short consistent transition interval. They are not an emergency reset or a way to skip an active cast's cost. Exact timing is tuned through playtesting.

The transition sequence is:

1. Check the requested dimension's unlock, location rules, and the current action state.
2. Preserve the character, position, health, resources, inventory, knowledge, cooldowns, and existing world effects.
3. Reject or defer a transition during an indivisible action commitment. Preserve any uncommitted spell draft for later editing.
4. Release held input and stop accepting commands under the old profile.
5. Activate the new movement, targeting, camera, input, and casting profile together.
6. Restore control and clearly indicate available actions and unsupported equipped items.

If activation fails, restore the previous profile and leave shared state intact. No partial state may leave top-down casting attached to third-person movement unintentionally.

A preserved live draft is suspended when its construction workflow is unavailable. Entering third person does not turn that draft into an equipped prepared spell. To use it there, the player must save a compatible version and prepare it through an allowed loadout interaction. Knowledge persists, while the current profile controls the available workflow.

Once cast, an effect continues under its existing definition. Switching dimensions does not duplicate it, refund it, remove its lifetime, or reset its cooldown. If an effect requires continuous manual control, the spell declares what happens when that control is released; that behavior is consistent for ordinary interruption and dimension switching.

Related ownership: [Dimension Coordinator](#12-core-architecture-and-ownership). Related action contract: [RequestDimensionTransition](#14-functions-contracts-and-data-flow).

## 5. Player loops and freedom of play

### 5.1 The everyday loop

Choose an unlocked style → explore or take an encounter → use familiar tools or spells → gain a useful reward or discovery → return, prepare, or continue.

This loop must remain rewarding with a small action set. The player can enjoy an evening of exploration or combat without opening a construction interface.

### 5.2 The discovery loop

Observe a phenomenon → try a simple interaction → recognize a relationship → record understanding → gain a capability or route → use it in the world.

Discovery is grounded in play. The game should demonstrate enough cause and effect that understanding a basic rule feels natural.

### 5.3 The mastery loop

Choose a question → experiment → construct a combination → test it → save a useful result → optionally use or refine it in live combat.

The result can become a prepared spell. A player may also use an authored recipe or an in-world learned recipe without personally deriving every operation. Recipe access still respects its stated knowledge, equipment, and resource requirements.

### 5.4 The companion loop

Open the Inner Module → read, experiment, or play a short puzzle → save a draft or earn a validated reward → use the result during main-world play.

Leaving an activity incomplete has no penalty. Phone engagement does not maintain a streak or protect a resource from decay.

### 5.5 Content commitments

- Each unlocked dimension has repeatable enjoyable activities and meaningful improvements within its own style.
- The principal adventure offers a route that does not require live construction or phone play. This can include guided introductions to dimensions and prepared solutions where appropriate.
- A player can remain in a preferred dimension for sustained play. Specialized optional routes can require a particular dimension when their requirements are clearly signposted.
- Simple builds remain effective through suitable equipment, preparation, and player skill. Complex builds gain expression and coordination rather than universal superiority.
- The game offers an inviting next discovery without treating unfinished knowledge as a debt.

**Proposed default for the principal adventure:** After onboarding, each principal objective has a viable solution in the player's preferred unlocked outer-world profile. First-person routes can use physical tools and environmental interactions; third-person routes can use prepared magic; top-down routes can use prepared or live constructions. Unlocking later dimensions remains a voluntary expansion. Optional specialist routes may require a particular dimension.

This is a content-design commitment as well as a system feature. It requires checking the authored route in each supported style, rather than assuming shared physics automatically makes every objective accessible.

## 6. Knowledge, gates, and progression

### 6.1 Knowledge has two distinct owners

The **Codex catalog** describes what a concept means and how it relates to other concepts. **Player knowledge state** records what this player has observed, understood, and unlocked. A catalog entry's existence does not mean the player already knows it.

**Proposed default:** Track these states separately where useful:

| State | Meaning | Example |
| --- | --- | --- |
| Observed | The player has encountered evidence of a concept. | A loose stone reacts near an artefact. |
| Understood | A defined interaction or guided experiment demonstrates the rule. | The player successfully lifts the stone. |
| Usable | A derived access result: current knowledge, tools, and profile allow an operation. | The earth-lift operation is available in elemental play. |
| Practiced | Optional achievements record deeper use. | The player uses the same operation in several creative solutions. |

These states must not become four obligatory grind bars. One meaningful interaction may establish several of them. Observations, understanding, and practice records persist across dimensions and devices. Usability is recalculated from the current context; it is not stored as an independent permanent unlock that can become stale when equipment or profiles change.

### 6.2 Gates

A gate references explicit conditions: discoveries, demonstrated operations, an item, an encounter outcome, or an authored combination of these. It also provides a readable reason when unavailable and a clue toward a relevant next action.

**Proposed default:** The first elemental gate opens through a short discovery sequence. The first top-down gate opens after a small set of demonstrated elemental fundamentals. It does not demand completion of every element or extensive practice counters.

The dimension route graph supports branches, return paths, and shortcuts. Its connections do not have to form one compulsory ladder. A completed gate stays unlocked unless a specifically communicated world event changes that route; player knowledge itself is not erased.

### 6.3 Different kinds of improvement

| Improvement | Player benefit | Guardrail |
| --- | --- | --- |
| Understanding | New operations and combinations | Core discoveries are demonstrated clearly. |
| Equipment | Useful tools, reliable strengths, new applications | Earlier styles receive relevant equipment. |
| Personal skill | Better movement, aim, timing, or composition | No single skill style is the universal requirement. |
| Preparation | More convenient or specialized actions | Saved complexity can remain easy to use. |
| Scale of control | Coordinate more relationships or effects | Costs and control requirements remain explicit. |

Analysis may help interpret evidence, reveal a relationship, or unlock a defined knowledge entry. Spending mana starts or supports that process; it is not a purchase of every unrelated discovery. See [Mana and analysis](#9-mana-analysis-and-puzzle-rewards).

## 7. Elements, spells, and construction

### 7.1 Primitive magic

Begin with a small set of observable rules and a few useful actions. The player should be able to predict why a small effect happens before being asked to combine many operations.

An element declares its supported capabilities. Earth may support solid geometry and physical motion. Other elements may involve flow, heat, propagation, or other appropriate behavior. These are examples for future design, not claims that all such simulations currently exist.

Forms, patterns, motion, and modifiers only appear where the chosen element supports them. An unavailable combination should explain its missing prerequisite or unsupported operation.

### 7.2 One definition, several construction methods

The same canonical spell representation is used by the workbench, prepared loadouts, live casting, and phone-authored drafts after validation.

Conceptually, a spell contains:

- Element and required capabilities.
- Form or other element-specific realization.
- Parameters and modifiers.
- Pattern: how many instances exist and where they are placed.
- Orientation: how each instance faces.
- Motion: how each instance travels.
- Targeting and placement requirements.
- Execution requirements, costs, and lifetime behavior.

Orientation and motion remain separate. Interface layout and decorative signs never define spell meaning.

The existing `FSpellDefinition` is the starting contract for single spells. Additional requirements should extend that model through deliberate contracts rather than introducing a separate mobile or dimension-specific spell format. More complex sequences can later use a spell program referencing canonical spell blocks.

### 7.3 Prepared and live casting

**Prepared casting:** Construct or learn a spell → validate it → save a version → assign a slot → choose placement → cast.

**Live casting:** Start blank or load a prepared spell → modify a temporary construction through the spell table → see validity and cost → choose placement → commit the cast.

Editing a temporary construction does not change the saved spell until the player explicitly saves it. A cast uses a snapshot of its definition; editing the library during flight does not change an existing projectile.

Prepared and live versions of the same definition use the same cost and effect rules under the same conditions. Any modifier from equipment, knowledge, or context must be explicit rather than a hidden camera bonus.

### 7.4 Validation and safe failure

Validation checks structure, element support, player access, profile capabilities, parameter limits, placement, and available resources. Draft validation can show warnings; execution validation runs again against current world state.

An invalid draft remains editable. A rejected cast explains why, creates no partial effect, and does not spend its committed resource cost. The exact reservation and commit ownership is defined in [Function contracts](#14-functions-contracts-and-data-flow).

## 8. Equipment and persistent rewards

Every acquired item has one identity and a clear purpose in the shared world. Its presentation or available use can change with a dimension while its ownership, charges, durability, and upgrades remain consistent.

| Illustrative item | First-person use | Third-person use | Top-down use | Inner Module use |
| --- | --- | --- | --- | --- |
| Resonant shard | Detect a nearby physical clue | Focus a compatible prepared spell | Supply a supported modifier during composition | Inspect the discovered resonance rule |
| Pattern artefact | A world object to examine or equip where supported | Enable a prepared multi-instance spell | Enable live control of that pattern | Experiment with the same pattern definition |
| Stored spell recipe | Inspect its description where supported | Assign and cast a valid prepared spell | Load it as a starting construction | Edit and save a new version |

These examples show possible connected uses. An item does not need an action in every dimension. Unsupported uses are visible and explained; the item remains owned.

Every meaningful acquired artefact declares a primary world use or a clear improvement to an existing action, the profiles that support it, and its link to the shared gameplay loop. A specialist item explains its purpose; an item with several manifestations references the same identity throughout. A phone-earned item follows this same rule and cannot exist only as an isolated companion-game reward.

New interaction equipment or devices can be added as interfaces to these same contracts. A phone's touch controls may provide a unique activity, but its resulting spell, knowledge, or resource must have an explicit main-world use. Reward descriptions say what was gained and where it can be used.

## 9. Mana, analysis, and puzzle rewards

### 9.1 Resource model

The player needs mana for magical actions and may use it to support analysis or experimentation. A single resource authority owns balances and transactions, including rewards from phone activities.

**Proposed default:** Distinguish recoverable **active mana** used for casting from a bounded **stored mana reserve** used for optional analysis, experiments, or permitted replenishment. Both are world resources, visible on PC and phone. This protects a return to ordinary combat after spending resources on research.

Active mana has an in-world recovery path and a combat capacity. Phone rewards do not permanently multiply this capacity. Replenishment from reserve follows the same rules and limits as an equivalent in-world resource action; it cannot become an unlimited stream into active combat.

The two-pool model is a design proposal. Its required outcome is that research spending and phone participation never become prerequisites for normal combat readiness.

### 9.2 Knowledge analysis

An analysis request identifies the evidence being studied, the concept or relationship it can reveal, and its cost. The player can preview the expected outcome before confirming. Unsupported or already-completed analyses cannot silently consume resources.

Basic knowledge needed for the principal adventure has a direct gameplay route. Optional analysis can reveal deeper relationships, provide help, or advance an available discovery through another activity.

### 9.3 World-logic puzzles

Puzzles use concepts recognizable from the game. Possible families include arranging a valid pattern, matching an element to a supported operation, directing a simple flow, or balancing a small system. Each puzzle references the actual concept definitions it teaches.

Difficulty may increase through more relationships, fewer hints, tighter constraints, or optional time limits. The phone interface should make each operation intuitive through touch and immediate feedback.

**Proposed default challenge progression:** Discovering a relevant concept opens its puzzle family. Completing a challenge opens the next optional tier in that family, introducing a new relationship or tighter constraint. A separate timed challenge track can shorten available time and reward higher scores; it does not gate the untimed track or essential knowledge. Puzzle Activities owns these definitions, the player's challenge progression, and eligibility. Knowledge and Progression remains the owner of the underlying discoveries.

**Proposed default reward policy:** A valid solution earns a baseline reward. An optional quality or challenge score adds a bounded bonus. Faster solutions can contribute to that score only in an explicitly timed challenge. Untimed play remains worthwhile.

The reward service computes rewards from an identified puzzle version, a validated attempt, and its score. Repeated delivery of the same attempt grants the reward once. Replaying a puzzle remains allowed; economic gains follow a disclosed per-challenge reward allowance, with additional rewards for meaningful new challenges or achievements rather than compulsory repetition.

Exact values and score weights are balance data. Required properties are bounded rewards, a useful untimed path, no daily streak requirement, and equivalent resource-earning opportunities in the main world.

## 10. The phone and Inner Module

### 10.1 Supported activities

The phone provides an accessible inner workspace for:

- Reading discovered Codex entries and their relationships.
- Inspecting owned equipment and learned spells.
- Building or editing spell drafts with touch-friendly controls.
- Running bounded experiments with clear preview assumptions.
- Playing short puzzles grounded in world rules.
- Reviewing validated resource rewards and pending synchronization.

PC access to the Inner Realm covers the essential preparation and knowledge functions. Owning or using a phone is optional.

The puzzle track can feel like a distinct small game: intuitive touch operations, short rounds, growing challenge, and its own sense of improvement. Its rules still reference world concepts, and its usable rewards return to the shared player record.

### 10.2 Connected behavior

The PC and phone refer to one player identity and one authoritative progression record. The phone submits intended changes; the authority validates and records them. It does not maintain a competing resource balance or spawn a second outer-world character.

While the PC is active, the phone can read snapshots and edit drafts. Changes to an equipped combat loadout take effect through an explicit, valid application point, rather than replacing a spell midway through a cast. Reading the Codex or completing a puzzle never moves, pauses, or protects the active PC character.

### 10.3 Offline behavior and conflicts

**Proposed default:** Offline access supports cached knowledge, local drafts, and practice puzzles. Offline results can be queued as pending claims, but spendable rewards are credited only after validation. If reliable attempt validation is unavailable, the activity remains practice without a claimed reward.

Each saved spell has an identity and version. If PC and phone edit the same version independently, preserve both drafts and ask the player which revision to keep or combine. Resource and unlock conflicts are resolved by the authoritative transaction record rather than by choosing the newest device timestamp.

The Companion Gateway transports and validates device requests, then invokes the Spell Library's save and conflict-resolution contract. The library alone records spell versions and persistent conflicts; the gateway returns that result to the device.

A failed connection leaves the draft intact and shows its synchronization state. It does not revoke already-recorded knowledge or apply an uncertain reward twice.

The interface distinguishes offline practice from a reward-eligible challenge before the player starts. It never promises a spendable reward when the current connection or validation model cannot support that promise.

### 10.4 Hosting scope

The initial local prototype can have the PC host its authoritative state. A phone connected to that host can synchronize while it is available. Always-available rewards, synchronization while the PC is offline, accounts, and remote access would require a separate service design.

That service is a later development slice. The concept does not assume an existing backend, a persistent online world, or multiplayer.

## 11. Shared world state and time

The state that persists through gameplay dimensions includes character identity and location; health and mana; inventory and equipment; discoveries and gate access; saved spells and loadouts; world object state; active effects; cooldowns; and encounter state.

A change of profile affects how commands enter that world and what the interface reveals. It does not create fresh copies of state. Perception can reveal a relationship or make information easier to read, but does not silently change a material's physical properties.

**Shared-law test:** Given the same definition, resources, source, target, and world conditions, the committed action has the same consequence through every interface that is allowed to request it.

### 11.1 Time policy

**Proposed defaults:**

- Outer-world dimension transitions preserve the world's timeline; they do not rewind enemies or reset effects.
- In solo play, explicit entry into a safe Inner Realm session may pause the entire simulation. It must never freeze only the player while claiming that the world is paused.
- Phone-only activity does not pause an active world session.
- When the local game is closed, its world simulation is suspended. Offline phone preparation does not simulate unobserved dungeon progress.
- If multiplayer is later added, pausing and body safety require a new explicit session policy. The solo pause rule cannot be carried over silently.

The same-place-and-time promise means all active interfaces refer to the same current world and progression, with the above explicit session rules. It does not require the phone to render or continuously simulate the dungeon.

### 11.2 Defeat and restoration

Defeat, respawn, and checkpoint restoration belong to the shared session policy. A dimension switch cannot clear defeat, escape a committed consequence, or create a fresh version of an encounter. The detailed loss and checkpoint model can be designed with the encounter system; every profile must use that same model.

Resource balances, spent items, and reward receipts must restore consistently. Loading a world checkpoint cannot make an already-claimed phone reward available to claim again.

## 12. Core architecture and ownership

The architecture follows the project's existing rule:

> Core routes. Modules execute. Submodules extend.

The core identifies the appropriate owner, validates cross-system requests, and coordinates transitions or transactions. Individual modules implement their own rules. A single universal manager should not absorb magic, progression, physics, phone synchronization, and presentation.

### 12.1 Ownership map

Names marked “proposed” describe responsibilities; they do not imply that a corresponding implementation already exists.

| System | Owns | Consumes or depends on | Produces |
| --- | --- | --- | --- |
| World Session (proposed) | Session identity, world time policy, save coordination, command authority | Persistent domain snapshots and runtime world state | Valid session context, saved state, world events |
| Dimension Coordinator (proposed) | Active dimension and transition lifecycle | Progression eligibility, location policy, action state, gameplay profiles | Atomic profile changes and transition results |
| Gameplay Profiles (proposed extension) | Movement, inputs, targeting, presentation, action access | Dimension configuration and available capabilities | Typed player action requests |
| WorldCodex | Stable concept vocabulary, classification, supported relationships | Authored definitions and registered capabilities | Readable concept definitions and lookup results |
| Knowledge and Progression (proposed) | Player discoveries, gate conditions, unlocked routes and dimensions | Codex IDs, validated observations, equipment facts | Knowledge state, eligibility, unlock events |
| Spell Construction | Canonical definitions, graph validation, compilation, resolution | Supported concepts, element capabilities, construction input | Validated spell definitions and resolved spells |
| Spell Library and Loadout | Saved spell versions and prepared slot references | Validated definitions and ownership/access state | Stable prepared spell snapshots |
| Live Casting | Temporary combat composition | Available concepts, profile actions, prepared spell snapshots | Draft state and cast requests |
| Spell Execution | Final cast validation, placement, and effect creation | Resolved definition, world state, resource authorization, realizers | Committed effects and execution results |
| Element and World Simulation | Element-specific realization, motion, material and impact response | Committed effect definitions and physical state | World changes and observations |
| Inventory and Equipment (proposed) | Item ownership, upgrades, charges, supported uses | Item definitions and player actions | Equipment capabilities and item state |
| Resources and Rewards (proposed) | Mana balances, reservations, grants, spending history | Validated cast, analysis, and puzzle requests | Atomic resource results |
| Puzzle Activities (proposed) | Puzzle definitions, attempt evaluation, player challenge progression and eligibility | Codex concepts, discovered knowledge, puzzle rules | Available challenges, validated scores, reward recommendations |
| Inner Realm Presentation | Realm lifecycle, navigation, workbench and Codex interfaces | Read models and domain action interfaces | User requests and previews |
| Companion Gateway (proposed) | Device access, version checks, queued synchronization | World authority and explicitly exposed domain actions | Validated changes, conflicts, synchronization status |

“Spell Library and Loadout” includes a proposed durable library/versioning responsibility; the current prepared-slot subsystem is a foundation, not proof that persistence exists.

### 12.2 Dependency direction

```text
First person / Third person / Top down / Inner Realm / Phone
                              |
                      typed action requests
                              |
               session and dimension coordination
                              |
         domain owner: progression / spells / items / resources
                              |
                    execution and world simulation
                              |
                recorded results and observable events
                              |
                    all relevant interfaces update
```

Presentation reads state and requests actions. Domain systems never depend on a camera widget, screen layout, touch button, or particular physical key.

Library edits, knowledge records, and reward grants complete at their domain owner. Only actions that create or change simulated world effects continue into execution and simulation. Their recorded results still update every relevant interface.

Direct dependencies carry required data and commands. Events report completed facts to interested systems. A global event mechanism must not hide who owns or authorizes a mutation.

## 13. Nodes, classification, and relationships

### 13.1 A node is an identifiable piece of meaning

The project can organize concepts as connected nodes while keeping their responsibilities distinct.

| Node family | Represents | Examples of links |
| --- | --- | --- |
| Concept | A world rule, element, property, or operation | Supports, combines with, describes |
| Knowledge record | A player's relationship to a concept | Observed through, understood through |
| Dimension | A playable profile and access context | Uses profile, entered through, reveals |
| Gate or route | A progression connection | Requires knowledge, leads to dimension |
| Spell or spell-program block | A semantic construction | Uses concept, requires capability, emits effect |
| Item | Persistent equipment or reward | Grants capability, modifies operation |
| Puzzle or analysis | An activity that uses world logic | Teaches concept, evaluates rule, grants reward |
| Reward transaction | A validated state change | Earned from attempt, credited to player |

These families share stable references, but they do not all need the same class or execution model. A catalog category is an organizational label; it is not automatically an executable spell node.

### 13.2 Common definition metadata

An authored definition has a stable ID, a kind, a readable name and description, category tags, an owning system, supported or required capabilities where relevant, typed relationships, and a schema/content version. Runtime objects and player records reference these definitions while keeping their changing state separately.

Definitions describe available content. Player state describes ownership, discovery, resource balances, and active use. A global definition must not hold one player's unlock status.

Useful classification axes include subject, operation, supported element, input profile, learning complexity, combat role, and implementation status. Each axis has its own field; a single “level” must not mean all of them.

### 13.3 Relationship examples

| From | Relationship | To |
| --- | --- | --- |
| Earth concept | supports | Lift operation |
| Lift discovery | satisfies | Elemental gate condition |
| Elemental gate | unlocks | Third-person gameplay profile |
| Wall recipe | uses | Earth, compatible form, placement requirements |
| Third-person profile | permits | Cast prepared wall |
| Top-down profile | permits | Compose and cast a compatible wall live |
| Pattern puzzle | teaches | Pattern relationship |
| Validated puzzle attempt | grants through Resources and Rewards | Stored mana transaction |
| Phone draft | compiles into | A canonical spell definition |

The first gate can use an authored trial interaction before full elemental access. This trial is explicitly allowed by the discovery sequence; it does not require the player to possess the unlock they are trying to obtain.

### 13.4 Graph rules

Maintain separate graphs for progression routes, knowledge relationships, and spell composition. Their nodes can reference each other by ID. Each graph validates its own allowed edges.

Unlock prerequisites must have a reachable starting path and avoid circular dependencies. Knowledge relationships can be cyclic when describing reciprocal concepts. Executable spell graphs follow their compiler's structural rules; future repeating programs need explicit bounded execution rules.

The existing Codex Tier I/II/III classification describes spell structure. Dimension access and player progression require separate fields. See [Project alignment](#17-project-alignment).

## 14. Functions, contracts, and data flow

### 14.1 Function management

Each public action has one owner, an explicit request shape, defined validation, a clear result, and a stated effect on persistent state. Names below are illustrative contracts rather than claims about existing APIs.

| Action | Owner | Key checks | Result |
| --- | --- | --- | --- |
| `RequestDimensionTransition` | Dimension Coordinator | Unlock, compatible location, safe action boundary | New active profile or a reason for rejection/deferment |
| `RecordObservation` | Knowledge and Progression | Valid world event, concept reference, evidence rules | Recorded evidence and any resulting discovery |
| `AnalyzeConcept` | Knowledge and Progression | Evidence, supported analysis, resource reservation | Recorded analysis outcome plus committed spending, or no change |
| `SaveSpellDraft` | Spell Library | Construction validation result, concept access, base version | Saved version, editable draft warnings, or conflict |
| `AssignPreparedSpell` | Spell Library and Loadout | Owned version, valid slot, profile compatibility | Updated slot reference at a valid application point |
| `TryCast` | Spell Execution | Snapshot validity, current access, placement, resources | Committed effect and cost, or a clear rejection |
| `UseEquipment` | Inventory and Equipment | Ownership, applicable use, charges, target | Item-backed action and consistent item state |
| `SubmitPuzzleAttempt` | Puzzle Activities | Puzzle/version, valid solution, attempt identity | Recorded score and an identified reward request |
| `GrantPuzzleReward` | Resources and Rewards | Validated score, reward allowance, prior transaction | One recorded reward result |
| `SyncDraft` | Companion Gateway | Player access, schema support, source version | The Spell Library's accepted revision/conflict result, or pending state |

Public readers return snapshots or query results. Public commands change state through the owner. Modules do not modify another module's private fields.

Repeated delivery of an identified external request must not duplicate its effect. Events such as `KnowledgeDiscovered`, `DimensionUnlocked`, `SpellSaved`, `CastCommitted`, and `RewardGranted` describe results after acceptance.

### 14.2 Casting flow

```text
Prepared slot / live spell table / validated saved construction
                         |
              canonical definition snapshot
                         |
            resolve capabilities and parameters
                         |
         validate current access, target, and placement
                         |
             reserve the required resource cost
                         |
          prepare effect creation and commit the cast
                         |
          pattern + orientation + motion + element
                         |
                 world simulation and response
```

Spell Execution coordinates resource reservation and effect creation. A successful commit records the cost and effect as one logical action. A failure releases the reservation and leaves no partially committed effect. A retried request returns its prior outcome rather than spawning another effect.

The same transaction principle applies to analysis and consumable equipment: the responsible action owner coordinates the resource or inventory change with its outcome.

Spell Library owns persistence of a draft and calls Spell Construction for validation. Puzzle Activities owns evaluation; Resources and Rewards owns the resulting economic transaction. Retrying a completed evaluation can resume or retrieve the same reward request without duplicating the grant.

### 14.3 Discovery and gate flow

World event → validated observation → player knowledge update → gate condition evaluation → route unlocked → relevant interfaces refresh.

Unlocking a gate does not force an immediate dimension switch. The player decides when to enter, subject to the transition contract.

### 14.4 Phone reward flow

Identified puzzle attempt → rule evaluation → reward allowance check → unique transaction → authoritative reserve update → PC and phone receive the same result.

The puzzle screen displays the result; it does not directly write the mana balance. Retries after a connection loss return the already-recorded transaction.

### 14.5 Extension contract

Adding an element, dimension, item family, or puzzle requires its definition, declared capabilities, responsible handlers, validation rules, presentation entry points, and focused verification. Existing systems discover registered capabilities through explicit interfaces.

An extension should not require unrelated camera code, UI categories, or physics modules to acquire its gameplay meaning. New categories improve navigation; registered handlers implement behavior.

## 15. A connected gameplay example

This example is illustrative content built around earth, the current project's strongest foundation.

1. **First-person arrival.** The player enters a chamber with movable stones, a blocked route, and a resonant artefact. A physical interaction provides a useful immediate solution and reveals a clue about earth manipulation.
2. **A small discovery.** A clearly introduced trial allows the player to make one stone react. Successful interaction records the elemental relationship and opens a dimensional gate.
3. **Third-person entry.** The gate activates direct WASD movement with a small prepared magic loadout. The player lifts or shapes earth through simple actions and learns why those effects work.
4. **A useful construction.** In the Inner Realm, the player turns a simple earth form into a wall spell. The saved version becomes a prepared action for third-person encounters.
5. **Optional further understanding.** A short experiment demonstrates a pattern relationship. It opens access to top-down play without requiring mastery of every element.
6. **A new gameplay instrument.** Mouse movement frees the keyboard for the spell table. The player can cast the saved wall immediately or alter its pattern live to fit the encounter.
7. **A connected phone activity.** Later, the player experiments with the discovered pattern on the phone or completes an untimed related puzzle. A draft returns to the spell library after validation; an earned mana reward enters the shared reserve once.
8. **Return by choice.** The player returns to third person with a compatible prepared result, or to first person for its exploration and supported tools. The gate, discoveries, equipment, damage to the chamber, and remaining resources persist.

For a wall cast with the same definition and placement in third person or top down, the wall has the same cost, structure, collision, and lifetime. A player making a larger live version pays the cost associated with that changed definition.

## 16. Readability, balance, and accessibility

The player should be able to answer four questions at any moment: what can I do here, what will it cost, why did it work or fail, and what interesting possibility can I try next?

### 16.1 Readability rules

- Introduce concepts through observable effects and short practical interactions.
- Reveal relevant options progressively; allow experienced players to expand the interface deliberately.
- Show compatible next operations, estimated costs, and missing requirements during construction.
- Distinguish saved spells, temporary drafts, active effects, and unsynchronized changes visually and verbally.
- Explain unavailable equipment or dimensions without removing their records from view.
- Keep a dependable prepared option available during a new casting tutorial.

### 16.2 Optional intensity

Timed puzzles, large compositions, and simultaneous effect management are optional sources of challenge. Untimed learning, prepared casting, and focused specialization receive meaningful rewards.

An advanced spell may be stronger in a particular situation because it spends more resources, uses a suitable form, or coordinates several effects. Complexity alone does not justify a universal power bonus. Encounters should value different strengths without requiring rapid switching through every profile.

### 16.3 Accessibility

Bindings are remappable. Essential commands support alternatives to demanding holds or rapid sequences. Spell-table layouts can expose a small subset first. Clear text accompanies signs and color cues. Tutorials demonstrate both controls and the underlying world relationship.

Input accommodations can preserve a dimension's available operations and decision structure. Camera preference or remapping must not accidentally bypass knowledge, equipment, or action-access rules.

## 17. Project alignment

This section connects the design to the inspected Unreal project. The documents and source provide foundations; they do not establish that POWR SCALE is already implemented.

Primary architecture reference: [Architecture V1](../../ARCHITECTURE_V1.md).

| Existing foundation | Relevant role | Additional work required by this design |
| --- | --- | --- |
| [PlayerViewModes](../../../Plugins/PlayerViewModes/Source/PlayerViewModes/Public/PlayerViewModeSubsystem.h) | Third-person/top-down view and movement foundations | First-person profile, complete profile contracts, progression access, coordinated transitions |
| [InnerRealm](../../../Plugins/InnerRealm/Source/InnerRealm/Public/InnerRealmSubsystem.h) | Realm lifecycle and access to preparation interfaces | Explicit session time policy, narrower page responsibilities as needed, companion-facing domain access |
| [WorldCodex](../../../Plugins/WorldCodex/Source/WorldCodex/Public/WorldCodexTypes.h) | Concept IDs, classification, capabilities, relationships | Separate player discovery state and gate evaluation; keep structural tiers distinct from progression |
| [SpellCreation](../../../Plugins/SpellCreation/Source/SpellCreation/Public/SpellDefinition.h) | Canonical spell definitions and resolution | Additional explicit access/cost/execution contracts where required |
| [SpellGraphCompiler](../../../Plugins/SpellGraph/Source/SpellGraph/Public/SpellGraphCompiler.h) | Translate semantic construction into a spell definition | Capability-based expansion and later bounded multi-block programs |
| [SpellLoadout](../../../Plugins/SpellLoadout/Source/SpellLoadout/Public/SpellLoadoutSubsystem.h) | Prepared spell slots | Durable library/versioning, persistence, profile compatibility |
| [LiveSpellCasting](../../../Plugins/LiveSpellCasting/Source/LiveSpellCasting/Public/LiveSpellSessionSubsystem.h) | Temporary construction and prepared-spell loading | A teachable keyboard spell table and explicit gameplay-profile access |
| [SpellCastingBindings](../../../Plugins/SpellCastingBindings/Source/SpellCastingBindings/Public/SpellCastingBindingSubsystem.h) | Configurable casting actions with top-down-gated live input | Broader spell-table presentation, discoverable bindings, and coordinated input/profile enforcement |
| [SpellExecution](../../../Plugins/SpellExecution/Source/SpellExecution/Public/SpellExecutionSubsystem.h) | Final execution boundary | Authoritative resource transactions and context validation |
| [EarthMagic](../../../Plugins/EarthMagic/Source/EarthMagic/Public/EarthSpellSpawner.h) | Earth realization | Use as the first element; introduce other elements through their own supported capabilities |
| [SpellPattern](../../../Plugins/SpellPattern/Source/SpellPattern/Public/SpellPatternResolver.h) and [SpellMotion](../../../Plugins/SpellMotion/Source/SpellMotion/Public/SpellMotionResolver.h) | Placement, orientation, and travel foundations | Preserve their separate meanings across every construction method |
| [ImpactSystem](../../../Plugins/ImpactSystem/Source/ImpactSystem/Public/ImpactSolver.h) and [PhysicalBody](../../../Plugins/PhysicalBody/Source/PhysicalBody/Public/PhysicalBodyState.h) | Shared physical response | Continue receiving world effects independently of the player's profile |

New responsibilities include dimension progression, player knowledge persistence, inventory/equipment integration, mana economy, puzzle evaluation, companion synchronization, and a complete session/save policy. These should be designed as focused additions rather than placed wholesale inside the Inner Realm or Codex.

Current control behavior already offers prepared slots in both outer-world views and gates live construction keys to top down. It does not yet enforce complete gameplay-profile rules: a live construction can survive a return to third person and remain castable. The proposed transition and execution contracts must explicitly close that gap. Existing player freezing in the Inner Realm also does not establish the proposed whole-session pause policy.

The current project is earth-first. Other elements, phone connectivity, a complete first-person mode, and the proposed progression/economy must be treated as future work until verified in an implementation.

## 18. Development slices and verification

This document is an overall design. Each substantial slice needs a focused implementation specification; the list below gives order and completion evidence rather than a code task plan.

| Slice | Scope | Evidence that it works |
| --- | --- | --- |
| 1. Shared-world proof | One room, one character, one element, first-person/third-person/top-down profiles | Controls change coherently; the same world objects, resources, and effects persist |
| 2. Discovery and access | One elemental discovery, one simple gate per introduced profile, return paths, saved knowledge | A player learns by doing, unlocks access, returns freely, and retains it after loading |
| 3. Prepared and live magic | A small workbench, saved wall/projectile, limited keyboard spell table | The same definition behaves consistently; both prepared and live play are enjoyable |
| 4. Optional depth and economy | A focused equipment reward, mana recovery/reserve, one analysis, one untimed puzzle with optional challenge | Ordinary play remains viable; rewards and spending are recorded once |
| 5. Companion proof | Phone-readable Codex, one editable draft, version conflict handling, validated reward synchronization | Both devices show consistent results; failed connections preserve drafts and avoid duplicated rewards |
| 6. Broader scale | More content, carefully introduced elements, optional multi-effect programs | New content extends explicit contracts without breaking simpler styles |

For the first slice, transition access can be temporarily available through a clearly identified test mechanism. The authored discovery gates arrive in the second slice. Cross-device infrastructure waits until the core control schemes and shared spell behavior are proven useful.

### 18.1 Required verification scenarios

| Scenario | Expected result |
| --- | --- |
| Enter third person | WASD moves the character; prepared casting and targeting use the active profile. |
| Enter top down | Mouse movement and targeting remain distinguishable; the keyboard spell table handles live composition. |
| Request a locked dimension | The current profile remains active and a specific missing requirement is shown. |
| Switch while an earth projectile is active | One projectile continues with the same definition and remaining lifetime. |
| Transition during an action commitment | The request follows the declared defer/reject rule, with no duplicated cast or resource refund. |
| Carry an unprepared live draft into third person | The draft is retained but cannot be cast as a prepared slot until saved, validated, and equipped. |
| Cast the same definition through two supported profiles | Equivalent starting conditions produce the same cost and world effect. |
| Use an invalid live construction | The draft remains editable; no effect or committed cost is produced. |
| Return to an earlier dimension | Knowledge and inventory remain; usable actions follow that profile. |
| Play with a small prepared loadout | The designed principal route remains enjoyable without live construction or a phone. |
| Follow a principal objective in each unlocked preferred profile | Each has a viable authored solution; advanced dimension unlocks remain optional. |
| Skip timed puzzle challenges | A worthwhile untimed activity and fair in-world resource path remain available. |
| Complete a puzzle-family tier | The next eligible challenge opens; a timed score is not required for the untimed track. |
| Deliver one puzzle result twice | Only one reward transaction is credited. |
| Edit one spell independently on PC and phone | Both revisions survive; neither silently overwrites the other. |
| Open the phone during active PC play | The outer-world character does not freeze, move, or become protected. |
| Save and reload | Profile access, knowledge, spells, items, gates, and resource balances remain consistent under the session save contract. |
| Restore a checkpoint after a phone reward | Resource restoration respects the recorded claim; the reward cannot be claimed twice. |
| Inspect an unsupported element operation | The interface explains the capability mismatch and does not force it through earth's implementation. |

Verification combines targeted state/contract tests with observed play sessions. Feel, clarity, and whether simple play remains fun require player-facing evaluation rather than only automated checks.

## 19. Decision register and concept coverage

### 19.1 Established direction

- Dungeon floors introduce dimensions within one connected world.
- The player begins in first person and can unlock further ways to play.
- Third person uses direct WASD movement and prepared, constructed spells.
- Top down uses mouse movement and a keyboard spell table for more direct live composition.
- Primitive elemental understanding leads toward optional deeper construction and control.
- Players can continue enjoying a simpler dimension or action set.
- The Inner Module can extend onto a phone with intuitive, world-related activities.
- Puzzle performance can provide mana that has a meaningful world use.
- Equipment, knowledge, spells, and rewards belong to the connected world.
- The core needs clear nodes, classification, ownership, and reusable function contracts.

### 19.2 Proposed defaults to test

| Decision | Baseline in this document | Why it is proposed |
| --- | --- | --- |
| Spatial relationship | Gates introduce dimensions; unlocked profiles work in compatible areas | Preserves meaningful dungeon discoveries and revisiting |
| Preferred-style route | Principal objectives have a viable solution in each unlocked outer-world profile | Makes continued play in a preferred dimension an explicit content commitment |
| First-person magic after discovery | An explicitly supported subset, rather than automatic access to every spell | Protects the dimension's intended gameplay |
| Transition timing | Explicit switch between committed actions with consistent transition time | Preserves control clarity and resource continuity |
| Live-casting time | Real time with readable previews, small starting choices, and prepared options | Preserves active composition while allowing gradual learning |
| Knowledge thresholds | A few demonstrated fundamentals open early dimensions | Supports discovery without mandatory study or repetition |
| Resource structure | Recoverable active mana plus bounded stored reserve | Connects research and phone rewards while protecting ordinary play |
| Puzzle scoring | Useful completion reward plus a bounded optional challenge bonus | Allows both relaxed play and higher-intensity improvement |
| Puzzle progression | Discovered concepts open families; completion opens harder optional tiers | Gives the companion game growth connected to world understanding |
| Phone identity | Companion surface with distinct puzzle gameplay, not a character dimension transition | Supports simultaneous use without changing the active world profile |
| Solo Inner Realm | Explicit safe entry can pause the whole local simulation | Makes preparation comfortable with a clear time rule |
| Offline phone use | Cached reading, drafts, and practice; validated claims before spending | Preserves usefulness and consistent authority |
| Early hosting | Local PC authority; remote service designed as a later slice | Avoids assuming an existing online infrastructure |
| Initial element | Earth | Builds the first proof on inspected project foundations |

### 19.3 Coverage map

| Original concept | Where it is defined | Main system link |
| --- | --- | --- |
| Floors are dimensions | [World and scale](#2-world-floors-dimensions-and-scale) | Gate → dimension → gameplay profile |
| Start in first person | [First-person play](#31-first-person-physical-discovery) | Exploration → observation → knowledge |
| Third-person primitive magic | [Third-person play](#32-third-person-embodied-elemental-magic) | Knowledge → prepared spell → execution |
| Mouse movement frees a spell keyboard | [Top-down play](#33-top-down-live-construction-and-coordination) | Profile → input actions → live construction |
| Fundamentals unlock new possibilities | [Progression](#6-knowledge-gates-and-progression) | Evidence → understanding → gate conditions |
| More knowledge allows more control | [Magic](#7-elements-spells-and-construction) | Capability access → valid combinations → effects |
| Simple play remains pleasurable | [Player freedom](#5-player-loops-and-freedom-of-play) | Content routes + prepared loadouts + fair rewards |
| Phone as an inner module | [Phone design](#10-the-phone-and-inner-module) | Companion gateway → shared domain owners |
| Puzzles grow in difficulty and award mana | [Mana and puzzles](#9-mana-analysis-and-puzzle-rewards) | Puzzle attempt → evaluation → resource transaction |
| Mana supports knowledge analysis | [Knowledge analysis](#92-knowledge-analysis) | Evidence + resource reservation → recorded discovery |
| New equipment has world use | [Equipment](#8-equipment-and-persistent-rewards) | Persistent item → supported profile operations |
| One place, time, and shared laws | [Shared state](#11-shared-world-state-and-time) | One session authority → consistent world consequences |
| Clean nodes and categorization | [Nodes and relationships](#13-nodes-classification-and-relationships) | Stable IDs + typed links + separate graph meanings |
| Clean function management | [Contracts and flow](#14-functions-contracts-and-data-flow) | Request → owner → validation → committed result |
| Expand through the same logic at another scale | [Extension contract](#145-extension-contract) | New profiles and capabilities → existing shared contracts |

