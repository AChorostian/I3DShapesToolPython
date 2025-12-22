import argparse
from app.main import main


def parse_args():
    parser = argparse.ArgumentParser(
        prog="I3DShapesToolPython",
        description="CLI tool to process I3D files"
    )

    parser.add_argument(
        "shapes_file",
        help="Path to .i3d.shapes file"
    )

    parser.add_argument(
        "i3d_file",
        help="Path to .i3d file"
    )

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    main(args)
