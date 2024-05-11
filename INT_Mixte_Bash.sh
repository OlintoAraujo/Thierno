#!/bin/bash

#cd /home/tbn/Desktop/INT_Network_2023
cd /home/tbn/Desktop/paper_2022/2023/INT_Mixte

# Store the arguments in variables
path=$1
nodes=$2
items=$3
monitoring=$4
flows=($5)
percent=$6
min_capacity=$7
max_capacity=$8

# Create a folder to store the log files
mkdir -p Solution/logs/$2_$3_$4_$7_$8
log_folder=Solution/logs/$2_$3_$4_$7_$8

# Loop to run the script multiple times
for i in "${!flows[@]}"; do
    # Start a new detached screen session and run the python script
    screen -d -m sh -c "python3.7 INT_Mixte_1.py $path $nodes $items $monitoring ${flows[i]} $percent $min_capacity $max_capacity | tee ${log_folder}/INT_Mixte_$2_$3_$4_${flows[i]}_$6.log"
done


#chmox +x INT_Mixte_Bash.sh
#./INT_Mixte_Bash.sh [path to network] [number nodes] [number items] [number monitoring application] "[50 10 150 200]" [percentage of given flows] [min_capacity] [max_capacity]
#./INT_Mixte_Bash.sh ./INT_Mixte_Bash.sh Data/Barabasi_Network_50_2_2023.csv 50 8 4 "30 40 50" 100 2 8





