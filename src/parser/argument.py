from argparse import ArgumentParser


parser = ArgumentParser()

parser.add_argument(
    "--runner",
    type=str,
    default=None,
    help="extract/transform/clean runners",
)
