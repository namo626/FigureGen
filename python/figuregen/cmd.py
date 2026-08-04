#!/usr/bin/env python3

import argparse
import sys
import os
import subprocess
from figuregen.parser import *
from figuregen.util import *
from enum import Enum

boxes = {
    "ocean": [-100, -60, 10, 50],
    "galveston": [-95.5, -94, 28.5, 30],
    "neches": [-94.13, 93.8, 29.93, 30.17],
}

class Inp(Enum):
    CONTOUR_FILE = 18
    F14 = 13
    GRID = 14
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
    ss[Inp.CONTOUR_FILE.value] = os.path.join("..", args.fname)

    if args.grid:
        ss[Inp.GRID.value] = '1'

    if args.region is not None:
        xmin, xmax, ymin, ymax = boxes[args.region]

    # Box is specified
    elif all([args.xmin, args.xmax, args.ymin, args.ymax]):
        xmin = args.xmin; xmax = args.xmax; ymin = args.ymin; ymax = args.ymax

    else: # find min and max from fort.14
        print("Using plot range from fort.14")
        f14 = Fort14("fort.14")
        xmin, xmax, ymin, ymax = f14.box()

    ss[Inp.XMIN.value] = str(xmin)
    ss[Inp.XMAX.value] = str(xmax)
    ss[Inp.YMIN.value] = str(ymin)
    ss[Inp.YMAX.value] = str(ymax)

    if None in [args.cmin, args.cmax]:
        print("Using default contour range [-1,5]")
        ss[Inp.CONTOUR_RANGE.value] = "-1,5"
    else:
        ss[Inp.CONTOUR_RANGE.value] = str(args.cmin) + ',' + str(args.cmax)

    if args.cint is not None:
        ss[Inp.CONTOUR_INT.value] = str(args.cint)
        

    with open(os.path.join(args.dir, "sample.inp"), 'w') as outfile:
        outfile.write('\n'.join(s for s in ss))

    with open(os.path.join(args.dir, "Default2.pal"), 'w') as outfile:
        outfile.write(default2)

def run_figuregen(args):
    newpath = os.path.join(os.getcwd(), args.dir)
    container_path = os.environ["FIG_PATH"]
    figpath = os.path.join(container_path, "figuregen.sif")

    p = subprocess.run(["singularity", "exec", figpath,
                        "mpirun", "-np", "2",
                        "figuregen", "-I", "sample.inp"],
                       cwd=newpath, capture_output=True, check=True)
    print(p.stdout.decode())

def main():
    try:
        container_path = os.environ["FIG_PATH"]
    except KeyError:
        print("ERROR: apptainer container path not set!")
        sys.exit()

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
    parser.add_argument("--grid", action="store_true", help="Plot grid lines")
    args = parser.parse_args()

    os.makedirs(args.dir, exist_ok=True)
    create_inp(args)
    run_figuregen(args)

if __name__ == "__main__":
    main()
