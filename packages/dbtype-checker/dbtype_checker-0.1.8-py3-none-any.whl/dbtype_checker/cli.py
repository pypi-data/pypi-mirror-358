import typer
from .checker import print_mismatches

app = typer.Typer()

@app.command()
def main(db_url: str):
    print_mismatches(db_url)

if __name__ == "__main__":
    app()
