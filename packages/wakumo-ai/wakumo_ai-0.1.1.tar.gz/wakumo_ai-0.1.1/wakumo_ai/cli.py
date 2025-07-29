import click
from wakumo_ai.commands.conversation import conversation
from wakumo_ai.log import set_verbose

@click.group(
    help="""
Wakumo AI CLI

A modern Python CLI and SDK to interact with Wakumo AI backend (API & WebSocket).

Examples:
  wakumo-ai --verbose conversation get --id <conversation_id>
  wakumo-ai conversation get --help
"""
)
@click.option('--verbose', is_flag=True, default=False, help='Show verbose debug output')
def cli(verbose):
    if verbose:
        set_verbose(True)

cli.add_command(conversation)

if __name__ == '__main__':
    cli()