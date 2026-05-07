import argparse
from cnf_io import parse_dimacs_cnf
from constants import TRUE
from sat_struct import init_assignment_array
from sat import cdcl
import sys

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MySAT Solver with Heuristic Toggles")
    parser.add_argument("cnf_file", type=str, help="Input DIMACS CNF file")
    parser.add_argument(
        "--dpll",
        action="store_true",
        help="Disable Conflict-Driven Learning and use pure DPLL",
    )
    parser.add_argument(
        "--wl", action="store_true", help="Use the Watched Literal heuristic for BCP"
    )
    args = parser.parse_args()

    clauses, num_vars, num_cls = parse_dimacs_cnf(args.cnf_file)
    assignments = init_assignment_array(num_vars)

    sat, final_assignments = cdcl(
        clauses, assignments, num_vars=num_vars, use_cdl=not args.dpll, use_wl=args.wl
    )

    if sat:
        print("RESULT:SAT")
        assignment_str = " ".join(
            f"{i + 1}=1" if v == TRUE else f"{i + 1}=0"
            for i, v in enumerate(final_assignments)
        )
        print("ASSIGNMENT:" + assignment_str)
    else:
        print("RESULT:UNSAT")
