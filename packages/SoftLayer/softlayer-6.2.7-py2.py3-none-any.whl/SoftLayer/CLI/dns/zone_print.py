"""Print zone in BIND format."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import helpers


@click.command(cls=SoftLayer.CLI.command.SLCommand, )
@click.argument('zone')
@environment.pass_env
def cli(env, zone):
    """Print zone in BIND format.

    Example::
        slcli dns zone-print ibm.com
        This command prints zone that is named ibm.com, and in BIND format.
"""

    manager = SoftLayer.DNSManager(env.client)
    zone_id = helpers.resolve_id(manager.resolve_ids, zone, name='zone')
    env.fout(manager.dump_zone(zone_id))
