#!/bin/bash

# Threshold values to test
thresholds=(0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 0.9)

for t in "${thresholds[@]}"; do
    echo "Running with threshold $t"
    python main_LOSO_RF.py "$t"
done
