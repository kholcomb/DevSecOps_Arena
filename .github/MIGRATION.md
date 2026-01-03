# Scripts Directory Migration

**Date:** 2026-01-03
**Version:** Post-v1.0.0

## What Changed

All utility scripts have been consolidated from scattered locations into a single organized `scripts/` directory.

### Old Structure ❌
```
├── tools/
│   ├── create_level.sh
│   ├── generate_level.py
│   └── progress_tracker.py
├── utils/
│   ├── audit_levels.sh
│   └── test-all-levels.sh
├── engine/
│   └── reset.py
└── cleanup-containers.sh
```

### New Structure ✅
```
scripts/
├── README.md           # Documentation for all scripts
├── development/
│   ├── create_level.sh
│   ├── generate_level.py
│   └── progress_tracker.py
└── maintenance/
    ├── audit_levels.sh
    ├── cleanup-containers.sh
    ├── reset.py
    └── test-all-levels.sh
```

## Migration Guide

### For Users

Update your commands to use the new paths:

| Old Command | New Command |
|------------|-------------|
| `python3 engine/reset.py all` | `python3 scripts/maintenance/reset.py all` |
| `./cleanup-containers.sh` | `./scripts/maintenance/cleanup-containers.sh` |
| `./tools/create_level.sh ...` | `./scripts/development/create_level.sh ...` |
| `./utils/audit_levels.sh` | `./scripts/maintenance/audit_levels.sh` |

### For Contributors

When referencing scripts in documentation or code:

```bash
# ✅ Good - Use new paths
./scripts/maintenance/cleanup-containers.sh

# ❌ Avoid - Old paths no longer exist
./cleanup-containers.sh
./engine/reset.py
```

### For Automation

If you have automated scripts or CI/CD that reference the old paths, update them:

```yaml
# Before
- run: python3 engine/reset.py all

# After
- run: python3 scripts/maintenance/reset.py all
```

## Benefits

1. **Organization** - Clear separation between development and maintenance tools
2. **Discoverability** - Single location for all utility scripts
3. **Documentation** - Comprehensive README in scripts directory
4. **Consistency** - Follows common project structure patterns

## Questions?

See [scripts/README.md](../scripts/README.md) for detailed documentation on all available scripts.
