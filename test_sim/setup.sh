#! /bin/bash

set -x
set -e

echo ""
echo "Install modules from conda"
echo "---------------------------"
CONDA_DIR=$PWD/conda
export PATH=$CONDA_DIR/bin:$PATH
(
        if [ ! -d $CONDA_DIR ]; then
                wget -c https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh
                chmod a+x Miniconda3-latest-Linux-x86_64.sh
                ./Miniconda3-latest-Linux-x86_64.sh -p $CONDA_DIR -b
                conda config --set always_yes yes --set changeps1 no
                conda update -q conda
        fi
        conda config --add channels timvideos
)
conda install binutils-lm32-elf
conda install gcc-lm32-elf
conda install verilator

# Install litex
echo ""
echo "Install litex into conda"
echo "---------------------------"
(
	cd ..
	python setup.py install
)

pip install -e git+git://github.com/enjoy-digital/litedram.git#egg=litedram
pip install -e git+git://github.com/enjoy-digital/liteeth.git#egg=liteeth
