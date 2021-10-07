import subprocess
import argparse
from pathlib import Path
import shutil
import time
import logging
import numpy as np
import nibabel as nb

IAFS = ["diff", "tc", "ct"]
DATASETS = {
    "population": {"sequence": "2D PCASL",
                   "bsupp": {"npulses": 2, "efficiency": 0.95},
                   "te": 10.4,
                   "tr_asl": 4.8,
                   "tr_m0": 10,
                   "pld": 2.025,
                   "slicedt": 0.0437647,
                   "bolus": 1.65,
                   "rpts": 30,
                   "iaf": "ct"},
    "synthetic": {"sequence": "3D PCASL",
                  "bsupp": False,
                  "te": 10.4,
                  "tr_asl": 4.8,
                  "tr_m0": 10,
                  "pld": 1.8,
                  "slicedt": False,
                  "bolus": 1.8,
                  "rpts": 30,
                  "iaf": "ct"}
}
SUBJECTS = {"sub-PopulationAverage": "population",
            "sub-DRO1": "synthetic",
            "sub-DRO2": "synthetic",
            "sub-DRO3": "synthetic",
            "sub-DRO4": "synthetic",
            "sub-DRO5": "synthetic",
            "sub-DRO6": "synthetic",
            "sub-DRO7": "synthetic",
            "sub-DRO8": "synthetic",
            "sub-DRO9": "synthetic"}

def masked_std(image_name, mask_name):
    # load image and mask
    image = nb.load(image_name)
    mask = nb.load(mask_name)

    # set values to NaN outside of mask
    nanned_image = np.where(mask.get_fdata()==1, image.get_fdata(), np.nan)

    return np.nanstd(nanned_image)

def run_cmd(subid, cmd, shell=False):
    logger = logging.getLogger(subid)
    logger.info(" ".join(cmd))
    if shell:
        cmd = " ".join(cmd)
    process = subprocess.Popen(cmd, shell=shell, stdout=subprocess.PIPE)
    while 1:
        retcode = process.poll()
        line = process.stdout.readline().decode("utf-8")
        logger.info(line)
        if line == "" and retcode is not None:
            break
    if retcode != 0:
        logger.info(f"retcode={retcode}")
        logger.exception("Process failed.")

def imcp_wrapper(name1, name2):
    imcp_cmd = ["imcp", str(name1), str(name2)]
    run_cmd(imcp_cmd)

def process_subject(study_dir, subid, intermediate_dir="", spatial=True, verbose=False, debug=False):
    #############################################################################
    ############################## general set up ###############################
    #############################################################################
    # get pipeline start time
    start_time = time.time()

    # check subject's directory exists in `study_dir`
    study_dir = Path(study_dir).resolve(strict=True)
    rawdata_dir = (study_dir/"rawdata").resolve(strict=True)
    sub_dir = (rawdata_dir/f"{subid}").resolve(strict=True)
    
    # create processing results directory for main results
    results_dir = study_dir/"processing"/intermediate_dir/subid
    results_dir.mkdir(exist_ok=True, parents=True)

    # set up logger
    logger_name = results_dir/f"{subid}.log"
    logger = logging.getLogger(subid)
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(message)s')
    fh = logging.FileHandler(logger_name, mode="w")
    handlers = [fh, ]
    if verbose:
        sh = logging.StreamHandler()
        handlers.append(sh)
    for handler in handlers:
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    # check `anat` and `perf` directories exist
    logger.info("Checking `anat` and `perf` directories exist.")
    anat_dir = (sub_dir/"anat").resolve(strict=True)
    perf_dir = (sub_dir/"perf").resolve(strict=True)

    # find subject's images
    logger.info("Checking necessary images exist.")
    t1 = (anat_dir/f"{subid}_T1w.nii.gz").resolve(strict=True)
    asl = (perf_dir/f"{subid}_asl.nii.gz").resolve(strict=True)
    m0 = (perf_dir/f"{subid}_m0scan.nii.gz").resolve(strict=True)

    # Create subdirectory for intermediate steps to house
    # data not specified in the submission guidelines.
    # Required data will later be copied from here into 
    # the parent directory.
    # TODO: Is there a BIDS convention for naming this kind of folder?
    intermediate_dir = results_dir/"intermediate_results"
    intermediate_dir.mkdir(exist_ok=True)

    # some of the subject's ASL images have NaNs. Use fslmaths to convert
    # NaNs in the ASL images to 0, otherwise BET fails in oxford_asl run
    logger.info("Converting any NaNs in the ASL image to 0.")
    asl_nonan = intermediate_dir/f"{subid}_asl_nonan.nii.gz"
    fslmaths_cmd = ["fslmaths",
                    str(asl),
                    "-nan",
                    str(asl_nonan)]
    run_cmd(subid, fslmaths_cmd)

    # if debug mode is enabled, also produce a mask of where the NaN 
    # values are in the ASL image for inspection
    if debug:
        logger.info("Producing a mask which is 1 at locations where the ASL image has NaNs.")
        asl_nanmask = intermediate_dir/f"{subid}_asl_nanmask.nii.gz"
        fslmaths_cmd = ["fslmaths",
                        str(asl),
                        "-nanm",
                        str(asl_nanmask)]
        run_cmd(subid, fslmaths_cmd)

    # get scan parameters
    scan_type = SUBJECTS[subid]
    params = DATASETS[scan_type]

    #############################################################################
    ################################ fsl_anat section ###########################
    #############################################################################
    # get start time
    logger.info("Running fsl_anat.")
    fsl_anat_start = time.time()
    
    # create fsl_anat command
    fsl_anat_out = intermediate_dir/f"{subid}_T1w"
    fsl_anat_cmd = ["fsl_anat",
                    "-i", str(t1),
                    "-o", str(fsl_anat_out),
                    "--clobber",
                    "--nosubcortseg"]
    
    # if dealing with population data, we don't want robust FoV 
    # cropping in fsl_anat
    if scan_type is "population":
        fsl_anat_cmd.append("--nocrop")

    # run fsl_anat command
    run_cmd(subid, fsl_anat_cmd)

    # get fsl_anat run time
    fsl_anat_end = time.time()
    logger.info(f"fsl_anat completed in {(fsl_anat_end-fsl_anat_start)/60:2f} minutes.")
    
    # append '.anat' to fsl_anat output directory name
    fsl_anat_out = fsl_anat_out.with_suffix(".anat")

    #############################################################################
    ################################ oxford_asl section #########################
    #############################################################################
    # create oxford_asl call
    oxford_asl_out = intermediate_dir/"OxfordASL"
    oxford_asl_cmd = ["oxford_asl",
                      "-i", str(asl_nonan),
                      "-o", str(oxford_asl_out),
                      "--casl",
                      "--mc",
                      f"--iaf={params['iaf']}",
                      f"--bolus={params['bolus']}",
                      "--fixbolus",
                      f"--fslanat={str(fsl_anat_out)}",
                      "-c", str(m0),
                      f"--tr={params['tr_m0']}",
                      "--cmethod=voxel",
                      f"--te={params['te']}",
                      f"--tis={params['bolus'] + params['pld']}",
                      f"--rpts={params['rpts']}",
                      "--pvcorr"]

    # if debug mode enabled, retain intermediate oxford_asl results
    if debug:
        oxford_asl_cmd.append("--debug")

    # if slicedt is in scan parameters, account for slice 
    # timing in oxford_asl
    if params['slicedt']:
        oxford_asl_cmd.append(f"--slicedt={params['slicedt']}")

    # if bsupp is in scan parameters, account for efficiency 
    # of background suppression inversion recovery pulses in 
    # oxford_asl, using assumed efficiency of 95% for each 
    # pulse
    if params['bsupp']:
        nbsupp, efficiency = params["bsupp"].values()
        oxford_asl_cmd.append(f"--alpha={0.85*(efficiency**nbsupp)}")
    
    # if not using spatial mode, turn this off in oxford_asl 
    # as it's enabled by default
    if not spatial:
        oxford_asl_cmd.append("--spatial=off")
    
    # print oxford_asl command to terminal and get start time
    logger.info("Running oxford_asl.")
    oxford_asl_start = time.time()
    
    # run oxford_asl command
    run_cmd(subid, oxford_asl_cmd, shell=True)

    # print oxford_asl run time
    oxford_asl_end = time.time()
    logger.info(f"oxford_asl completed in {(oxford_asl_end-oxford_asl_start)/60:2f} minutes.")
    
    #############################################################################
    ############################## clean up section #############################
    #############################################################################
    logger.info("Getting files into format expected for OSIPI submission.")

    ### non partial volume corrected results
    # move perfusion_calib to location expected for submission to OSIPI
    logger.info("Copying non-partial volume corrected results to expected locations.")
    native_dir = oxford_asl_out/"native_space"
    perfusion_calib = native_dir/"perfusion_calib.nii.gz"
    imcp_wrapper(perfusion_calib, results_dir/"CBF.nii.gz")

    # get GM and WM masks and move to expected location
    gm_mask, wm_mask = [native_dir/f"{t}_roi.nii.gz" for t in ("gm", "wm")]
    for mask_src, tissue in zip((gm_mask, wm_mask), ("GM", "WM")):
        imcp_wrapper(mask_src, results_dir/f"{tissue}_mask_lowres.nii.gz")

    # names of mean ROI estimates
    gm_mean, wm_mean = [native_dir/f"perfusion_calib_{t}_mean.txt" for t in ("gm", "wm")]

    # calculate standard deviation within tissue mask and write mean and std to file
    for t_mean, t_mask, t in zip((gm_mean, wm_mean), (gm_mask, wm_mask), ("GM", "WM")):
        echo_cmd = ["echo",  f"\"$(cat {str(t_mean)})\"",  ">", str(results_dir/f"{t}_CBF.txt")]
        run_cmd(subid, echo_cmd, shell=True)
        std_cmd = ["echo", f"\"$(fslstats {str(perfusion_calib)} -k {str(t_mask)} -S)\"", ">>", str(results_dir/f"{t}_CBF.txt")]
        run_cmd(subid, std_cmd, shell=True)
    
    ### partial volume corrected results
    # move partial volume corrected GM and WM perfusion estimates
    logger.info("Copying partial volume corrected results and partial volume estimates to expected locations.")
    pvcorr_dir = native_dir/"pvcorr"
    pgm_perfusion_calib = pvcorr_dir/"perfusion_calib.nii.gz"
    imcp_wrapper(pgm_perfusion_calib, results_dir/"CBF_GMpv.nii.gz")
    pwm_perfusion_calib = pvcorr_dir/"perfusion_wm_calib.nii.gz"
    imcp_wrapper(pwm_perfusion_calib, results_dir/"CBF_WMpv.nii.gz")

    # move T1w space PVEs
    gm_pve, wm_pve = [fsl_anat_out/f"T1_fast_pve_{n}" for n in (0, 1)]
    for pve, t in zip((gm_pve, wm_pve), ("GM", "WM")):
        imcp_wrapper(pve, results_dir/f"{t}_pv.nii.gz")

    # calculate standard deviation within tissue mask and write mean and std to file
    pgm_mean, pwm_mean = [native_dir/f"perfusion_{t}_mean.txt" for t in ("calib_gm", "wm_calib_wm")]
    for t_perf, t_mean, t_mask, t in zip((pgm_perfusion_calib, pwm_perfusion_calib), (pgm_mean, pwm_mean), (gm_mask, wm_mask), ("GM", "WM")):
        echo_cmd = ["echo",  f"\"$(cat {str(t_mean)})\"",  ">", str(results_dir/f"{t}_CBF.txt")]
        run_cmd(subid, echo_cmd, shell=True)
        std_cmd = ["echo", f"\"$(fslstats {str(t_perf)} -k {str(t_mask)} -S)\"", ">>", str(results_dir/f"{t}pv_CBF.txt")]
        run_cmd(subid, std_cmd, shell=True)

    # if not in debug mode, delete intermediate_results directory
    if not debug:
        logger.info("Cleaning up intermediate files.")
        shutil.rmtree(intermediate_dir)

    # end of processing pipeline!
    end_time = time.time()
    logger.info(f"Processing completed! Time taken = {(end_time - start_time)/60:2f} minutes.")

if __name__ == '__main__':
    # argument handling
    parser = argparse.ArgumentParser(description="Process a single subject for the OSIPI ASL Challenge submission.")
    parser.add_argument("--study_dir",
                        help="Path to the study's base directory.",
                        required=True)
    parser.add_argument("--subid",
                        help="Subject id, for example sub-DROx or sub-PopulationAverage.",
                        required=True,
                        choices=SUBJECTS.keys())
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
    
    # parse arguments
    args = parser.parse_args()
    process_subject(study_dir=args.study_dir,
                    subid=args.subid,
                    intermediate_dir=args.intermediate,
                    spatial=not args.nospatial,
                    verbose=args.verbose,
                    debug=args.debug)