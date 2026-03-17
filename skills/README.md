# Skills Directory

This directory contains version-controlled copies of Claude Code skills.

## Why This Exists

Claude Code skills live in `.claude/skills/` which is gitignored (contains local config). This `skills/` directory provides:
- Version control for skill definitions
- Ability to track changes over time
- Easy restore if `.claude/` is deleted

## Files

- `add-expense.md` - The expense tracking skill (version-controlled copy)
- `sync.sh` - Script to sync between here and `.claude/skills/`

## Syncing

### After editing the skill locally (backup to git):
```bash
./skills/sync.sh pull
git add skills/add-expense.md
git commit -m "update add-expense skill"
```

### After pulling changes from git (deploy to Claude Code):
```bash
./skills/sync.sh push
```

## Active Skill Location

The skill that Claude Code actually uses is at:
```
.claude/skills/add-expense/SKILL.md
```

This `skills/` directory is just a backup for version control.
