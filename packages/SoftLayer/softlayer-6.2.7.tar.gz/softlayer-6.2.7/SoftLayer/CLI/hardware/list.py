"""List hardware servers."""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import columns as column_helper
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting
from SoftLayer.CLI import helpers
from SoftLayer import utils

# pylint: disable=unnecessary-lambda

COLUMNS = [
    column_helper.Column('guid', ('globalIdentifier',)),
    column_helper.Column('primary_ip', ('primaryIpAddress',)),
    column_helper.Column('backend_ip', ('primaryBackendIpAddress',)),
    column_helper.Column('datacenter', ('datacenter', 'name')),
    column_helper.Column(
        'action',
        lambda server: formatting.active_txn(server),
        mask='activeTransaction[id, transactionStatus[name, friendlyName]]'),
    column_helper.Column(
        'owner',
        lambda created_by: utils.lookup(created_by, 'billingItem', 'orderItem', 'order', 'userRecord', 'username'),
        mask='billingItem[id,orderItem[id,order[id,userRecord[username]]]]'),
    column_helper.Column(
        'tags',
        lambda server: formatting.tags(server.get('tagReferences')),
        mask="tagReferences.tag.name"),
]

DEFAULT_COLUMNS = [
    'id',
    'hostname',
    'primary_ip',
    'backend_ip',
    'datacenter',
    'action',
    'owner',
    'tags',
]


@click.command(cls=SoftLayer.CLI.command.SLCommand, )
@click.option('--cpu', '-c', help='Filter by number of CPU cores')
@click.option('--domain', '-D', help='Filter by domain')
@click.option('--datacenter', '-d', help='Filter by datacenter')
@click.option('--hostname', '-H', help='Filter by hostname')
@click.option('--memory', '-m', help='Filter by memory in gigabytes')
@click.option('--network', '-n', help='Filter by network port speed in Mbps')
@click.option('--owner', help='Filter by created_by username')
@click.option('--primary_ip', help='Filter by Primary Ip Address')
@click.option('--backend_ip', help='Filter by Backend Ip Address')
@click.option('--search', is_flag=False, flag_value="", default=None,
              help="Use the more flexible Search API to list instances. See `slcli search --types` for list " +
                   "of searchable fields.")
@helpers.multi_option('--tag', help='Filter by tags')
@click.option('--sortby', help='Column to sort by', default='hostname', show_default=True)
@click.option('--columns',
              callback=column_helper.get_formatter(COLUMNS),
              help='Columns to display. [options: %s]' % ', '.join(column.name for column in COLUMNS),
              default=','.join(DEFAULT_COLUMNS),
              show_default=True)
@click.option('--limit', '-l',
              help='How many results to get in one api call, default is 100',
              default=100,
              show_default=True)
@environment.pass_env
def cli(env, sortby, cpu, domain, datacenter, hostname, memory, network, owner, primary_ip, backend_ip,
        search, tag, columns, limit):
    """List hardware servers."""

    if search is not None:
        object_mask = "mask[resource(SoftLayer_Hardware)]"
        search_manager = SoftLayer.SearchManager(env.client)
        servers = search_manager.search_hadrware_instances(
            hostname=hostname,
            domain=domain,
            datacenter=datacenter,
            tags=tag,
            search_string=search,
            mask=object_mask)

    else:
        manager = SoftLayer.HardwareManager(env.client)
        servers = manager.list_hardware(
            hostname=hostname,
            domain=domain,
            cpus=cpu,
            memory=memory,
            datacenter=datacenter,
            nic_speed=network,
            tags=tag,
            owner=owner,
            public_ip=primary_ip,
            private_ip=backend_ip,
            mask="mask(SoftLayer_Hardware_Server)[%s]" % columns.mask(),
            limit=limit)

    table = formatting.Table(columns.columns)
    table.sortby = sortby
    table.align['created_by'] = 'l'
    table.align['tags'] = 'l'

    for server in servers:
        table.add_row([value or formatting.blank()
                       for value in columns.row(server)])

    env.fout(table)
