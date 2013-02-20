#!/bin/bash
DIR="~/Desktop/ECG/data"
txt_files=$(ls ~/Desktop/ECG/data/*.txt)

for txt_file in $txt_files
do
	echo $txt_file
	python ~/Desktop/ECG/applescript/DICOM_Constructor.py $txt_file
done

