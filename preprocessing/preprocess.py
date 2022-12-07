import argparse
from utils.preprocess_utils import *

parser = argparse.ArgumentParser(
    description="Set parameters for preprocessing pipeline",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
)

parser.add_argument(
    "--position",
    "-p",
    type=str,
    required=True,
    help="Enter the position you want data from",
)

args = parser.parse_args()


def main():

    # Load Data
    df = load_csv(args.position)
    # Preprocess Data
    preprocess_data(df, args.position)
    # Save
    save_csv(args.position, df)


if __name__ == "__main__":
    main()
