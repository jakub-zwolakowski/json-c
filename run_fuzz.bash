#!/bin/bash

let nb_of_tests=`ls trustinsoft/fuzz_inputs/ | wc -l`

echo "Number of tests = ${nb_of_tests}"

num_processes=11

seq ${nb_of_tests} | xargs -P ${num_processes} -L 1 -I'SELECT' bash -c \
  "echo \"Test SELECT RUNNING...\"; \
   TIS_ADVANCED_FLOAT=1 \
   tis-analyzer \
     --interpreter \
     -info-json-results fuzz_test_SELECT.json \
     -tis-config-load fuzz.tis.config \
     -tis-config-select SELECT \
     > fuzz_test_SELECT.log; \
   echo \"Test SELECT DONE!\";"
