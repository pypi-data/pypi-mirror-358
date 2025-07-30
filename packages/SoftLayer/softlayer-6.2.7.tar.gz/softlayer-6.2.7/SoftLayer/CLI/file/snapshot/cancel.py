"""Cancel a snapshot space subscription."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import formatting


@click.command(cls=SoftLayer.CLI.command.SLCommand, )
@click.argument('volume-id')
@click.option('--reason', help="An optional reason for cancellation")
@click.option('--immediate',
              is_flag=True,
              help="Cancels the snapshot space immediately instead "
                   "of on the billing anniversary")
@click.option('--force', default=False, is_flag=True, help="Force cancel block volume without confirmation")
@environment.pass_env
def cli(env, volume_id, reason, immediate, force):
    """Cancel existing snapshot space for a given volume.

    Example::
        slcli file snapshot-cancel 12345678 --immediate -f
        This command cancels snapshot with ID 12345678 immediately without asking for confirmation.
    """

    file_storage_manager = SoftLayer.FileStorageManager(env.client)

    if not force:
        if not (env.skip_confirmations or formatting.no_going_back(volume_id)):
            raise exceptions.CLIAbort('Aborted.')

    cancelled = file_storage_manager.cancel_snapshot_space(
        volume_id, reason, immediate)

    if cancelled:
        if immediate:
            click.echo('File volume with id %s has been marked'
                       ' for immediate snapshot cancellation' % volume_id)
        else:
            click.echo('File volume with id %s has been marked'
                       ' for snapshot cancellation' % volume_id)
    else:
        click.echo('Unable to cancel snapshot space for file volume %s'
                   % volume_id)
