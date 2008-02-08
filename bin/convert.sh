#!/bin/bash

#############
# PS to PDF #
#############
#
# First, convert the ps pechas to PDF format
#
FILES="$1 $2"
STYLE=$3
USAGE="Usage: $0 filenames_prefix*[.ps] [style]"
if [[ "$FILES" == "" ]]; then
    echo $USAGE
    exit
fi

for FILE in $FILES
    do
    CHECK=`echo $FILE|grep '_odd.ps'`
    if [[ "$CHECK" != "" ]]; then
        ODD_PS=$FILE
        ODD_PDF=`echo $ODD_PS|sed -e 's/\.ps$/\.pdf/'`
        MARKED_PDF=`echo $ODD_PS|sed -e 's/\.ps$/_marked\.pdf/'`
    else
        EVEN_PS=$FILE
        EVEN_PDF=`echo $EVEN_PS|sed -e 's/\.ps$/\.pdf/'`
    fi
    echo "Processing $FILE ..."
    pstopdf $FILE -p -l
    done

################
# Crop Markers #
################
#
# After converting to PDF, we're ready to add the crop markers
#
echo "Adding crop marks to $ODD_PDF ..."
if [[ "$STYLE" == "trim" ]]; then
    python ./bin/addCropMarks.py --flip=True --style=trim $ODD_PDF
else
    python ./bin/addCropMarks.py --flip=True $ODD_PDF
fi

###################
# Merge PDF Files #
###################
#
# Merge PDF files, interleaving even and odd page
#
echo "Merging PDF files $MARKED_PDF and $EVEN_PDF ..."
python ./bin/interLeave.py $MARKED_PDF $EVEN_PDF

############
# Clean Up #
############
#
for FILE in $ODD_PDF $EVEN_PDF $MARKED_PDF
    do
    rm $FILE
    done
