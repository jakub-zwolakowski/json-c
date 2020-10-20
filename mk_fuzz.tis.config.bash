
fuzz_json_inputs=`ls trustinsoft/fuzz_inputs/`

echo "["

first=0

i=0
for fuzz_json_input in $fuzz_json_inputs; do

i=$((i+1))

if (test $first -eq 0); then
  first=1
else
  echo "  },"
fi

echo "  {"

cat << EOF
    "name": "test_fuzz #${i}: input ${fuzz_json_input}",
    "include": "common.config",
    "compilation_cmd": " -I . -I trustinsoft/build",
    "files": [
        "trustinsoft/test_fuzz.c"
    ],
    "filesystem": {
        "files": [
            {
                "from": "trustinsoft/fuzz_inputs/${fuzz_json_input}",
                "name": "./test.json"
            }
        ]
    },
    "val-args": " ./test.json"
EOF

done

echo "  }"

echo "]"
