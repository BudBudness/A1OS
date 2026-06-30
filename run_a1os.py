import sys
from pathlib import Path

def build_single_file():
    root = Path("~/A1OS").expanduser()
    generated = root / "build" / "generated"
    
    # Gather all operational subsystem artifacts
    files = sorted(list(generated.rglob("*.py")))
    
    output_file = root / "a1os_monolithic.py"
    print(f"[A1OS] Consolidating {len(files)} subsystems into a single format file: {output_file}")
    
    # Single format monolithic aggregator
    with open(output_file, "w", encoding="utf8") as outfile:
        outfile.write("# ==================================================\n")
        outfile.write("# A1OS SOVEREIGN RUNTIME - MONOLITHIC DISTRIBUTION\n")
        outfile.write("# ==================================================\n\n")
        
        outfile.write("import sys\nimport json\nimport sqlite3\nimport threading\nimport time\nimport importlib\nfrom pathlib import Path\n\n")
        
        for f in files:
            if f.name == "__init__.py":
                continue
            
            rel_path = f.relative_to(generated)
            outfile.write(f"\n# --------------------------------------------------\n")
            outfile.write(f"# MODULE: {rel_path}\n")
            outfile.write(f"# --------------------------------------------------\n\n")
            
            with open(f, "r", encoding="utf8", errors="ignore") as infile:
                outfile.write(infile.read())
                outfile.write("\n\n")
                
        outfile.write("# ==================================================\n")
        outfile.write("# END OF MONOLITHIC DISTRIBUTION\n")
        outfile.write("# ==================================================\n")

    print(f"✔ A1OS monolithic build complete at: {output_file}")
    print(f"✔ Executing single format platform matrix scan...")

    # Run direct LOC calculator and matrix tally
    loc = 0
    total_artifacts = 0
    for f in files:
        if f.name == "__init__.py":
            continue
        total_artifacts += 1
        with open(f, "r", encoding="utf8", errors="ignore") as fp:
            loc += sum(1 for _ in fp)

    print("==================================================")
    print("A1OS PLATFORM MATURITY MATRIX (MONOLITHIC RUNTIME)")
    print("==================================================")
    for f in files:
        if f.name == "__init__.py":
            continue
        with open(f, "r", encoding="utf8", errors="ignore") as fp:
            floc = sum(1 for _ in fp)
            print(f"{str(f.relative_to(generated)):<35} : {floc:>3} lines")
    print("==================================================")
    print(f"Total Subsystem Artifacts : {total_artifacts}")
    print(f"Total Operational LOC     : {loc}")
    print("==================================================")

if __name__ == "__main__":
    build_single_file()
