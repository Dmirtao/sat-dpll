from pathlib import Path
from cnf_io import parse_dimacs_cnf
from sat_struct import (
    init_assignment_array,
    get_assignment_bitmasks,
    get_clause_bitmasks,
)


def unit_propagate(unit_clause: tuple, clauses: list[tuple]) -> list[tuple]:
    """This function takes a unit clause and the current list of clauses, and
    returns an updated list of clauses after performing unit propagation based
    on the unit clause.
    If a clause is a unit clause, i.e. it contains only
     a single unassigned literal, this clause can only be
     satisfied by assigning the necessary value to make this
    literal true. Thus, no choice is necessary. Unit
    propagation consists in removing every clause containing
    a unit clause's literal and in discarding the
    complement of a unit clause's literal from every
    clause containing that complement. In practice,
    this often leads to deterministic cascades of units,
    thus avoiding a large part of the naive search space.

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
    # Set the unit clauses single unassigned literal to true
    return clauses


def get_unit_clauses(clauses: list[tuple], assignments: bytearray) -> list[tuple]:
    """Returns a list of unit clauses from the input clause list based on the current variable assignments.
    A unit clause is a clause that has exactly one unassigned literal and all other literals are falsified by the current assignment.

    Parameters
    ----------
    clauses : list[tuple]
        List of tuples representing the clauses, where each tuple contains integers representing literals (positive for true, negative for false).
    assignments : bytearray
        Bytearray representing the current variable assignments. Each index corresponds to a variable, and the value can be UNASSIGNED, TRUE, or FALSE.

    Returns
    -------
    list[tuple]
        List of unit clauses.
    """
    unit_clauses: list[tuple] = []
    true_mask, false_mask, full_mask = get_assignment_bitmasks(assignments)
    for clause in clauses:
        clause_p_mask, clause_n_mask = get_clause_bitmasks(clause)
        if is_unit(clause_p_mask, clause_n_mask, true_mask, false_mask, full_mask):
            unit_clauses.append(clause)
    return unit_clauses


def is_unit(
    clause_p_mask: int, clause_n_mask: int, true_mask: int, false_mask: int, full_mask: int 
) -> bool:
    """Checks if an input clause is a unit clause.

    Parameters
    ----------
    clause_p_mask : int
        Bitmask representing the positive literals in the clause. A bit is 1 if the variable appears as a positive literal, otherwise it's zero.
    clause_n_mask : int
        Bitmask representing the negative literals in the clause. A bit is 1 if the variable appears as a negative literal, otherwise it's zero.
    true_mask : int
        Bitmask representing the variables assigned TRUE in the current assignment.
    false_mask : int
        Bitmask representing the variables assigned FALSE in the current assignment.

    Returns
    -------
    bool
        Returns True if the clause is a unit clause, False otherwise.
    """
    # 1. If a clause is already satisfied, then it is not unit.
    if true_mask & clause_p_mask or false_mask & clause_n_mask:
        return False
    # 2. Get literals that are not yet falsified
    # BUG: If you have one literal and no assigned false or true in the mask what then.
    # FIX: Use the full_mask of all ones to expand the mask to avoid Python bitmask weirdness
    remaining_lits = (clause_p_mask & (false_mask ^ full_mask)) | (clause_n_mask & (true_mask ^ full_mask))
    # 3. Check if exactly one bit is set == exactly one literal is not yet falsified
    # (n > 0 and n & (n - 1) == 0 is the classic bit-trick for power of 2)
    return remaining_lits > 0 and (remaining_lits & (remaining_lits - 1)) == 0


def dpll(clauses: list[tuple], assignments: bytearray) -> list[tuple]:
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
    # DEBUG: Make clause[0] a unit clause. Need negative indices for endianness
    assignments[-9] = 2
    assignments[-12] = 2
    unit_clauses = get_unit_clauses(clauses, assignments)
    #  Unit clause propagation
    for unit_clause in unit_clauses:
        clauses = unit_propagate(unit_clause, clauses)

    # Pure literal elimination would go here (not implemented yet)
    # while there is a literal l that occurs pure in Φ do
    # Φ ← pure-literal-assign(l, Φ);

    # Stopping conditions for DPLL go here (e.g. if clauses is empty, or if any clause is empty, etc.)
    if not clauses:
        # If there are no clauses left, then the formula is satisfied by the current assignment
        print("SAT")
        # TODO: Print the satisfying assignment
    if clauses and any(len(clause) == 0 for clause in clauses):
        # If there are clauses left but any clause is empty, then the formula is unsatisfiable under the current assignment
        print("UNSAT")
    # DPLL Procedure code goes here (e.g. choose a variable, assign it, recurse, backtrack, etc.)
    # TODO: Implement a better heuristic for choosing a literal
    # return dpll(clauses, assignments) or dpll(clauses, assignments)
    raise NotImplementedError("DPLL procedure not implemented yet.")


if __name__ == "__main__":
    # Load in target file
    clauses, num_vars, num_cls = parse_dimacs_cnf(
        Path("benchmarks\\uf20-91\\uf20-010.cnf")
    )
    assignments = init_assignment_array(num_vars)
    # Retrieve the list of unit clauses in the current clause list
    dpll(clauses, assignments)
    print("Done")
