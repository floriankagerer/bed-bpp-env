#!/bin/bash
VENV="/home/$USER/path/to/venv_dir/bed-bpp"
ACTIVATE_VENV="${VENV}/bin/activate"

echo "Activate the Virtual Environment for BED-BPP Environment"
echo "========================================================"

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
ROOT_DIR_REPO="${SCRIPT_DIR}/code"

if [ -d "$VENV" ]; then
    echo "venv exists => activate it"
    source "$ACTIVATE_VENV"
    echo "venv is activated (type \`deactivate\` to deactivate the venv)"
    # check whether pythonpath contains repo_dir/code/ folder
    if [[ "$PYTHONPATH" != *"$ROOT_DIR_REPO"* ]]; then
        echo "PYTHONPATH = ${PYTHONPATH}"
        echo "append \"${ROOT_DIR_REPO}\" to PYTHONPATH"
        export PYTHONPATH=$PYTHONPATH:$ROOT_DIR_REPO
        echo "PYTHONPATH = ${PYTHONPATH}"
    fi
    
else
    echo "check your venv directory ($VENV)"

fi
