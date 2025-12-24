#!/usr/bin/env python3
"""
K8sQuest Reset Tool - Clean level state
"""

import sys
import subprocess
from pathlib import Path
from rich.console import Console
from rich.prompt import Confirm

console = Console()

def reset_level(world, level):
    """Reset a specific level to initial state"""
    base_dir = Path(__file__).parent.parent
    level_path = base_dir / "worlds" / world / level
    
    if not level_path.exists():
        console.print(f"[red]Error: Level not found: {world}/{level}[/red]")
        return False
    
    broken_file = level_path / "broken.yaml"
    if not broken_file.exists():
        console.print(f"[red]Error: No broken.yaml found in {level}[/red]")
        return False
    
    console.print(f"[yellow]Resetting {world}/{level}...[/yellow]\n")
    
    # Delete namespace (clean slate)
    console.print("1️⃣  Deleting namespace...")
    subprocess.run(
        ["kubectl", "delete", "namespace", "k8squest", "--ignore-not-found"],
        capture_output=True
    )
    
    # Recreate namespace
    console.print("2️⃣  Creating fresh namespace...")
    subprocess.run(
        ["kubectl", "create", "namespace", "k8squest"],
        capture_output=True
    )
    
    # Apply broken state
    console.print("3️⃣  Deploying broken resources...")
    result = subprocess.run(
        ["kubectl", "apply", "-n", "k8squest", "-f", str(broken_file)],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        console.print("\n[green]✅ Level reset successfully![/green]")
        console.print(f"[dim]You can now retry: {level}[/dim]\n")
        return True
    else:
        console.print(f"\n[red]❌ Reset failed: {result.stderr}[/red]\n")
        return False

def reset_all():
    """Reset entire game state"""
    console.print("[yellow]This will reset ALL levels and clear your progress![/yellow]")
    
    if not Confirm.ask("Are you sure?", default=False):
        console.print("[dim]Cancelled[/dim]")
        return
    
    # Delete namespace
    console.print("\n[yellow]Cleaning up...[/yellow]")
    subprocess.run(
        ["kubectl", "delete", "namespace", "k8squest", "--ignore-not-found"],
        capture_output=True
    )
    
    # Remove progress file
    base_dir = Path(__file__).parent.parent
    progress_file = base_dir / "progress.json"
    if progress_file.exists():
        progress_file.unlink()
    
    console.print("[green]✅ Game reset complete![/green]\n")

def main():
    if len(sys.argv) < 2:
        console.print("[bold]K8sQuest Reset Tool[/bold]\n")
        console.print("Usage:")
        console.print("  python3 engine/reset.py <level-name>")
        console.print("  python3 engine/reset.py all")
        console.print("\nExamples:")
        console.print("  python3 engine/reset.py level-1-pods")
        console.print("  python3 engine/reset.py level-2-deployments")
        console.print("  python3 engine/reset.py all")
        return
    
    if sys.argv[1] == "all":
        reset_all()
    else:
        level = sys.argv[1]
        reset_level("world-1-basics", level)

if __name__ == "__main__":
    main()
