#!/bin/bash
# AWS Native Modernization Phase 6 - Push Commands

# Display changes
echo "📊 Changes Summary:"
echo "==================="
git diff origin/main..main --stat
echo ""

# Display commits
echo "📝 Commits to Push:"
echo "==================="
git log --oneline origin/main..main
echo ""

# Ready to push
echo "✅ Ready to push!"
echo ""
echo "Execute this command to push to GitHub:"
echo ""
echo "  git push origin main"
echo ""

# Alternative with verbose
echo "Or with verbose output:"
echo "  git push origin main -v"
echo ""

# Show the exact files being added
echo "📦 Files to be pushed:"
git diff origin/main..main --name-status
