"""Data structures"""

from constants import UNASSIGNED, TRUE, FALSE

def init_assignment_array(num_vars: int) -> bytearray:
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

# def set_assignment_arr(assignment:bytearray, ) -> bytearray:

def get_assignment_bitmasks(assignment: bytearray) -> tuple[int, int, int]:
    """Returns a tuple of int
    This operation can be expensive so only call when really necessary.

    Parameters
    ----------
    assignment : bytearray
        _description_

    Returns
    -------
    tuple[int,int,int]
        _description_
    """
    true_mask = 0
    false_mask = 0

    for i, val in enumerate(assignment):
        if val == TRUE:
            true_mask |= (1 << i)
        elif val == FALSE:
            false_mask |= (1 << i)
    full_mask = (1 << len(assignment)) - 1
    return (true_mask, false_mask, full_mask)

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

class ImplicationGraph:
    """Tracks the implication graph for CDCL

    Each node in the graph is a variable. Edges represent implications:
    an edge from variable u to variable v means the assignment of u (via
    some clause) forced the assignment of v.

    Attributes
    ----------
    antecedent : dict[int, tuple | None]
        Maps variable index (0-based) to the clause that implied it,
        or None if it was a decision literal.
    decision_level : dict[int, int]
        Maps variable index (0-based) to the decision level at which it
        was assigned.
    trail : list[int]
        Ordered list of literals assigned so far (in assignment order)
        Positive literal = variable assigned TRUE: negative = assigned FALSE
    level_start : list[int]
        trail index at which each decision level begins, level_start[d] is
        the index into trail where decision level d started.
    current_level : int
        The current decision level
    """

    def __init__(self) -> None:
        self.antecedent: dict[int, tuple | None] = {}
        self.decision_level: dict[int, int] = {}
        self.trail: list[int] = []
        self.level_start: list[int] = [0]
        self.current_level: int = 0

    def decide(self, lit: int) -> None:
        """Record a decision literal (no antecedent clause)

        Parameters
        ----------
        lit : int
            The decided literal (positive for TRUE, negative for FALSE)
        """
        self.current_level += 1
        self.level_start.append(len(self.trail))
        var = abs(lit) - 1
        self.antecedent[var] = None
        self.decision_level[var] = self.current_level
        self.trail.append(lit)

    def imply(self, lit: int, clause: tuple) -> None:
        """Record an implied literal with its antecedent clause

        Parameters
        ----------
        lit : int
            The implied literal
        clause : tuple
            the unit clause
        """
        var = abs(lit) - 1
        self.antecedent[var] = clause
        self.decision_level[var] = self.current_level
        self.trail.append(lit)

    def backjump(self, target_level: int, assignments: bytearray) -> None:
        """Undo all assignments above target_level

        Parameters
        ----------
        target_level : int
            The decision level to jump back to
        assignments : bytearray
            The assignment array to update (variables are reset to UNASSIGNED)
        """
        # Find trail index of the start of target_level + 1
        if target_level + 1 < len(self.level_start):
            rollback_idx = self.level_start[target_level + 1]
        else:
            rollback_idx = 0

        # Undo all assignments from rollback_idx onward
        for lit in self.trail[rollback_idx:]:
            var = abs(lit) - 1
            assignments[var] = UNASSIGNED
            self.antecedent.pop(var, None)
            self.decision_level.pop(var, None)

        self.trail = self.trail[:rollback_idx]
        self.level_start = self.level_start[: target_level + 1]
        self.current_level = target_level

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
