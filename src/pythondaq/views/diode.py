import click
from pythondaq.models.DiodeExperiment import DiodeExperiment as DE
from pythondaq.models.DiodeExperiment import listing
import numpy as np


@click.group()
def cmd_group():
    pass


@cmd_group.command(
    "list",
    help="Returns list of devices connected to your device using criteria.",
)
@click.option(
    "-s", "--search", default="", help="Reduces the list of devices to the given string"
)
def list_devices(search):
    """Returns the list of devices connected to your device conforming to the search criteria."""
    return listing(search)


@cmd_group.command("info", help="Gives the Device ID of the device on the given port. ")
@click.argument("port")
def info(port):
    """Gives the Device ID of the device on the given port."""
    device = DE(port=port)
    id = device.deviceinfo()
    click.echo(f"Device ID is: /n {id}")


@cmd_group.command(
    "measure", help="Returns the current of the diode at a set output voltage."
)
@click.argument("port")
@click.option(
    "-v",
    "--setvoltage",
    default=2,
    show_default=True,
    type=click.FloatRange(0, 3.3),
    help="Sets the output voltage to a value between 0 and 3.3 V",
)
def measure(port, setvoltage):
    device = DE(port=port)
    device.set_voltage(setvoltage)
    I = device.meas_curr_diode()
    click.echo(f"The current over the diode at output of {setvoltage} V is {I:.4f} A")
    device.reset_out()


@cmd_group.command(
    "scan", help="Sweeps output voltage while measuring U and I over diode."
)
@click.argument("port")
@click.option(
    "-s",
    "--startrange",
    default=0,
    show_default=True,
    type=click.FloatRange(0, 3.3),
    help="Sets the starting output voltage of the voltage sweep. Can only be a value between 0 and 3.3V",
)
@click.option(
    "-e",
    "--endrange",
    default=3.3,
    show_default=True,
    type=click.FloatRange(0, 3.3),
    help="Sets the end output voltage of the voltage sweep. Can only be a value between 0 and 3.3V",
)
@click.option(
    "-o",
    "--output",
    default=None,
    type=str,
    help="Makes a csv of the scan. NDEe will be the given nDEe. If no nDEe is given no csv will be made.",
)
@click.option(
    "--error/--no-error",
    default=False,
    help="Creates a dataframe with the average calculated voltages and currents over the diode including the errors on the values. Number of scans to average from can be selected using -n INTEGER.",
)
@click.option(
    "-n",
    "--nsamples",
    default=2,
    show_default=True,
    help="Number of samples to average from",
)
@click.option(
    "-d",
    "--nsteps",
    default=200,
    show_default=True,
    help="Number of steps to take in the given voltage range.",
)
def scan(port, startrange, endrange, output, error, nsamples, nsteps):
    """Sweeps output voltage while measuring voltage and current over diode.
    Can also calculate average and error on multiple measurements using --error as option.
    Lots of options can be given to tailor the scan to your needs."""
    device = DE(port=port)
    if error:
        # Not the most elegant way to move a whole dataframe to the view but
        # the way that worked.
        errordf = device.error(nsamples, nsteps, begin=startrange, end=endrange)
        click.echo("Mean current (A), Mean voltage (V), \u03B4 I (A), \u03B4 U (V)")
        for current, voltage, errorcurrent, errorvoltage in zip(
            errordf["mean current (A)"],
            errordf["mean voltage (V)"],
            errordf["error current"],
            errordf["error voltage"],
        ):
            click.echo(
                f"{current:.4f}, {voltage:.4f}, {errorcurrent:.4f}, {errorvoltage:.4f}"
            )
    else:
        for data in device.sweep_waardes(nsteps, startrange, endrange):
            I, U = data
            click.echo(f"{I=:.4f}, {U=:.4f}")

    if output != None:
        device.csv_maker(error, filename=output)


if __name__ == "__main__":
    cmd_group()
