#!/bin/bash

let nb_of_tests=`ls tis/fuzz_inputs/ | wc -l`

echo "Number of tests = ${nb_of_tests}"

num_processes=11

seq ${nb_of_tests} | xargs -P ${num_processes} -L 1 -I'SELECT' bash -c \
  "echo \"Test SELECT RUNNING...\"; \
   tis-analyzer \
     --interpreter \
     -info-json-results fuzz_test_SELECT.json \
     -tis-config-load fuzz.tis.config \
     -tis-config-select SELECT \
     > fuzz_test_SELECT.log; \
   echo \"Test SELECT DONE!\";"


# First stab at parallelization: better than nothing.

# for select in `seq 1 ${nb_of_tests}`
# do
#   ((i=i%num_processes)); ((i++==0)) && wait
#   echo "Test $select RUNNING..."
#   tis-analyzer \
#     --interpreter \
#     -info-json-results fuzz_test_${select}.json \
#     -tis-config-load fuzz.tis.config \
#     -tis-config-select ${select} \
#     > fuzz_test_${select}.log \
#     && echo "Test $select DONE!" &
# done


# Trying to use GNU parallel, without success.

# for select in `seq 1 ${nb_of_tests}`
# do
#   sem -j+0 \
#     "echo \"Test $select RUNNING...\"; \
#     tis-analyzer \
#       --interpreter \
#       -info-json-results fuzz_test_${select}.json \
#       -tis-config-load fuzz.tis.config \
#       -tis-config-select ${select} \
#       > fuzz_test_${select}.log; \
#       echo \"Test $select DONE!\";"
# done
# sem --wait
