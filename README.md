# osipi_asl
This repository contains pipelines which carry out analysis for the OSIPI ASL Challenge 2021.

The OSIPI ASL Challenge 2021 dataset consists of 1 Population-Averaged subject and 9 synthetic subjects.
An extensive description of the dataset can be found in [1], [2].
The pipelines assume the data will be in the form as provided by the OSIPI ASL Challenge 2021:

```
OsipiDir
|
└───Challenge_Data
    |
    │   README.md
    └───Population_based
    |   |
    |   └───rawdata
    |       |   README
    |       |   dataset_description.json
    |       |
    |       └───sub-PopulationAverage
    |           └───anat
    |           |   |   sub-PopulationAverage_T1w.json
    |           |   |   sub-PopulationAverage_T1w.nii.gz
    |           |
    |           └───perf
    |               |   sub-PopulationAverage_asl.json
    |               |   sub-PopulationAverage_asl.nii.gz
    |               |   sub-PopulationAverage_aslcontext.tsv
    |               |   sub-PopulationAverage_m0scan.json
    |               |   sub-PopulationAverage_m0scan.nii.gz
    └───synthetic
        |
        └───rawdata
            |   README
            |   dataset_description.json
            |
            └───sub-DRO1
            |   └───anat
            |   |   |   sub-DRO1_T1w.json
            |   |   |   sub-DRO1_T1w.nii.gz
            |   |
            |   └───perf
            |       |   sub-DRO1_asl.json
            |       |   sub-DRO1_asl.nii.gz
            |       |   sub-DRO1_aslcontext.tsv
            |       |   sub-DRO1_m0scan.json
            |       |   sub-DRO1_m0scan.nii.gz
            .
            .
            .
            |
            |
            └───sub-DRO9
                └───anat
                |   |   sub-DRO9_T1w.json
                |   |   sub-DRO9_T1w.nii.gz
                |
                └───perf
                    |   sub-DRO9_asl.json
                    |   sub-DRO9_asl.nii.gz
                    |   sub-DRO9_aslcontext.tsv
                    |   sub-DRO9_m0scan.json
                    |   sub-DRO9_m0scan.nii.gz
```

### Collaborators
In alphabetical order: Jack Toner, Jian Hu

# Pipelines
There are 2 processing pipelines in this repository:

## process_osipi_subject.py
* This script performs the analysis of a single OSIPI subject's data.

* The `process_osipi_subject.py` script has the following arguments:

    Argument          |  Type          |  Description
    ------------------|----------------|---------------
    `--study_dir`     | string         | Study directory within the OSIPI Challenge_Data directory, i.e. `$OsipiDir/Challenge_Data/${synthetic, Population_based}`
    `--subid`         | string         | Subject ID, i.e. `sub-DRO1`
    `--intermediate`  | string         | Create an intermediate results directory, i.e. store results in `$OsipiDir/Challenge_Data/$Study/$IntermediateDir/$subid`
    `--quiet`         | bool           | Don't ouput print statements to the terminal
    `--debug`         | bool           | Retain all intermediate results

## process_osipi_all.py
* This script runs `process_osipi_subject.py` on each subject in the OSIPI ASL Challenge.

* The `process_osipi_all.py` script has the following arguments:

    Argument          |  Type          |  Description
    ------------------|----------------|---------------
    `--challenge_dir` | string         | Challenge directory within the OSIPI directory, i.e. `$OsipiDir/Challenge_Data`. Should contain the `synthetic` and `Population_based` subdirectories as provided as part of the OSIPI ASL Challenge.
    `--intermediate`  | string         | Create an intermediate results directory in which to save the results from each subject, i.e. store results in `$OsipiDir/Challenge_Data/$Study/$IntermediateDir/$subid`
    `--quiet`         | bool           | Don't ouput print statements to the terminal
    `--debug`         | bool           | Retain all intermediate results

# Docker Installation
## Getting docker image from dockerhub
We have installed the scripts and all of their dependencies in a docker image to make running them and reproducing our results as simple as possible.
There are only a couple of steps needed to install the docker image:

* Install Docker: https://docs.docker.com/engine/installation/
* Get the latest version of the docker image: 
> docker pull jacktonermhcn/osipi:latest

You now have a docker image containing our 2 processing pipelines!

## Running via docker image
It is simple to run each of the processing pipelines via the docker image.
The call to `process_osipi_all.py` can be used to process all of the OSIPI subjects' data with the user only having to provide the path to `$OsipiDir` on their local machine as described below.
The call to `process_osipi_subject.py` can be used to process a single OSIPI subject's data with the user substituting `${Study}` for `Population_based` or `synthetic` as described below as well as specifying `$OsipiDir` and `${subid}`.
This is the recommended way to run the pipeline as it ensures the same OS and versions of tools will be used.

### Mounting the data directory
In the command below, `-v $OsipiDir/Challenge_Data:/osipi/Challenge_Data` can be seen.
Users will need to substitute `$OsipiDir` for the path to the directory on their local machine which contains the `Challenge_Data` directory like in the directory structure above.
The second part after the colon should not be changed. This command mounts the `$OsipiDir/Challenge_Data` directory on the user's local machine to the `/osipi/Challenge_Data` directory within the Docker container.

### Specifying the study directory and subject ID
If using the `processing_osipi_subject.py` script directly, the user will also need to provide the study directory (`--study_dir Challenge_Data/${Study}`) and subject ID (`--subid ${subid}`).
This is the path to the study directory within the container and users should simply substitute `${Study}` for `Population_based` or `synthetic` as appropriate.
Users should substitute `${subid}` for the subject's ID, e.g., `sub-DRO1`.

* process_osipi_all.py:

        docker run --rm \
        -v $OsipiDir/Challenge_Data:/osipi/Challenge_Data \ # share `Challenge_Data` directory on the
                                                          \ # host with the docker container
        -t jacktonermhcn/osipi:latest \ # name of the docker image you want to run
        process_osipi_all.py \ # run the pipeline on all the OSIPI subjects
        --challenge_dir Challenge_Data \ # location of the challenge directory within the container

* process_osipi_subject.py:

        docker run --rm \
        -v $OsipiDir/Challenge_Data:/osipi/Challenge_Data \ # share `Challenge_Data` directory on the host
                                                        \ # with the docker container
        -t jacktonermhcn/osipi:latest \ # name of the docker image you want to run
        process_osipi_subject.py \ # run the single-subject processing pipeline
        --study_dir Challenge_Data/${Study} \ # location of the study directory within the container
        --subid ${subid} # Subject ID

    * The results of the pipeline should be found at `$OsipiDir/Challenge_Data/$Study/$subid`.


# Native Installation
The pipeline relies on FSL v6.0.4.
Installation instructions for FSL can be found [here](https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/FslInstallation).
In short, users will be guided to download an installation script, `fslinstaller.py`.
Users can specify which version of FSL to install when running the script using the `-V` option: the user should install FSL 6.0.4.

The results from running the pipeline this way may differ from OS to OS and if different versions of backend tools are installed.
The `$FSLDIR` environment variable should be set and `$FSLDIR/bin` should be on `$PATH`.

## Running Natively
To run the pipeline natively, FSL should be installed and all environment variables set as above.
The `fslpython` environment can then be used to run the pipelines as follows.
The user should substitute `$CodeDir` for the parent directory of the processing scripts and `$OsipiDir` for the base OSIPI data directory as illustrated above.
If using the `process_osipi_subject.py` script, the user should also substitute `${Study}` for `Population_based` or `synthetic` according to the subject whose data they want to process.
`${subid}` should also be substituted for the subject's ID, e.g., `sub-DRO1`.

    fslpython $CodeDir/process_osipi_subject.py \ # run the single-subject processing pipeline
    --study_dir $OsipiDir/Challenge_Data/${Study} \ # location of the study directory
    --subid ${subid} # Subject ID

    fslpython $CodeDir/process_osipi_all.py \ # run the pipeline on all the OSIPI subjects
    --challenge_dir $OsipiDir/Challenge_Data \ # location of the challenge directory within the container


# References
[1]: Anazodo et al., ‘The Open Source Initiative for Perfusion Imaging (OSIPI) ASL MRI Challenge’, Proc. ISMRM., 2021

[2]: Anazodo, U. & Croal, P.L., “OSIPI ASL MRI Challenge (2021)”, OSF, 2021, 
https://doi.org/10.17605/OSF.IO/6XYU3