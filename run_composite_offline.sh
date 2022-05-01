#!/bin/bash

###############################################################################
## Sample script for running SPECjbb2015 in Composite mode.
## 
## This sample script demonstrates launching the Controller, TxInjector and 
## Backend in a single JVM.
###############################################################################

# Launch command: java [options] -jar specjbb2015.jar [argument] [value] ...

# Benchmark options (-Dproperty=value to override the default and property file value)
# Please add -Dspecjbb.controller.host=$CTRL_IP (this host IP) and -Dspecjbb.time.server=true
# when launching Composite mode in virtual environment with Time Server located on the native host.
SPEC_OPTS=""

# Java options for Composite JVM
JAVA_OPTS=""

# Optional arguments for the Composite mode (-l <num>, -p <file>, -skipReport, etc.)
MODE_ARGS=""

# Number of successive runs
NUM_OF_RUNS=1

###############################################################################
# This benchmark requires a JDK7 compliant Java VM.  If such a JVM is not on
# your path already you must set the JAVA environment variable to point to
# where the 'java' executable can be found.
#
# If you are using a JDK9 (or later) Java VM, see the FAQ at:
#                       https://spec.org/jbb2015/docs/faq.html
# and the Known Issues document at:
#                       https://spec.org/jbb2015/docs/knownissues.html
###############################################################################

# 改一下java环境
JAVA=/usr/bin/java

which $JAVA > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "ERROR: Could not find a 'java' executable. Please set the JAVA environment variable or update the PATH."
    exit 1
fi

for ((n=1; $n<=$NUM_OF_RUNS; n=$n+1)); do

  # Create result directory                
  timestamp=$(date '+%y-%m-%d_%H%M%S')
  result=./offline_$timestamp
  echo $result
  mkdir -p $result/config

  # Copy current config to the result directory
  cp -r /home/changzhihao.czh/ali-online/config_offline/* $result/config/

  cd $result

  echo "Run $n: $timestamp"
  echo "Launching SPECjbb2015 in Composite mode..."
  # echo

  echo "Start Composite JVM"
  # numactl --physcpubind=0-95 $JAVA $JAVA_OPTS $SPEC_OPTS -jar specjbb2015.jar -m COMPOSITE $MODE_ARGS 2>composite.log > composite.out &
  $JAVA $JAVA_OPTS $SPEC_OPTS -jar /home/changzhihao.czh/ali-online/specjbb2015.jar -m COMPOSITE $MODE_ARGS 2>composite.log > composite.out &

    COMPOSITE_PID=$!
    echo "Composite JVM PID = $COMPOSITE_PID"
    echo "$COMPOSITE_PID" >> ../offline_PID_LOG
  echo 
  # sleep 3

  # echo
  # echo "SPECjbb2015 is running..."
  # echo "Please monitor $result/controller.out for progress"

  # wait $COMPOSITE_PID
  # echo
  # echo "Composite JVM has stopped"

  # echo "SPECjbb2015 has finished"
  # echo

 cd ..

done

exit 0
