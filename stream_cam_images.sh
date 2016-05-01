#!/bin/bash

for i in {1..1000} ; 
do
	echo $i
	raspistill --nopreview -w 256 -h 256 -t 100 -o ./$i.jpg
	#scp $i.jpg adriennetran@192.168.1.199:/Users/adriennetran/Dropbox/2016coding/flask-video-stream/
	scp $i.jpg ybarhomi@192.168.1.180:/media/images/
done
