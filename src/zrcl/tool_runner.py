import sys
import click
import importlib
import os

incase_args = sys.argv[2:]

# Dictionary to store modules
pkgs = {}

# Get the current directory where the script is located
currentDir = os.path.dirname(os.path.realpath(__file__))

# Loop through all packages that start with 'tool_' in the current directory
for file in os.listdir(currentDir):
    name = f"zrcl.{os.path.splitext(file)[0]}"

    if not name.startswith("zrcl.tool_"):
        continue  # Skip packages that do not start with 'tool_'

    if name == "zrcl.tool_runner":
        continue

    # Import the module dynamically
    pkg = importlib.import_module(name)

    # Check if the module has a 'run' attribute, and add it to the dictionary if it does
    if hasattr(pkg, "run"):
        pkgs[name[10:]] = pkg


class CMD(click.Command):
    def format_help(self, ctx, formatter):
        ctx.invoke(run, name=incase_args[0], args=incase_args[1:])


@click.group()
def cli():
    pass


@cli.command()
def list():
    """List all available tools."""
    for name in pkgs.keys():
        try:
            click.echo(f"{name}\t\t- {pkgs[name].run.__doc__.strip()}")
        except AttributeError:
            click.echo(f"{name}\t\t- (No description provided)")


@cli.command("run", cls=CMD)
@click.argument(
    "name", type=click.STRING, shell_complete=lambda _, __, **kwargs: list(pkgs.keys())
)
@click.argument("args", type=click.UNPROCESSED, nargs=-1)
def _run(name, args):
    """Run a specified tool by name."""
    if name not in pkgs:
        click.echo(f"Package {name} not found")
        return

    # Get the package and call its 'run' function
    pkg = pkgs[name]

    # pop first 2 of sys.argv
    sys.argv = (name, *args)

    pkg.run()


def run():
    cli()


if __name__ == "__main__":
    cli()
