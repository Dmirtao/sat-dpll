from pathlib import Path
from cnf_io import parse_dimacs_cnf
from sat_struct import (
    create_assignment_array,
    get_assignment_bitmasks,
    get_clause_bitmasks,
)


def unit_propagate(unit_clause: tuple, clauses: list[tuple]) -> list[tuple]:
    """_summary_

    Parameters
    ----------
    unit_clause : tuple
        _description_
    clauses : list[tuple]
        _description_

    Returns
    -------
    list[tuple]
        _description_

    """
    # TODO: Perform the unit clause propagation
    return clauses


def get_unit_clauses(clauses: list[tuple], assignments: bytearray) -> list[tuple]:
    """_summary_

    Parameters
    ----------
    clauses : list[tuple]
        _description_
    assignments : bytearray
        _description_

    Returns
    -------
    list[tuple]
        _description_
    """
    true_mask, false_mask = get_assignment_bitmasks(assignments)
    for clause in clauses:
        clause_p_mask, clause_n_mask = get_clause_bitmasks(clause)
        if is_unit(clause_p_mask, clause_n_mask, true_mask, false_mask):
            print(f"Found unit clause: {clause}")
    unit_clauses = []
    return unit_clauses


def is_unit(
    clause_p_mask: int, clause_n_mask: int, true_mask: int, false_mask: int
) -> bool:
    """Checks if an input clause is a unit clause.

    Parameters
    ----------
    clause_p_mask : int
        _description_
    clause_n_mask : int
        _description_
    true_mask : int
        _description_
    false_mask : int
        _description_

    Returns
    -------
    bool
        _description_
    """
    # 1. If a clause is already satisfied, then it is not unit.
    if true_mask & clause_p_mask or false_mask & clause_n_mask:
        return False
    # 2. Get literals that are not yet falsified
    remaining_lits = (clause_p_mask & ~false_mask) | (clause_n_mask & ~true_mask)
    # 3. Check if exactly one bit is set
    # (n > 0 and n & (n - 1) == 0 is the classic bit-trick for power of 2)
    
    return False


if __name__ == "__main__":
    # Load in target file
    clauses, num_vars, num_cls = parse_dimacs_cnf(Path("examples/simple_v3_v2.cnf"))
    assignments = create_assignment_array(num_vars)
    # true_assign_mask, false_assign_mask = get_assignment_bitmasks(assignments)
    # Retreive the list of unit clauses in the current clause list
    unit_clauses = get_unit_clauses(clauses, assignments)
    #  Unit propagation
    for unit_clause in unit_clauses:
        clauses = unit_propagate(unit_clause, clauses)
    print("Hello")
