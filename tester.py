from interpreterv1 import Interpreter
from bparser import BParser
import argparse

parser = argparse.ArgumentParser(description='runs brewin files')
parser.add_argument('filename', help='relative path to the brewin program you wish to run')

args = parser.parse_args()


def main(program_path):
    f = open(program_path)
    program_lines = list(map(lambda x: x.rstrip("\n"), f.readlines()))
    my_int = Interpreter()
    my_int.run(program_lines)
    f.close()


if __name__ == '__main__':
    main(args.filename)