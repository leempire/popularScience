import argparse
from utils.agent import run

parser = argparse.ArgumentParser(description='Generate popular science articles')
parser.add_argument('input', type=str, help='The input topic for the article')
args = parser.parse_args()
run(args.input)
