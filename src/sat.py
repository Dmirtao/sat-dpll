from collections import deque
from sat_struct import ImplicationGraph
from constants import UNASSIGNED, TRUE, FALSE


def init_watchers(clauses: list[tuple], num_vars: int) -> tuple[dict, list]:
    """Initializes the data structure to watch the first two literals.

    Parameters
    ----------
    clauses : list[tuple]
        Full clause database.
    num_vars : int
        Number of variables in DIMACS input
    """
    watchers = {lit: [] for lit in range(-num_vars, num_vars + 1) if lit != 0}
    watched_lits = []

    for i, c in enumerate(clauses):
        if len(c) > 1:
            w1, w2 = c[0], c[1]
            watchers[w1].append(i)
            watchers[w2].append(i)
            watched_lits.append([w1, w2])
        elif len(c) == 1:
            w1 = c[0]
            watchers[w1].append(i)
            watched_lits.append([w1, w1])
        else:
            watched_lits.append([])

    return watchers, watched_lits


def bcp_watched(
    clauses: list[tuple],
    assignments: bytearray,
    graph: ImplicationGraph,
    watchers: dict,
    watched_lits: list[list[int]],
    seed_lits: list[int] | None,
) -> tuple[bool, tuple | None]:
    """Variant of Boolean Constant Propagation (based on unit propagate), that includes watched literals.
    Starting from an optional list of seeds and thier literals (the most recently decided literal),
    Iteratively find unit clauses and force the implied assignmemnt until no unit clauses exist
    or a conflict is detected

    Parameters
    ----------
    clauses : list[tuple]
        Full clause database.
    assignments : bytearray
        Current variable assignments; updated in-place as literals are implied.
    graph : ImplicationGraph
        Implication graph; updated in-place with every implied literal.
    watchers : dict
        Watcher data structure
    watched_lits : list[list[int]]
        Lists of watched literals
    seed_lits : list[int] | None
        Literals whose assignment may have created new unit clauses. When
        None, all clauses are scanned from scratch (used at decision level 0).

    Returns
    -------
    tuple[bool, tuple | None]
        _description_
    """
    queue = deque(seed_lits or [])

    # Bootstrap: identify unit clauses if no seed is provided
    if not seed_lits:
        for i, c in enumerate(clauses):
            if len(c) == 1:
                lit = c[0]
                var = abs(lit) - 1
                val = assignments[var]
                if val == UNASSIGNED:
                    assignments[var] = TRUE if lit > 0 else FALSE
                    graph.imply(lit, c)
                    queue.append(lit)
                elif (lit > 0 and val == FALSE) or (lit < 0 and val == TRUE):
                    return True, c

    while queue:
        assigned_lit = queue.popleft()
        falsified_lit = -assigned_lit

        old_watches = watchers[falsified_lit][:]
        watchers[falsified_lit].clear()

        for j, c_idx in enumerate(old_watches):
            clause = clauses[c_idx]
            w1, w2 = watched_lits[c_idx]

            # Make w2 the falsified literal for simplicity
            if w1 == falsified_lit:
                w1, w2 = w2, w1
                watched_lits[c_idx] = [w1, w2]

            w1_var = abs(w1) - 1
            w1_val = assignments[w1_var]

            # If the other watched literal is TRUE, the clause is already satisfied
            if (w1 > 0 and w1_val == TRUE) or (w1 < 0 and w1_val == FALSE):
                watchers[falsified_lit].append(c_idx)
                continue

            # Search for a new unassigned or true literal to watch
            new_watch = None
            for lit in clause:
                if lit == w1 or lit == w2:
                    continue
                l_var = abs(lit) - 1
                l_val = assignments[l_var]
                if (
                    l_val == UNASSIGNED
                    or (lit > 0 and l_val == TRUE)
                    or (lit < 0 and l_val == FALSE)
                ):
                    new_watch = lit
                    break

            if new_watch is not None:
                watched_lits[c_idx][1] = new_watch
                watchers[new_watch].append(c_idx)
            else:
                # No new watch found; restore the old one. This means unit or conflict.
                watchers[falsified_lit].append(c_idx)
                if w1_val == UNASSIGNED:
                    assignments[w1_var] = TRUE if w1 > 0 else FALSE
                    graph.imply(w1, clause)
                    queue.append(w1)
                elif (w1 > 0 and w1_val == FALSE) or (w1 < 0 and w1_val == TRUE):
                    # Restore the remaining unprocessed watchers before returning
                    for remaining_c_idx in old_watches[j + 1:]:
                        watchers[falsified_lit].append(remaining_c_idx)
                    return True, clause

    return False, None


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
        return var + 1


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

    def _add_clause_lits(clause: tuple, ignore_var: int = -1) -> None:
        # Resolve a clause into seen (current-level vars) and learned_lits (others)
        for lit in clause:
            var = abs(lit) - 1
            # Skip the variable we are actively resolving out
            if var == ignore_var:
                continue
            # skip unassigned literals since theyre not a part of why the conflict is happening
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
            # Pass the variable to ignore so it doesn't get added back to seen
            _add_clause_lits(antecedent, ignore_var=var)

    # The single remaining seen variable is the 1-UIP; add its negation
    if seen:
        learned_vars.add(next(iter(seen)))

    sorted_vars = sorted(
            list(learned_vars),
            key=lambda v: graph.decision_level.get(v, 0),
            reverse=True,
    )

    learned_clause = tuple(
        _assignment_negation(var, assignments) for var in sorted_vars
    )

    backjump_level = graph.decision_level.get(sorted_vars[1], 0) if len(sorted_vars) > 1 else 0

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
    num_vars: int = 0,
    use_cdl: bool = True,
    use_wl: bool = False,
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
    graph = ImplicationGraph()
    learned_clause_set: set[frozenset] = set()
    decision_stack = []

    if use_wl:
        watchers, watched_lits = init_watchers(clauses, num_vars)
    else:
        watchers, watched_lits = None, None

    # Phase 0: BCP at decision level 0 (root-level unit propagation)
    if use_wl:
        conflict, conflict_clause = bcp_watched(
            clauses, assignments, graph, watchers, watched_lits, seed_lits=None
        )
    else:
        conflict, conflict_clause = bcp(clauses, assignments, graph, seed_lits=None)

    if conflict:
        return False, assignments  # UNSAT: conflict at root level

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
            # assign the chosen variable TRUE (try TRUE first).
            decision_lit = var_idx + 1
            assignments[var_idx] = TRUE
            graph.decide(decision_lit)

            if not use_cdl:
                decision_stack.append(
                    (decision_lit, False)
                )  # Track that the literal was flipped

            if use_wl:
                conflict, conflict_clause = bcp_watched(
                    clauses,
                    assignments,
                    graph,
                    watchers,
                    watched_lits,
                    seed_lits=[decision_lit],
                )
            else:
                conflict, conflict_clause = bcp(
                    clauses, assignments, graph, seed_lits=[decision_lit]
                )

        while conflict:
            if graph.current_level == 0:
                # Conflict at root level -> UNSAT
                return False, assignments

            if use_cdl:
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
                    if use_wl:
                        c_idx = len(clauses) - 1
                        if len(learned_clause) > 1:
                            w1, w2 = learned_clause[0], learned_clause[1]
                            watchers[w1].append(c_idx)
                            watchers[w2].append(c_idx)
                            watched_lits.append([w1, w2])
                        else:
                            w1 = learned_clause[0]
                            watchers[w1].append(c_idx)
                            watched_lits.append([w1, w1])

                graph.backjump(backjump_level, assignments)

                unit_lit = next(
                    (
                        lit
                        for lit in learned_clause
                        if assignments[abs(lit) - 1] == UNASSIGNED
                    ),
                    None,
                )
                if unit_lit is not None:
                    var = abs(unit_lit) - 1
                    assignments[var] = TRUE if unit_lit > 0 else FALSE
                    graph.imply(unit_lit, learned_clause)
                    seeds = [unit_lit]
                else:
                    seeds = None

                if use_wl:
                    conflict, conflict_clause = bcp_watched(
                        clauses,
                        assignments,
                        graph,
                        watchers,
                        watched_lits,
                        seed_lits=seeds,
                    )
                else:
                    conflict, conflict_clause = bcp(
                        clauses, assignments, graph, seed_lits=seeds
                    )

            else:
                # DPLL Chronological Fallback
                last_decision, flipped = decision_stack.pop()
                while flipped:
                    graph.backjump(graph.current_level - 1, assignments)
                    if not decision_stack:
                        return False, assignments
                    last_decision, flipped = decision_stack.pop()
                
                # Backtrack the unflipped level and flip it
                graph.backjump(graph.current_level - 1, assignments)
                flipped_lit = -last_decision
                decision_stack.append((flipped_lit, True))
                
                var = abs(flipped_lit) - 1
                assignments[var] = TRUE if flipped_lit > 0 else FALSE
                graph.decide(flipped_lit)
                
                if use_wl:
                    conflict, conflict_clause = bcp_watched(clauses, assignments, graph, watchers, watched_lits, seed_lits=[flipped_lit])
                else:
                    conflict, conflict_clause = bcp(clauses, assignments, graph, seed_lits=[flipped_lit])      
        conflict = False
