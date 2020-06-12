
fuzz_json_inputs=`ls tis/fuzz_inputs/`

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
    "compilation_database": [
      "tis/build"
    ],
    "compilation_cmd": " -I . -I tis/build",
    "files": [
      "tis/test_fuzz.c",
      "json_c_version.c",
      "json_util.c",
      "printbuf.c",
      "json_tokener.c",
      "json_object.c",
      "linkhash.c",
      "strerror_override.c",
      "arraylist.c",
      "json_object_iterator.c",
      "json_visit.c",
      "json_pointer.c"
    ],
    "filesystem": {
      "files": [
        {
          "from": "tis/fuzz_inputs/${fuzz_json_input}",
          "name": "./test.json"
        }
      ]
    },
    "raw_options": {
      "-val-args": " ./test.json"
    }
EOF

done

echo "  }"

echo "]"
