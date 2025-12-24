#!/usr/bin/env python3
"""
K8sQuest Retro Gaming UI - Contra/Mario Style
ASCII art, animations, and classic arcade aesthetics
"""

import time
import random
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich import box

console = Console()

# Retro Gaming ASCII Art
KUBECTL_HERO = r"""
    ⚔️
   /|\    
   / \    
 KUBECTL 
  HERO!  
"""

KUBERNETES_LOGO = r"""
    ⎈⎈⎈
   ⎈⎈⎈⎈⎈
  ⎈⎈⎈⎈⎈⎈⎈
 ⎈⎈⎈⎈⎈⎈⎈⎈⎈
⎈⎈⎈ K8s ⎈⎈⎈
 ⎈⎈⎈⎈⎈⎈⎈⎈⎈
  ⎈⎈⎈⎈⎈⎈⎈
   ⎈⎈⎈⎈⎈
    ⎈⎈⎈
"""

LEVEL_START_BANNER = r"""
╔══════════════════════════════════════════╗
║  ███╗   ███╗██╗███████╗███████╗██╗ ██████╗ ███╗   ██╗
║  ████╗ ████║██║██╔════╝██╔════╝██║██╔═══██╗████╗  ██║
║  ██╔████╔██║██║███████╗███████╗██║██║   ██║██╔██╗ ██║
║  ██║╚██╔╝██║██║╚════██║╚════██║██║██║   ██║██║╚██╗██║
║  ██║ ╚═╝ ██║██║███████║███████║██║╚██████╔╝██║ ╚████║
║  ╚═╝     ╚═╝╚═╝╚══════╝╚══════╝╚═╝ ╚═════╝ ╚═╝  ╚═══╝
║               🎮 READY PLAYER ONE! 🎮                  
╚══════════════════════════════════════════╝
"""

VICTORY_SCREEN = r"""
██╗   ██╗██╗ ██████╗████████╗ ██████╗ ██████╗ ██╗   ██╗██╗
██║   ██║██║██╔════╝╚══██╔══╝██╔═══██╗██╔══██╗╚██╗ ██╔╝██║
██║   ██║██║██║        ██║   ██║   ██║██████╔╝ ╚████╔╝ ██║
╚██╗ ██╔╝██║██║        ██║   ██║   ██║██╔══██╗  ╚██╔╝  ╚═╝
 ╚████╔╝ ██║╚██████╗   ██║   ╚██████╔╝██║  ██║   ██║   ██╗
  ╚═══╝  ╚═╝ ╚═════╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚═╝
"""

GAME_OVER = r"""
╔═══════════════════════════════════════════════════════╗
║   ██████╗  █████╗ ███╗   ███╗███████╗                ║
║  ██╔════╝ ██╔══██╗████╗ ████║██╔════╝                ║
║  ██║  ███╗███████║██╔████╔██║█████╗                  ║
║  ██║   ██║██╔══██║██║╚██╔╝██║██╔══╝                  ║
║  ╚██████╔╝██║  ██║██║ ╚═╝ ██║███████╗                ║
║   ╚═════╝ ╚═╝  ╚═╝╚═╝     ╚═╝╚══════╝                ║
║   ██████╗ ██╗   ██╗███████╗██████╗                   ║
║  ██╔═══██╗██║   ██║██╔════╝██╔══██╗                  ║
║  ██║   ██║██║   ██║█████╗  ██████╔╝                  ║
║  ██║   ██║╚██╗ ██╔╝██╔══╝  ██╔══██╗                  ║
║  ╚██████╔╝ ╚████╔╝ ███████╗██║  ██║                  ║
║   ╚═════╝   ╚═══╝  ╚══════╝╚═╝  ╚═╝                  ║
╚═══════════════════════════════════════════════════════╝
"""

LIVES_DISPLAY = [
    "❤️❤️❤️",
    "❤️❤️🖤",
    "❤️🖤🖤",
    "🖤🖤🖤"
]

WORLD_BANNERS = {
    "world-1": r"""
    ╔═══════════════════════════════════════╗
    ║   🌍 WORLD 1: KUBERNETES BASICS 🌍   ║
    ║      ⚡ Difficulty: BEGINNER ⚡      ║
    ╚═══════════════════════════════════════╝
    """,
    "world-2": r"""
    ╔═══════════════════════════════════════╗
    ║ 🔥 WORLD 2: DEPLOYMENTS & SCALING 🔥 ║
    ║    ⚡ Difficulty: INTERMEDIATE ⚡    ║
    ╚═══════════════════════════════════════╝
    """,
    "world-3": r"""
    ╔═══════════════════════════════════════╗
    ║   🌐 WORLD 3: NETWORKING NINJA 🌐    ║
    ║    ⚡ Difficulty: INTERMEDIATE ⚡    ║
    ╚═══════════════════════════════════════╝
    """,
    "world-4": r"""
    ╔═══════════════════════════════════════╗
    ║  💾 WORLD 4: STORAGE & STATEFUL 💾   ║
    ║      ⚡ Difficulty: ADVANCED ⚡      ║
    ╚═══════════════════════════════════════╝
    """,
    "world-5": r"""
    ╔═══════════════════════════════════════╗
    ║   🛡️ WORLD 5: SECURITY & OPS 🛡️     ║
    ║      ⚡ Difficulty: EXPERT ⚡       ║
    ╚═══════════════════════════════════════╝
    """
}

COIN_ANIMATION = ["⭐", "💫", "✨", "💎", "⭐"]
POWER_UP = "🍄"
STAR = "⭐"
TROPHY = "🏆"

def typewriter_effect(text, delay=0.03, style="bold green"):
    """Print text with typewriter effect"""
    for char in text:
        console.print(char, end="", style=style)
        time.sleep(delay)
    console.print()

def flash_text(text, count=3, delay=0.3, style="bold yellow"):
    """Flash text on/off"""
    for _ in range(count):
        console.print(text, style=style)
        time.sleep(delay)
        console.clear()
        time.sleep(delay)
    console.print(text, style=style)

def show_retro_welcome():
    """Display retro-style welcome screen"""
    console.clear()
    
    # Main title with animation
    title_art = r"""
    ╦╔═╔═╗╔═╗ ╦ ╦╔═╗╔═╗╔╦╗
    ╠╩╗╚═╗║═╬╗║ ║║╣ ╚═╗ ║ 
    ╩ ╩╚═╝╚═╝╚╚═╝╚═╝╚═╝ ╩ 
    """
    
    console.print(title_art, style="bold cyan")
    console.print()
    console.print(Align.center("🎮 KUBERNETES ADVENTURE GAME 🎮"), style="bold yellow")
    console.print(Align.center("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"), style="cyan")
    console.print()
    
    # Animated loading
    with console.status("[bold green]🕹️  LOADING GAME...", spinner="dots"):
        time.sleep(1.5)
    
    console.print()
    console.print(Align.center("✨ PRESS START TO BEGIN ✨"), style="bold magenta blink")
    console.print()

def show_world_entry(world_num):
    """Animated world entry screen"""
    console.clear()
    
    world_key = f"world-{world_num}"
    if world_key in WORLD_BANNERS:
        console.print(WORLD_BANNERS[world_key], style="bold yellow")
    
    # Countdown
    for i in range(3, 0, -1):
        console.print(Align.center(f"⏱️  {i}"), style="bold red")
        time.sleep(0.5)
        console.clear()
        if world_key in WORLD_BANNERS:
            console.print(WORLD_BANNERS[world_key], style="bold yellow")
    
    console.print(Align.center("🚀 GO! GO! GO!"), style="bold green")
    time.sleep(1)

def show_level_start(level_num, title, xp, difficulty):
    """Show level start screen like classic games"""
    console.clear()
    
    console.print(LEVEL_START_BANNER, style="bold cyan")
    console.print()
    
    # Level info
    info_panel = Panel(
        f"[bold yellow]LEVEL {level_num}[/bold yellow]\n"
        f"[cyan]{title}[/cyan]\n\n"
        f"[green]⭐ XP REWARD: {xp}[/green]\n"
        f"[magenta]⚡ DIFFICULTY: {difficulty.upper()}[/magenta]",
        border_style="yellow",
        box=box.DOUBLE,
        title="[bold red]🎯 MISSION BRIEFING[/bold red]"
    )
    
    console.print(Align.center(info_panel))
    console.print()
    console.print(Align.center("⌨️  Press any key to start..."), style="dim")

def show_victory(xp_earned, total_xp):
    """Victory screen with celebration"""
    console.clear()
    
    console.print(VICTORY_SCREEN, style="bold green")
    console.print()
    
    # XP Animation
    console.print(Align.center("🎊 MISSION COMPLETE! 🎊"), style="bold yellow")
    console.print()
    
    for coin in COIN_ANIMATION:
        console.print(Align.center(f"{coin} +{xp_earned} XP {coin}"), style="bold yellow")
        time.sleep(0.2)
        console.clear()
        console.print(VICTORY_SCREEN, style="bold green")
        console.print()
        console.print(Align.center("🎊 MISSION COMPLETE! 🎊"), style="bold yellow")
        console.print()
    
    console.print(Align.center(f"⭐ +{xp_earned} XP ⭐"), style="bold yellow")
    console.print(Align.center(f"💎 TOTAL XP: {total_xp} 💎"), style="bold cyan")
    console.print()

def show_game_complete():
    """Final game completion screen"""
    console.clear()
    
    console.print(VICTORY_SCREEN, style="bold yellow")
    console.print()
    console.print(Align.center("🏆🏆🏆 KUBERNETES MASTER! 🏆🏆🏆"), style="bold yellow")
    console.print()
    console.print(Align.center("YOU'VE CONQUERED ALL 50 LEVELS!"), style="bold green")
    console.print(Align.center("⎈⎈⎈ PERFECT! ⎈⎈⎈"), style="bold cyan")
    console.print()
    
    # Fireworks
    for _ in range(5):
        firework = random.choice(["💥", "✨", "🎆", "🎇", "⭐"])
        console.print(Align.center(f"{firework} {firework} {firework}"), style="bold yellow")
        time.sleep(0.3)

def show_hp_bar(current_hp, max_hp=3):
    """Show health/lives bar like classic games"""
    hearts = "❤️" * current_hp + "🖤" * (max_hp - current_hp)
    return f"[bold red]LIVES: {hearts}[/bold red]"

def show_xp_bar(current_xp, max_xp=10200):
    """Show XP progress bar"""
    percentage = (current_xp / max_xp) * 100
    filled = int(percentage / 5)
    bar = "█" * filled + "░" * (20 - filled)
    return f"[bold yellow]XP: [{bar}] {current_xp}/{max_xp}[/bold yellow]"

def show_command_menu():
    """Show retro-style command menu"""
    menu = Panel(
        "[bold cyan]🎮 GAME COMMANDS 🎮[/bold cyan]\n\n"
        "[yellow]check[/yellow]     - 👁️  Monitor resources\n"
        "[yellow]guide[/yellow]     - 📖 Step-by-step solution\n"
        "[yellow]hints[/yellow]     - 💡 Progressive hints\n"
        "[yellow]solution[/yellow]  - 📄 View solution.yaml\n"
        "[yellow]validate[/yellow]  - ✅ Test your fix\n"
        "[yellow]skip[/yellow]      - ⏭️  Skip level\n"
        "[yellow]quit[/yellow]      - 🚪 Save & exit",
        border_style="cyan",
        box=box.HEAVY,
        title="[bold red]⚔️ ACTIONS[/bold red]"
    )
    return menu

def show_power_up_notification(power_up_type):
    """Show power-up collection notification"""
    power_ups = {
        "hint": ("💡", "HINT UNLOCKED!"),
        "guide": ("📖", "GUIDE ACTIVATED!"),
        "solution": ("📄", "SOLUTION REVEALED!"),
        "skip": ("⏭️", "LEVEL SKIP!"),
        "complete": ("⭐", "LEVEL CLEARED!")
    }
    
    icon, text = power_ups.get(power_up_type, ("✨", "POWER UP!"))
    
    console.print()
    console.print(Panel(
        f"[bold yellow]{icon} {text} {icon}[/bold yellow]",
        border_style="yellow",
        box=box.DOUBLE
    ))
    console.print()

def show_loading_animation(text="Loading", duration=2):
    """Show retro loading animation"""
    frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    end_time = time.time() + duration
    
    i = 0
    while time.time() < end_time:
        frame = frames[i % len(frames)]
        console.print(f"\r{frame} {text}...", end="", style="bold cyan")
        time.sleep(0.1)
        i += 1
    
    console.print(f"\r✓ {text} complete!", style="bold green")

def show_error_screen(error_message):
    """Show error in retro style"""
    console.print()
    console.print(Panel(
        f"[bold red]❌ ERROR! ❌[/bold red]\n\n"
        f"[yellow]{error_message}[/yellow]\n\n"
        f"[dim]Press any key to continue...[/dim]",
        border_style="red",
        box=box.HEAVY,
        title="[bold red]⚠️  SYSTEM ALERT[/bold red]"
    ))
    console.print()

def show_retro_header(level_name, xp, total_xp):
    """Show retro-style header with stats"""
    header = (
        f"[bold cyan]═══════════════════════════════════════════════════════════[/bold cyan]\n"
        f"[bold yellow]🎮 K8SQUEST[/bold yellow]  │  "
        f"[cyan]Level: {level_name}[/cyan]  │  "
        f"[green]XP: {total_xp}[/green]  │  "
        f"[yellow]⭐ Reward: +{xp}[/yellow]\n"
        f"[bold cyan]═══════════════════════════════════════════════════════════[/bold cyan]"
    )
    return header

def show_8bit_separator(char="═", length=60, style="cyan"):
    """Show retro separator line"""
    console.print(char * length, style=style)

def celebrate_milestone(milestone_type):
    """Celebrate achievements with retro animations"""
    celebrations = {
        "world_complete": ("🌍 WORLD CLEARED!", "bold green"),
        "halfway": ("🔥 HALFWAY THERE!", "bold yellow"),
        "final_boss": ("👾 FINAL BOSS UNLOCKED!", "bold red"),
        "master": ("🏆 KUBERNETES MASTER!", "bold yellow")
    }
    
    message, style = celebrations.get(milestone_type, ("🎉 ACHIEVEMENT!", "bold cyan"))
    
    console.print()
    flash_text(f"{'─' * 50}\n{' ' * 10}{message}\n{'─' * 50}", count=3, style=style)
    console.print()

# Konami Code Easter Egg
KONAMI_CODE = ["↑", "↑", "↓", "↓", "←", "→", "←", "→", "B", "A"]

def check_konami_code(input_sequence):
    """Check if player entered Konami code"""
    if input_sequence == KONAMI_CODE:
        console.print()
        console.print("🎮 KONAMI CODE ACTIVATED! 🎮", style="bold yellow blink")
        console.print("⭐ +1000 BONUS XP! ⭐", style="bold green")
        console.print("💫 ALL HINTS UNLOCKED! 💫", style="bold cyan")
        console.print()
        return True
    return False
