import argparse
from cli.main import launch_cli
from gui.main_window import launch_gui


def parse_args():
    parser = argparse.ArgumentParser(
        prog="I3DShapesToolPython",
        description="CLI tool to process I3D files"
    )

    parser.add_argument(
        "files",
        nargs="*",
        help="Input files (.i3d, .i3d.shapes, .xml)"
    )

    parser.add_argument(
        "--nogui",
        action="store_true",
        help="Run in CLI mode without GUI"
    )

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    if (args.nogui):
        launch_cli(args.files)
    else:
        launch_gui(args.files)