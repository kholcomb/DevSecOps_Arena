#!/usr/bin/env python3
"""
Test suite for DevSecOps Arena Safety Guards
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from engine.safety import check_command_safety
from rich.console import Console

console = Console()

def test_safety_guards():
    """Test all safety guard rules"""
    
    tests = [
        # (command, should_be_safe, description)
        
        # Should be blocked (critical)
        ("kubectl delete namespace kube-system", False, "Delete kube-system namespace"),
        ("kubectl delete namespace kube-public", False, "Delete kube-public namespace"),
        ("kubectl delete namespace default", False, "Delete default namespace"),
        ("kubectl delete node kind-control-plane", False, "Delete cluster node"),
        ("kubectl delete crd mycrd.example.com", False, "Delete CRD"),
        ("kubectl delete clusterrole admin", False, "Delete ClusterRole"),
        ("kubectl delete clusterrolebinding admin", False, "Delete ClusterRoleBinding"),
        ("kubectl delete pods --all-namespaces", False, "Delete pods in all namespaces"),
        
        # Should warn but not block
        ("kubectl delete namespace arena", False, "Delete arena namespace (warning)"),
        ("kubectl delete pods --all -n arena", False, "Delete all pods (warning)"),
        ("kubectl delete pv my-pv", False, "Delete PersistentVolume (warning)"),
        
        # Should be safe
        ("kubectl get pods -n arena", True, "Get pods in arena"),
        ("kubectl delete pod nginx-broken -n arena", True, "Delete specific pod"),
        ("kubectl apply -f deployment.yaml -n arena", True, "Apply deployment"),
        ("kubectl scale deployment web --replicas=3 -n arena", True, "Scale deployment"),
        ("kubectl logs my-pod -n arena", True, "View pod logs"),
        ("kubectl describe pod my-pod -n arena", True, "Describe pod"),
        ("kubectl exec -it my-pod -n arena -- bash", True, "Exec into pod"),
        ("kubectl get nodes", True, "List nodes (read-only)"),
        ("kubectl get namespaces", True, "List namespaces"),
    ]
    
    passed = 0
    failed = 0
    
    console.print("\n[bold cyan]Testing DevSecOps Arena Safety Guards[/bold cyan]\n")
    console.print("="*70)
    
    for command, should_be_safe, description in tests:
        is_safe, message, severity = check_command_safety(command)
        
        # For warnings, consider them "not safe" for blocking purposes
        is_actually_safe = is_safe and severity == "safe"
        
        if is_actually_safe == should_be_safe:
            status = "[green]✅ PASS[/green]"
            passed += 1
        else:
            status = "[red]❌ FAIL[/red]"
            failed += 1
        
        console.print(f"{status} - {description}")
        if is_actually_safe != should_be_safe:
            console.print(f"  [dim]Command: {command}[/dim]")
            console.print(f"  [dim]Expected: {'safe' if should_be_safe else 'blocked'}, Got: {'safe' if is_actually_safe else 'blocked'}[/dim]")
            if message:
                console.print(f"  [dim]Message: {message}[/dim]")
    
    console.print("="*70)
    console.print(f"\n[bold]Results:[/bold] {passed} passed, {failed} failed out of {len(tests)} tests\n")
    
    if failed == 0:
        console.print("[bold green]🎉 All safety guard tests passed![/bold green]\n")
        return 0
    else:
        console.print(f"[bold red]⚠️  {failed} test(s) failed![/bold red]\n")
        return 1

if __name__ == "__main__":
    exit_code = test_safety_guards()
    sys.exit(exit_code)
