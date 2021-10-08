FROM brainlife/fsl:6.0.4

WORKDIR /osipi
COPY process_osipi_all.py process_osipi_all.py
COPY process_osipi_subject.py process_osipi_subject.py
RUN apt-get install -y bc

ENTRYPOINT ["fslpython"]
CMD ["-c", "print('This Docker image can be used to run 2 Python scripts via fslpython: process_osipi_all.py and process_osipi_subject.py. See the documentation for more info.')"]