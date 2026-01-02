#!/usr/bin/env python3
"""
Domain Abstract Base Class

Defines the core interface for security training domains.
Each domain (Kubernetes, Web Security, Container Security, etc.) implements this interface.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import yaml


@dataclass
class DomainConfig:
    """
    Configuration for a security domain.

    Loaded from domain_config.yaml in each domain directory.
    """
    id: str                              # Unique domain identifier (e.g., "kubernetes")
    name: str                            # Display name (e.g., "Kubernetes Security")
    icon: str                            # Icon/emoji for UI (e.g., "⎈")
    description: str                     # Brief description
    worlds: List[str]                    # List of world directories
    deployment_backend: str              # Backend tool (kubectl, docker-compose, terraform)
    requires_cluster: bool = False       # Whether external cluster is required
    namespace: Optional[str] = None      # Default namespace/isolation boundary
    safety_enabled: bool = True          # Whether safety guards are enabled

    @classmethod
    def from_yaml(cls, yaml_path: Path) -> 'DomainConfig':
        """Load configuration from YAML file"""
        with open(yaml_path, 'r') as f:
            data = yaml.safe_load(f)

        metadata = data.get('metadata', {})
        capabilities = data.get('capabilities', {})

        return cls(
            id=metadata.get('id', ''),
            name=metadata.get('name', ''),
            icon=metadata.get('icon', '🎮'),
            description=metadata.get('description', ''),
            worlds=data.get('worlds', []),
            deployment_backend=capabilities.get('deployment_backend', 'unknown'),
            requires_cluster=capabilities.get('requires_cluster', False),
            namespace=capabilities.get('namespace'),
            safety_enabled=capabilities.get('safety_enabled', True)
        )


@dataclass
class Challenge:
    """
    Represents a single challenge level.

    Attributes:
        id: Unique identifier (e.g., "k8s-01-pod-crash")
        name: Display name
        path: Path to level directory
        world: World identifier
        xp: XP reward
        difficulty: beginner | intermediate | advanced | expert
        expected_time: Estimated completion time
        concepts: List of learning concepts
        metadata: Additional metadata from mission.yaml
    """
    id: str
    name: str
    path: Path
    world: str
    xp: int
    difficulty: str
    expected_time: str
    concepts: List[str]
    metadata: Dict[str, Any]

    @classmethod
    def from_mission_yaml(cls, level_path: Path, world: str) -> 'Challenge':
        """Load challenge from mission.yaml"""
        mission_file = level_path / "mission.yaml"

        if not mission_file.exists():
            raise FileNotFoundError(f"mission.yaml not found in {level_path}")

        with open(mission_file, 'r') as f:
            data = yaml.safe_load(f)

        return cls(
            id=f"{world}-{level_path.name}",
            name=data.get('name', level_path.name),
            path=level_path,
            world=world,
            xp=data.get('xp', 100),
            difficulty=data.get('difficulty', 'beginner'),
            expected_time=data.get('expected_time', 'unknown'),
            concepts=data.get('concepts', []),
            metadata=data
        )


class Domain(ABC):
    """
    Abstract base class for security training domains.

    Each domain implements this interface to integrate with the game engine.
    Domains are discovered automatically by scanning the domains/ directory.
    """

    def __init__(self, domain_path: Path):
        """
        Initialize the domain.

        Args:
            domain_path: Path to domain directory (e.g., domains/kubernetes/)
        """
        self.path = domain_path
        self.config = self._load_config()
        self._deployer = None
        self._validator = None
        self._safety_guard = None
        self._visualizer = None

    def _load_config(self) -> DomainConfig:
        """Load domain configuration from domain_config.yaml"""
        config_file = self.path / "domain_config.yaml"

        if not config_file.exists():
            raise FileNotFoundError(
                f"domain_config.yaml not found in {self.path}"
            )

        return DomainConfig.from_yaml(config_file)

    @abstractmethod
    def create_deployer(self):
        """
        Create and return domain-specific deployer.

        Returns:
            ChallengeDeployer instance

        Example:
            >>> domain.create_deployer()
            KubectlDeployer(config)
        """
        raise NotImplementedError("Subclass must implement create_deployer()")

    @abstractmethod
    def create_validator(self):
        """
        Create and return domain-specific validator.

        Returns:
            ChallengeValidator instance

        Example:
            >>> domain.create_validator()
            BashScriptValidator(config)
        """
        raise NotImplementedError("Subclass must implement create_validator()")

    @abstractmethod
    def create_safety_guard(self):
        """
        Create and return domain-specific safety guard.

        Returns:
            SafetyGuard instance

        Example:
            >>> domain.create_safety_guard()
            K8sSafetyGuard(config)
        """
        raise NotImplementedError("Subclass must implement create_safety_guard()")

    @abstractmethod
    def create_visualizer(self):
        """
        Create and return domain-specific visualizer.

        Returns:
            DomainVisualizer instance

        Example:
            >>> domain.create_visualizer()
            K8sVisualizer(config)
        """
        raise NotImplementedError("Subclass must implement create_visualizer()")

    # Lazy-loaded properties for domain components
    @property
    def deployer(self):
        """Get or create deployer instance"""
        if self._deployer is None:
            self._deployer = self.create_deployer()
        return self._deployer

    @property
    def validator(self):
        """Get or create validator instance"""
        if self._validator is None:
            self._validator = self.create_validator()
        return self._validator

    @property
    def safety_guard(self):
        """Get or create safety guard instance"""
        if self._safety_guard is None:
            self._safety_guard = self.create_safety_guard()
        return self._safety_guard

    @property
    def visualizer(self):
        """Get or create visualizer instance"""
        if self._visualizer is None:
            self._visualizer = self.create_visualizer()
        return self._visualizer

    def get_worlds(self) -> List[Path]:
        """
        Get list of world directories for this domain.

        Returns:
            List of Path objects for world directories
        """
        worlds_dir = self.path / "worlds"
        if not worlds_dir.exists():
            return []

        return sorted([
            d for d in worlds_dir.iterdir()
            if d.is_dir() and d.name in self.config.worlds
        ])

    def discover_challenges(self, world_name: str) -> List[Challenge]:
        """
        Discover all challenges in a world.

        Args:
            world_name: World identifier (e.g., "world-1-basics")

        Returns:
            List of Challenge objects

        Example:
            >>> domain.discover_challenges("world-1-basics")
            [Challenge(id="k8s-01", name="Fix Pod", ...), ...]
        """
        world_path = self.path / "worlds" / world_name

        if not world_path.exists():
            return []

        challenges = []
        import re

        def natural_sort_key(path: Path):
            """Extract numbers for natural sorting"""
            parts = re.split(r'(\d+)', path.name)
            return [int(part) if part.isdigit() else part for part in parts]

        # Find all level directories
        level_dirs = sorted(
            [d for d in world_path.iterdir() if d.is_dir() and d.name.startswith('level-')],
            key=natural_sort_key
        )

        for level_path in level_dirs:
            try:
                challenge = Challenge.from_mission_yaml(level_path, world_name)
                challenges.append(challenge)
            except Exception as e:
                # Log warning but continue discovering other challenges
                print(f"Warning: Could not load challenge from {level_path}: {e}")

        return challenges

    def get_progress_key(self) -> str:
        """
        Get the progress tracking key for this domain.

        Returns:
            Domain ID for use in progress.json

        Example:
            >>> domain.get_progress_key()
            "kubernetes"
        """
        return self.config.id

    def health_check(self) -> tuple[bool, str]:
        """
        Check if domain is ready to run challenges.

        Returns:
            tuple[bool, str]: (is_healthy, status_message)
        """
        return self.deployer.health_check()
