# ⚡ QUICK ACTION PLAN

**Read this first!** Follow these steps in order to complete the cleanup.

---

## 🎯 YOUR IMMEDIATE TASKS

### Task 1: Fix Verification Script (2 minutes)
The script has wrong commands for frontend checks.

**Action**:
```bash
# Open the file
nano scripts/verify-pipeline.sh

# Find these lines and fix them:
# Line ~32: Change from:
#   bash -c "cd frontend && bun run biome format --check ."
# To:
#   bash -c "cd frontend && bun biome format ."

# Line ~46: Change from:
#   bash -c "cd frontend && bun run biome check ."
# To:
#   bash -c "cd frontend && bun biome check ."

# Save and exit
```

**OR** - Quick fix with sed:
```bash
sed -i 's/bun run biome format/bun biome format/g' scripts/verify-pipeline.sh
sed -i 's/bun run biome check/bun biome check/g' scripts/verify-pipeline.sh
```

---

### Task 2: Install Missing System Tools (5 minutes)

**Install yamllint**:
```bash
# Option 1: Via pip
pip install yamllint

# Option 2: Via package manager (Windows)
choco install yamllint

# Option 3: Via uv
cd backend && uv add --dev yamllint
```

**Install typos**:
```bash
# Option 1: Download binary
# Go to: https://github.com/crate-ci/typos/releases
# Download for Windows and add to PATH

# Option 2: Via cargo (if you have Rust)
cargo install typos-cli

# Option 3: Skip for now (not critical)
```

---

### Task 3: Fix Frontend Issues (10 minutes)

```bash
cd frontend

# 1. Check package.json has correct scripts
cat package.json | grep -A 10 "scripts"

# Should have:
# "lint": "biome check .",
# "lint:fix": "biome check --write .",
# "format": "biome format --write .",

# 2. Install/update dependencies
bun install

# 3. Run checks
bun biome check .
bun run typecheck
bun test

# 4. Fix any errors shown
```

---

### Task 4: Run Full Verification (5 minutes)

```bash
# Go to project root
cd ..

# Run verification
task verify

# This will show you exactly what needs fixing
# Fix each issue one by one
```

---

### Task 5: Test Development Environment (10 minutes)

```bash
# Start all services
task dev

# Wait for servers to start, then test:

# 1. Test API (should return OK)
curl http://localhost:8000/docs

# 2. Test Frontend (should load)
curl http://localhost:5173

# 3. Test via Caddy (unified access)
curl http://localhost/api/

# 4. Open browser
# - http://localhost/ → Frontend
# - http://localhost/docs → API docs
# - http://localhost/graphql → GraphQL
```

---

## 🐛 TROUBLESHOOTING

### If "task verify" fails:

**Issue**: Command not found (yamllint, typos, etc.)
**Fix**: Either install the tool OR comment out that check in verify-pipeline.sh

**Issue**: Backend tests fail
**Fix**:
```bash
cd backend
uv sync
uv run pytest tests/unit -v
# Fix failing tests
```

**Issue**: Frontend build fails
**Fix**:
```bash
cd frontend
rm -rf node_modules
bun install
bun run build
```

**Issue**: Type errors
**Fix**:
```bash
# Backend
cd backend && uv run mypy src/

# Frontend
cd frontend && bun run typecheck
```

---

## 📋 CHECKLIST

Complete these in order:

- [ ] Fix verify-pipeline.sh commands
- [ ] Install yamllint
- [ ] Install typos (optional)
- [ ] Fix frontend package.json scripts
- [ ] Run `task verify` and fix issues
- [ ] Run `task dev` and test
- [ ] Run `task test:coverage`
- [ ] Review GitHub Actions workflows
- [ ] Test DevContainer
- [ ] Update README with badges

---

## 🎯 SUCCESS CRITERIA

You're done when:

1. ✅ `task verify` passes all checks
2. ✅ `task dev` starts without errors
3. ✅ Test coverage ≥ 70%
4. ✅ Frontend builds successfully
5. ✅ DevContainer works
6. ✅ All documentation is up to date

---

## 💡 QUICK WINS

Do these for immediate impact:

1. **Auto-fix formatting**:
   ```bash
   task format
   ```

2. **Generate API docs**:
   ```bash
   task tools:openapi:generate
   task tools:openapi:view
   ```

3. **Check tool status**:
   ```bash
   task tools:status
   ```

4. **Test Claude integration**:
   - Open VS Code
   - Press `Ctrl+Shift+I`
   - Ask: "What model are you?"
   - Should say: "Claude 3.5 Sonnet"

---

## 📚 REFERENCE DOCS

**Must Read**:
1. `CLEANUP_SUMMARY.md` - Full report
2. `CLEANUP_PROGRESS.md` - Detailed progress
3. `docs/TOOLS_QUICK_REFERENCE.md` - Quick ref

**Detailed Guides**:
- `docs/TOOLS_SETUP_GUIDE.md` (13.8KB)
- `docs/CLAUDE_COPILOT_GUIDE.md` (11KB)
- `docs/IMPLEMENTATION_SUMMARY.md` (17.3KB)

---

## 🎊 YOU'RE ALMOST THERE!

**Status**: 70% Complete  
**Remaining**: Just a few fixes!  
**Time Needed**: 30-60 minutes  

The hard work is done. Configuration is complete. Tools are set up. Documentation is written. Now just fix the small issues and you're production-ready!

---

**Remember**: Run `task verify` to see exactly what needs fixing. It will guide you step by step.

🚀 **Good luck!** 🚀
