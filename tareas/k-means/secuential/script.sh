#!/bin/bash
rm o.o
g++ -std=c++11 kmeans.cpp -o o.o

#$k="\n"

for i in {1..10}
do
	./o.o datos.csv 5 20 #centroides.csv #>> salida.csv
	#echo $k
done
