import typer

app = typer.Typer()


@app.command()
def hello(name: str):
    print(f"Hello {name}")


@app.command()
def goodbye(name: str, formal: bool = False):
    if formal:
        print(f"Goodbye Ms. {name}. Have a good day.")
    else:
        print(f"Bye {name}!")


if __name__ == "__main__":
    app()
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Compile .envyro file to .env.<env>")
    parser.add_argument("--file", "-f", required=True, help="Path to the .envyro file")
    parser.add_argument("--env", "-e", required=True, help="Environment name (e.g., dev, prod)")

    args = parser.parse_args()
    compiler = EnvyroCompiler(args.file, args.env)
    compiler.compile()