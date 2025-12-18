#!/bin/bash

echo "HelloWorld"

tot_file_num=910265
loop_num=1
std_year=$1   
DATA_PATH="/usr/share/d_ollama"
src_path=$DATA_PATH"/data/src/"$std_year"_src_2324"
excel_path=$DATA_PATH"/data/src/"$std_year"_excel_2324/"

echo $std_year
cd $src_path


tot_file_num=`ls -al | wc -l`

for file in ./*.py
do
	dir_path=$(dirname $file)/
	name=$(basename $file)
	ex=".csv"
	old_nm="complexipy"
	new_nm="${name%.*}"

	new_file="./$new_nm$ex"
	old_file="./$old_nm$ex"
	
	complexipy `echo $file` -l file -o
	mv `echo $old_file` `echo $new_file`
	cp `echo $new_file` `echo $excel_path`
	\rm `echo $new_file`
	
	loop_num=$[$loop_num+1]
	left_file_num=$[$tot_file_num-$loop_num]


	echo "============================================="
	echo "total file number : "$tot_file_num
	echo "left file number : "$left_file_num
	echo "============================================="
done	
