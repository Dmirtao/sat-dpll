from cnf_io import parse_dimacs_cnf
from constants import TRUE
from sat_struct import init_assignment_array
from sat import cdcl
import sys

if __name__ == "__main__":
    clauses, num_vars, num_cls = parse_dimacs_cnf(sys.argv[1])
    assignments = init_assignment_array(num_vars)
    sat, final_assignments = cdcl(clauses, assignments)
    
    if sat:
        print("RESULT:SAT")
        assignment_str = " ".join(f"{i+1}=1" if v == TRUE else f"{i+1}=0" for i, v in enumerate(final_assignments))
        print("ASSIGNMENT:" + assignment_str)
    else:
        print("RESULT:UNSAT")
