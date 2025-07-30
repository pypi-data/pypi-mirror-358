"""Hardware internal Sensor ."""
# :license: MIT, see LICENSE for more details.

import SoftLayer
from SoftLayer.CLI import click
from SoftLayer.CLI import environment
from SoftLayer.CLI import formatting


@click.command(cls=SoftLayer.CLI.command.SLCommand, )
@click.argument('identifier')
@click.option('--discrete', is_flag=True, default=False, help='Show discrete units associated hardware sensor')
@environment.pass_env
def cli(env, identifier, discrete):
    """Retrieve a server’s hardware state via its internal sensors."""
    mgr = SoftLayer.HardwareManager(env.client)
    sensors = mgr.get_sensors(identifier)

    temperature_table = formatting.Table(["Sensor", "Status", "Reading", "Critical Min", "Min", "Max", "Critical Max"],
                                         title='Temperature (c)')

    volts_table = formatting.Table(["Sensor", "Status", "Reading", "Critical Min", "Min", "Max", "Critical Max"],
                                   title='Volts')

    watts_table = formatting.Table(["Sensor", "Status", "Reading", "Critical Min", "Min", "Max", "Critical Max"],
                                   title='Watts')

    rpm_table = formatting.Table(["Sensor", "Status", "Reading", "Critical Min", "Min", "Max", "Critical Max"],
                                 title='RPM')

    discrete_table = formatting.Table(["Sensor", "Status", "Reading"],
                                      title='Discrete')

    for sensor in sensors:
        if sensor.get('sensorUnits') == 'degrees C':
            temperature_table.add_row([sensor.get('sensorId'),
                                       sensor.get('status'),
                                       sensor.get('sensorReading'),
                                       sensor.get('lowerCritical'),
                                       sensor.get('lowerNonCritical'),
                                       sensor.get('upperNonCritical'),
                                       sensor.get('upperCritical')])

        if sensor.get('sensorUnits') == 'Volts':
            volts_table.add_row([sensor.get('sensorId'),
                                 sensor.get('status'),
                                 sensor.get('sensorReading'),
                                 sensor.get('lowerCritical'),
                                 sensor.get('lowerNonCritical'),
                                 sensor.get('upperNonCritical'),
                                 sensor.get('upperCritical')])

        if sensor.get('sensorUnits') == 'Watts':
            watts_table.add_row([sensor.get('sensorId'),
                                 sensor.get('status'),
                                 sensor.get('sensorReading'),
                                 sensor.get('lowerCritical'),
                                 sensor.get('lowerNonCritical'),
                                 sensor.get('upperNonCritical'),
                                 sensor.get('upperCritical')])

        if sensor.get('sensorUnits') == 'RPM':
            rpm_table.add_row([sensor.get('sensorId'),
                               sensor.get('status'),
                               sensor.get('sensorReading'),
                               sensor.get('lowerCritical'),
                               sensor.get('lowerNonCritical'),
                               sensor.get('upperNonCritical'),
                               sensor.get('upperCritical')])

        if sensor.get('sensorUnits') == 'discrete':
            discrete_table.add_row([sensor.get('sensorId'),
                                    sensor.get('status'),
                                    sensor.get('sensorReading')])
    env.fout(temperature_table)
    env.fout(rpm_table)
    env.fout(volts_table)
    env.fout(watts_table)
    if discrete:
        env.fout(discrete_table)
