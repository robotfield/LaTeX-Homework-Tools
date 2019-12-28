#! /bin/bash

LINES=$(cat .genlatex_project_info | wc -l)

if [ $LINES -eq 0 ]
then
	>&2 echo "Please write the name of the main file in '.genlatex_project_info'."
	exit 1
fi

MAIN=$(head -n 1 .genlatex_project_info)

echo -n "Starting or Waiting for Change..."

while true
do
	
	MD5=$(find -L . -name "*.tex" -exec cat {} \; | md5sum | awk '{print $1}')
	# echo $MD5
	
	CHANGED=true
	
	if [ $LINES -eq 2 ]
	then
		OLD_MD5=$(tail -n 1 .genlatex_project_info)
		if [ "$OLD_MD5" = "$MD5" ]
		then
			CHANGED=false
			# echo "No changes"
		else
			echo -e "$MAIN\n$MD5" > .genlatex_project_info
		fi
	else
		echo -e "$MAIN\n$MD5" > .genlatex_project_info
	fi
	
	if $CHANGED
	then
		echo -ne "\033[0K\r"
		echo -ne  "                                                            "
		echo -ne "\033[0K\r"
		if pdflatex -interaction nonstopmode -no-file-line-error $MAIN > pdflatex.log
		then 
			echo -n "Compiled successfully as of" $(date)
		else
			echo "$MAIN" > .genlatex_project_info
			echo -n "Errors encountered. Check 'pdflatex.log' for more detail."
		fi
		# echo "Recompiled."
	fi
	
	sleep 1
done
