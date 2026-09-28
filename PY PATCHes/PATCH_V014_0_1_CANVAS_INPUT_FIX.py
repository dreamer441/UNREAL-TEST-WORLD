from pathlib import Path

ROOT = Path(__file__).resolve().parent
CPP = ROOT / "Plugins/InnerRealm/Source/InnerRealm/Private/InnerRealmSubsystem.cpp"

if not CPP.exists():
    raise RuntimeError(f"Expected file missing: {CPP}")

text = CPP.read_text(encoding="utf-8").replace("\r\n", "\n")

old = '''        .Visibility_Lambda([this]()
        {
            return (ActivePage == EInnerRealmPage::Spell ||
                    ActivePage == EInnerRealmPage::Canvas)
                ? EVisibility::Visible
                : EVisibility::Collapsed;
        })
        .HAlign(HAlign_Right)'''

new = '''        .Visibility_Lambda([this]()
        {
            // The preview is display-only. When Rune Canvas is open it sits
            // above the Canvas in the viewport Z-order, so Visible would put
            // its full-screen root into the hit-test path and swallow clicks
            // intended for Canvas buttons underneath.
            //
            // HitTestInvisible keeps the 3D preview/frame visible while
            // allowing pointer input to pass through to the Rune Canvas.
            return (ActivePage == EInnerRealmPage::Spell ||
                    ActivePage == EInnerRealmPage::Canvas)
                ? EVisibility::HitTestInvisible
                : EVisibility::Collapsed;
        })
        .HAlign(HAlign_Right)'''

if new in text:
    print("v0.14.0.1 preview hit-test fix is already present.")
elif old in text:
    text = text.replace(old, new, 1)
    CPP.write_text(text, encoding="utf-8", newline="\n")
    print("v0.14.0.1 Rune Canvas input fix applied.")
else:
    raise RuntimeError(
        "Could not find the v0.14.0 PreviewFrame visibility block. "
        "Send the current InnerRealmSubsystem.cpp around PreviewFrameWidget."
    )
