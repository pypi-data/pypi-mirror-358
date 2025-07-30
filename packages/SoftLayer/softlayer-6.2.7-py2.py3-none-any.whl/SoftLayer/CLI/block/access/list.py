"""List hosts with access to block volume."""
# :license: MIT, see LICENSE for more details.

import click
import SoftLayer
from SoftLayer.CLI import columns as column_helper
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer.CLI import helpers
from SoftLayer.CLI import storage_utils


@click.command(cls=SoftLayer.CLI.command.SLCommand, )
@click.argument('volume_id')
@click.option('--columns',
              callback=column_helper.get_formatter(storage_utils.COLUMNS),
              help=f"Columns to display. Options are: {', '.join(column.name for column in storage_utils.COLUMNS)}.",
              default=','.join(storage_utils.DEFAULT_COLUMNS))
@click.option('--sortby',
              help=f"Column to sort by. Options are: {', '.join(column.name for column in storage_utils.COLUMNS)}.",
              default='name')
@environment.pass_env
def cli(env, columns, sortby, volume_id):
    """List hosts that are authorized to access the volume.

    EXAMPLE::

            slcli block access-list 12345678 --sortby id
            This command lists all hosts that are authorized to access volume with ID 12345678 and sorts them by ID.
    """
    block_manager = SoftLayer.BlockStorageManager(env.client)
    resolved_id = helpers.resolve_id(block_manager.resolve_ids, volume_id, 'Volume Id')
    access_list = block_manager.get_block_volume_access_list(
        volume_id=resolved_id)
    table = formatting.Table(columns.columns)
    table.sortby = sortby

    for key, type_name in [('allowedVirtualGuests', 'VIRTUAL'),
                           ('allowedHardware', 'HARDWARE'),
                           ('allowedSubnets', 'SUBNET'),
                           ('allowedIpAddresses', 'IP')]:
        for obj in access_list.get(key, []):
            obj['type'] = type_name
            table.add_row([value or formatting.blank()
                           for value in columns.row(obj)])

    env.fout(table)
