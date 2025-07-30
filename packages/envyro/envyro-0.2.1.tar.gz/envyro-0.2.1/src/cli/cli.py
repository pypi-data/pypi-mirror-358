import typer
from typer import Option
from rich.console import Console

from cli.utils.get_files import scan_envyro_files
# from parser import EnvyroCompiler
from parser import EnvyroParser

app = typer.Typer()
console = Console()


@app.command()
def export(
    env: str = Option(
        None,
        "--env", "-e",
        help="For which environment do we need to export the .envyro file? (e.g., dev, prod, staging)"
    ),
    source: str = Option(
        None,
        "--source", "-s",
        help="Path to the source .envyro file that requires conversion"
    ),
    shell: bool = Option(
        False,
        "--shell",
        help="Export variables to shell instead of a file"
    ),
):

    if source is None:
        console.print(
            "[bold yellow]Source not mentioned, scanning current dir...[/bold yellow]")
        source = scan_envyro_files()
        if len(source) == 0:
            console.print(
                "[bold red]No .envyro files found in the current directory.[/bold red]")
            raise typer.Exit(code=1)
        elif len(source) > 1:  # More than one .envyro file found ::> should we give a prompt to select one? maybe yes, TODO
            console.print(
                "[bold red]Multiple .envyro files found, please specify one using --source option.[/bold red]")
            raise typer.Exit(code=1)
        else:
            source = source[0]
        console.print(
            f"[bold green]Using source file: {source}[/bold green]")
    else:
        source = source.strip()
        console.print(
            f"[bold green]Using source file: {source}[/bold green]")
        
    if env is None:
        console.print(
            "[bold red]Please provide at least one of the following options: --env")
        raise typer.Exit(code=1)
    # compiler = EnvyroCompiler(source, env)

    try:
        parser = EnvyroParser(source)
        if shell:
            env_vars = parser.get_env_vars(env)
            for key, val in env_vars.items():
                env_key = key.upper().replace(".", "_")
                print(f"export {env_key}={val}")
        else:
            parser.export_env_file(env)
            console.print(
                f"[bold green]Compilation successful for environment '{env}'[/bold green]")
    except Exception as e:
        console.print(f"[bold red]Error: {e}[/bold red]")
        raise typer.Exit(code=1)


@app.command()
def split(source: str = Option(
    None,
    "--source", "-s",
    help="Path to the source .envyro file that requires conversion"
)):
    if source is None:

        console.print(
            "[bold yellow]Source not mentioned, scanning current dir...[/bold yellow]")
        source = scan_envyro_files()
        if len(source) == 0:
            console.print(
                "[bold red]No .envyro files found in the current directory.[/bold red]")
            raise typer.Exit(code=1)
        elif len(source) > 1:  # More than one .envyro file found ::> should we give a prompt to select one? maybe yes, TODO
            console.print(
                "[bold red]Multiple .envyro files found, please specify one using --source option.[/bold red]")
            raise typer.Exit(code=1)
        else:
            source = source[0]
    else:
        source = source.strip()
    console.print(
        f"[bold green]Using source file: {source}[/bold green]")

    try:
        parser = EnvyroParser(source)
        envs = parser.export_all()
        console.print(
            f"[bold green]Compilation successful for environments {', '.join(envs)}[/bold green]")
    except Exception as e:
        console.print(f"[bold red]Error: {e}[/bold red]")
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
