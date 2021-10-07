import subprocess
from pathlib import Path
import argparse

def process_subject(subid, study_dir, intermediate, nospatial=False, verbose=False, debug=False):
    cmd = ["python", "./process_osipi_subject.py",
           "--study_dir", str(study_dir),
           "--subid", str(subid),
           "--intermediate", intermediate]
    if nospatial:
        cmd.append("--nospatial")
    if verbose:
        cmd.append("--verbose")
    if debug:
        cmd.append("--debug")
    print(" ".join(cmd))
    subprocess.run(cmd, check=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Processing script for all subjects in the OSIPI ASL Challenge submission.")
    parser.add_argument("--challenge_dir",
                        help="OSIPI directory which contains the `Population_based` and "
                            +"`synthetic` directories.",
                        required=True)
    parser.add_argument("--intermediate",
                        help="Provide the name of an intermediate results directory. "
                            +"By providing a different value for this argument on each "
                            +"run you can avoid overwriting the results from other runs.",
                        default="")
    parser.add_argument("--nospatial",
                        help="If provided, oxford_asl run won't use spatial prior.",
                        action="store_true")
    parser.add_argument("--verbose",
                        help="If provided, the pipeline will print out statements on "
                            +"what the pipeline is doing.",
                        action="store_true")
    parser.add_argument("--debug",
                        help="If provided, the pipeline will retain intermediate "
                            +"for inpsection. If not, only the files required for "
                            +"OSIPI submission will be retained.",
                        action="store_true")
    args = parser.parse_args()

    # data directories
    osipi_dir = Path(args.challenge_dir).resolve(strict=True)
    population_dir = (osipi_dir/"Population_based").resolve(strict=True)
    synthetic_dir = (osipi_dir/"synthetic").resolve(strict=True)

    # list of subject IDs
    subjects = (("sub-PopulationAverage", population_dir),
                ("sub-DRO1", synthetic_dir),
                ("sub-DRO2", synthetic_dir),
                ("sub-DRO3", synthetic_dir),
                ("sub-DRO4", synthetic_dir),
                ("sub-DRO5", synthetic_dir),
                ("sub-DRO6", synthetic_dir),
                ("sub-DRO7", synthetic_dir),
                ("sub-DRO8", synthetic_dir),
                ("sub-DRO9", synthetic_dir))

    # iterate over subjects running the pipeline on them
    for subid, study_dir in subjects:
        process_subject(subid=subid,
                        study_dir=study_dir,
                        intermediate=args.intermediate,
                        nospatial=args.nospatial,
                        verbose=args.verbose,
                        debug=args.debug)