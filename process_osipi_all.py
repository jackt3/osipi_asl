import subprocess
from pathlib import Path
import argparse

def process_subject(subid, study_dir, intermediate, quiet=True, debug=False):
    """
    Wrapper for the process_osipi_subject.py script which processes a single 
    OSIPI subject's data.
    """
    # create process_osipi_subject.py call
    cmd = ["fslpython", "./process_osipi_subject.py",
           "--study_dir", str(study_dir),
           "--subid", str(subid),
           "--intermediate", intermediate]
    if quiet:
        cmd.append("--quiet")
    if debug:
        cmd.append("--debug")
    # print the process_osipi_subject.py call to be run for sanity checking
    print(" ".join(cmd))
    # process the subject's data using the process_osipi_subject.py script
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
    parser.add_argument("--quiet",
                        help="If provided, the pipeline won't print as much infomation "
                            +"on what the pipeline is doing to the command line.",
                        action="store_true")
    parser.add_argument("--debug",
                        help="If provided, the pipeline will retain intermediate "
                            +"for inpsection. If not, only the files required for "
                            +"OSIPI submission will be retained.",
                        action="store_true")
    args = parser.parse_args()

    # data directories
    # these are expected to be in the format 
    # $OsipiDir/Challenge_Data/{Population_based, synthetic}/rawdata
    # as provided for the OSIPI ASL Challenge 
    osipi_dir = Path(args.challenge_dir).resolve(strict=True)
    population_dir = (osipi_dir/"Population_based").resolve(strict=True)
    synthetic_dir = (osipi_dir/"synthetic").resolve(strict=True)

    # list of subject IDs and their corresponding study directory
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

    # iterate over subjects running the process_osipi_subject.py 
    # pipeline on them
    for subid, study_dir in subjects:
        process_subject(subid=subid,
                        study_dir=study_dir,
                        intermediate=args.intermediate,
                        quiet=args.quiet,
                        debug=args.debug)