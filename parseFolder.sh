#!/bin/bash

PATHTOREAD=$1

python parseDocx.py $PATHTOREAD
python parsePdf.py $PATHTOREAD
python parseEmail_html.py $PATHTOREAD
python parseEmail_txt.py $PATHTOREAD
