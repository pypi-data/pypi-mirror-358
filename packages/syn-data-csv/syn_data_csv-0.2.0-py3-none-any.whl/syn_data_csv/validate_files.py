import yaml
import sys
import pandas as pd
import csv


def load_yaml(file_path):
    """Load YAML configuration file."""
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)


def validate_yaml(config):
    """Validate the structure of the YAML configuration file."""
    required_keys = {"columns", "prompt"}
    
    if not isinstance(config, dict):
        raise ValueError("YAML configuration should be a dictionary.")

    print("✅ YAML configuration format is valid.")


def validate_csv(file_path):
    """Validate the CSV reference file format and detect separator."""
    try:
        # Read a small sample to guess the delimiter
        with open(file_path, 'r', encoding='utf-8') as f:
            sample = f.read(2048)
            try:
                dialect = csv.Sniffer().sniff(sample)
                delimiter = dialect.delimiter
                print(f"✅ Detected delimiter: '{delimiter}'")
            except csv.Error:
                # Fallback to semicolon if sniffing fails
                delimiter = ';'
                print("⚠️ Could not detect delimiter. Using fallback delimiter ';'")

        # Now read using the detected or fallback delimiter
        df = pd.read_csv(file_path, sep=delimiter, nrows=5)
        print("✅ CSV reference file format is valid.")

        return df, delimiter

    except Exception as e:
        raise ValueError(f"Error reading CSV file: {e}")


def process_and_validate_files(args):

    yaml_file = None
    config = None
    reference_file = None

    if len(args) >= 2 and not args[-2].endswith(('.yaml', '.yml', '.csv')):
        api_key = args[-2]
        model = args[-1]
        file_args = args[:-2]
    elif len(args) >= 1 and not args[-1].endswith(('.yaml', '.yml', '.csv')):
        api_key = args[-1]
        file_args = args[:-1]
    else:
        file_args = args

    # Identify YAML and CSV files
    for arg in file_args:
        if arg.endswith(('.yaml', '.yml')):
            yaml_file = arg
        elif arg.endswith('.csv'):
            reference_file = arg

    if not yaml_file and not reference_file:
        print("❌ No valid .yaml or .csv files provided.")
        print("✅ Usage: python test1.py <file.yaml> <file.csv> [api_key] [model]")
        sys.exit(1)

    # Validate YAML format
    if yaml_file:
        config = load_yaml(yaml_file)
        delimiter = ','
        try:
            validate_yaml(config)
        except ValueError as e:
            print(f"❌ YAML validation error: {e}")
            sys.exit(1)

    # Validate CSV format
    if reference_file:
        try:
            reference_file, delimiter = validate_csv(reference_file)
        except ValueError as e:
            print(f"❌ CSV validation error: {e}")
            sys.exit(1)

    return config, reference_file, delimiter