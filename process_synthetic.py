import subprocess

import argparse

from pathlib import Path

import time

IAFS = ["diff", "tc", "ct"]

def process_subject(study_dir, subid, iaf, intermediate_dir="", verbose=False):
    if verbose:
        print("Running the pipeline in verbose mode.")
        start_time = time.time()

    # check subject's directory exists in `study_dir`
    if verbose:
        print("Checking study and subject directories exist.")
    study_dir = Path(study_dir).resolve(strict=True)
    rawdata_dir = (study_dir/"rawdata").resolve(strict=True)
    sub_dir = (rawdata_dir/subid).resolve(strict=True)

    # check `anat` and `perf` directories exist
    if verbose:
        print("Checking `anat` and `perf` directories exist.")
    anat_dir = (sub_dir/"anat").resolve(strict=True)
    perf_dir = (sub_dir/"perf").resolve(strict=True)

    # find subject's images
    if verbose:
        print("Checking necessary images exist.")
    t1 = (anat_dir/f"{subid}_T1w.nii.gz").resolve(strict=True)
    asl = (perf_dir/f"{subid}_asl.nii.gz").resolve(strict=True)
    m0 = (perf_dir/f"{subid}_m0scan.nii.gz").resolve(strict=True)

    # check `iaf` is an allowed type
    if iaf not in IAFS:
        raise ValueError(f"Provided `iaf` ({iaf}) is not an allowed type: {IAFS}.")
    
    # create processing results directory for main results
    if verbose:
        print("Creating results directories.")
    results_dir = study_dir/"processing"/intermediate_dir/subid
    results_dir.mkdir(exist_ok=True, parents=True)

    # Create subdirectory for intermediate steps to house
    # data not specified in the submission guidelines.
    # Required data will later be copied from here into 
    # the parent directory.
    # TODO: Is there a BIDS convention for naming this kind of folder?
    intermediate_dir = results_dir/"intermediate_results"
    intermediate_dir.mkdir(exist_ok=True)

    # run fsl_anat on structural image
    if verbose:
        print("Running fsl_anat.")
        fsl_anat_start = time.time()
    fsl_anat_out = intermediate_dir/f"{subid}_T1w"
    fsl_anat_cmd = ["fsl_anat", "-i", str(t1), "-o", str(fsl_anat_out), "--clobber", "--nosubcortseg"]
    if verbose:
        print(" ".join(fsl_anat_cmd))
    subprocess.run(fsl_anat_cmd, check=True)
    if verbose:
        fsl_anat_end = time.time()
        print(f"fsl_anat completed in {(fsl_anat_end-fsl_anat_start)/60:2f} minutes.")
    fsl_anat_out = fsl_anat_out.with_suffix(".anat")
    
    # run oxford_asl
    oxford_asl_out = intermediate_dir/"OxfordASL"
    oxford_asl_cmd = ["oxford_asl",
                      "-i", str(asl),
                      "-o", str(oxford_asl_out),
                      "--mc",
                      f"--iaf={iaf}",
                      "--bolus=1.8", "--fixbolus",
                      f"--fslanat={str(fsl_anat_out)}",
                    #   "--senscorr",
                      "-c", str(m0), "--tr=10", "--cmethod=voxel",
                      "--te=10.4",
                      "--tis=1.8",
                      "--pvcorr"
    ]
    oxford_asl_cmd = " ".join(oxford_asl_cmd)
    if verbose:
        print("Running oxford_asl.")
        print(oxford_asl_cmd)
        oxford_asl_start = time.time()
    subprocess.run(oxford_asl_cmd, shell=True)
    if verbose:
        oxford_asl_end = time.time()
        print(f"oxford_asl completed in {(oxford_asl_end-oxford_asl_start)/60:2f} minutes.")
    
    # move files to locations expected for submission to OSIPI

    # end of processing pipeline!
    if verbose:
        end_time = time.time()
        print(f"Processing completed! Time taken = {(end_time - start_time)/60:2f} minutes.")

if __name__ == '__main__':
    # argument handling
    parser = argparse.ArgumentParser(description="Processing script for OSIPI ASL Challenge submission.")
    parser.add_argument("--study_dir",
                        help="Path to the study's base directory.",
                        required=True)
    parser.add_argument("--subid",
                        help="Subject id, for example sub-DROx.",
                        required=True)
    parser.add_argument("--iaf",
                        help="Type of input ASL images.",
                        required=True,
                        choices=IAFS)
    parser.add_argument("--intermediate",
                        help="Provide the name of an intermediate results directory. "
                            +"By providing a different value for this argument on each "
                            +"run you can avoid overwriting the results from other runs.",
                        default="")
    parser.add_argument("--verbose",
                        help="If provided, the pipeline will print out statements on "
                            +"what the pipeline is doing.",
                        action="store_true")
    
    # parse arguments
    args = parser.parse_args()
    process_subject(study_dir=args.study_dir,
                    subid=args.subid,
                    iaf=args.iaf,
                    intermediate_dir=args.intermediate,
                    verbose=args.verbose)