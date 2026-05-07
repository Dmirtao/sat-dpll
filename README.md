
# sat-dpll
A basic SAT solver implementing DPLL + heuristics. It is executed using the command line. The default configuration enables **Conflict-Driven Clause Learning (CDCL)** paired with a standard Boolean Constraint Propagation (BCP) algorithm. You can toggle different heuristics and fallback modes using command-line flags.
## Directory Structure

 - `src/` contains all source code. This is the folder that `mySAT.py` should be run from for testing.
	 - `cnf_io.py` contains function(s) for parsing .cnf files
	 - `constants.py` contains assignment constants used in other code.
	 - `mySAT.py` is the **main command line entrance** into the program.
	 - `sat_struct.py` contains some obsoleted helper functions and the Implication Graph structure for CDCL.
	 - `sat.py` contains the main functions and logic of the SAT solver
 - `benchmarks/` contains many CNF files taken from https://www.cs.ubc.ca/%7Ehoos/SATLIB/benchm.html used for SAT performance benchmarking.
 - `tests/` contains helper test functions used for report generation and benchmarking.

## Compilation
The code provided is based in Python and uses only the standard Python libraries. It does not require compilation and was tested on Python 3.13.

## Basic Execution 
To run the solver with the default settings (CDCL + Standard BCP): 
```bash
python3 src/mySAT.py path/to/input.cnf
```

### Configuration Flags

 - `--wl`: **Two-Watched Literals BCP**: Enables the Watched Literals heuristic for BCP. Instead of scanning every clause on an assignment, the sovler only updates clauses where the assigned variable is actively being "watched."
 - `--dpll`: **Pure DPLL (No Learning)**:  Disables conflict analysis, clause learning, and non-chronological backjumping. The solver reverts to standard DPLL with chronological backtracking on a conflict detection.

## Execution Examples
**CDCL with BCP and Watched Literals (Recommended)**
```bash
python3 src/mySAT.py path/to/input.cnf --wl 
```

**CDCL with BCP**
```bash
python3 src/mySAT.py path/to/input.cnf
```
**Pure DPLL**
```bash
python3 src/mySAT.py path/to/input.cnf --dpll
```

**DPLL with Watched Literals**
```bash
python3 src/mySAT.py path/to/input.cnf --dpll --wl
```

