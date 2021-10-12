# osipi_asl
This repository contains pipelines which carry out analysis for the OSIPI ASL Challenge 2021.

The OSIPI ASL Challenge 2021 dataset consists of 1 Population-Averaged subject and 9 synthetic subjects.
An extensive description of the dataset can be found in [1], [2].

### Collaborators
In alphabetical order: Jack Toner, Jian Hu, Xin Zhang

# Pipelines
There are 2 processing pipelines in this repository:

## process_osipi_subject.py
* This script performs the analysis of a single OSIPI subject's data.

* The `process_osipi_subject.py` script has the following arguments:

    Argument          |  Type          |  Description
    ------------------|----------------|---------------
    `--study_dir`     | string         | Study directory within the OSIPI Challenge_Data directory, i.e. `$OsipiDir/Challenge_Data/${synthetic, Population_based}`
    `--subid`         | string         | Subject ID, i.e. `sub-DRO1`
    `--intermediate`  | string         | Create an intermediate results directory, i.e. store results in `$PWD/Challenge_Data/$Study/$IntermediateDir/$subid`
    `--nospatial`     | bool           | Turn off spatial prior in `oxford_asl`
    `--quiet`         | bool           | Don't ouput print statements to the terminal
    `--debug`         | bool           | Retain all intermediate results

## process_osipi_all.py
* This script runs `process_osipi_subject.py` on each subject in the OSIPI ASL Challenge.

* The `process_osipi_all.py` script has the following arguments:

    Argument          |  Type          |  Description
    ------------------|----------------|---------------
    `--challenge_dir` | string         | Challenge directory within the OSIPI directory, i.e. `$OsipiDir/Challenge_Data`. Should contain the `synthetic` and `Population_based` subdirectories as provided as part of the OSIPI ASL Challenge.
    `--intermediate`  | string         | Create an intermediate results directory in which to save the results from each subject, i.e. store results in `$PWD/Challenge_Data/$Study/$IntermediateDir/$subid`
    `--nospatial`     | bool           | Turn off spatial prior in `oxford_asl`
    `--quiet`         | bool           | Don't ouput print statements to the terminal
    `--debug`         | bool           | Retain all intermediate results

# Docker Installation
## Getting docker image from dockerhub
We have installed the pipeline and all of its dependencies in a docker image to make running it and reproducing our results as simple as possible.
There are only a couple of steps needed to run the docker image:

* Install Docker: https://docs.docker.com/engine/installation/
* Get the latest version of the docker image: 
> docker pull jacktonermhcn/osipi:latest

You now have a docker image containing our 2 processing pipelines!

## Running via docker image
It is simple to run each of the processing pipelines via the docker image.
* process_osipi_subject.py:

        docker run --rm \
        -v $PWD/Challenge_Data:/osipi/Challenge_Data \ # share `Challenge_Data` directory on the host
                                                        \ # with the docker container
        -t jacktoner/osipi:latest \ # name of the docker image you want to run
        process_osipi_subject.py \ # run the single-subject processing pipeline
        --study_dir Challenge_Data/${Study} \ # location of the study directory within the container
        --subid ${subid} # Subject ID

    * The results of the pipeline should be found at `$PWD/Challenge_Data/$Study/$subid`.
* process_osipi_all.py:

        docker run --rm \
        -v $PWD/Challenge_Data:/osipi/Challenge_Data \ # share `Challenge_Data` directory on the host
                                                        \ # with the docker container
        -t jacktoner/osipi:latest \ # name of the docker image you want to run
        process_osipi_all.py \ # run the pipeline on all the OSIPI subjects
        --challenge_dir Challenge_Data \ # location of the challenge directory within the container

# Native Installation
The pipeline relies on FSL v6.0.4.
Installation instructions for that can be found [here](https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/FslInstallation).
The results from running the pipeline this way may differ from OS to OS and if different versions of backend tools are installed.

## Running Natively
To run the pipeline natively, FSL should be installed and all environment variables set as expected.
The `fslpython` environment can then be used to run the pipelines as follows:

    fslpython $PWD/process_osipi_subject.py \ # run the single-subject processing pipeline
    --study_dir $OsipiDir/Challenge_Data/${Study} \ # location of the study directory
    --subid ${subid} # Subject ID

    fslpython $PWD/process_osipi_all.py \ # run the pipeline on all the OSIPI subjects
    --challenge_dir $OsipiDir/Challenge_Data \ # location of the challenge directory within the container


# References
[1]: Anazodo et al., ‘The Open Source Initiative for Perfusion Imaging (OSIPI) ASL MRI Challenge’, Proc. ISMRM., 2021

[2]: Anazodo, U. & Croal, P.L., “OSIPI ASL MRI Challenge (2021)”, OSF, 2021, 
https://doi.org/10.17605/OSF.IO/6XYU3