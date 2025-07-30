import argparse
import os
import yaml
from pathlib import Path
from collections import OrderedDict
from yamlordereddictloader import SafeDumper
from yamlordereddictloader import SafeLoader


def parse_commandline_args():
    """
    parse command line inputs
    """
    parser = argparse.ArgumentParser(
        description='Plot output for the decoder zoo.')
    parser.add_argument('-r', '--run_dir', type=str, default=None,
                        help = 'The run directory.')

    return parser.parse_args()


def parse_dirname_to_sorted_ordereddict(dirname):
    parts = dirname.split("_")
    output = sorted(parts)
    return output
    

def read_result_yaml_from_dir(directory):
    dir_path = Path(directory)

    # Find the first YAML file starting with "result"
    result_file = next(
        (f for f in dir_path.iterdir() if f.name.startswith("result") and f.suffix in {".yaml", ".yml"}),
        None
    )
    if result_file is None:
        raise FileNotFoundError(f"No YAML file starting with 'result' found in {directory}")

    # Load YAML content
    with open(result_file, "r") as f:
        yaml_data = yaml.load(f, Loader=SafeLoader)

    # Generate sorted OrderedDict from directory name
    sorted_key = parse_dirname_to_sorted_ordereddict(dir_path.name)

    return sorted_key, yaml_data


def main():
    args = parse_commandline_args()
    root_dir = Path(args.run_dir)

    results_dict = OrderedDict()

    for subfolder in root_dir.iterdir():
        if subfolder.is_dir():
            results_files = list(subfolder.glob("result*"))

            if results_files:
                print(f"{subfolder}: result ready.")
                output_key, output_value = read_result_yaml_from_dir(subfolder)
                results_dict[str(output_key)] = output_value
            else:
                print(f"{subfolder}: result NOT ready.")

    print(results_dict)


if __name__ == '__main__':
    main()

