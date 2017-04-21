#!/bin/bash

CONDA_DIR=$PWD/conda
export PATH=$CONDA_DIR/bin:$PATH

TARGET=litex.boards.targets.sim
CMD=$(python -c "import $TARGET; print($TARGET.__file__)")

$CMD
