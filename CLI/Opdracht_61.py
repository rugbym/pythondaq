import click
import time


@click.command()
@click.argument("name")
@click.option(
    "-c",
    "--count",
    default=1,
    help="number of times to print greeting.",
    show_default=True,
)
@click.option(
    "-w",
    "--waittime",
    default=1.0,
    help="time to wait between printing lines",
    show_default=True,
)
def hello(name, count, waittime):
    for n in range(count):
        print(f"hello {name}")
        if n + 1 < count:
            time.sleep(waittime)


if __name__ == "__main__":
    hello()
