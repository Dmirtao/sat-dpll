import os
from pathlib import Path
from cnf_io import parse_dimacs_cnf
from collections import deque
from sat_struct import (
    init_assignment_array,
    get_assignment_bitmasks,
    get_clause_bitmasks,
    ImplicationGraph
)
from constants import UNASSIGNED, TRUE, FALSE
def bcp(
    clauses: list[tuple],
    assignments: bytearray,
    graph: ImplicationGraph,
    seed_lits: list[int] | None = None,
) -> tuple[bool, tuple | None]:
    """
    Boolean Constant Propagation (based on unit propagate)
    Starting form an optional list of seeds and thier literals (the most recently decided literal),
    Iteratively find unit clauses and force the implied assignmemnt until no unit clauses exist
    or a conflict is detected

    a conflict is defined as wehn a clause becomes a empty under the current assignment

    Parameters
    ----------
    clauses : list[tuple]
        Full clause database.
    assignments : bytearray
        Current variable assignments; updated in-place as literals are implied.
    graph : ImplicationGraph
        Implication graph; updated in-place with every implied literal.
    seed_lits : list[int] | None
        Literals whose assignment may have created new unit clauses. When
        None, all clauses are scanned from scratch (used at decision level 0).

    Returns
    -------
    tuple[bool, tuple | None]
        (conflict, conflict_clause)
        conflict is True if a conflict was detected.
        conflict_clause is the falsified clause that caused the conflict,
        or None if no conflict occurred.
    """
    # Queue of literals that were just assigned and may trigger implications
    queue: deque[int] = deque(seed_lits or [])
 
    # Bootstrap: scan all clauses when there are no seeds.
    if not seed_lits:
        for clause in clauses:
            result = _evaluate_clause(clause, assignments)
            if result == "conflict":
                return True, clause
            if result is not None and result != "satisfied":
                implied_lit = result
                var = abs(implied_lit) - 1
                if assignments[var] == UNASSIGNED:
                    val = TRUE if implied_lit > 0 else FALSE
                    assignments[var] = val
                    graph.imply(implied_lit, clause)
                    queue.append(implied_lit)

    while queue:
        _ = queue.popleft()
        for clause in clauses:
            result = _evaluate_clause(clause, assignments)
            if result == "conflict":
                return True, clause
            if result is not None and result != "satisfied":
                implied_lit = result
                var = abs(implied_lit) - 1
                if assignments[var] == UNASSIGNED:
                    val = TRUE if implied_lit > 0 else FALSE
                    assignments[var] = val
                    graph.imply(implied_lit, clause)
                    queue.append(implied_lit)
 
    return False, None

def _evaluate_clause(clause: tuple, assignments: bytearray) -> str | int | None:
    """Evaluate a single clause under the current assignment.

    Parameters
    ----------
    clause : tuple
        Clause to evaluate.
    assignments : bytearray
        Current variable assignments.

    Returns
    -------
    str | int | None
        "satisfied" if the clause is already satisfied,
        "conflict" if every literal is falsified,
        an implied literal (int) if it is a unit clause,
        None if the clause is not decided.
    """
    unassigned_lit: int | None = None
    unassigned_count = 0

    for lit in clause:
        var = abs(lit) - 1
        val = assignments[var]
        if val == UNASSIGNED:
            unassigned_count += 1
            unassigned_lit = lit
        else:
            is_positive = lit > 0
            if (is_positive and val == TRUE) or (not is_positive and val == FALSE):
                return "satisfied"

    if unassigned_count == 0:
        return "conflict"
    if unassigned_count == 1:
        return unassigned_lit  # implied literal
    return None  # undecided

def all_clauses_satisfied(clauses: list[tuple], assignments: bytearray) -> bool:
    """Check whether all clauses are satisfied in current assignment

    Parameters
    ----------
    clauses : list[tuple]
        all clauses
    assignments : bytearray
        Current variable assignments

    Returns
    -------
    bool
        True if every clause has at least one satisfied literal
    """
    for clause in clauses:
        satisfied = False
        for lit in clause:
            var = abs(lit) - 1
            val = assignments[var]
            is_positive = lit > 0
            if (is_positive and val == TRUE) or (not is_positive and val == FALSE):
                satisfied = True
                break
        if not satisfied:
            return False
    return True

def _assignment_negation(var: int, assignments: bytearray) -> int:
    """Return the literal that negates how var is currently assigned
 
    Parameters
    ----------
    var : int
        0-based variable index. Must be assigned (TRUE or FALSE)
    assignments : bytearray
        Current variable assignments
 
    Returns
    -------
    int
        The negated literal (1-based).
    """
    if assignments[var] == TRUE:
        return -(var + 1)
    else:
        return (var + 1)

def analyze_conflict(
    conflict_clause: tuple,
    assignments: bytearray,
    graph: ImplicationGraph,
) -> tuple[tuple, int]:
    """Derive a conflict clause using the 1-UIP (First Unique Implication Point) algorithm
    and compute the backjump level

    The 1-UIP is the closest dominator of the conflict node in the implication
    graph at the current decision level. The learned clause is the negation of
    the assignments that caused the conflict. The backjump level is the second
    highest decision level among the literals in the learned clause (or 0 if
    all literals are at level 0 / the clause is unit at the root).

    Algorithm
    ---------
    Starting from the conflict clause, resolve against the antecedent of the
    most-recently-assigned literal at the current decision level, one step at
    a time, until exactly one literal from the current decision level remains
    in the working set, the remaining literal is the First Unique Implicaiton point (1-UIP)

    Parameters
    ----------
    conflict_clause : tuple
        The clause that became empty (all literals false)
    assignments : bytearray
        Current variable assignments (used to read decision levels via graph)
    graph : ImplicationGraph
        The implication graph with antecedents and decision levels

    Returns
    -------
    tuple[tuple, int]
        (learned_clause, backjump_level)
        learned_clause is the derived conflict clause (as a tuple of literals)
        backjump_level is the decision level to jump back to
    """
    current_level = graph.current_level

    # Working set of variables in the current "reason" clause (as a set of literals)
    seen: set[int] = set()
    learned_vars: set[int] = set()

    def _add_clause_lits(clause: tuple) -> None:
        #Resolve a clause into seen (current-level vars) and learned_lits (others)
        for lit in clause:
            var = abs(lit) - 1
            #skip unassigned literals since theyre not a part of why the conflict is happening
            if assignments[var] == UNASSIGNED:
                continue
            dl = graph.decision_level.get(var, 0)
            if dl == current_level:
                seen.add(var)
            else:
                # Store the variable; _assignment_negation will handle the literal logic
                learned_vars.add(var)

    _add_clause_lits(conflict_clause)
    
    # Walk the trail in reverse to resolve until 1-UIP
    for lit in reversed(graph.trail):
        if len(seen) <= 1:
            # Exactly one current-level literal remains → 1-UIP found
            break
        var = abs(lit) - 1
        if var not in seen:
            continue
        seen.discard(var)
        antecedent = graph.antecedent.get(var)
        if antecedent is None:
            # This was a decision literal; keep its negation in the learned clause
            learned_vars.add(var)
        else:
            _add_clause_lits(antecedent)

    # The single remaining seen variable is the 1-UIP; add its negation
    if seen:
        learned_vars.add(next(iter(seen)))

    learned_clause = tuple(_assignment_negation(var, assignments) for var in learned_vars)

    # Compute backjump level: second-highest decision level among learned_lits
    levels = sorted(
        {graph.decision_level.get(var, 0) for var in learned_vars},
        reverse=True,
    )
    backjump_level = levels[1] if len(levels) > 1 else 0
 
    return learned_clause, backjump_level


def pick_unassigned_var(assignments: bytearray) -> int | None:
    """Choose the next unassigned variable using the first-unassigned heuristic.

    Placeholder for DLIS or VSIDS

    Parameters
    ----------
    assignments : bytearray
        Current variable assignments.

    Returns
    -------
    int | None
        0-based index of an unassigned variable, or None if all are assigned.
    """
    for i, val in enumerate(assignments):
        if val == UNASSIGNED:
            return i
    return None

def cdcl(
    clauses: list[tuple],
    assignments: bytearray,
) -> tuple[bool, bytearray]:
    """Conflict-Driven Clause Learning (CDCL) SAT solver.

    Implements the full CDCL loop:
      1. BCP at the current decision level.
      2. If conflict at level 0 → UNSAT.
      3. If conflict at level > 0 → analyze conflict, learn clause, backjump.
      4. If all variables assigned → SAT.
      5. Otherwise → pick a new variable, decide, and repeat.

    Parameters
    ----------
    clauses : list[tuple]
        Initial clause database (will be extended with learned clauses).
    assignments : bytearray
        Initial variable assignments (all UNASSIGNED at the start).

    Returns
    -------
    tuple[bool, bytearray]
        (satisfiable, assignments)
        satisfiable is True if a satisfying assignment was found.
        assignments holds the final (satisfying) variable assignment when SAT,
        or an indeterminate state when UNSAT.
    """
    print("starting CDCL")
    graph = ImplicationGraph()
    learned_clause_set: set[frozenset] = set()
    print("done with graph")
    # Phase 0: BCP at decision level 0 (root-level unit propagation)
    conflict, conflict_clause = bcp(clauses, assignments, graph, seed_lits=None)
    if conflict:
        return False, assignments  # UNSAT: conflict at root level
    print("first loop")
    while True:
        # Check if all variables have been assigned
        var_idx = pick_unassigned_var(assignments)

        if var_idx is None:
            # All variables assigned; verify every clause is satisfied
            if all_clauses_satisfied(clauses, assignments):
                return True, assignments
            # Shouldn't happen if BCP is correct, but guard anyway
            # Find a conflict clause manually
            for cl in clauses:
                if _evaluate_clause(cl, assignments) == "conflict":
                    conflict_clause = cl
                    conflict = True
                    break
        
        if not conflict:
            #assign the chosen variable TRUE (try TRUE first).
            decision_lit = var_idx + 1
            assignments[var_idx] = TRUE
            graph.decide(decision_lit)
            conflict, conflict_clause = bcp(
                clauses, assignments, graph, seed_lits=[decision_lit]
            )
 


        while conflict:
            if graph.current_level == 0:
                # Conflict at root level -> UNSAT
                return False, assignments

            # Conflict analysis to derive learned clause and backjump level
            learned_clause, backjump_level = analyze_conflict(
                conflict_clause, assignments, graph
            )
            if backjump_level >= graph.current_level:
                backjump_level = max(0, graph.current_level - 1)
            
            frozen = frozenset(learned_clause)
            if frozen not in learned_clause_set:
                learned_clause_set.add(frozen)
                clauses.append(learned_clause)

            graph.backjump(backjump_level, assignments)

            unit_lit = next(
                (lit for lit in learned_clause
                 if assignments[abs(lit) - 1] == UNASSIGNED),
                None,
            )
            if unit_lit is not None:
                var = abs(unit_lit) - 1
                assignments[var] = TRUE if unit_lit > 0 else FALSE
                graph.imply(unit_lit, learned_clause)
                conflict, conflict_clause = bcp(
                    clauses, assignments, graph, seed_lits=[unit_lit]
                )
            else:
                conflict, conflict_clause = bcp(
                    clauses, assignments, graph, seed_lits=None
                )
        conflict = False


#def unit_propagate(unit_clause: tuple, clauses: list[tuple], assignments: bytearray) -> tuple[list[tuple], bytearray]:
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
    # NOTE: This can likely be merged with is_unit as it repeats a few of the same steps.
    # TODO: Perform the unit clause propagation
    # Set the unit clauses single unassigned literal to true
    true_mask, false_mask, full_mask = get_assignment_bitmasks(assignments)
    clause_p_mask, clause_n_mask = get_clause_bitmasks(unit_clause)
    remaining_lit = (clause_p_mask & (false_mask ^ full_mask)) | (clause_n_mask & (true_mask ^ full_mask))
    # Check if remaining lit is positive or negative
    if (remaining_lit & (remaining_lit - 1)) == 0:
        bit_ndx = remaining_lit.bit_length() - 1
        
        val_to_assign = TRUE if (remaining_lit & clause_p_mask) else FALSE

        assignments[bit_ndx] = val_to_assign
    
    return clauses, assignments


#def get_unit_clauses(clauses: list[tuple], assignments: bytearray) -> list[tuple]:
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


#def is_unit(clause_p_mask: int, clause_n_mask: int, true_mask: int, false_mask: int, full_mask: int ) -> bool:
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


#def dpll(clauses: list[tuple], assignments: bytearray) -> list[tuple]:
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
        clauses = unit_propagate(unit_clause, clauses, assignments)

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
    for root, dirs, files in os.walk(Path("benchmarks/uf20-91/")):
        for name in files:
            print("Parsing dimacs")
            clauses, num_vars, num_cls = parse_dimacs_cnf(
                os.path.join(root, name)
            )
            print("making assignments")
            assignments = init_assignment_array(num_vars)
            print("starting cdcl")
            sat, final_assignments = cdcl(clauses, assignments)
            if sat:
                print("SAT")
                assignment_str = " ".join(
                    str(i + 1) if v == TRUE else str(-(i + 1))
                    for i, v in enumerate(final_assignments)
                )
                print(assignment_str)
            else:
                print("UNSAT")
            # Retrieve the list of unit clauses in the current clause list
            #dpll(clauses, assignments)
    print("Done")
