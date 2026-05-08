from cnf_io import parse_dimacs_cnf
from sat_struct import init_assignment_array
from sat import cdcl
import os
from pathlib import Path
import cProfile
import pstats
import pytest
from tqdm import tqdm

@pytest.fixture(autouse=True)
def profile_test(request):
    """Automatically profiles every test, filtering out built-ins."""
    profiler = cProfile.Profile()
    profiler.enable()
    
    yield 
    
    profiler.disable()
    txt_file = f"{request.node.name}_stats.txt"
    with open(txt_file, "w") as f:
        # Pass the file handle as the stream
        stats = pstats.Stats(profiler, stream=f)
        stats.sort_stats(pstats.SortKey.CUMULATIVE)
        f.write(f"--- Profile for {request.node.name} ---\n")
        
        # Still filter to only show your src/ directory
        stats.print_stats("sat-dpll.src")
        
    # 2. Dump the binary stats for Snakeviz
    prof_file = f"{request.node.name}.prof"
    stats.dump_stats(prof_file)

def run_benchmark_folder(
    benchmark_path: Path, subset: int = 0, use_cdl=True, use_wl=False
) -> tuple[int, int]:
    was_sat = []
    was_unsat = []
    # Load in target file
    for root, dirs, files in os.walk(benchmark_path):
        if subset > 0:
            files = files[:subset]
        for idx, name in enumerate(tqdm(files, desc=f"Benchmarking {benchmark_path.name}")):
            clauses, num_vars, num_cls = parse_dimacs_cnf(os.path.join(root, name))
            assignments = init_assignment_array(num_vars)
            sat, final_assignments = cdcl(
                clauses, assignments, num_vars=num_vars, use_cdl=use_cdl, use_wl=use_wl
            )
            if sat:
                was_sat.append(name)
            else:
                was_unsat.append(name)
    return (len(was_sat), len(was_unsat))


def test_uf20_91():
    (was_sat, was_unsat) = run_benchmark_folder(
        Path("benchmarks/uf20-91/"), use_wl=False
    )
    assert was_sat == 1000
    assert was_unsat == 0


def test_uf100_430():
    subset_count = 10
    (was_sat, was_unsat) = run_benchmark_folder(
        Path("benchmarks/uf100-430/"), subset=subset_count, use_wl=False
    )
    assert was_sat == subset_count
    assert was_unsat == 0


def test_uuf100_430():
    subset_count = 10
    (was_sat, was_unsat) = run_benchmark_folder(
        Path("benchmarks/uuf100-430/"), subset=subset_count, use_wl=False
    )
    assert was_sat == 0
    assert was_unsat == subset_count
