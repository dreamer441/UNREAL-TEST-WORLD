from pathlib import Path

ROOT = Path(__file__).resolve().parent
CPP = ROOT / "Plugins/InnerRealm/Source/InnerRealm/Private/InnerRealmSubsystem.cpp"

if not CPP.exists():
    raise RuntimeError(f"Expected file missing: {CPP}")

text = CPP.read_text(encoding="utf-8").replace("\r\n", "\n")

old = '''                            return FText::FromString(FString::Printf(
                                SelectedCodexConcept == EntryId
                                    ? TEXT("[ %s ]  %s")
                                    : TEXT("  %s    %s"),
                                *CurrentEntry->Sign.Glyph,
                                *CurrentEntry->DisplayName.ToString()));'''

new = '''                            if (SelectedCodexConcept == EntryId)
                            {
                                return FText::FromString(FString::Printf(
                                    TEXT("[ %s ]  %s"),
                                    *CurrentEntry->Sign.Glyph,
                                    *CurrentEntry->DisplayName.ToString()));
                            }

                            return FText::FromString(FString::Printf(
                                TEXT("  %s    %s"),
                                *CurrentEntry->Sign.Glyph,
                                *CurrentEntry->DisplayName.ToString()));'''

if new in text:
    print("v0.13.4.1 fix is already present.")
elif old in text:
    text = text.replace(old, new, 1)
    CPP.write_text(text, encoding="utf-8", newline="\n")
    print("v0.13.4.1 Codex format-string fix applied.")
else:
    raise RuntimeError(
        "Could not find the expected Codex label block. "
        "Send the current InnerRealmSubsystem.cpp around line 1400."
    )
