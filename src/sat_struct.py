"""Data structures"""

# Assignment constants
UNASSIGNED = 0
TRUE = 1
FALSE = 2


def create_assignment_array(num_vars: int) -> bytearray:
    """Creates an array to hold the variable assignments, initialized to UNASSIGNED.
    This array will be indexed by variable number (0-based index for variable 1, etc.)
    and will hold the assignment state (UNASSIGNED, TRUE, FALSE) for each variable.
    This function is useful for initializing the assignment state before starting the DPLL
    algorithm. It should really be only used once at the beginning of the algorithm, and
    then the same array should be updated in place as the algorithm progresses.

    Parameters
    ----------
    num_vars : int
        Number of variables in the SAT problem, used to determine the size of the assignment array.

    Returns
    -------
    bytearray
        Array initialized with UNASSIGNED values.
    """
    return bytearray([UNASSIGNED] * num_vars)


def get_assignment_bitmasks(assignment: bytearray) -> tuple[int, int]:
    """Returns a tuple of int
    This operation can be expensive so only call when really necessary.

    Parameters
    ----------
    assignment : bytearray
        _description_

    Returns
    -------
    tuple[int,int]
        _description_
    """

    true_mask_list: list[int] = [
        lit & TRUE for lit in assignment
    ]  # Bits of variables assigned TRUE
    false_mask_list: list[int] = [
        lit & FALSE for lit in assignment
    ]  # Bits of variables assigned FALSE
    true_mask: int = int("".join(map(str, true_mask_list)))
    false_mask: int = int("".join(map(str, false_mask_list)))
    return (true_mask, false_mask)


def get_clause_bitmasks(clause: tuple[int]) -> tuple[int, int]:
    """In these bitmasks, for the positive mask a bit is 1 if the variable appears
    as a positive literal, otherwise it's zero. For the negative mask a bit is 1 if the
    variable appears as a negative literal, otherwise it's zero.

    Parameters
    ----------
    clause : tuple[int]
        Tuple of integers representing the literals in the clause. Positive integers represent positive literals, and negative integers represent negative literals.

    Returns
    -------
    tuple[int,int]
        Tuple of bitmasks (p_mask, n_mask) where p_mask is the bitmask for positive literals and n_mask is the bitmask for negative literals.
    """
    p_mask: int = 0
    n_mask: int = 0
    for lit in clause:
        lit_ndx = abs(lit) - 1
        if lit > 0:
            p_mask |= 1 << lit_ndx
        else:
            n_mask |= 1 << lit_ndx
    return p_mask, n_mask


# def is_lit_satisfied(lit, assigns):
#     var = lit >> 1
#     is_negated = lit & 1
#     val = assigns[var]

#     if val == UNASSIGNED:
#         return False

#     # If parity is 0 (pos), we need TRUE (1)
#     # If parity is 1 (neg), we need FALSE (2)
#     target = 2 if is_negated else 1
#     return val == target
