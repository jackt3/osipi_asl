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
	&& curl https://fsl.fmrib.ox.ac.uk/fsldownloads/fslinstaller.py -o fslinstaller.py\
	&& echo "Changing permissions for fslinstaller" \
	&& chmod 755 fslinstaller.py \
	&& echo "Running fslinstaller" \
	&& echo "please ignore the 'failed to download miniconda' error coming soon" \
	&& su -c "python2.7 fslinstaller.py -V 6.0.5 -d /osipi/fsl -q" \
	&& echo "Setting FSLDIR environment variable" \
	&& export FSLDIR=/osipi/fsl \
	&& echo "retrying miniconda install ..." \
	&& /osipi/fsl/etc/fslconf/post_install.sh \
	&& mkdir -p /etc/fsl \
	&& echo "FSLDIR=/osipi/fsl; . \${FSLDIR}/etc/fslconf/fsl.sh; PATH=\${FSLDIR}/bin:\${PATH}; export FSLDIR PATH" > /etc/fsl/fsl.sh

