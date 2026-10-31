import argparse
import logging
import random
import sys
from pathlib import Path
from faker import Faker

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def setup_argparse():
    """
    Sets up the argument parser for the command line interface.
    """
    parser = argparse.ArgumentParser(
        description="Identifies and removes subtle correlations between data points in a dataset to prevent re-identification of masked data.",
        epilog="Example: python main.py --input data.csv --columns name,city --error-rate 0.05"
    )

    parser.add_argument(
        "--input",
        type=str,
        required=True,
        help="Path to the input CSV file."
    )

    parser.add_argument(
        "--columns",
        type=str,
        required=True,
        help="Comma-separated list of column names to process."
    )

    parser.add_argument(
        "--error-rate",
        type=float,
        default=0.01,
        help="Probability (0-1) of introducing an error in a data point. Default: 0.01"
    )

    parser.add_argument(
        "--output",
        type=str,
        default="output.csv",
        help="Path to the output CSV file. Default: output.csv"
    )

    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Seed for the random number generator to ensure reproducibility."
    )
    return parser

def introduce_error(data, error_rate, faker, seed):
    """
    Introduces errors into the data to break correlations.

    Args:
        data (list): A list of data points, in their original types.
            Numbers take the numeric noise branch and stay numbers;
            strings are replaced with a fake word.
        error_rate (float): The probability of introducing an error.
        faker (Faker): A Faker instance for generating fake data.
        seed (int): Seed for reproducibility.

    Returns:
        list: A list of data points with errors introduced.
    """
    # No reseeding in here. This runs once per column, and restarting the
    # sequence on every call picked the same row positions for corruption
    # in every column, which is itself a cross-column pattern, the thing
    # this tool exists to break. main seeds once before the column loop.
    modified_data = []
    for item in data:
        if random.random() < error_rate:
            # Introduce a random error. Can be customized based on data type
            # Example: Replace with fake data.
            if isinstance(item, str):  # Ensure the item is a string
                modified_data.append(faker.word())  # Replace with a random word
            elif isinstance(item, (int, float)):
                 modified_data.append(item + random.uniform(-0.1 * item, 0.1 * item))  # Add a small random noise
            else:
                modified_data.append(faker.word()) # Default to random word if type is unknown
            logging.debug(f"Introduced error: Replaced '{item}' with fake data.")

        else:
            modified_data.append(item)
    return modified_data


def main():
    """
    Main function to process the data.
    """
    parser = setup_argparse()
    args = parser.parse_args()

    input_file = args.input
    columns_to_process = args.columns.split(",")
    error_rate = args.error_rate
    output_file = args.output
    seed = args.seed

    # Input validation
    if not 0 <= error_rate <= 1:
        logging.error("Error rate must be between 0 and 1.")
        sys.exit(1)

    # The output may not name the input file, in any spelling. Resolved
    # paths are compared, so a ./ alias or a symlink to the input is
    # caught as well as the same string. Refuse before any write.
    if Path(output_file).resolve() == Path(input_file).resolve():
        logging.error("Output file must not be the input file. Choose a different output path.")
        sys.exit(1)

    try:
        import pandas as pd  # Import pandas here to handle import error gracefully

        try:
            df = pd.read_csv(input_file)
        except FileNotFoundError:
            logging.error(f"Input file not found: {input_file}")
            sys.exit(1)
        except pd.errors.EmptyDataError:
            logging.error(f"Input file is empty: {input_file}")
            sys.exit(1)
        except Exception as e:
             logging.error(f"Error reading input file: {e}")
             sys.exit(1)

        # Check if columns exist
        for col in columns_to_process:
            if col not in df.columns:
                logging.error(f"Column not found in input file: {col}")
                sys.exit(1)

        fake = Faker()
        if seed is not None:
            Faker.seed(seed) # Seed Faker for reproducibility
            random.seed(seed) # Seeded once for the whole run; see introduce_error

        for col in columns_to_process:
            try:
                # Pass the values in their original types. Converting to
                # str first would send every value down the fake word
                # branch, so a numeric column came out holding words and
                # lost its type. Typed values let numeric columns take
                # the numeric noise branch and stay numeric.
                df[col] = introduce_error(df[col].tolist(), error_rate, fake, seed)
            except Exception as e:
                 logging.error(f"Error processing column '{col}': {e}")
                 sys.exit(1)

        try:
            df.to_csv(output_file, index=False)
            logging.info(f"Processed data saved to {output_file}")
        except Exception as e:
            logging.error(f"Error writing to output file: {e}")
            sys.exit(1)


    except ImportError:
        logging.error("Pandas is not installed. Please install it using: pip install pandas")
        sys.exit(1)


if __name__ == "__main__":
    main()