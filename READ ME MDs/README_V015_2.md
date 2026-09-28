# AMADEUS Gameplay v0.15.2
## Architecture Cleanup Phase 3A — Presentation Source Split

Requires the working **v0.15.1 Generic Workbench**.

This is deliberately a behavior-preserving refactor.

The goal is to stop `InnerRealmSubsystem.cpp` from being the implementation
home for every UI system before we introduce new spell features.

## New source layout

```text
InnerRealm/
└── Source/InnerRealm/
    ├── Public/
    │   └── InnerRealmSubsystem.h
    │
    └── Private/
        ├── InnerRealmSubsystem.cpp
        │      realm lifecycle/orchestration
        │
        └── UI/
            ├── InnerRealmShellUI.cpp
            │      navigation + ready slots
            │
            ├── InnerRealmPageHost.cpp
            │      page construction / teardown
            │
            ├── SpellWorkbenchUI.cpp
            │      Workbench presentation helpers
            │
            ├── CodexUI.cpp
            │      Codex presentation helpers
            │
            └── RuneCanvasUI.cpp
                   Canvas layout/rendering
```

## Important

These are still member functions of `UInnerRealmSubsystem` in this phase.
Implementation is physically separated first because that is the lowest-risk
migration.

The next Phase 3 step can introduce dedicated page objects/state models without
simultaneously moving thousands of lines and changing behavior.

## No behavior changes intended

This patch does not change spell data, graph semantics, Codex vocabulary,
loadout behavior, pattern/motion logic, physics, or Canvas design.
