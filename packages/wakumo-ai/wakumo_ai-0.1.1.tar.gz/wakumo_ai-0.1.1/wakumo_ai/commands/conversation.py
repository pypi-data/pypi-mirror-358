import click
import json
from wakumo_ai import WakumoAIClient

@click.group(
    help="""
Conversation related commands: create, get, list, etc.

Examples:
  wakumo-ai conversation get --id <conversation_id>
  wakumo-ai conversation trajectory-v2 --id <conversation_id> [--per-page 50] [--direction next] [--cursor <cursor>]
  wakumo-ai conversation get --help
"""
)
def conversation():
    pass

@conversation.command(
    help="""
Get conversation details by ID.

Example:
  wakumo-ai conversation get --id <conversation_id>
"""
)
@click.option('--id', 'conversation_id', required=True, help='Conversation ID')
def get(conversation_id):
    """Get conversation details by ID."""
    client = WakumoAIClient()
    info = client.conversation.get_conversation(conversation_id)
    if info:
        click.echo(json.dumps(info.model_dump(), indent=2, ensure_ascii=False))
    else:
        click.echo('Conversation not found', err=True)

@conversation.command(
    help="""
Get conversation trajectory (v2) with cursor-based pagination.

Example:
  wakumo-ai conversation trajectory-v2 --id <conversation_id> [--per-page 50] [--direction next] [--cursor <cursor>]
"""
)
@click.option('--id', 'conversation_id', required=True, help='Conversation ID')
@click.option('--cursor', default=None, help='Cursor for pagination (event id)')
@click.option('--per-page', default=50, show_default=True, type=int, help='Number of items per page (max 100)')
@click.option('--direction', default='next', show_default=True, type=click.Choice(['next', 'previous']), help='Pagination direction')
def trajectory_v2(conversation_id, cursor, per_page, direction):
    """Get conversation trajectory (v2) with cursor-based pagination."""
    client = WakumoAIClient()
    result = client.conversation.get_trajectory_v2(
        conversation_id=conversation_id,
        cursor=cursor,
        per_page=per_page,
        direction=direction
    )
    click.echo(json.dumps(result, indent=2, ensure_ascii=False))