FROM brainlife/fsl:6.0.4

WORKDIR /osipi
COPY process_osipi_all.py process_osipi_all.py
COPY process_osipi_subject.py process_osipi_subject.py
RUN apt-get install -y bc

RUN echo "Downloading anaconda..." \
    && wget https://repo.continuum.io/archive/Anaconda3-5.0.1-Linux-x86_64.sh \
    && chmod 755 Anaconda3-5.0.1-Linux-x86_64.sh \
    && echo "Installing anaconda..." \
    && bash Anaconda3-5.0.1-Linux-x86_64.sh -b -p /osipi/conda \
    && rm Anaconda3-5.0.1-Linux-x86_64.sh 
    
ENV PATH /osipi/conda/bin:$PATH
    
RUN echo "Creating environment for quantiphyse" \
    && conda create -n qp python=3.7  \
    && echo "conda activate qp" > ~/.bashrc \
    && echo "Installing quantiphyse" \
    && pip install quantiphyse

ENTRYPOINT ["fslpython"]
CMD ["-c", "print('This Docker image can be used to run 2 Python scripts via fslpython: process_osipi_all.py and process_osipi_subject.py. See the documentation for more info.')"]
