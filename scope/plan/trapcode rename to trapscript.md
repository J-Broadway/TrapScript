# TrapCode → TrapScript Rename Plan

## Overview

Rename the library from "TrapCode" to "TrapScript" to avoid trademark conflicts with Red Giant Maxon's Trapcode product suite.

**Naming Convention:**
- Library name: `TrapCode` → `TrapScript`
- Module name: `trapcode` → `trapscript`
- Import alias: `tc` → `ts`
- Internal prefixes: `[TrapCode]` → `[TrapScript]`

---

## Phase 1: Core Library Rename

### 1.1 Rename Main File
- [ ] `trapcode.py` → `trapscript.py`

### 1.2 Update Internal References in `trapscript.py`

All log/print prefixes and comments:
- [ ] `[TrapCode]` → `[TrapScript]` (print statements, log messages)
- [ ] `[TrapCode:category]` → `[TrapScript:category]` (debug logging)
- [ ] Comments referencing "TrapCode"

Locations to update:
```
Line 20:  print(f"[TrapCode]{where} ...")
Line 41:  print(f"[TrapCode:{category}] {msg}")
Line 94:  print(f"[TrapCode] pulse on_click error: ...")
Line 142: print(f"[TrapCode] changed callback error: ...")
Line 807: print("[TrapCode] Reminder: Call tc.update()...")
Line 2611: print("[TrapCode] Initialized")
```

---

## Phase 2: Example/Boilerplate Files

### 2.1 Update `default (trapcode).py`
- [ ] Rename file: `default (trapcode).py` → `default (trapscript).py`
- [ ] Update import: `import trapcode as tc` → `import trapscript as ts`
- [ ] Update all `tc.` references → `ts.`

### 2.2 Update `scope/scope.py`
- [ ] Update import: `import trapcode as tc` → `import trapscript as ts`
- [ ] Update all `tc.` references → `ts.`

### 2.3 Update `scope/test.py`
- [ ] Update import: `import trapcode as tc` → `import trapscript as ts`
- [ ] Update all `tc.` references → `ts.`

---

## Phase 3: Documentation

### 3.1 Update `README.md`

Full search/replace needed:
- [ ] "TrapCode" → "TrapScript" (title, descriptions)
- [ ] "trapcode" → "trapscript" (file references, imports)
- [ ] `tc.` → `ts.` (all code examples)
- [ ] `import TrapCode as tc` → `import TrapScript as ts`
- [ ] `TrapCode.py` → `TrapScript.py` (file references)
- [ ] `[TrapCode]` → `[TrapScript]` (log output examples)

Key sections to review:
- Title and intro
- Installation instructions (FL Studio path)
- All code examples throughout (~100+ occurrences of `tc.`)
- Debug logging section
- Any URLs or references

### 3.2 Update Planning/Research Docs (Optional)

These are internal docs, lower priority:
- [ ] `scope/plan/*.md` - Update if referencing tc/trapcode
- [ ] `scope/research docs/*.md` - Update if referencing tc/trapcode
- [ ] `scope/helper docs.md` - Update if referencing tc/trapcode

---

## Phase 4: Cursor Configuration

### 4.1 Update `.cursor/rules/trapcode-workflow.mdc`
- [ ] Rename file: `trapcode-workflow.mdc` → `trapscript-workflow.mdc`
- [ ] Update all "TrapCode" → "TrapScript" references
- [ ] Update "`scope.py` is the working environment for TrapCode" → TrapScript

### 4.2 Update `.cursor/skills/update/SKILL.md`
- [ ] Update title: "Update TrapCode" → "Update TrapScript"
- [ ] Update description
- [ ] Update command: `cp trapcode.py` → `cp trapscript.py`
- [ ] Update all references

### 4.3 Update `.cursor/commands/*.md` (if any reference trapcode)
- [ ] Check `phase1.md`, `dialogue.md` for references

---

## Phase 5: Git/Repository (Post-Rename)

### 5.1 Rename Repository
- [ ] Rename local folder: `TrapCode/` → `TrapScript/`
- [ ] Rename GitHub repo (Settings → General → Repository name)
- [ ] Update local remote URL: `git remote set-url origin <new-url>`
- [ ] Update any external references (if published)

### 5.2 Commit Strategy
Option A: Single atomic commit
Option B: Staged commits (library → docs → config)

Recommended: Single atomic commit with message:
```
Rename TrapCode to TrapScript

- Avoid trademark conflict with Red Giant Maxon's Trapcode suite
- trapcode.py → trapscript.py
- tc → ts import alias
- Updated all documentation, examples, and cursor config
```

---

## Verification Checklist

After rename, verify:
- [ ] `import trapscript as ts` works
- [ ] All `ts.` API calls function correctly
- [ ] Debug output shows `[TrapScript]` prefix
- [ ] README renders correctly with new naming
- [ ] Cursor rules load properly
- [ ] /update skill deploys `trapscript.py` to FL Studio

---

## Reference: Files to Modify

| File | Changes |
|------|---------|
| `trapcode.py` → `trapscript.py` | Rename + internal strings |
| `default (trapcode).py` → `default (trapscript).py` | Rename + imports |
| `scope/scope.py` | Import + all `tc.` refs |
| `scope/test.py` | Import + all `tc.` refs |
| `README.md` | ~200+ replacements |
| `.cursor/rules/trapcode-workflow.mdc` → `trapscript-workflow.mdc` | Rename + content |
| `.cursor/skills/update/SKILL.md` | Content updates |

---

## Notes

- The `ts` alias maintains the same brevity as `tc` (2 characters)
- "TrapScript" is more descriptive: references trap music + VFX Script
- All API signatures remain unchanged—only naming/branding changes
- No breaking changes to functionality
