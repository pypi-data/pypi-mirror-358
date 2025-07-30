import argparse
from pathlib import Path


def parse_commandline_args():
    """
    parse command line inputs
    """
    parser = argparse.ArgumentParser(
        description='Test output for the decoder zoo.')
    parser.add_argument('-r', '--run_dir', type=str, default=None,
                        help = 'The run directory.')

    return parser.parse_args()


def main():
    args = parse_commandline_args()
    root_dir = Path(args.run_dir)

    total_sim = 0
    total_result = 0
    for subfolder in sorted(root_dir.iterdir()):
        if subfolder.is_dir():
            total_sim += 1
            results_files = list(subfolder.glob("result*"))
            
            if results_files:
                print(f"{subfolder}: result ready.")
                total_result += 1
            else:
                print(f"{subfolder}: result NOT ready.")

    print(f"{total_result/total_sim*100:.2f} % simulations are done.")


if __name__ == '__main__':
    main()

