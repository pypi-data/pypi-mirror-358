import argparse
from clyp import __version__
import sys
from clyp.transpiler import parse_clyp
import os

def main():
    parser = argparse.ArgumentParser(description="Clyp CLI tool.")
    parser.add_argument('file', nargs='?', type=str, help="Path to the Clyp file to execute.")
    parser.add_argument('--version', action='store_true', help="Display the version of Clyp.")
    
    args = parser.parse_args()

    if args.version:
        print(f"{__version__}")
    elif args.file:
        try:
            file_path = os.path.abspath(args.file)
            with open(file_path, 'r', encoding='utf-8') as f:
                clyp_code = f.read()
            python_code = parse_clyp(clyp_code, file_path)
            exec(python_code, {'__name__': '__main__', '__file__': file_path})
        except Exception as e:
            print(f"Error processing file {args.file}: {e}\n\n Warning: These errors come from the transpiled Python code and will likely not provide helpful information.", file=sys.stderr)
    else:
        print(f"clyp version {__version__}, Python version {sys.version}")

if __name__ == "__main__":
    main()
