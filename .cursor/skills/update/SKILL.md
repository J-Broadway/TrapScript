---
name: update
description: Deploy trapscript.py to FL Studio's Python Lib folder. Use when the user says /update or asks to deploy/copy trapscript to FL Studio.
---

# Update TrapScript

Deploy `trapscript.py` to FL Studio's Python Lib folder.

## Command

Run this command to copy trapscript.py:

```bash
cp trapscript.py "/Applications/FL Studio 2025.app/Contents/Resources/FL/Shared/Python/Lib/"
```

## After Deployment
- Make sure README.md is updated (for trapscript.py)
- Remind the user to recompile their script in VFX Script (click Compile) to load the updated library.
- If this is the first deploy after the rename, also remove the old trapcode.py:

```bash
rm "/Applications/FL Studio 2025.app/Contents/Resources/FL/Shared/Python/Lib/trapcode.py"
```
