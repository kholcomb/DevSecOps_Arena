#!/usr/bin/env python3
"""
Challenge Validator Abstract Base Class

Defines the interface for validating challenge solutions.
Most domains use bash scripts (validate.sh), but this abstraction
allows for domain-specific validation logic.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, Optional
import subprocess


class ChallengeValidator(ABC):
    """
    Abstract base class for challenge validation.

    Most domains execute a validate.sh script, but this abstraction
    allows for custom validation logic if needed.
    """

    def __init__(self, domain_config: Dict[str, Any]):
        """
        Initialize the validator with domain-specific configuration.

        Args:
            domain_config: Configuration dictionary from domain_config.yaml
        """
        self.config = domain_config

    @abstractmethod
    def validate(self, level_path: Path) -> tuple[bool, str]:
        """
        Validate the challenge solution.

        Args:
            level_path: Path to the level directory

        Returns:
            tuple[bool, str]: (is_valid, message)
                - is_valid: True if validation passed
                - message: Success/failure message to show user

        Example:
            >>> validator.validate(Path("domains/kubernetes/worlds/world-1/level-1"))
            (True, "✅ Pod is running correctly")
        """
        raise NotImplementedError("Subclass must implement validate()")

    def get_validation_script(self, level_path: Path) -> Optional[Path]:
        """
        Get path to validation script if it exists.

        Override this if your domain uses a different naming convention
        than validate.sh.

        Args:
            level_path: Path to the level directory

        Returns:
            Path to validation script, or None if not found

        Example:
            >>> validator.get_validation_script(level_path)
            Path("domains/kubernetes/worlds/world-1/level-1/validate.sh")
        """
        validate_script = level_path / "validate.sh"
        return validate_script if validate_script.exists() else None


class BashScriptValidator(ChallengeValidator):
    """
    Default validator implementation that executes validate.sh scripts.

    This is the standard validator used by most domains.
    """

    def validate(self, level_path: Path) -> tuple[bool, str]:
        """
        Execute validate.sh script and return results.

        Args:
            level_path: Path to the level directory

        Returns:
            tuple[bool, str]: (success, output_message)
        """
        validate_script = self.get_validation_script(level_path)

        if not validate_script:
            return False, "❌ Validation script not found (validate.sh)"

        if not validate_script.is_file():
            return False, f"❌ Validation script is not a file: {validate_script}"

        try:
            result = subprocess.run(
                ["bash", str(validate_script)],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=level_path
            )

            # Return success based on exit code
            output = result.stdout.strip() if result.stdout else result.stderr.strip()

            if result.returncode == 0:
                return True, output or "✅ Validation passed"
            else:
                return False, output or "❌ Validation failed"

        except subprocess.TimeoutExpired:
            return False, "❌ Validation timed out (30s limit)"
        except Exception as e:
            return False, f"❌ Validation error: {str(e)}"
