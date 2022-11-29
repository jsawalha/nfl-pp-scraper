import argparse
from utils.preprocess_utils import *

parser = argparse.ArgumentParser(description='Set parameters for preprocessing pipeline')

parser.add_argument('--position', '-p', type=str, required=True, help='Enter the position you want data from')

args = parser.parse_args()

def main():

    df = load_csv(args.position)

    # Cleaning data: Position
    convert_nan('position', df)
    df['position'] = df['position'].apply(lambda x: remove_str(x))

    # Team
    df['team'], team_idx = df['team'].factorize()

    # Draft
    df['draft'] = df['draft'].str.lower().replace('undrafted', '0').apply(lambda x: draft_decimal_check(x))
    convert_nan('draft', df)
    df['draft'] = df['draft'].astype(float)

    # College
    convert_nan('college', df)

    # Others
    rest_of = ['age', '40-yard', 'speed', 'burst', 'agility', 'bench', 'col-dom',
                'col-ypr', 'col-breakout', 'col-sparq', 'games-played', 'targets',
                'rec', 'rec-yards', 'ypr', 'air-yards', 'tds', 'fantasy-ppg']

    convert_multi_nan(rest_of, df)

   



if __name__ == '__main__':

    main()



