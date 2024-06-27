import sys
import click
import importlib
import pkgutil
import os

incase_args = sys.argv[2:]

# Dictionary to store modules
pkgs = {}

# Get the current directory where the script is located
currentDir = os.path.dirname(os.path.realpath(__file__))

# Loop through all packages that start with 'tool_' in the current directory
for finder, name, ispkg in pkgutil.walk_packages([currentDir]):
    if not name.startswith("tool_"):
        continue  # Skip packages that do not start with 'tool_'

    if name == "tool_runner":
        continue

    # Import the module dynamically
    pkg = importlib.import_module(name)

    # Check if the module has a 'run' attribute, and add it to the dictionary if it does
    if hasattr(pkg, "run"):
        pkgs[name[5:]] = pkg


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
        click.echo(f"{name}\t\t- {pkgs[name].run.__doc__.strip()}")


@cli.command(cls=CMD)
@click.argument(
    "name", type=click.STRING, shell_complete=lambda _, __, **kwargs: list(pkgs.keys())
)
@click.argument("args", type=click.UNPROCESSED, nargs=-1)
def run(name, args):
    """Run a specified tool by name."""
    if name not in pkgs:
        click.echo(f"Package {name} not found")
        return

    # Get the package and call its 'run' function
    pkg = pkgs[name]

    # pop first 2 of sys.argv
    sys.argv = (name, *args)

    pkg.run()


if __name__ == "__main__":
    cli()
