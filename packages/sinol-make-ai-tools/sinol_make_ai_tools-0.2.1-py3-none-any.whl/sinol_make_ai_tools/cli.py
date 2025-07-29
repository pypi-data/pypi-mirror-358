import argparse
import sys

# Import the functions from your other modules
from . import create_prompt
from . import unserialize_dir
from . import create_package
from . import clear_in_out

def main():
    """Main function for the command-line interface."""
    parser = argparse.ArgumentParser(
        prog="sinol-make-ai-tools",
        description="Interface for using ai to build packages."
    )
    parser.add_argument(
        '-v', '--version',
        action='version',
        version='%(prog)s 0.1.0' # Should match pyproject.toml version
    )

    # This is the key to creating sub-commands like 'git status' or 'docker run'
    subparsers = parser.add_subparsers(dest="command", required=True, help="Available commands")

    parser_init = subparsers.add_parser("init", help="Create a package.")
    parser_init.add_argument("package_id", type=str, help="Three letter package code.")
    parser_init.set_defaults(func=create_package.main)

    # --- Sub-command for 'create-prompt' ---
    parser_prompt = subparsers.add_parser("prompt", help="Create a prompt from a description.txt.")
    parser_prompt.set_defaults(func=create_prompt.main) # Link to the function to run

    # --- Sub-command for 'unserialize' ---
    parser_unserialize = subparsers.add_parser("unserialize", help="Unserialize ai code.")
    parser_unserialize.set_defaults(func=unserialize_dir.main)

    parser_clear = subparsers.add_parser("clear", help="Clear in/ and out/.")
    parser_clear.set_defaults(func=clear_in_out.main)

    # Parse the arguments from the command line
    args = parser.parse_args()

    # Call the function that was set by set_defaults
    # We pass the parsed arguments to it
    args.func(args)

if __name__ == '__main__':
    main()