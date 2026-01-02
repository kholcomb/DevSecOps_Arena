# Domain Plugin Base Classes

**Status:** ✅ Phase 1 Complete

This package provides the abstract base classes for implementing domain plugins in DevSecOps Arena. Each security domain (Kubernetes, Web Security, Container Security, etc.) implements these interfaces to integrate with the game engine.

## Architecture Overview

```
domains/_base/
├── __init__.py          # Package exports
├── domain.py            # Domain abstract class (302 LOC)
├── deployer.py          # ChallengeDeployer interface (183 LOC)
├── validator.py         # ChallengeValidator interface (118 LOC)
├── safety_guard.py      # SafetyGuard interface (193 LOC)
└── visualizer.py        # DomainVisualizer interface (182 LOC)

Total: 1,006 lines of code
```

## Available Classes

### Abstract Base Classes
- **`Domain`** - Main domain interface
- **`ChallengeDeployer`** - Challenge deployment (kubectl, docker-compose, terraform)
- **`ChallengeValidator`** - Challenge validation
- **`SafetyGuard`** - Safety checks for dangerous operations
- **`DomainVisualizer`** - Real-time visualization data

### Concrete Implementations
- **`BashScriptValidator`** - Standard validator using validate.sh scripts
- **`NoOpSafetyGuard`** - Safety guard that allows everything
- **`NoOpVisualizer`** - Minimal visualizer for unsupported domains

### Data Classes
- **`DomainConfig`** - Domain configuration (loaded from domain_config.yaml)
- **`Challenge`** - Challenge metadata (loaded from mission.yaml)
- **`SafetyPattern`** - Dangerous pattern definition
- **`SafetySeverity`** - Enum: SAFE, WARNING, CRITICAL

## Quick Start

### Creating a New Domain

```python
from pathlib import Path
from domains._base import Domain, ChallengeDeployer, SafetyGuard, DomainVisualizer

class MyDomain(Domain):
    def create_deployer(self) -> ChallengeDeployer:
        return MyCustomDeployer(self.config.to_dict())
    
    def create_validator(self):
        # Most domains use the standard bash script validator
        return BashScriptValidator(self.config.to_dict())
    
    def create_safety_guard(self) -> SafetyGuard:
        return MyCustomSafetyGuard(self.config.to_dict())
    
    def create_visualizer(self) -> DomainVisualizer:
        return MyCustomVisualizer(self.config.to_dict())
```

### Implementing a Deployer

```python
from domains._base import ChallengeDeployer

class MyCustomDeployer(ChallengeDeployer):
    def health_check(self) -> tuple[bool, str]:
        # Check if deployment tool is available
        return True, "Tool is ready"
    
    def deploy_challenge(self, level_path: Path) -> tuple[bool, str]:
        # Deploy the challenge environment
        return True, "Challenge deployed"
    
    def cleanup_challenge(self, level_path: Path) -> tuple[bool, str]:
        # Clean up resources
        return True, "Resources cleaned up"
    
    def get_status(self, level_path: Path) -> dict:
        # Return current status
        return {'ready': True, 'message': 'All systems operational'}
```

### Implementing a Safety Guard

```python
from domains._base import SafetyGuard, SafetyPattern, SafetySeverity

class MyCustomSafetyGuard(SafetyGuard):
    def get_dangerous_patterns(self) -> list[SafetyPattern]:
        return [
            SafetyPattern(
                pattern=r"rm\s+-rf\s+/",
                message="Cannot delete root filesystem!",
                severity=SafetySeverity.CRITICAL
            ),
            SafetyPattern(
                pattern=r"docker\s+run.*--privileged",
                message="Privileged containers require confirmation",
                severity=SafetySeverity.WARNING
            )
        ]
    
    def validate_command(self, command: str, interactive: bool = True) -> tuple[bool, str, SafetySeverity]:
        # Check command against patterns
        # Return (allowed, message, severity)
        return True, "", SafetySeverity.SAFE
```

## Interface Documentation

### Domain

Main domain interface that ties everything together.

**Required Methods:**
- `create_deployer() -> ChallengeDeployer`
- `create_validator() -> ChallengeValidator`
- `create_safety_guard() -> SafetyGuard`
- `create_visualizer() -> DomainVisualizer`

**Helper Methods:**
- `get_worlds() -> List[Path]` - Get list of world directories
- `discover_challenges(world_name) -> List[Challenge]` - Find all challenges in a world
- `get_progress_key() -> str` - Get domain ID for progress tracking
- `health_check() -> tuple[bool, str]` - Check if domain is ready

### ChallengeDeployer

Handles deployment of challenge environments.

**Required Methods:**
- `health_check() -> tuple[bool, str]` - Check if deployment backend is available
- `deploy_challenge(level_path) -> tuple[bool, str]` - Deploy challenge
- `cleanup_challenge(level_path) -> tuple[bool, str]` - Clean up resources
- `get_status(level_path) -> Dict[str, Any]` - Get current status

**Optional Hooks:**
- `pre_deploy_hook(level_path) -> tuple[bool, str]`
- `post_deploy_hook(level_path) -> tuple[bool, str]`
- `get_deployment_files(level_path) -> List[Path]`

### ChallengeValidator

Validates challenge solutions.

**Required Methods:**
- `validate(level_path) -> tuple[bool, str]` - Validate solution

**Helper Methods:**
- `get_validation_script(level_path) -> Optional[Path]` - Get validation script path

### SafetyGuard

Prevents dangerous operations.

**Required Methods:**
- `get_dangerous_patterns() -> List[SafetyPattern]` - Define dangerous patterns
- `validate_command(command, interactive) -> tuple[bool, str, SafetySeverity]` - Check command safety

**Helper Methods:**
- `is_enabled() -> bool` - Check if safety is enabled
- `enable()` - Enable safety
- `disable()` - Disable safety (use with caution!)
- `pre_deploy_check(level_path) -> tuple[bool, str]` - Pre-deployment safety check
- `get_safety_info() -> str` - Get safety documentation

### DomainVisualizer

Provides real-time visualization data.

**Required Methods:**
- `get_visualization_data(level_path) -> Dict[str, Any]` - Get current state data

**Optional Methods:**
- `get_diagram_template(world, level) -> Optional[Dict]` - Get diagram config
- `detect_issues() -> List[Dict]` - Detect current issues
- `get_resource_graph() -> Dict` - Get resource relationship graph

## Testing

All base classes have been verified:

```bash
python3 -c "from domains._base import *; print('✅ All imports successful')"
```

## Next Steps

**Phase 2:** Kubernetes Domain Wrapper
- Move existing 50 K8s challenges to `domains/kubernetes/`
- Extract kubectl logic from `engine/engine.py`
- Move `engine/safety.py` to `domains/kubernetes/safety_guard.py`
- Create `domain_config.yaml` for Kubernetes domain
- Test that all 50 challenges work identically

## Design Principles

1. **Separation of Concerns** - Each component has a single responsibility
2. **Extensibility** - Easy to add new domains without modifying engine
3. **Flexibility** - Domains can use different deployment tools
4. **Safety First** - Safety guards prevent destructive operations
5. **Developer Experience** - Clear interfaces with comprehensive docstrings
6. **Type Safety** - Full type hints for better IDE support

## Notes

- All abstract classes use `ABC` and `@abstractmethod` decorators
- Concrete implementations provided for common use cases
- Domain configuration loaded from YAML files
- Challenge metadata follows existing 8-file structure
- Backward compatible with current K8s challenges
