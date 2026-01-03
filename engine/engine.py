#!/usr/bin/env python3
"""
DevSecOps Arena - Multi-Domain Security Training Platform
Master security through hands-on challenges across multiple domains
Retro Gaming UI | Domain Plugin System | Progressive Learning
"""

import os
import sys
import json
import yaml
import subprocess
import time
import argparse
import webbrowser
import signal
import atexit
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.layout import Layout
from rich.text import Text
from rich.markdown import Markdown
from rich.live import Live
from rich.align import Align
from rich import box
from datetime import datetime

# Import retro UI components
try:
    from engine.retro_ui import (
        show_retro_welcome, show_level_start, show_victory,
        show_command_menu, show_power_up_notification,
        show_retro_header, show_xp_bar, show_world_entry,
        show_game_complete, celebrate_milestone
    )
    RETRO_UI_ENABLED = True
except ImportError:
    try:
        from retro_ui import (
            show_retro_welcome, show_level_start, show_victory,
            show_command_menu, show_power_up_notification,
            show_retro_header, show_xp_bar, show_world_entry,
            show_game_complete, celebrate_milestone
        )
        RETRO_UI_ENABLED = True
    except ImportError:
        RETRO_UI_ENABLED = False
        print("Retro UI not available, using standard interface")

# Import player name generator
try:
    from engine.player_name import get_player_name
except ImportError:
    try:
        from player_name import get_player_name
    except ImportError:
        def get_player_name(console, current_name=None):
            from rich.prompt import Prompt
            return Prompt.ask("Enter your name", default="K8s Explorer")

# Import safety guards
try:
    from engine.safety import validate_kubectl_command, print_safety_info
    SAFETY_ENABLED = os.environ.get("ARENA_SAFETY", "on").lower() != "off"
except ImportError:
    try:
        from safety import validate_kubectl_command, print_safety_info
        SAFETY_ENABLED = os.environ.get("ARENA_SAFETY", "on").lower() != "off"
    except ImportError:
        SAFETY_ENABLED = False
        print("⚠️  Warning: Safety guards module not found. Running without protection.")

# Import visualization server
try:
    sys.path.insert(0, str(Path(__file__).parent.parent / "visualizer"))
    from server import VisualizationServer
    VISUALIZER_ENABLED = True
except ImportError as e:
    VISUALIZER_ENABLED = False
    print(f"ℹ️  Visualization server not available: {e}")

console = Console()


def discover_domains(base_dir: Path) -> dict:
    """
    Discover available domain plugins by scanning domains/ directory.

    Each domain must have:
    - domain_config.yaml with metadata
    - domain.py with load_domain() function

    Returns:
        Dict mapping domain_id -> Domain instance
    """
    domains = {}
    domains_dir = base_dir / "domains"

    if not domains_dir.exists():
        console.print("[yellow]Warning: domains/ directory not found[/yellow]")
        return domains

    # Scan for domain directories (skip _base)
    for domain_path in sorted(domains_dir.iterdir()):
        if not domain_path.is_dir() or domain_path.name.startswith('_'):
            continue

        # Check for required files
        config_file = domain_path / "domain_config.yaml"
        domain_module = domain_path / "domain.py"

        if not config_file.exists() or not domain_module.exists():
            continue

        try:
            # Dynamically import the domain module
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                f"domains.{domain_path.name}",
                domain_module
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Load domain using load_domain() function
            if hasattr(module, 'load_domain'):
                domain = module.load_domain(domain_path)
                domains[domain.config.id] = domain
                console.print(f"[dim]Discovered domain: {domain.config.icon} {domain.config.name}[/dim]")
            else:
                console.print(f"[yellow]Warning: {domain_path.name}/domain.py missing load_domain() function[/yellow]")

        except Exception as e:
            console.print(f"[yellow]Warning: Could not load {domain_path.name} domain: {e}[/yellow]")

    return domains


def select_domain(domains: dict, preselected_domain_id: str = None):
    """
    Select which domain to play.

    If a domain_id is provided, use that directly.
    If only one domain exists, auto-select it.
    If multiple domains exist, show selection menu.

    Args:
        domains: Dict of available domains
        preselected_domain_id: Optional domain ID to pre-select (e.g., 'kubernetes', 'web_security')

    Returns:
        Selected Domain instance
    """
    if len(domains) == 0:
        console.print("[red]Error: No domains found![/red]")
        sys.exit(1)

    # If domain was pre-selected via command line
    if preselected_domain_id:
        if preselected_domain_id in domains:
            selected_domain = domains[preselected_domain_id]
            console.print(f"\n[green]✓ Using domain: {selected_domain.config.name}[/green]\n")
            return selected_domain
        else:
            console.print(f"[red]Error: Domain '{preselected_domain_id}' not found![/red]")
            console.print(f"[yellow]Available domains: {', '.join(domains.keys())}[/yellow]")
            sys.exit(1)

    if len(domains) == 1:
        # Auto-select single domain (backward compatibility)
        domain = list(domains.values())[0]
        return domain

    # Multiple domains - show selection menu
    console.print("\n[bold cyan]Select Training Domain:[/bold cyan]\n")

    domain_list = list(domains.items())
    for i, (domain_id, domain) in enumerate(domain_list, 1):
        console.print(f"  {i}. {domain.config.icon}  {domain.config.name}")
        console.print(f"     [dim]{domain.config.description}[/dim]\n")

    choice = Prompt.ask(
        "Choose domain",
        choices=[str(i) for i in range(1, len(domain_list) + 1)],
        default="1"
    )

    selected_domain = domain_list[int(choice) - 1][1]
    console.print(f"\n[green]Selected: {selected_domain.config.name}[/green]\n")

    return selected_domain


class Arena:
    def __init__(self, enable_visualizer=True, domain=None):
        self.base_dir = Path(__file__).parent.parent
        self.progress_file = self.base_dir / "progress.json"

        # Discover and select domain
        self.domains = discover_domains(self.base_dir)
        self.current_domain = select_domain(self.domains, preselected_domain_id=domain)

        # Load progress (will auto-migrate old format)
        self.progress = self.load_progress()

        self.current_mission = None
        self.current_level_path = None
        self.deployed_level_path = None  # Track deployed level for cleanup
        self.visualizer = None
        self.level_completed_externally = False  # Flag for visualizer completion
        self.enable_visualizer = enable_visualizer and VISUALIZER_ENABLED
        
    def load_progress(self):
        """
        Load player progress from JSON file.

        Handles migration from old format (flat) to new format (domain-aware).
        """
        domain_id = self.current_domain.config.id

        if self.progress_file.exists():
            with open(self.progress_file, 'r') as f:
                progress = json.load(f)

                # Check if old format (has total_xp at root level)
                if "total_xp" in progress and "domains" not in progress:
                    # Migrate old format → domain-aware format
                    console.print("[yellow]📦 Migrating progress to multi-domain format...[/yellow]")

                    old_progress = progress.copy()
                    new_progress = {
                        "player_name": old_progress.get("player_name", "Padawan"),
                        "domains": {
                            domain_id: {
                                "total_xp": old_progress.get("total_xp", 0),
                                "completed_levels": old_progress.get("completed_levels", []),
                                "current_world": old_progress.get("current_world", "world-1-basics"),
                                "current_level": old_progress.get("current_level")
                            }
                        }
                    }

                    # Save migrated version
                    with open(self.progress_file, 'w') as fw:
                        json.dump(new_progress, fw, indent=2)

                    console.print("[green]✅ Progress migrated successfully![/green]\n")
                    return new_progress

                # Already new format
                # Ensure domain exists in progress
                if "domains" not in progress:
                    progress["domains"] = {}

                if domain_id not in progress["domains"]:
                    progress["domains"][domain_id] = {
                        "total_xp": 0,
                        "completed_levels": [],
                        "current_world": self.current_domain.config.worlds[0] if self.current_domain.config.worlds else "world-1-basics",
                        "current_level": None,
                        "unlocked_hints": {}
                    }

                # Ensure current_level and unlocked_hints exist for resume functionality
                if "current_level" not in progress["domains"][domain_id]:
                    progress["domains"][domain_id]["current_level"] = None
                if "unlocked_hints" not in progress["domains"][domain_id]:
                    progress["domains"][domain_id]["unlocked_hints"] = {}

                return progress

        # No existing progress - create new
        return {
            "player_name": "Padawan",
            "domains": {
                domain_id: {
                    "total_xp": 0,
                    "completed_levels": [],
                    "current_world": self.current_domain.config.worlds[0] if self.current_domain.config.worlds else "world-1-basics",
                    "current_level": None,
                    "unlocked_hints": {}
                }
            }
        }
    
    def cleanup_current_level(self):
        """Cleanup currently deployed level resources"""
        if not self.deployed_level_path:
            return

        try:
            console.print("\n[yellow]🧹 Cleaning up challenge environment...[/yellow]")
            success, message = self.current_domain.deployer.cleanup_challenge(self.deployed_level_path)

            if success:
                console.print(f"[green]✓ {message}[/green]")
            else:
                console.print(f"[yellow]⚠ {message}[/yellow]")

            self.deployed_level_path = None

        except Exception as e:
            console.print(f"[yellow]⚠ Cleanup error: {str(e)}[/yellow]")

    def save_progress(self):
        """Save player progress"""
        with open(self.progress_file, 'w') as f:
            json.dump(self.progress, indent=2, fp=f)

    @property
    def domain_progress(self):
        """
        Get progress for current domain.

        Returns dictionary with: total_xp, completed_levels, current_world, current_level
        """
        domain_id = self.current_domain.config.id
        return self.progress["domains"][domain_id]

    def get_game_state(self):
        """Get current game state for visualization"""
        return {
            'total_xp': self.domain_progress.get('total_xp', 0),
            'completed_levels': self.domain_progress.get('completed_levels', []),
            'current_world': self.domain_progress.get('current_world', 'world-1-basics'),
            'current_level': self.domain_progress.get('current_level'),
            'unlocked_hints': self.domain_progress.get('unlocked_hints', {}),
            'player_name': self.progress.get('player_name', 'Padawan'),
            'current_mission': self.current_mission.get('name', '') if self.current_mission else None,
            'current_domain': self.current_domain.config.id
        }

    def get_current_level_path(self):
        """Get path to current level directory for domain visualizer"""
        return self.current_level_path

    def validate_flag(self, level_path, flag):
        """Validator callback for visualizer flag submission"""
        if not self.current_domain or not self.current_domain.validator:
            return False, "❌ No validator available"

        try:
            success, message = self.current_domain.validator.validate(level_path, flag)

            # If validation succeeds, update game state
            if success and self.current_mission:
                level_name = level_path.name

                # Award XP if not already completed
                if level_name not in self.domain_progress["completed_levels"]:
                    xp_earned = self.current_mission.get("xp", 0)
                    self.domain_progress["total_xp"] += xp_earned

                    # Mark as completed
                    self.domain_progress["completed_levels"].append(level_name)

                    # Save progress
                    self.save_progress()

                    # Set flag for CLI to detect
                    self.level_completed_externally = True

                    # Include XP in success message
                    message = f"{message}\n\n🌟 +{xp_earned} XP! Total: {self.domain_progress['total_xp']} XP"

            return success, message
        except Exception as e:
            return False, f"❌ Validation error: {str(e)}"

    def unlock_hint(self, level_path, hint_number):
        """Unlock a hint for the current level (called from visualizer or CLI)"""
        if not self.current_mission:
            return False, "❌ No level loaded", 0

        level_name = level_path.name

        # Get hint cost from mission config
        hint_costs = self.current_mission.get('hints_cost', {})
        hint_key = f'hint_{hint_number}'
        cost = hint_costs.get(hint_key, 0)

        # Check if already unlocked
        if level_name not in self.domain_progress['unlocked_hints']:
            self.domain_progress['unlocked_hints'][level_name] = []

        if hint_number in self.domain_progress['unlocked_hints'][level_name]:
            return True, "✅ Hint already unlocked", cost

        # Check if player has enough XP
        if cost > 0 and self.domain_progress['total_xp'] < cost:
            return False, f"❌ Not enough XP! Need {cost} XP, have {self.domain_progress['total_xp']} XP", cost

        # Deduct XP and unlock hint
        self.domain_progress['total_xp'] -= cost
        self.domain_progress['unlocked_hints'][level_name].append(hint_number)
        self.save_progress()

        if cost > 0:
            return True, f"✅ Hint unlocked! (Cost: {cost} XP, Remaining: {self.domain_progress['total_xp']} XP)", cost
        else:
            return True, "✅ Hint unlocked!", cost

    def start_visualizer(self, port=8080):
        """Start the visualization server"""
        if not self.enable_visualizer:
            return None

        try:
            self.visualizer = VisualizationServer(
                port=port,
                game_state_callback=self.get_game_state,
                domain_visualizer=self.current_domain.visualizer,
                current_level_path_callback=self.get_current_level_path,
                validator_callback=self.validate_flag,
                unlock_hint_callback=self.unlock_hint,
                verbose=False
            )
            url = self.visualizer.start()

            console.print()

            # Domain-specific visualization message
            requires_cluster = self.current_domain.config.capabilities.get('requires_cluster', False)
            viz_desc = "View real-time cluster architecture and issues" if requires_cluster else "View real-time challenge environment and issues"

            console.print(Panel(
                f"[green]Visualization Server Started[/green]\n\n"
                f"[cyan]Open in browser:[/cyan] [yellow]{url}[/yellow]\n"
                f"[dim]{viz_desc}[/dim]",
                title="[bold cyan]VISUAL MODE[/bold cyan]",
                border_style="cyan"
            ))
            console.print()

            # Try to open browser automatically
            try:
                webbrowser.open(url)
            except:
                pass  # If it fails, user can open manually

            return url
        except Exception as e:
            console.print(f"[yellow]Could not start visualizer: {e}[/yellow]")
            return None

    def stop_visualizer(self):
        """Stop the visualization server"""
        if self.visualizer:
            try:
                self.visualizer.stop()
            except:
                pass

    def show_welcome(self):
        """Display welcome screen with retro gaming style"""
        if RETRO_UI_ENABLED:
            show_retro_welcome()
            time.sleep(1)
        
        console.clear()

        # Domain-specific branding
        domain_icon = self.current_domain.config.icon
        domain_name = self.current_domain.config.name

        # Retro-style title
        title = """
    ╔═╗╦═╗╔═╗╔╗╔╔═╗
    ╠═╣╠╦╝║╣ ║║║╠═╣
    ╩ ╩╩╚═╚═╝╝╚╝╩ ╩
        """

        welcome_panel = Panel(
            Text(title, style="bold cyan") +
            Text(f"\n {domain_icon}  {domain_name} \n", style="bold yellow") +
            Text("Contra-Style Learning | Arcade Action | Boss Battles", style="dim"),
            title="[bold magenta]  DEVSECOPS ARENA  [/bold magenta]",
            border_style="cyan",
            box=box.HEAVY
        )

        console.print(welcome_panel)
        console.print()
        
        # Player stats in retro gaming style
        stats = Table(show_header=False, box=box.HEAVY, border_style="yellow")
        stats.add_column("Stat", style="cyan bold")
        stats.add_column("Value", style="yellow bold")

        # Get domain-specific info
        domain_icon = self.current_domain.config.icon
        domain_name = self.current_domain.config.name
        total_challenges = self.current_domain.config.progression.get('total_challenges', 50)
        total_xp = self.current_domain.config.progression.get('total_xp', 10200)

        stats.add_row("🎮 PLAYER", self.progress["player_name"])
        stats.add_row(f"{domain_icon} DOMAIN", domain_name)
        stats.add_row("💎 TOTAL XP", str(self.domain_progress["total_xp"]))
        stats.add_row("⭐ LEVELS CLEARED", f"{len(self.domain_progress['completed_levels'])}/{total_challenges}")

        # Calculate completion percentage
        completion = (len(self.domain_progress['completed_levels']) / total_challenges) * 100 if total_challenges > 0 else 0
        progress_bar = "█" * int(completion / 5) + "░" * (20 - int(completion / 5))
        stats.add_row("📊 PROGRESS", f"[{progress_bar}] {completion:.0f}%")

        # Show current level if resuming
        if self.domain_progress.get("current_level"):
            stats.add_row("🎯 CURRENT MISSION", self.domain_progress["current_level"])
        
        # Add safety status with gaming flair
        safety_status = "🛡️  ACTIVE" if SAFETY_ENABLED else "⚠️  DISABLED"
        safety_color = "green" if SAFETY_ENABLED else "red"
        stats.add_row("🛡️  SHIELDS", f"[{safety_color}]{safety_status}[/{safety_color}]")

        # Add visualizer status
        viz_status = "📊 ENABLED" if self.enable_visualizer else "⚙️  DISABLED"
        viz_color = "cyan" if self.enable_visualizer else "dim"
        stats.add_row("🌐 VISUAL MODE", f"[{viz_color}]{viz_status}[/{viz_color}]")
        
        console.print(Panel(stats, title="[bold yellow]⚡ PLAYER STATUS ⚡[/bold yellow]", border_style="yellow", box=box.HEAVY))
        
        # Show XP progress bar
        if RETRO_UI_ENABLED:
            console.print()
            total_xp = self.current_domain.config.progression.get('total_xp', 10200)
            console.print(show_xp_bar(self.domain_progress["total_xp"], total_xp))
        
        # Show safety reminder if enabled with gaming theme (domain-aware)
        if SAFETY_ENABLED:
            console.print()

            # Domain-specific safety messages
            requires_cluster = self.current_domain.config.capabilities.get('requires_cluster', False)
            if requires_cluster:
                safety_msg = (
                    "[green]DEFENSE SYSTEMS ONLINE[/green]\n"
                    "[dim]✓ Prevents cluster destruction\n"
                    "✓ Namespace protection active\n"
                    "Type 'safety info' for shield details[/dim]"
                )
            else:
                safety_msg = (
                    "[green]DEFENSE SYSTEMS ONLINE[/green]\n"
                    "[dim]✓ Prevents destructive operations\n"
                    "✓ Environment protection active\n"
                    "Type 'safety info' for shield details[/dim]"
                )

            console.print(Panel(
                safety_msg,
                border_style="green",
                box=box.HEAVY,
                title="[bold green]SAFETY PROTOCOLS[/bold green]"
            ))
        console.print()
    
    def load_mission(self, level_path):
        """Load mission metadata"""
        mission_file = level_path / "mission.yaml"
        with open(mission_file, 'r') as f:
            return yaml.safe_load(f)
    
    def show_mission_briefing(self, mission, level_name):
        """Display mission briefing screen"""
        console.clear()
        
        briefing = f"""
# 🎯 {mission['name']}

**Mission**: {mission['description']}

**Objective**: {mission['objective']}

**XP Reward**: {mission['xp']} XP
        """
        
        console.print(Panel(
            Markdown(briefing),
            title=f"[bold cyan]Level: {level_name}[/bold cyan]",
            border_style="yellow",
            box=box.DOUBLE
        ))
        console.print()
    
    def show_hints_system(self, level_path):
        """Show hints with unlock system"""
        # Load mission to get hint costs
        mission = self.load_mission(level_path)
        hint_costs = mission.get('hints_cost', {})

        # Get unlocked hints for this level
        level_name = level_path.name
        unlocked = self.domain_progress.get('unlocked_hints', {}).get(level_name, [])

        hints_available = []
        for i in range(1, 4):
            hint_file = level_path / f"hint-{i}.txt"
            if hint_file.exists():
                hints_available.append(i)

        if not hints_available:
            console.print("[yellow]No hints available for this level[/yellow]")
            return

        # Show current XP
        console.print(f"[yellow]💰 Your XP: {self.domain_progress['total_xp']}[/yellow]\n")

        # Show hints
        console.print(Panel(
            f"[bold yellow]💡 Hints ({len(unlocked)}/{len(hints_available)} Unlocked)[/bold yellow]",
            border_style="yellow"
        ))

        for i in hints_available:
            hint_file = level_path / f"hint-{i}.txt"
            cost = hint_costs.get(f'hint_{i}', 0)

            if i in unlocked:
                # Show unlocked hint
                with open(hint_file, 'r') as f:
                    hint_content = f.read().strip()

                hint_style = "cyan" if i == 1 else ("yellow" if i == 2 else "green")
                console.print(f"\n[bold {hint_style}]✅ Hint {i}:[/bold {hint_style}] {hint_content}")
            else:
                # Show locked hint with unlock option
                cost_text = "Free" if cost == 0 else f"{cost} XP"
                console.print(f"\n[dim]🔒 Hint {i}: Locked (Cost: {cost_text})[/dim]")

        console.print()

        # Ask if user wants to unlock a hint
        locked_hints = [i for i in hints_available if i not in unlocked]
        if locked_hints:
            if Confirm.ask(f"\n💡 Unlock a hint?", default=False):
                # Show options
                hint_choices = [str(h) for h in locked_hints] + ["cancel"]
                hint_choice = Prompt.ask(
                    "Which hint?",
                    choices=hint_choices,
                    default="cancel"
                )

                if hint_choice != "cancel":
                    hint_num = int(hint_choice)
                    success, message, cost = self.unlock_hint(level_path, hint_num)

                    if success:
                        console.print(f"\n[green]{message}[/green]")
                        # Show the newly unlocked hint
                        hint_file = level_path / f"hint-{hint_num}.txt"
                        with open(hint_file, 'r') as f:
                            hint_content = f.read().strip()
                        console.print(f"\n[bold cyan]💡 Hint {hint_num}:[/bold cyan] {hint_content}\n")
                    else:
                        console.print(f"\n[red]{message}[/red]\n")
    
    def show_debrief(self, level_path):
        """Show the post-mission debrief with learning explanations"""
        debrief_file = level_path / "debrief.md"
        
        if not debrief_file.exists():
            console.print("[yellow]No debrief available for this level[/yellow]")
            return
        
        with open(debrief_file, 'r') as f:
            debrief_content = f.read()
        
        console.clear()
        console.print(Panel(
            Markdown(debrief_content),
            title="[bold green]🎓 Mission Debrief - What You Learned[/bold green]",
            border_style="green",
            box=box.DOUBLE
        ))
        console.print()
        
        Prompt.ask("\n[dim]Press ENTER to continue[/dim]", default="")
    
    def show_solution_file(self, level_path):
        """Display the solution.yaml file contents"""
        solution_file = level_path / "solution.yaml"
        
        if not solution_file.exists():
            console.print("[yellow]No solution file available for this level[/yellow]")
            return
        
        with open(solution_file, 'r') as f:
            solution_content = f.read()
        
        console.print(Panel(
            f"[cyan]{solution_content}[/cyan]",
            title="[bold green]📄 solution.yaml[/bold green]",
            border_style="green",
            box=box.ROUNDED
        ))
        console.print()
    
    def show_hints(self, level_name, level_path=None):
        """Show helpful hints based on the level - DEPRECATED, use show_progressive_hints"""
        hints = {
            "level-1-pods": [
                "Use `kubectl get pod nginx-broken -n arena` to check status",
                "Use `kubectl describe pod nginx-broken -n arena` to see events",
                "Use `kubectl logs nginx-broken -n arena` to check logs",
                "The pod has a bad command. Check what command is being run.",
                "Remember: You can't edit a running pod - delete and recreate it!"
            ],
            "level-2-deployments": [
                "Use `kubectl get deployment web -n arena` to check status",
                "Use `kubectl describe deployment web -n arena` for details",
                "Scale with `kubectl scale deployment web --replicas=N -n arena`",
                "Or edit with `kubectl edit deployment web -n arena`"
            ]
        }
        
        level_hints = hints.get(level_name, ["Explore with kubectl commands!"])
        
        hint_table = Table(title="💡 Helpful Commands", box=box.ROUNDED, border_style="blue")
        hint_table.add_column("Hint", style="cyan")
        
        for hint in level_hints:
            hint_table.add_row(hint)
        
        console.print(hint_table)
        console.print()
        
        # Ask if they want to see the solution
        if level_path:
            if Confirm.ask("[yellow]📄 Would you like to see the solution.yaml file?[/yellow]", default=False):
                console.print()
                self.show_solution_file(level_path)
                console.print("[dim]💡 Tip: You can use this as a reference to fix the issue[/dim]\n")
    
    def get_resource_status(self, level_name, level_path=None):
        """Get current status using domain deployer"""
        if not level_path:
            # Fallback to generic message
            return "Status check not available"

        try:
            status_dict = self.current_domain.deployer.get_status(level_path)
            return status_dict.get('message', 'Unknown')
        except Exception as e:
            return f"Error: {str(e)}"
    
    def show_terminal_instructions(self, level_name):
        """Show clear instructions about opening another terminal"""
        # Get domain-specific instructions
        requires_cluster = self.current_domain.config.capabilities.get('requires_cluster', False)

        if requires_cluster:
            # Kubernetes-specific instructions
            instructions_text = (
                "[bold yellow]📟 OPEN A NEW TERMINAL WINDOW[/bold yellow]\n\n"
                "[cyan]While this game is running:[/cyan]\n"
                "1️⃣  Open a NEW terminal window/tab\n"
                "2️⃣  Navigate to this directory\n"
                "3️⃣  Use kubectl commands to fix the issue\n"
                "4️⃣  Come back here and choose 'validate' or 'check'\n\n"
                "[dim]💡 Tip: Use Cmd+T (Mac) or Ctrl+Shift+T (Linux) to open a new tab[/dim]"
            )
        else:
            # Web security / other domain instructions
            instructions_text = (
                "[bold yellow]🌐 OPEN YOUR BROWSER[/bold yellow]\n\n"
                "[cyan]Challenge is ready:[/cyan]\n"
                "1️⃣  Open your web browser\n"
                "2️⃣  Navigate to the vulnerable application URL shown above\n"
                "3️⃣  Exploit the vulnerability to extract the flag\n"
                "4️⃣  Submit via visualizer (http://localhost:8080) OR come back here and choose 'validate'\n\n"
                "[dim]💡 Tip: You can submit flags directly in the visualizer's 'Submit Flag' tab![/dim]\n"
                "[dim]   After submitting in the visualizer, press Enter here to continue.[/dim]"
            )

        instructions = Panel(
            Text.from_markup(instructions_text),
            title="[bold red]⚠️  IMPORTANT[/bold red]",
            border_style="red",
            box=box.DOUBLE
        )
        console.print(instructions)
        console.print()
    
    def monitor_status(self, level_path, level_name, duration=10):
        """Monitor resource status in real-time"""
        console.print(f"\n[yellow]👀 Monitoring challenge status for {duration} seconds...[/yellow]\n")

        status_table = Table(box=box.SIMPLE, show_header=True, header_style="bold cyan")
        status_table.add_column("Time", style="dim")
        status_table.add_column("Status", style="yellow")

        with Live(status_table, refresh_per_second=2, console=console) as live:
            for i in range(duration):
                status = self.get_resource_status(level_name, level_path)
                status_table.add_row(
                    datetime.now().strftime("%H:%M:%S"),
                    status
                )
                time.sleep(1)

        console.print()
    
    def show_step_by_step_guide(self, level_name):
        """Show detailed step-by-step guide for beginners"""
        guides = {
            "level-1-pods": """
# 🎓 Step-by-Step Guide: Fix the Crashing Pod

## What's Wrong?
The pod has a bad command `nginxzz` that doesn't exist.

## How to Fix It:

### Step 1: Check what's wrong
```bash
kubectl get pod nginx-broken -n arena
kubectl describe pod nginx-broken -n arena
```

### Step 2: View the solution
Look at the file: `worlds/world-1-basics/level-1-pods/solution.yaml`

### Step 3: Delete the broken pod
```bash
kubectl delete pod nginx-broken -n arena
```

### Step 4: Apply the fix
```bash
kubectl apply -n arena -f worlds/world-1-basics/level-1-pods/solution.yaml
```

### Step 5: Verify it's working
```bash
kubectl get pod nginx-broken -n arena
```
Look for "Running" status!
            """,
            "level-2-deployments": """
# 🎓 Step-by-Step Guide: Fix the Deployment

## What's Wrong?
The deployment has 0 replicas, so no pods are running.

## How to Fix It:

### Step 1: Check the deployment
```bash
kubectl get deployment web -n arena
```

### Step 2: Scale up the replicas
```bash
kubectl scale deployment web --replicas=2 -n arena
```

### Step 3: Verify it's working
```bash
kubectl get deployment web -n arena
kubectl get pods -n arena
```
Look for "2/2" ready replicas!
            """
        }
        
        guide = guides.get(level_name, "No guide available for this level.")
        
        console.print(Panel(
            Markdown(guide),
            title="[bold green]📚 Beginner's Guide[/bold green]",
            border_style="green",
            box=box.ROUNDED
        ))
        console.print()
    
    def deploy_mission(self, level_path, level_name):
        """Deploy the challenge using domain deployer"""
        # Cleanup previous level if one was deployed
        if self.deployed_level_path and self.deployed_level_path != level_path:
            self.cleanup_current_level()

        console.print("\n[yellow]🚀 Deploying mission environment...[/yellow]")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            console=console
        ) as progress:
            task = progress.add_task("Deploying challenge...", total=1)

            # Use domain deployer
            success, message = self.current_domain.deployer.deploy_challenge(level_path)

            progress.advance(task)

        # Track deployed level for cleanup
        if success:
            self.deployed_level_path = level_path

        if not success:
            console.print(f"\n[red]Deployment failed: {message}[/red]\n")
            return

        console.print("\n")

        # Domain-specific deployment message
        requires_cluster = self.current_domain.config.capabilities.get('requires_cluster', False)
        deployment_backend = self.current_domain.config.capabilities.get('deployment_backend', None)

        # For domains with custom deployment backends, show the deployer's message
        if deployment_backend in ['mcp-gateway']:
            # MCP and similar domains provide their own detailed setup instructions
            console.print(message)
        elif requires_cluster:
            # Kubernetes challenges - fixing broken resources
            deployment_msg = (
                Text("🔴 MISSION DEPLOYED WITH BUGS! 🔴", style="bold red", justify="center") +
                Text("\n\nSomething is broken in the challenge environment.", style="yellow") +
                Text("\nYour mission: Find and fix the issue!", style="cyan")
            )
            console.print(Panel(
                deployment_msg,
                border_style="red",
                box=box.DOUBLE
            ))
        else:
            # Web security / exploitation challenges
            deployment_msg = (
                Text("🎯 VULNERABLE APPLICATION DEPLOYED! 🎯", style="bold yellow", justify="center") +
                Text("\n\nThe vulnerable application is now running.", style="green") +
                Text("\nYour mission: Exploit the vulnerability and capture the flag!", style="cyan")
            )
            console.print(Panel(
                deployment_msg,
                border_style="yellow",
                box=box.DOUBLE
            ))
        console.print()
    
    def validate_mission(self, level_path, level_name):
        """Validate solution using domain validator"""
        console.print("\n[yellow]🔍 Validating your solution...[/yellow]\n")

        # For web security domains, prompt for flag input
        flag = None
        if self.current_domain.config.id in ['web_security', 'container_security']:
            flag = Prompt.ask("🚩 Enter the flag you discovered")

        # Use domain validator
        success, message = self.current_domain.validator.validate(level_path, flag)

        if success:
            # Success!
            console.print(Panel(
                Text("✅ MISSION COMPLETE! ✅", style="bold green", justify="center") +
                Text(f"\n\n{message}", style="green"),
                border_style="green",
                box=box.DOUBLE
            ))
            return True
        else:
            # Failed
            console.print(Panel(
                Text("❌ Not quite there yet...", style="bold red", justify="center") +
                Text(f"\n\n{message}", style="red"),
                border_style="red",
                box=box.ROUNDED
            ))
            return False
    
    def play_level(self, level_path, level_name):
        """Play a single level with retro gaming UI"""
        mission = self.load_mission(level_path)
        self.current_mission = mission  # Set for visualizer
        self.current_level_path = level_path  # Set for domain visualizer

        # Show retro level start screen
        if RETRO_UI_ENABLED:
            level_num = int(level_name.split('-')[1]) if 'level-' in level_name else 0
            show_level_start(level_num, mission['name'], mission['xp'], mission.get('difficulty', 'beginner'))
            input()  # Wait for player to press any key
        
        # Show mission briefing with metadata
        console.clear()
        
        # Display retro-style header
        if RETRO_UI_ENABLED:
            console.print(show_retro_header(mission['name'], mission['xp'], self.domain_progress["total_xp"]))
            console.print()
        
        # Display difficulty and time estimate with gaming flair
        difficulty_colors = {
            "beginner": "green",
            "intermediate": "yellow",
            "advanced": "red",
            "expert": "magenta"
        }
        diff_color = difficulty_colors.get(mission.get('difficulty', 'beginner'), 'cyan')
        
        difficulty_icons = {
            "beginner": "⚡",
            "intermediate": "⚡⚡",
            "advanced": "⚡⚡⚡",
            "expert": "💀"
        }
        diff_icon = difficulty_icons.get(mission.get('difficulty', 'beginner'), '⚡')
        
        metadata = f"[{diff_color}]{diff_icon}[/{diff_color}] {mission.get('difficulty', 'Unknown').upper()}"
        metadata += f"  |  ⏱️  ~{mission.get('expected_time', '?')}"
        if 'concepts' in mission:
            metadata += f"  |  🎯 {', '.join(mission['concepts'])}"
        
        console.print(Panel(metadata, border_style=diff_color, box=box.HEAVY))
        console.print()
        
        self.show_mission_briefing(mission, level_name)
        
        # Deploy the mission
        self.deploy_mission(level_path, level_name)
        
        # Show terminal instructions prominently
        self.show_terminal_instructions(level_name)

        # Interactive loop with retro UI
        attempts = 0
        while True:
            console.print()
            
            # Show retro command menu
            if RETRO_UI_ENABLED:
                console.print(show_command_menu())
            else:
                # Domain-specific action descriptions
                requires_cluster = self.current_domain.config.capabilities.get('requires_cluster', False)

                console.print("="*60)
                console.print("[bold cyan]🎮 What would you like to do?[/bold cyan]")
                console.print("="*60)

                if requires_cluster:
                    console.print("  [cyan]check[/cyan]     - 👁️  Monitor the resource status")
                    console.print("  [cyan]guide[/cyan]     - 📖 Step-by-step instructions")
                    console.print("  [cyan]hints[/cyan]     - 💡 Helpful kubectl commands")
                    console.print("  [cyan]solution[/cyan]  - 📄 View the solution.yaml file")
                    console.print("  [cyan]validate[/cyan]  - ✅ Test if you've fixed it")
                else:
                    console.print("  [cyan]check[/cyan]     - 👁️  Check challenge status")
                    console.print("  [cyan]guide[/cyan]     - 📖 Step-by-step exploitation guide")
                    console.print("  [cyan]hints[/cyan]     - 💡 Progressive hints for exploitation")
                    console.print("  [cyan]solution[/cyan]  - 📄 View the solution walkthrough")
                    console.print("  [cyan]validate[/cyan]  - ✅ Submit your captured flag")

                console.print("  [cyan]skip[/cyan]      - ⏭️  Skip this level")
                console.print("  [cyan]quit[/cyan]      - 🚪 Exit the game")
                console.print("="*60)
            
            console.print()

            # Check if level was completed externally (via visualizer)
            if self.level_completed_externally:
                self.level_completed_externally = False  # Reset flag
                console.print("\n[bold green]🎉 LEVEL COMPLETED VIA VISUALIZER! 🎉[/bold green]")
                console.print(f"[yellow]🌟 +{self.current_mission.get('xp', 0)} XP! Total: {self.domain_progress['total_xp']} XP[/yellow]\n")

                # Show debrief
                self.show_debrief(level_path)

                if Confirm.ask("Ready for the next challenge?", default=True):
                    return True
                else:
                    return False

            action = Prompt.ask(
                "⚔️  Choose your action",
                choices=["check", "guide", "hints", "solution", "validate", "skip", "quit"],
                default="check"
            )

            if action == "check":
                # Real-time status monitoring
                self.monitor_status(level_path, level_name, duration=10)
                
            elif action == "guide":
                if RETRO_UI_ENABLED:
                    show_power_up_notification("guide")
                self.show_step_by_step_guide(level_name)
                
            elif action == "hints":
                if RETRO_UI_ENABLED:
                    show_power_up_notification("hint")
                console.print()
                self.show_hints_system(level_path)
            
            elif action == "solution":
                console.print("\n[yellow]📄 Showing solution file...[/yellow]\n")
                if RETRO_UI_ENABLED:
                    show_power_up_notification("solution")
                self.show_solution_file(level_path)
                console.print("[dim]💡 Use this as reference to fix the broken configuration[/dim]\n")
                
            elif action == "validate":
                attempts += 1
                console.print(f"\n[dim]⚔️  ATTEMPT #{attempts}[/dim]")
                
                if self.validate_mission(level_path, level_name):
                    # Victory with retro UI!
                    if RETRO_UI_ENABLED:
                        xp_earned = mission["xp"]
                        self.domain_progress["total_xp"] += xp_earned
                        show_victory(xp_earned, self.domain_progress["total_xp"])
                    else:
                        # Standard success animation
                        console.print("\n")
                        for i in range(3):
                            console.print("⭐ " * 20)
                            time.sleep(0.2)
                        
                        # Award XP
                        xp_earned = mission["xp"]
                        self.domain_progress["total_xp"] += xp_earned
                    
                    if level_name not in self.domain_progress["completed_levels"]:
                        self.domain_progress["completed_levels"].append(level_name)
                    self.save_progress()
                    
                    if not RETRO_UI_ENABLED:
                        console.print(f"\n[bold yellow]🌟 +{xp_earned} XP! Total: {self.domain_progress['total_xp']} XP[/bold yellow]")
                    console.print(f"[dim]⚡ Cleared in {attempts} attempt(s)[/dim]\n")
                    
                    # Check for milestones
                    if RETRO_UI_ENABLED:
                        completed_count = len(self.domain_progress["completed_levels"])
                        if completed_count == 10:
                            celebrate_milestone("world_complete")
                        elif completed_count == 25:
                            celebrate_milestone("halfway")
                        elif completed_count == 49:
                            celebrate_milestone("final_boss")
                        elif completed_count == 50:
                            show_game_complete()
                    
                    # Show debrief - THE LEARNING MOMENT!
                    self.show_debrief(level_path)
                    
                    if Confirm.ask("Ready for the next challenge?", default=True):
                        return True
                    else:
                        return False
                else:
                    encouragement = [
                        "Don't give up! You're learning! 💪",
                        "Every mistake teaches you something! 🧠",
                        "Try the 'guide' option for step-by-step help! 📚",
                        "Use 'check' to see real-time status! 👀"
                    ]
                    console.print(f"\n[yellow]{encouragement[attempts % len(encouragement)]}[/yellow]\n")
                    
                    if not Confirm.ask("Try again?", default=True):
                        return False
                        
            elif action == "skip":
                if Confirm.ask("Skip this level? (No XP will be awarded)", default=False):
                    return True
                    
            elif action == "quit":
                console.print("\n[yellow]👋 Thanks for playing DevSecOps Arena![/yellow]")
                cleanup_on_exit(self)
                console.print("[green]Progress saved![/green]\n")
                sys.exit(0)
    
    def play_world(self, world_name):
        """Play all levels in a world"""
        # Use domain-specific worlds directory
        world_path = self.current_domain.path / "worlds" / world_name

        if not world_path.exists():
            console.print(f"[red]Error: World '{world_name}' not found at {world_path}[/red]")
            return False
        
        # Get all level directories with natural sorting (level-1, level-2, ..., level-10)
        import re
        def natural_sort_key(path):
            """Extract numbers from path for natural sorting"""
            parts = re.split(r'(\d+)', path.name)
            return [int(part) if part.isdigit() else part for part in parts]
        
        levels = sorted([d for d in world_path.iterdir() if d.is_dir()], key=natural_sort_key)
        
        # Find where to resume from
        start_index = 0
        if self.progress.get("current_level"):
            # Try to find the current level in the list
            for i, level_path in enumerate(levels):
                if level_path.name == self.domain_progress["current_level"]:
                    # If the level is already completed, start from the next one
                    if self.domain_progress["current_level"] in self.domain_progress["completed_levels"]:
                        start_index = i + 1
                    else:
                        start_index = i
                    break
        
        # Play levels starting from resume point
        for level_path in levels[start_index:]:
            level_name = level_path.name
            
            # Save current level before playing
            self.domain_progress["current_level"] = level_name
            self.domain_progress["current_world"] = world_name
            self.save_progress()
            
            if not self.play_level(level_path, level_name):
                return False  # Player quit or stopped
        
        # World complete!
        console.clear()
        console.print(Panel(
            Text("🎉 WORLD COMPLETE! 🎉", style="bold green", justify="center") +
            Text(f"\n\nTotal XP: {self.domain_progress['total_xp']}", style="yellow", justify="center"),
            border_style="green",
            box=box.DOUBLE
        ))
        time.sleep(2)
        
        return True  # World completed successfully


def cleanup_on_exit(game_instance=None):
    """
    Cleanup function called on exit or signal interrupt.
    Ensures all game containers are properly cleaned up.
    """
    try:
        if game_instance:
            console.print("\n[yellow]Cleaning up game containers...[/yellow]")
            game_instance.cleanup_current_level()
            game_instance.stop_visualizer()

            # Additional cleanup for Docker-based domains
            if hasattr(game_instance, 'current_domain') and game_instance.current_domain:
                deployer = game_instance.current_domain.deployer
                # Check if this is a Docker deployer with cleanup_all method
                if hasattr(deployer, 'cleanup_all_containers'):
                    deployer.cleanup_all_containers()

            console.print("[green]Cleanup complete![/green]")
    except Exception as e:
        console.print(f"[yellow]Cleanup warning: {e}[/yellow]")


def signal_handler(signum, frame):
    """Handle SIGTERM and SIGINT signals for graceful shutdown."""
    import __main__
    console.print(f"\n[yellow]Received signal {signum}, shutting down gracefully...[/yellow]")
    if hasattr(__main__, 'game_instance') and __main__.game_instance:
        cleanup_on_exit(__main__.game_instance)
    sys.exit(0)


def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='DevSecOps Arena - Multi-Domain Security Training Platform')
    parser.add_argument('--no-viz', action='store_true',
                        help='Disable visualization server for a more realistic terminal-only experience')
    parser.add_argument('--viz-port', type=int, default=8080,
                        help='Port for visualization server (default: 8080)')
    parser.add_argument('--domain', type=str, default=None,
                        help='Pre-select a domain (e.g., kubernetes, web_security)')
    args = parser.parse_args()

    # Create game instance
    game = Arena(enable_visualizer=not args.no_viz, domain=args.domain)

    # Store for cleanup
    import __main__
    __main__.game_instance = game

    # First time setup - get player name
    if game.progress["player_name"] == "Padawan":
        console.print()
        game.progress["player_name"] = get_player_name(console)
        game.save_progress()
        console.print(f"\n[green]✨ Welcome, {game.progress['player_name']}![/green]\n")
        time.sleep(1)

    game.show_welcome()

    # Start visualizer if enabled
    if game.enable_visualizer:
        game.start_visualizer(port=args.viz_port)
        time.sleep(1)
    
    # Get worlds from domain configuration
    all_worlds = game.current_domain.config.worlds

    # Check if there's progress to resume
    has_progress = len(game.domain_progress["completed_levels"]) > 0 or game.domain_progress.get("current_level")

    if has_progress:
        current_level = game.domain_progress.get("current_level", "None")
        current_world = game.domain_progress.get("current_world", all_worlds[0] if all_worlds else "world-1-basics")
        completed_count = len(game.domain_progress["completed_levels"])

        console.print(Panel(
            f"[yellow]📍 Resume Point Detected[/yellow]\n\n"
            f"Current Level: [cyan]{current_level}[/cyan]\n"
            f"Completed: [green]{completed_count}[/green] levels\n"
            f"Total XP: [yellow]{game.domain_progress['total_xp']}[/yellow]",
            title="[bold]Continue Your Journey[/bold]",
            border_style="yellow"
        ))
        console.print()

        if Confirm.ask("Continue from where you left off?", default=True):
            # Find which world to start from
            start_world_index = 0
            for i, world in enumerate(all_worlds):
                if world == current_world:
                    start_world_index = i
                    break

            # Play from current world through to the end
            for world in all_worlds[start_world_index:]:
                if not game.play_world(world):
                    break  # Player quit

        elif Confirm.ask("Start from the beginning instead?", default=False):
            game.domain_progress["current_level"] = None
            game.domain_progress["completed_levels"] = []
            game.domain_progress["total_xp"] = 0
            game.save_progress()

            # Play all worlds from the beginning
            for world in all_worlds:
                if not game.play_world(world):
                    break  # Player quit
        else:
            console.print("\n[yellow]See you later, Padawan![/yellow]\n")
    else:
        if Confirm.ask("Ready to start your training?", default=True):
            # Play all worlds from the beginning
            for world in all_worlds:
                if not game.play_world(world):
                    break  # Player quit
        else:
            console.print("\n[yellow]See you later, Padawan![/yellow]\n")

if __name__ == "__main__":
    game_instance = None
    try:
        # Store reference to game for cleanup
        import __main__
        __main__.game_instance = None

        # Register signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        # Register cleanup function to run on normal exit
        atexit.register(lambda: cleanup_on_exit(__main__.game_instance) if hasattr(__main__, 'game_instance') else None)

        main()
    except KeyboardInterrupt:
        console.print("\n\n[yellow]👋 Game interrupted. Cleaning up...[/yellow]")
        if hasattr(__main__, 'game_instance') and __main__.game_instance:
            cleanup_on_exit(__main__.game_instance)
        console.print("[yellow]Progress saved![/yellow]\n")
        sys.exit(0)
    finally:
        # Clean up resources if game was started
        if hasattr(__main__, 'game_instance') and __main__.game_instance:
            cleanup_on_exit(__main__.game_instance)
