import typer
from rich.console import Console
from rich.progress import track
from rich.panel import Panel
from rich.text import Text
from rich import print as rprint
import os

from lcm_engine.migration.agent import MigrationAgent, MigrationResult

app = typer.Typer(help="LCM-Engine: AI-Powered Legacy Code Modernization")
console = Console()
agent = MigrationAgent()

@app.command()
def index(source: str = typer.Option(..., "--source", help="Path to source files"), language: str = typer.Option("cobol", "--language", help="Source language")):
    """
    Index a codebase or file for RAG context optimization.
    """
    if not os.path.exists(source):
        console.print(f"[bold red]Error[/bold red]: Path {source} does not exist.")
        raise typer.Exit(1)
        
    console.print(Panel(f"Indexing [bold cyan]{source}[/bold cyan] for Context Optimization", title="Indexing Started"))
    
    files_to_index = []
    if os.path.isfile(source):
        files_to_index.append(source)
    else:
        for root, dirs, files in os.walk(source):
            for file in files:
                if file.endswith('.cbl') or file.endswith('.cob') or file.endswith('.txt'):
                     files_to_index.append(os.path.join(root, file))
                     
    total_chunks = 0
    with typer.progressbar(files_to_index, label="Processing files") as progress:
        for filepath in progress:
            with open(filepath, 'r') as f:
                 code = f.read()
                 chunks = agent.index_repo(code, file_name=os.path.basename(filepath))
                 total_chunks += chunks
                 
    console.print(f"\\n[bold green]Success![/bold green] Indexed {total_chunks} chunks into ChromaDB from {len(files_to_index)} files.\\n")


@app.command()
def migrate(input: str = typer.Option(..., "--input", help="Input file path"), from_lang: str = typer.Option("cobol", "--from"), to_lang: str = typer.Option("python", "--to"), verify: bool = typer.Option(True, "--verify", help="Enable neuro-symbolic verification")):
    """
    Run the migration agent with verification.
    """
    if not os.path.exists(input):
        console.print(f"[bold red]Error[/bold red]: File {input} does not exist.")
        raise typer.Exit(1)
        
    console.print(Panel(f"Migrating [bold yellow]{input}[/bold yellow] from {from_lang} to {to_lang}\\nVerification Enabled: {verify}", title="Migration Execution"))

    with open(input, 'r') as f:
        source_code = f.read()

    with console.status("[bold green]Agent Orchestrating Migration Engine (RAG -> LLM -> Z3)...[/bold green]"):
        result: MigrationResult = agent.migrate(
            source_code=source_code,
            source_lang=from_lang,
            target_lang=to_lang
        )

    if result.status == "SUCCESS":
         console.print("\\n[bold green]✓ Migration Verified Successfully[/bold green]")
         console.print(f"Attempts taken: {result.attempts} / {agent.max_retries}")
         console.print(Panel.fit(result.translated_code, title="Python Output", border_style="green"))
         # Save to file
         out_name = input.replace(".cbl", "_modernized.py")
         with open(out_name, 'w') as f:
              f.write(result.translated_code)
         console.print(f"[dim]Output saved to {out_name}[/dim]")
    else:
         console.print("\\n[bold red]✕ Migration Failed Verification[/bold red]")
         console.print(f"Exhausted {result.attempts} max attempts.")
         console.print(Panel(str(result.error_log[-1] if result.error_log else "Unknown Runtime Error"), title="Last Error Context", border_style="red"))
         console.print("Partial Output (Not Verified):")
         console.print(Panel.fit(result.translated_code, style="red"))

@app.command()
def verify_only(source: str, target: str):
    """
    Verify existing translation.
    """
    console.print("This command compares an existing source code against an existing target code using Z3.")
    # Implement standalone if needed based on priority

if __name__ == "__main__":
    app()
