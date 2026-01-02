#!/usr/bin/env python3
"""
Script to complete the engine.py refactoring for Phase 3.

This script makes targeted replacements to update engine.py to use the domain plugin system.
"""

import re
from pathlib import Path

def refactor_engine():
    engine_file = Path("engine/engine.py")

    with open(engine_file, 'r') as f:
        content = f.read()

    # Track changes
    changes = []

    # 1. Replace self.progress["total_xp"] with self.domain_progress["total_xp"]
    pattern1 = r'self\.progress\["total_xp"\]'
    replacement1 = 'self.domain_progress["total_xp"]'
    if re.search(pattern1, content):
        content = re.sub(pattern1, replacement1, content)
        changes.append("Updated total_xp references")

    # 2. Replace self.progress["completed_levels"] with self.domain_progress["completed_levels"]
    pattern2 = r'self\.progress\["completed_levels"\]'
    replacement2 = 'self.domain_progress["completed_levels"]'
    if re.search(pattern2, content):
        content = re.sub(pattern2, replacement2, content)
        changes.append("Updated completed_levels references")

    # 3. Replace self.progress["current_level"] with self.domain_progress["current_level"]
    pattern3 = r'self\.progress\["current_level"\]'
    replacement3 = 'self.domain_progress["current_level"]'
    if re.search(pattern3, content):
        content = re.sub(pattern3, replacement3, content)
        changes.append("Updated current_level references")

    # 4. Replace self.progress["current_world"] with self.domain_progress["current_world"]
    pattern4 = r'self\.progress\["current_world"\]'
    replacement4 = 'self.domain_progress["current_world"]'
    if re.search(pattern4, content):
        content = re.sub(pattern4, replacement4, content)
        changes.append("Updated current_world references")

    # 5. Update deploy_mission to use domain.deployer
    deploy_old = '''    def deploy_mission(self, level_path, level_name):
        """Deploy the broken Kubernetes resources"""
        console.print("\\n[yellow]🚀 Deploying mission environment...[/yellow]")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            console=console
        ) as progress:
            task = progress.add_task("Setting up namespace...", total=3)

            # Delete and recreate namespace
            subprocess.run(
                ["kubectl", "delete", "namespace", "k8squest", "--ignore-not-found"],
                capture_output=True
            )
            progress.advance(task)

            subprocess.run(
                ["kubectl", "create", "namespace", "k8squest"],
                capture_output=True
            )
            progress.update(task, description="Deploying broken resources...")
            progress.advance(task)

            # Apply broken config (without forcing namespace to respect YAML)
            result = subprocess.run(
                ["kubectl", "apply", "-f", str(level_path / "broken.yaml")],
                capture_output=True,
                text=True
            )
            # Log errors for debugging (optional)
            if result.returncode != 0:
                console.print(f"[dim red]Warning: {result.stderr}[/dim red]")

            progress.update(task, description="✅ Environment ready!")
            progress.advance(task)'''

    deploy_new = '''    def deploy_mission(self, level_path, level_name):
        """Deploy the challenge using domain deployer"""
        console.print("\\n[yellow]🚀 Deploying mission environment...[/yellow]")

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

            if not success:
                console.print(f"[red]Deployment failed: {message}[/red]")
                return'''

    if deploy_old in content:
        content = content.replace(deploy_old, deploy_new)
        changes.append("Updated deploy_mission() to use domain.deployer")

    # 6. Update validate_mission to use domain.validator
    validate_old = '''    def validate_mission(self, level_path, level_name):
        """Run validation script and show results"""
        console.print("\\n[yellow]🔍 Validating your solution...[/yellow]\\n")

        validate_script = level_path / "validate.sh"
        result = subprocess.run(
            ["bash", str(validate_script)],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            # Success!
            console.print(Panel(
                Text("✅ MISSION COMPLETE! ✅", style="bold green", justify="center") +
                Text(f"\\n\\n{result.stdout}", style="green"),
                border_style="green",
                box=box.DOUBLE
            ))
            return True
        else:
            # Failed
            console.print(Panel(
                Text("❌ Not quite there yet...", style="bold red", justify="center") +
                Text(f"\\n\\n{result.stdout}", style="red"),
                border_style="red",
                box=box.ROUNDED
            ))
            return False'''

    validate_new = '''    def validate_mission(self, level_path, level_name):
        """Validate solution using domain validator"""
        console.print("\\n[yellow]🔍 Validating your solution...[/yellow]\\n")

        # Use domain validator
        success, message = self.current_domain.validator.validate(level_path)

        if success:
            # Success!
            console.print(Panel(
                Text("✅ MISSION COMPLETE! ✅", style="bold green", justify="center") +
                Text(f"\\n\\n{message}", style="green"),
                border_style="green",
                box=box.DOUBLE
            ))
            return True
        else:
            # Failed
            console.print(Panel(
                Text("❌ Not quite there yet...", style="bold red", justify="center") +
                Text(f"\\n\\n{message}", style="red"),
                border_style="red",
                box=box.ROUNDED
            ))
            return False'''

    if validate_old in content:
        content = content.replace(validate_old, validate_new)
        changes.append("Updated validate_mission() to use domain.validator")

    # 7. Update get_resource_status to use domain.deployer
    status_old = '''    def get_resource_status(self, level_name):
        """Get current status of the Kubernetes resource"""
        try:
            if "pod" in level_name:
                result = subprocess.run(
                    ["kubectl", "get", "pod", "nginx-broken", "-n", "k8squest",
                     "-o", "jsonpath={.status.phase}"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                return result.stdout.strip() or "Unknown"
            elif "deployment" in level_name:
                result = subprocess.run(
                    ["kubectl", "get", "deployment", "web", "-n", "k8squest",
                     "-o", "jsonpath={.status.readyReplicas}"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                ready = result.stdout.strip() or "0"
                return f"{ready} replicas ready"
        except:
            return "Unknown"
        return "Unknown"'''

    status_new = '''    def get_resource_status(self, level_name, level_path=None):
        """Get current status using domain deployer"""
        if not level_path:
            # Fallback to generic status
            return "Status unavailable"

        try:
            status_dict = self.current_domain.deployer.get_status(level_path)
            return status_dict.get('message', 'Unknown')
        except:
            return "Unknown"'''

    if status_old in content:
        content = content.replace(status_old, status_new)
        changes.append("Updated get_resource_status() to use domain.deployer")

    # Write back
    with open(engine_file, 'w') as f:
        f.write(content)

    print("Refactoring complete!")
    print("Changes made:")
    for change in changes:
        print(f"  ✅ {change}")

    return len(changes)

if __name__ == "__main__":
    changes = refactor_engine()
    print(f"\nTotal changes: {changes}")
