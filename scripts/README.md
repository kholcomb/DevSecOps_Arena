# DevSecOps Arena Scripts

Utility scripts organized by purpose for development and maintenance tasks.

## Directory Structure

```
scripts/
├── development/     # Tools for creating and developing challenges
└── maintenance/     # Tools for testing, auditing, and cleanup
```

---

## Development Scripts

Scripts for creating new challenges and tracking development progress.

### create_level.sh

**Purpose:** Quick scaffold for new Kubernetes challenge levels

**Usage:**
```bash
cd scripts/development
./create_level.sh <world-num> <level-num> <level-name> <short-description>
```

**Example:**
```bash
./create_level.sh 2 11 deployment-stuck "Rolling update failed"
```

**What it creates:**
- Level directory structure
- Template files (mission.yaml, broken.yaml, solution.yaml, validate.sh)
- Hint files (hint1.md, hint2.md, hint3.md)
- Debrief template

---

### generate_level.py

**Purpose:** Generate level metadata and documentation

**Usage:**
```bash
python3 generate_level.py [options]
```

**Features:**
- Automates level metadata generation
- Creates consistent documentation structure
- Validates level configuration

---

### progress_tracker.py

**Purpose:** Track development progress across all domains

**Usage:**
```bash
python3 progress_tracker.py
```

**Output:**
- Completion percentage by domain
- Missing required files
- OWASP coverage statistics
- Challenge count summaries

---

## Maintenance Scripts

Scripts for testing, cleanup, and system maintenance.

### cleanup-containers.sh

**Purpose:** Remove all DevSecOps Arena Docker containers across all domains

**Usage:**
```bash
cd scripts/maintenance
./cleanup-containers.sh
```

**What it cleans:**
- MCP domain containers (gateway + backend)
- Web Security domain containers (arena_web prefix)
- API Security domain containers (arena_api prefix)
- Orphaned Docker networks

**When to use:**
- After force-killing the game (Ctrl+Z, kill -9)
- When containers are left running after a crash
- Before fresh reinstall
- To free up Docker resources

**Note:** Normal game exit (quit, Ctrl+C) handles cleanup automatically.

---

### reset.py

**Purpose:** Reset challenge progress and state

**Usage:**
```bash
cd scripts/maintenance
python3 reset.py <level-name>
python3 reset.py all
```

**Examples:**
```bash
# Reset specific level
python3 reset.py level-1-pods

# Reset all progress
python3 reset.py all
```

**What it resets:**
- Player progress file
- XP and completion status
- Deployed challenge state

---

### audit_levels.sh

**Purpose:** Audit all levels for missing or invalid files

**Usage:**
```bash
cd scripts/maintenance
./audit_levels.sh
```

**Checks for:**
- Required files present (mission.yaml, broken.yaml, solution.yaml, validate.sh)
- Hint files (hint1.md, hint2.md, hint3.md)
- Debrief documentation
- File permissions (executable scripts)

**Output:**
- Summary of issues by domain
- List of incomplete levels
- Recommendations for fixes

---

### test-all-levels.sh

**Purpose:** Run validation tests across all challenge levels

**Usage:**
```bash
cd scripts/maintenance
./test-all-levels.sh [domain]
```

**Examples:**
```bash
# Test all domains
./test-all-levels.sh

# Test specific domain
./test-all-levels.sh kubernetes
./test-all-levels.sh web_security
```

**Features:**
- Deploys each challenge
- Runs validation script
- Reports pass/fail status
- Generates test coverage report

**Requirements:**
- Docker/kubectl running
- Clean environment (no running challenges)

---

## Quick Reference

| Task | Script | Command |
|------|--------|---------|
| Create new level | create_level.sh | `./scripts/development/create_level.sh 2 11 level-name "desc"` |
| Clean up containers | cleanup-containers.sh | `./scripts/maintenance/cleanup-containers.sh` |
| Reset progress | reset.py | `python3 scripts/maintenance/reset.py all` |
| Audit levels | audit_levels.sh | `./scripts/maintenance/audit_levels.sh` |
| Test all levels | test-all-levels.sh | `./scripts/maintenance/test-all-levels.sh` |
| Track progress | progress_tracker.py | `python3 scripts/development/progress_tracker.py` |

---

## Contributing New Scripts

When adding new utility scripts:

1. **Choose the right directory:**
   - `development/` - For creating/modifying challenges
   - `maintenance/` - For testing, cleanup, system tasks

2. **Make scripts executable:**
   ```bash
   chmod +x your-script.sh
   ```

3. **Add documentation:**
   - Update this README with script purpose, usage, and examples
   - Add header comments to the script itself

4. **Follow naming conventions:**
   - Use kebab-case: `script-name.sh`
   - Use descriptive names: `cleanup-containers.sh` not `clean.sh`

5. **Test thoroughly:**
   - Run on clean environment
   - Test error cases
   - Verify cleanup on exit

---

## Migration Notes

**Previous Locations → New Locations:**

| Old Path | New Path |
|----------|----------|
| `tools/create_level.sh` | `scripts/development/create_level.sh` |
| `tools/generate_level.py` | `scripts/development/generate_level.py` |
| `tools/progress_tracker.py` | `scripts/development/progress_tracker.py` |
| `utils/audit_levels.sh` | `scripts/maintenance/audit_levels.sh` |
| `utils/test-all-levels.sh` | `scripts/maintenance/test-all-levels.sh` |
| `engine/reset.py` | `scripts/maintenance/reset.py` |
| `cleanup-containers.sh` | `scripts/maintenance/cleanup-containers.sh` |

**Backward Compatibility:**

All scripts work from any location if you use relative paths from the project root:
```bash
# Works from project root
./scripts/maintenance/cleanup-containers.sh

# Works from anywhere
cd /path/to/DevSecOps_Arena
./scripts/maintenance/cleanup-containers.sh
```
