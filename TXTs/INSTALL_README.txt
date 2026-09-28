AMADEUS UNREAL TOOLS v1.2

FIX
Your selected terrain is LandscapeStreamingProxy, which means the Open World map splits the terrain into streaming pieces. v1.1 could successfully set the property on the one selected proxy, but that is not sufficient to reliably refresh/change the visible full landscape.

v1.2:
- Finds the parent Landscape.
- Finds all loaded streaming proxies belonging to it.
- Uses Unreal's landscape-specific editor material setter when exposed.
- Refreshes the landscape components/viewport.
- Uses a brand-new material asset M_AMADEUS_Earth_v12 so an older cached material cannot interfere.

INSTALL
1. Close Unreal Editor.
2. Extract this ZIP directly into D:\TESTUNREALPROJECT\
3. Replace the files in Content\Python when asked.
4. Reopen the project.
5. Select any piece of the large terrain.
6. Tools -> AMADEUS -> Make Selected Ground Earth
7. Press Ctrl+S.

If the ground still does not turn brown:
Tools -> AMADEUS -> Inspect Selected Actor
Send a screenshot of that dialog. v1.2 reports the current Landscape Material and whether the dedicated landscape setter is available.
