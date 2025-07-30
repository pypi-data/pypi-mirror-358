"""Enable or Disable vpn subnets manual config for a user."""
# :license: MIT, see LICENSE for more details.


import click

import SoftLayer
from SoftLayer.CLI import environment
from SoftLayer.CLI import helpers


@click.command(cls=SoftLayer.CLI.command.SLCommand, )
@click.argument('user')
@click.option('--enable/--disable', default=True,
              help="Enable or disable vpn subnets manual config.")
@environment.pass_env
def cli(env, user, enable):
    """Enable or disable user vpn subnets manual config"""
    mgr = SoftLayer.UserManager(env.client)
    user_id = helpers.resolve_id(mgr.resolve_ids, user, 'username')

    result = mgr.vpn_manual(user_id, enable)
    message = f"{user} vpn manual config {'enable' if enable else 'disable'}"

    if result:
        click.secho(message, fg='green')
    else:
        click.secho(f"Failed to update {user}", fg='red')
