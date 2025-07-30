"""Check if a virtual server is ready."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import helpers


@click.command(cls=SoftLayer.CLI.command.SLCommand, )
@click.argument('identifier')
@click.option('--wait', default=0, show_default=True, type=click.INT, help="Seconds to wait")
@environment.pass_env
def cli(env, identifier, wait):
    """Check if a virtual server is ready."""

    vsi = SoftLayer.VSManager(env.client)
    vs_id = helpers.resolve_id(vsi.resolve_ids, identifier, 'VS')
    ready = vsi.wait_for_ready(vs_id, wait)
    if ready:
        env.fout("READY")
    else:
        raise exceptions.CLIAbort(f"Instance {vs_id} not ready")
