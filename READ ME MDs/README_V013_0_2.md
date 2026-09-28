# v0.13.0.2 — SpellParameterRanges compatibility fix

The current local project is ahead of the pushed GitHub repository.

The build log proves Desktop GPT's cleanup is already present locally:
- SpellExecution is being compiled.
- The old LiveSpellRanges header has been removed.
- The cleanup plan moved those ranges into SpellCreation as SpellParameterRanges.

Patch 1 was built from the last pushed GitHub code, so its replacement
SpellPreviewSubsystem.cpp accidentally restored:

    #include "LiveSpellRanges.h"
    LiveSpellRanges::

This patch converts those references to:

    #include "SpellParameterRanges.h"
    SpellParameterRanges::

No gameplay behavior is changed.
