"""Order snapshot space for a file storage volume."""
# :license: MIT, see LICENSE for more details.

import click
import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions


@click.command(cls=SoftLayer.CLI.command.SLCommand, )
@click.argument('volume_id')
@click.option('--capacity',
              type=int,
              help='Size of snapshot space to create in GB',
              required=True)
@click.option('--tier',
              help='Endurance Storage Tier (IOPS per GB) of the file'
              ' volume for which space is ordered [optional, and only'
              ' valid for endurance storage volumes]',
              type=click.Choice(['0.25', '2', '4', '10']))
@click.option('--upgrade',
              type=bool,
              help='Flag to indicate that the order is an upgrade',
              default=False,
              is_flag=True)
@environment.pass_env
def cli(env, volume_id, capacity, tier, upgrade):
    """Order snapshot space for a file storage volume.

    Example::
    slcli file snapshot-order 12345678 -s 1000 -t 4
    This command orders snapshot space for volume with ID 12345678, the size is 1000GB, the tier level is 4 IOPS per GB.
"""
    file_manager = SoftLayer.FileStorageManager(env.client)

    if tier is not None:
        tier = float(tier)

    try:
        order = file_manager.order_snapshot_space(
            volume_id,
            capacity=capacity,
            tier=tier,
            upgrade=upgrade
        )
    except ValueError as ex:
        raise exceptions.ArgumentError(str(ex))

    if 'placedOrder' in order.keys():
        click.echo(f"Order #{order['placedOrder']['id']} placed successfully!")
        for item in order['placedOrder']['items']:
            click.echo(" > %s" % item['description'])
        if 'status' in order['placedOrder'].keys():
            click.echo(" > Order status: %s" % order['placedOrder']['status'])
    else:
        click.echo("Order could not be placed! Please verify your options " +
                   "and try again.")
