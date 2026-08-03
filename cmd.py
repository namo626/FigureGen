#!/usr/bin/env python3

import argparse
import os
import subprocess
from parser import *
from enum import Enum

boxes = {
    "ocean": [-100, -60, 10, 50],
    "galveston": [-95.5, -94, 28.5, 30],
    "neches": [-94.13, 93.8, 29.93, 30.17],
}

class Inp(Enum):
    CONTOUR_FILE = 18
    PLOT_LABEL = 7
    XMIN = 9
    XMAX = 10
    YMIN = 11
    YMAX = 12
    CONTOUR_RANGE = 25
    CONTOUR_INT = 26

# 19 - input coutour file name
def create_inp(args):
    ss = samples
    ss[Inp.CONTOUR_FILE.value] = args.fname

    if args.region is not None:
        xmin, xmax, ymin, ymax = boxes[args.region]
        ss[Inp.XMIN.value] = str(xmin)
        ss[Inp.XMAX.value] = str(xmax)
        ss[Inp.YMIN.value] = str(ymin)
        ss[Inp.YMAX.value] = str(ymax)

    # Box is specified
    elif all([args.xmin, args.xmax, args.ymin, args.ymax]):
        ss[Inp.XMIN.value] = str(args.xmin)
        ss[Inp.XMAX.value] = str(args.xmax)
        ss[Inp.YMIN.value] = str(args.ymin)
        ss[Inp.YMAX.value] = str(args.ymax)
    else:
        raise ValueError("No coordinates specified!")

    if None in [args.cmin, args.cmax]:
        print("Using default contour range")
        ss[Inp.CONTOUR_RANGE.value] = "FIND"
    else:
        ss[Inp.CONTOUR_RANGE.value] = str(args.cmin) + ',' + str(args.cmax)

    if args.cint is not None:
        ss[Inp.CONTOUR_INT.value] = str(args.cint)
        

    with open(os.path.join(args.dir, "sample.inp"), 'w') as outfile:
        outfile.write('\n'.join(s for s in ss))

def plot_f63(dirname: str):
    newpath = os.path.join(os.getcwd(), dirname)
    p = subprocess.run(["touch", "hello.txt"], cwd=newpath, capture_output=True, check=True)
    p = subprocess.run(["ls", "-l"], cwd=newpath, capture_output=True, check=True)
    print(p.stdout.decode())

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("fname", help="Input contour file")
    parser.add_argument("dir", help="Directory to hold the plots")
    parser.add_argument("--cmin", type=float, help="Contour min")
    parser.add_argument("--cmax", type=float, help="Contour max")
    parser.add_argument("--cint", type=float, help="Contour interval")
    parser.add_argument("--xmin", type=float, help="Left longitude")
    parser.add_argument("--xmax", type=float, help="Right longitude")
    parser.add_argument("--ymin", type=float, help="Lower latitude")
    parser.add_argument("--ymax", type=float, help="Upper latitude")
    parser.add_argument("--region", choices=boxes.keys(), help="Predefined plot boxes")
    args = parser.parse_args()

    os.makedirs(args.dir, exist_ok=True)
    #plot_f63(args.dir)
    create_inp(args)

if __name__ == "__main__":
    main()
