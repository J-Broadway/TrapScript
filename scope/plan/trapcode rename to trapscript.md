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
- [ ] `import trapcode as tc` → `import trapscript as ts`
- [ ] `trapcode.py` → `trapscript.py` (file references)
- [ ] `[TrapCode]` → `[TrapScript]` (log output examples)

Key sections to review:
- Title and intro
- Installation instructions (FL Studio path)
- All code examples throughout (~100+ occurrences of `tc.`)
- Debug logging section
- Any URLs or references

### 3.2 Update `.gitignore`
- [ ] Update comment: `# Strudel experiments (not part of TrapCode)` → `TrapScript`

### 3.3 Update `scope/todo.md`
- [ ] Update all `tc.` references → `ts.`

### 3.4 Update Planning/Research Docs

Files with references to update:
- [ ] `scope/plan/debugging_system.md` - Multiple `tc.` and `[TrapCode]` refs
- [ ] `scope/plan/voice_triggering_questions.md`
- [ ] `scope/plan/voice_triggering.md`
- [ ] `scope/plan/strudel_mini_notation.md`
- [ ] `scope/plan/pattern state access/pattern_state_acces.md`
- [ ] `scope/plan/phase1/phase1.3_chord_symbols.md`
- [ ] `scope/plan/phase1/finished/phase1_tier1_implementation.md`
- [ ] `scope/plan/phase1/finished/phase1.2_note_representations.md`
- [ ] `scope/plan/archive/voice_triggering_questions.md`
- [ ] `scope/research docs/studel/Python Implementation of Strudle's Mini-Notation.md`
- [ ] `scope/research docs/archive/strudel_supercollider_research.md`

---

## Phase 4: Cursor Configuration

### 4.1 Update `.cursor/rules/trapcode-workflow.mdc`
- [ ] Rename file: `trapcode-workflow.mdc` → `trapscript-workflow.mdc`
- [ ] Update all "TrapCode" → "TrapScript" references
- [ ] Update "`scope.py` is the working environment for TrapCode" → TrapScript

### 4.2 Update `.cursor/skills/update/SKILL.md`
- [ ] Update title: "Update TrapCode" → "Update TrapScript"
- [ ] Update description in frontmatter
- [ ] Update command: `cp trapcode.py` → `cp trapscript.py`
- [ ] Add cleanup step for old `trapcode.py` in FL Studio Lib folder
- [ ] Update all references

### 4.3 Update `.cursor/commands/*.md` (if any reference trapcode)
- [ ] Check `phase1.md`, `dialogue.md` for references

---

## Phase 5: Git/Repository

### 5.1 Commit Strategy

**Recommended: Single atomic commit**

Commit message:
```
Rename TrapCode to TrapScript

- Avoid trademark conflict with Red Giant Maxon's Trapcode suite
- trapcode.py → trapscript.py
- tc → ts import alias
- Updated all documentation, examples, and cursor config
```

### 5.2 Push and Rename GitHub Repository

**Order of operations (important):**
1. Complete all file renames and content updates
2. Commit changes locally
3. Push to current `TrapCode` repo on GitHub
4. Rename repo on GitHub: Settings → General → Repository name → `TrapScript`
5. Update local remote URL:
   ```bash
   git remote set-url origin https://github.com/J-Broadway/TrapScript.git
   ```
6. (Optional) Rename local folder: `TrapCode/` → `TrapScript/`

**Notes:**
- GitHub automatically redirects old URLs to new repo name
- Local folder name doesn't need to match repo name (git works regardless)

### 5.3 FL Studio Cleanup
- [ ] After first deploy of `trapscript.py`, remove old `trapcode.py` from:
  `/Applications/FL Studio 2025.app/Contents/Resources/FL/Shared/Python/Lib/`

---

## Verification Checklist

After rename, verify:
- [ ] `import trapscript as ts` works
- [ ] All `ts.` API calls function correctly
- [ ] Debug output shows `[TrapScript]` prefix
- [ ] README renders correctly with new naming
- [ ] Cursor rules load properly
- [ ] /update skill deploys `trapscript.py` to FL Studio
- [ ] Old `trapcode.py` removed from FL Studio Lib folder
- [ ] GitHub repo accessible at new URL
- [ ] Old GitHub URL redirects correctly

---

## Reference: Files to Modify

| File | Changes |
|------|---------|
| `trapcode.py` → `trapscript.py` | Rename + internal strings |
| `default (trapcode).py` → `default (trapscript).py` | Rename + imports |
| `scope/scope.py` | Import + all `tc.` refs |
| `scope/test.py` | Import + all `tc.` refs |
| `README.md` | ~200+ replacements |
| `.gitignore` | Comment update |
| `scope/todo.md` | `tc.` refs |
| `scope/plan/debugging_system.md` | `tc.` and `[TrapCode]` refs |
| `scope/plan/voice_triggering*.md` | `tc.` refs |
| `scope/plan/strudel_mini_notation.md` | `tc.` refs |
| `scope/plan/pattern state access/*.md` | `tc.` refs |
| `scope/plan/phase1/*.md` | `tc.` refs |
| `scope/research docs/**/*.md` | `tc.` refs |
| `.cursor/rules/trapcode-workflow.mdc` → `trapscript-workflow.mdc` | Rename + content |
| `.cursor/skills/update/SKILL.md` | Content + cleanup step |

---

## Notes

- The `ts` alias maintains the same brevity as `tc` (2 characters)
- "TrapScript" is more descriptive: references trap music + VFX Script
- All API signatures remain unchanged—only naming/branding changes
- No breaking changes to functionality
