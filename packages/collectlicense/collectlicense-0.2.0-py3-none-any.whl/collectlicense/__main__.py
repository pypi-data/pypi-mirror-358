from pathlib import Path
import argparse


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='python -m collectlicense',
        description='Collect license files for packages installed with pip.')
    
    parser.add_argument('--out',
                        help='License filr output directory.',
                        default=Path(".") / ".licenses")
    parser.add_argument('--clear',
                        help='Clear output directory.',
                        action='store_true')

    args = parser.parse_args()
    from collectlicense.app import app
    app.main(Path(args.out), args.clear)
