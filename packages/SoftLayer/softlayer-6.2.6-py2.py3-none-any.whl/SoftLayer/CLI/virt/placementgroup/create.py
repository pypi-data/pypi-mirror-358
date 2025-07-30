"""Create a placement group"""

import click

from SoftLayer.CLI.command import SLCommand as SLCommand
from SoftLayer.CLI import environment
from SoftLayer.CLI import helpers
from SoftLayer.managers.vs_placement import PlacementManager as PlacementManager


@click.command(cls=SLCommand)
@click.option('--name', type=click.STRING, required=True, prompt=True, help="Name for this new placement group.")
@click.option('--backend_router', '-b', required=True, prompt=True,
              help="backendRouter, can be either the hostname or id.")
@click.option('--rule', '-r', required=True, prompt=True,
              help="The keyName or Id of the rule to govern this placement group.")
@environment.pass_env
def cli(env, **args):
    """Create a placement group."""
    manager = PlacementManager(env.client)
    backend_router_id = helpers.resolve_id(manager.get_backend_router_id_from_hostname,
                                           args.get('backend_router'),
                                           'backendRouter')
    rule_id = helpers.resolve_id(manager.get_rule_id_from_name, args.get('rule'), 'Rule')
    placement_object = {
        'name': args.get('name'),
        'backendRouterId': backend_router_id,
        'ruleId': rule_id
    }

    result = manager.create(placement_object)
    click.secho(f"Successfully created placement group: ID: {result['id']}, Name: {result['name']}", fg='green')
