from cnf_io import parse_dimacs_cnf
from constants import TRUE
from sat_struct import init_assignment_array
from sat import cdcl
import os
from pathlib import Path


def run_benchmark_folder(benchmark_path: Path, subset: int = 0) -> tuple[int, int]:
    was_sat = []
    was_unsat = []
    # Load in target file
    for root, dirs, files in os.walk(benchmark_path):
        for idx, name in enumerate(files):
            # Exit condition if a subset was defined.
            if subset > 0 and idx >= subset:
                return (len(was_sat), len(was_unsat))
            clauses, num_vars, num_cls = parse_dimacs_cnf(os.path.join(root, name))
            assignments = init_assignment_array(num_vars)
            sat, final_assignments = cdcl(clauses, assignments)
            if sat:
                was_sat.append(name)
            else:
                was_unsat.append(name)
    return (len(was_sat), len(was_unsat))


def test_uf20_91():
    (was_sat, was_unsat) = run_benchmark_folder(Path("benchmarks/uf20-91/"))
    assert was_sat == 1000
    assert was_unsat == 0


def test_uf100_430():
    (was_sat, was_unsat) = run_benchmark_folder(Path("benchmarks/uf100-430/"), subset=5)
    assert was_sat == 5
    assert was_unsat == 0


def test_uuf100_430():
    (was_sat, was_unsat) = run_benchmark_folder(
        Path("benchmarks/uuf100-430/"), subset=5
    )
    assert was_sat == 0
    assert was_unsat == 5
