"""Disable scheduled snapshots of a specific volume"""
# :license: MIT, see LICENSE for more details.

import click
import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions


@click.command(cls=SoftLayer.CLI.command.SLCommand, )
@click.argument('volume_id')
@click.option('--schedule-type',
              help='Snapshot schedule [INTERVAL|HOURLY|DAILY|WEEKLY]',
              required=True)
@environment.pass_env
def cli(env, volume_id, schedule_type):
    """Disables snapshots on the specified schedule for a given volume

    Example::

        slcli file snapshot-disable 12345678 -s DAILY
        This command disables daily snapshot for volume with ID 12345678.
    """

    if (schedule_type not in ['INTERVAL', 'HOURLY', 'DAILY', 'WEEKLY']):
        raise exceptions.CLIAbort(
            '--schedule_type must be INTERVAL, HOURLY, DAILY, or WEEKLY')

    file_manager = SoftLayer.FileStorageManager(env.client)
    disabled = file_manager.disable_snapshots(volume_id, schedule_type)

    if disabled:
        click.echo('%s snapshots have been disabled for volume %s'
                   % (schedule_type, volume_id))
