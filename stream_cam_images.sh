#!/bin/bash

sven_address=ybarhomi@192.168.1.180
adrienne_address=adriennetrain@192.168.1.199

for i in {1..1000} ; 
do
	DATE=$(date +"%Y-%m-%d_%H_%M_%S")
	echo $i
	raspistill --nopreview -w 256 -h 256 -t 100 -o ./$DATE.jpg
	#scp $DATE.jpg $adrienne_address:/Users/adriennetran/Dropbox/2016coding/flask-video-stream/
	scp $DATE.jpg $sven_address:/media/images/
done
