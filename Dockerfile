FROM ubuntu:18.04

RUN apt-get update && apt-get upgrade -y && apt-get clean

RUN apt-get install -y \
	wget \
	g++-5 \
	git \
	cmake \
	unzip \
	bc \
	python2.7 \
	python-contextlib2 \
	libtbb-dev \
	libboost-dev \
	zlib1g-dev \
	libxt-dev \
	libexpat1-dev \
	libgstreamer1.0-dev \
	libqt4-dev \
	dc \
	sudo \
	curl

WORKDIR /osipi
COPY process_osipi_all.py process_osipi_all.py
COPY process_osipi_subject.py process_osipi_subject.py

RUN echo "Downloading fslinstaller.py" \
	&& curl https://fsl.fmrib.ox.ac.uk/fsldownloads/fslinstaller.py -o fslinstaller.py \
	&& echo "Changing permissions for fslinstaller" \
	&& chmod 755 fslinstaller.py \
	&& echo "Running fslinstaller" \
	&& mkdir /osipi/modules \
	&& su -c "python2.7 fslinstaller.py -V 6.0.5 -d /osipi/modules/fsl -e -q" \
	&& echo "Setting FSLDIR environment variable" \
	&& export FSLDIR=/osipi/modules/fsl \
	&& echo "retrying miniconda install ..." \
	&& /osipi/modules/fsl/etc/fslconf/post_install.sh \
	&& echo "FSLDIR=/osipi/modules/fsl" >> ~/.bashrc \
	&& echo "PATH=\${FSLDIR}/bin:\${PATH}" >> ~/.bashrc \
	&& echo "export FSLDIR PATH" >> ~/.bashrc

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