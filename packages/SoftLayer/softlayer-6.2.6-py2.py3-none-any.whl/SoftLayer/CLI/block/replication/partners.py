"""List existing replicant volumes for a block volume."""
# :license: MIT, see LICENSE for more details.

import click
import SoftLayer
from SoftLayer.CLI import columns as column_helper
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer.CLI import storage_utils

COLUMNS = storage_utils.REPLICATION_PARTNER_COLUMNS
DEFAULT_COLUMNS = storage_utils.REPLICATION_PARTNER_DEFAULT


@click.command(cls=SoftLayer.CLI.command.SLCommand, )
@click.argument('volume-id')
@click.option('--columns',
              callback=column_helper.get_formatter(COLUMNS),
              help=f"Columns to display. Options: {', '.join(column.name for column in COLUMNS)}",
              default=','.join(DEFAULT_COLUMNS))
@click.option('--sortby', help='Column to sort by', default='Username')
@environment.pass_env
def cli(env, columns, sortby, volume_id):
    """List existing replica volumes for a block volume."""
    block_storage_manager = SoftLayer.BlockStorageManager(env.client)

    legal_volumes = block_storage_manager.get_replication_partners(
        volume_id
    )

    if not legal_volumes:
        click.echo("There are no replication partners for the given volume.")
    else:
        table = formatting.Table(columns.columns)
        table.sortby = sortby
        for legal_volume in legal_volumes:
            table.add_row([value or formatting.blank()
                           for value in columns.row(legal_volume)])

        env.fout(table)
