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
COPY process_synthetic.py Code/process_synthetic.py

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