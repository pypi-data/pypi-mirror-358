import typer
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt
import sys

app = typer.Typer()
console = Console()


def create_welcome_panel():
    """创建欢迎面板"""
    content = Text()
    content.append("* Welcome to ", style="white")
    content.append("Vin", style="bold white")
    content.append("!\n\n", style="white")
    content.append("/help", style="green")
    content.append(" for help, ", style="white")
    content.append("/status", style="green")
    content.append(" for your current setup\n\n", style="white")
    content.append("cwd: ", style="white")

    panel = Panel(content, border_style="orange1", padding=(1, 2), expand=False)
    return panel


def create_tips_section():
    """创建提示部分"""
    tips = [
        "Tips for getting started:\n",
        "1. Run /init to create a VIN.md file with instructions for Vin",
        "2. Use Vin to help with file analysis, editing, bash commands and git",
        "3. Be as specific as you would with another engineer for the best results",
        "4. ✓ Run /terminal-setup to set up terminal integration\n",
        "* Tip: Use /memory to view and manage Vin memory",
    ]

    console.print()
    for tip in tips:
        if tip.startswith("4."):
            console.print(tip, style="white")
        else:
            console.print(tip, style="dim white")


def interactive_mode():
    """交互模式主循环"""
    console.print("Enter to confirm · Esc to exit", style="dim white")
    console.print()

    # 显示欢迎面板
    console.print(create_welcome_panel())

    # 显示提示信息
    create_tips_section()

    console.print()
    console.rule(style="dim white")
    console.print()

    # 主循环
    while True:
        try:
            # 使用 rich 的 Prompt 获取用户输入
            user_input = Prompt.ask("> ", console=console)

            # 处理用户输入
            if user_input.lower() in ["exit", "quit", "q"]:
                console.print("Goodbye!", style="green")
                break
            elif user_input.lower() == "hi":
                console.print("hello world", style="green")
            else:
                console.print(f"You typed: {user_input}", style="yellow")

        except KeyboardInterrupt:
            console.print("\nGoodbye!", style="green")
            break
        except EOFError:
            console.print("\nGoodbye!", style="green")
            break


@app.command()
def main():
    """VIN CLI - AI工作流优化工具"""
    interactive_mode()


if __name__ == "__main__":
    app()
