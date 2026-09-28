# v0.13.0.1 Dependency Cycle Fix

The build log reported:

`SpellPreview -> PlayerViewModes -> InnerRealm -> SpellPreview`

Patch 1 accidentally made `InnerRealm` depend on `SpellPreview` so it could switch
the Workbench preview on/off. That violates the intended observer boundary.

This fix reverses that relationship:

- InnerRealm owns TAB realm/editor/reference-model state.
- SpellPreview depends on/observes InnerRealm.
- SpellPreview checks `InnerRealm::IsActive()` and finds the realm actor to get
  the Workbench preview reference transform.
- InnerRealm no longer includes, calls, or declares a plugin dependency on
  SpellPreview.

No gameplay behavior is intentionally changed.

Install over v0.13 and run `APPLY_AND_REBUILD_V013_0_1.bat`.
