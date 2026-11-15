"""Offline numeric CLI; no CAD runtime is loaded."""
import argparse
import json
from .core import calculate


def main():
    parser=argparse.ArgumentParser(description='Excel-compatible wrinkle source preview; CAD untested')
    parser.add_argument('l1',type=float,help='unfolded length in mm')
    parser.add_argument('l2',type=float,help='projected span in mm')
    parser.add_argument('--thickness',type=float,default=None,help='optional mm, simplified strain only')
    args=parser.parse_args()
    try:
        result=calculate(args.l1,args.l2,args.thickness)
    except (ValueError,ArithmeticError) as exc:
        parser.error(str(exc))
    print(json.dumps(result,indent=2,allow_nan=False))

if __name__ == '__main__': main()
