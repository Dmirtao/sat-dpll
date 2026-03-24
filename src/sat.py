from pathlib import Path


def parse_dimacs_cnf(filename: Path) -> tuple[list[tuple], int, int]:
    """_summary_

    Parameters
    ----------
    filename : Path
        _description_

    Returns
    -------
    tuple[list[tuple], int, int]
        _description_

    Raises
    ------
    ValueError
        _description_
    ValueError
        _description_
    """
    clauses: list = []
    with open(filename, "r") as f:
        for line in f:
            line = line.strip()
            if line.startswith("c") or not line:
                # Ignore lines that start with "c"
                continue
            if line.startswith("p"):
                # Parse header: p cnf <n_vars> <n_clauses>
                parts: list[str] = line.split()
                if len(parts) == 4 and parts[1] == "cnf":
                    num_vars = int(parts[2])
                    num_clauses = int(parts[3])
                else:
                    raise ValueError(
                        f"The header line of file input {filename} is badly formed: {line}"
                    )
                continue
            if line.startswith("%"):
                # "%" indicates the end of the file
                break
            # Parse clause line
            # Varisat manual mentions clauses can span multiple lines and
            # any combination of spaces/newlines are separators
            # The following logic assumes each line is one clause (or part of one)
            # A more robust parser would handle multi-line clauses better.
            literals: tuple[int] = tuple([int(x) for x in line.split() if x != "0"])
            if literals:
                clauses.append(literals)
    # Verification step before returning
    if len(clauses) != num_clauses:
        raise ValueError(
            f"The number of clauses {num_clauses} in the header did not match number of parsed clauses {len(clauses)}."
        )

    return clauses, num_vars, num_clauses


if __name__ == "__main__":
    # Load in target file
    clauses, num_vars, num_cls = parse_dimacs_cnf(
        Path("examples/simple_v3_v2.cnf")
    )
    print("Hello")

