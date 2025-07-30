import typer
from bashbuddy.commands.generate import generate
from bashbuddy.commands.explain import explain
from bashbuddy.commands.fix import fix
from bashbuddy.commands.explain_code import explain_code
from bashbuddy.commands.ask import ask
from bashbuddy.commands.setup import setup

app = typer.Typer(help="BashBuddy: Your AI-powered shell assistant.")

app.command()(generate)
app.command()(explain)
app.command()(fix)
app.command()(explain_code)
app.command()(ask)
app.command()(setup)

if __name__ == "__main__":
    app() 