"""List file storage volumes."""
# :license: MIT, see LICENSE for more details.

import click
import SoftLayer
from SoftLayer.CLI import columns as column_helper
from SoftLayer.CLI import environment
from SoftLayer.CLI import storage_utils

COLUMNS = [
    column_helper.Column('id', ('id',), mask="id"),
    column_helper.Column('username', ('username',), mask="username"),
    column_helper.Column('datacenter',
                         ('serviceResource', 'datacenter', 'name'),
                         mask="serviceResource.datacenter.name"),
    column_helper.Column(
        'storage_type',
        lambda b: b['storageType']['keyName'].split('_').pop(0)
        if 'storageType' in b and 'keyName' in b['storageType']
           and isinstance(b['storageType']['keyName'], str)
        else '-',
        mask="storageType.keyName"),
    column_helper.Column('capacity_gb', ('capacityGb',), mask="capacityGb"),
    column_helper.Column('bytes_used', ('bytesUsed',), mask="bytesUsed"),
    column_helper.Column('ip_addr', ('serviceResourceBackendIpAddress',),
                         mask="serviceResourceBackendIpAddress"),
    column_helper.Column('active_transactions', ('activeTransactionCount',),
                         mask="activeTransactionCount"),
    column_helper.Column('mount_addr', ('fileNetworkMountAddress',),
                         mask="fileNetworkMountAddress", ),
    column_helper.Column('rep_partner_count', ('replicationPartnerCount',),
                         mask="replicationPartnerCount"),
    column_helper.Column(
        'created_by',
        ('billingItem', 'orderItem', 'order', 'userRecord', 'username')),
    column_helper.Column('notes', ('notes',), mask="notes"),
]

DEFAULT_COLUMNS = [
    'id',
    'username',
    'datacenter',
    'storage_type',
    'capacity_gb',
    'bytes_used',
    'ip_addr',
    'active_transactions',
    'mount_addr',
    'rep_partner_count',
    'notes',
]

DEFAULT_NOTES_SIZE = 20


@click.command(cls=SoftLayer.CLI.command.SLCommand, )
@click.option('--username', '-u', help='Volume username')
@click.option('--datacenter', '-d', help='Datacenter shortname')
@click.option('--order', '-o', type=int, help='Filter by ID of the order that purchased the block storage')
@click.option('--storage-type',
              help='Type of storage volume',
              type=click.Choice(['performance', 'endurance']))
@click.option('--sortby', help='Column to sort by', default='username')
@click.option('--columns',
              callback=column_helper.get_formatter(COLUMNS),
              help=f"Columns to display. Options: {', '.join(column.name for column in COLUMNS)}",
              default=','.join(DEFAULT_COLUMNS))
@environment.pass_env
def cli(env, sortby, columns, datacenter, username, storage_type, order):
    """List file storage.

    Example::
            slcli file volume-list -d dal10 --storage-type endurance --sortby capacity_gb
    """
    file_manager = SoftLayer.FileStorageManager(env.client)
    file_volumes = file_manager.list_file_volumes(datacenter=datacenter,
                                                  username=username,
                                                  storage_type=storage_type,
                                                  order=order,
                                                  mask=columns.mask())

    table = storage_utils.build_output_table(env, file_volumes, columns, sortby)
    env.fout(table)
