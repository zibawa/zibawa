#!/bin/bash
localhostenabled=(3000 5671 5672 8083 8086 8096 15672)
anyenabled=(80 443 8883)

for i in "${localhostenabled[@]}"
do
	sudo ufw allow from 127.0.0.1 to any port $i
	echo $i
done 

for i in "${anyenabled[@]}"
do
	sudo ufw allow $i
done
