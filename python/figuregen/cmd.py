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
    CONTOUR_FORMAT = 19
    CONTOUR_SCALE = 20
    F14 = 13
    GRID = 14
    FILENAME = 6
    PLOT_LABEL = 7
    XMIN = 9
    XMAX = 10
    YMIN = 11
    YMAX = 12
    CONTOUR_RANGE = 25
    CONTOUR_INT = 26
    VECTOR_FLAG = 39
    VECTOR_FILE = 40
    ALTERNATE = 57
    ANNOTATE = 58

# 19 - input coutour file name
def create_inp(args):
    F14_FILE = "fort.14"
    if os.path.isfile("fort.14.renum"):
      F14_FILE = "fort.14.renum"

    ss = samples
    ss[Inp.F14.value] = "../" + F14_FILE
    ss[Inp.CONTOUR_FILE.value] = os.path.join("..", args.fname)

    if args.bath:
        ss[Inp.CONTOUR_FORMAT.value] = "GRID-BATH"
        ss[Inp.CONTOUR_FILE.value] = "../" + F14_FILE
        ss[Inp.CONTOUR_SCALE.value] = "-1"
        ss[Inp.FILENAME.value] = "bath"

    if args.grid:
        ss[Inp.GRID.value] = '1'

    if args.region is not None:
        xmin, xmax, ymin, ymax = boxes[args.region]

    # Box is specified
    elif all([args.xmin, args.xmax, args.ymin, args.ymax]):
        xmin = args.xmin; xmax = args.xmax; ymin = args.ymin; ymax = args.ymax

    else: # find min and max from fort.14
        print("Using plot range from fort.14")
        f14 = Fort14(F14_FILE)
        xmin, xmax, ymin, ymax = f14.box()

    ss[Inp.XMIN.value] = str(xmin)
    ss[Inp.XMAX.value] = str(xmax)
    ss[Inp.YMIN.value] = str(ymin)
    ss[Inp.YMAX.value] = str(ymax)

    dx = xmax - xmin
    dy = ymax - ymin
    spacing = max(dx, dy) / 10.
    ss[Inp.ALTERNATE.value] = "%.1f" % spacing
    ss[Inp.ANNOTATE.value] = "%.1f" % spacing

    if None in [args.cmin, args.cmax]:
        print("Using default contour range [-1,5]")
        ss[Inp.CONTOUR_RANGE.value] = "-1,5"
    else:
        ss[Inp.CONTOUR_RANGE.value] = str(args.cmin) + ',' + str(args.cmax)

    if args.cint is not None:
        ss[Inp.CONTOUR_INT.value] = str(args.cint)
        
    if args.vector:
        ss[Inp.VECTOR_FLAG.value] = '1'
        ss[Inp.VECTOR_FILE.value] = '../' + args.vector_file
        print(f"Using vector file {args.vector_file}")

    with open(os.path.join(args.dir, "sample.inp"), 'w') as outfile:
        outfile.write('\n'.join(s for s in ss))

    with open(os.path.join(args.dir, "Default2.pal"), 'w') as outfile:
        outfile.write(default2)

def run_figuregen(args):
    dirpath = os.getcwd()
    newpath = os.path.join(os.getcwd(), args.dir)
    figpath = os.path.join(os.environ["FIG_PATH"], "figuregen.sif")
    np = 4

    os.chdir(newpath)
    os.system("singularity exec %s mpirun -np %d figuregen -I sample.inp" % (figpath, np))
    os.chdir(dirpath)
    # p = subprocess.run(["singularity", "exec", figpath,
    #                     "mpirun", "-np", "2",
    #                     "figuregen", "-I", "sample.inp"],
    #                    cwd=newpath, capture_output=True, check=True)
    # print(p.stdout.decode())

def create_animation(args):
    dirpath = os.getcwd()
    newpath = os.path.join(os.getcwd(), args.dir)

    os.chdir(newpath)
    os.system("ffmpeg -framerate 10 -i plot%04d.jpg -vf \"pad=ceil(iw/2)*2:ceil(ih/2)*2\" -y movie.mp4")
    os.chdir(dirpath)
    

def check_figuregen():
    try:
        container_path = os.environ["FIG_PATH"]
    except KeyError:
        print("ERROR: apptainer container path not set!")
        sys.exit()

    if not os.path.exists(os.path.join(container_path, "figuregen.sif")):
        print("ERROR: figuregen.sif not found in FIG_PATH!")
        sys.exit()

def check_input(args):
    contour = os.path.join(os.getcwd(), args.fname)
    f14 = os.path.join(os.getcwd(), "fort.14")

    if not os.path.exists(contour):
        print("ERROR: specified contour file \"%s\" does not exist!" % args.fname)
        sys.exit()
        
    if not os.path.exists(f14):
        print("ERROR: fort.14 does not exist!")
        sys.exit()

    if args.vector and (not os.path.exists(args.vector_file)):
        print(f"ERROR: {args.vector_file} not found!")
        sys.exit()
    
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
    parser.add_argument("--grid", action="store_true", help="Plot grid lines")
    parser.add_argument("--animate", action="store_true", help="Also produce a movie. Ignored if plotting maxele.63")
    parser.add_argument("--vector", action="store_true", help="Plot velocity vectors from fort.64 file with the same name as the given fort.63 file.")
    parser.add_argument("--bath", action="store_true", help="Plot bathymetry.")
    args = parser.parse_args()

    if args.vector:
        args.vector_file = args.fname.replace("63", "64")

    check_figuregen()
    check_input(args)

    if "maxele" in args.fname:
        args.animate = False

    os.makedirs(args.dir, exist_ok=True)
    create_inp(args)
    run_figuregen(args)
    if args.animate:
        create_animation(args)

if __name__ == "__main__":
    main()
