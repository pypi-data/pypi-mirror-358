"""Enable or Disable specific noticication for the current user"""
# :license: MIT, see LICENSE for more details.

import click

import SoftLayer
from SoftLayer.CLI import environment


@click.command(cls=SoftLayer.CLI.command.SLCommand, )
@click.option('--enable/--disable', default=True,
              help="Enable (DEFAULT) or Disable selected notification")
@click.argument('notification', nargs=-1, required=True)
@environment.pass_env
def cli(env, enable, notification):
    """Enable or Disable specific notifications for the active user.

    Notification names should be enclosed in quotation marks.
    Example::

        slcli user edit-notifications --enable 'Order Approved' 'Reload Complete'

    """

    mgr = SoftLayer.UserManager(env.client)

    if enable:
        result = mgr.enable_notifications(notification)
    else:
        result = mgr.disable_notifications(notification)

    if result:
        click.secho(f"Notifications updated successfully: {', '.join(notification)}", fg='green')
    else:
        click.secho(f"Failed to update notifications: {', '.join(notification)}", fg='red')
