#!/bin/bash
# Sync skill files between git-tracked skills/ and active .claude/skills/
#
# Usage:
#   ./skills/sync.sh push   # Copy from skills/ to .claude/skills/ (deploy)
#   ./skills/sync.sh pull   # Copy from .claude/skills/ to skills/ (backup)

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
SKILLS_DIR="$PROJECT_DIR/skills"
CLAUDE_SKILLS_DIR="$PROJECT_DIR/.claude/skills/add-expense"

case "$1" in
  push)
    echo "Deploying skill from skills/ to .claude/skills/..."
    mkdir -p "$CLAUDE_SKILLS_DIR"
    cp "$SKILLS_DIR/add-expense.md" "$CLAUDE_SKILLS_DIR/SKILL.md"
    echo "Done. Skill deployed to .claude/skills/add-expense/SKILL.md"
    ;;
  pull)
    echo "Backing up skill from .claude/skills/ to skills/..."
    cp "$CLAUDE_SKILLS_DIR/SKILL.md" "$SKILLS_DIR/add-expense.md"
    echo "Done. Skill backed up to skills/add-expense.md"
    ;;
  *)
    echo "Usage: $0 {push|pull}"
    echo ""
    echo "  push  - Deploy from skills/ to .claude/skills/ (after git pull)"
    echo "  pull  - Backup from .claude/skills/ to skills/ (before git commit)"
    exit 1
    ;;
esac
