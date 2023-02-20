#!/bin/bash
VENV="/home/$USER/path/to/venv_dir/py37-o3dbpp-pct"
ACTIVATE_VENV="${VENV}/bin/activate"


echo "Activate the Virtual Environment for O3DBPP-PTC"
echo "==============================================="

if [ -d "$VENV" ]; then
    echo "venv exists => activate it"
    source "$ACTIVATE_VENV"
    echo "venv is activated (type \`deactivate\` to deactivate the venv)"

else
    echo "check your venv directory ($VENV)"

fi


