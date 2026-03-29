import difflib
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

console = Console()

class HITLGate:
    @staticmethod
    def request_approval(filepath: str, old_content: str, new_content: str) -> bool:
        diff = difflib.unified_diff(
            old_content.splitlines(),
            new_content.splitlines(),
            fromfile=f'OLD: {filepath}',
            tofile=f'NEW: {filepath}',
            lineterm=''
        )
        diff_text = '\\n'.join(diff)
        if not diff_text:
            return True  # No changes, ignore

        console.print(Panel(Syntax(diff_text, 'diff', theme='monokai'), title=f'🚨 APPROVAL REQUIRED: {filepath}', subtitle='Accept changes? (y/n)'))
        choice = input('>> ').strip().lower()
        return choice == 'y'
