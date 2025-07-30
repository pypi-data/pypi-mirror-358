from pathlib import Path
import obsinfo


def main():
    file = Path(obsinfo.__file__).parent.joinpath("version.py")

    version = {}
    with open(file) as fp:
        exec(fp.read(), version)

    name = "obsinfo"
    version = version['__version__']

    print(name + " v" + version)
