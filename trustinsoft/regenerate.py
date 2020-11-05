#! /usr/bin/env python3

# This script regenerates TrustInSoft CI configuration.

# Run from the root of the JSON-C project:
# $ python3 trustinsoft/regenerate.py

import re # sub
import json # dumps, load
import os # path, makedirs
import binascii # hexlify
import shutil # copyfileobj

# Outputting JSON.
def string_of_json(obj):
    # Output standard pretty-printed JSON (RFC 7159) with 4-space indentation.
    s = json.dumps(obj, indent=4)
    # Sometimes we need to have multiple "include" fields in the outputted
    # JSON, which is unfortunately impossible in the internal python
    # representation (OK, it is technically possible, but too cumbersome to
    # bother implementing it here), so we can name these fields 'include_',
    # 'include__', etc, and they are all converted to 'include' before
    # outputting as JSON.
    s = re.sub(r'"include_+"', '"include"', s)
    return s

build_dir = "build"

# Generated files which need to be a part of the repository.
files_to_copy = [
    {
        "src": os.path.join(build_dir, "apps_config.h"),
        "dst": os.path.join("trustinsoft", "build", "apps_config.h"),
    },
    {
        "src": os.path.join(build_dir, "config.h"),
        "dst": os.path.join("trustinsoft", "build", "config.h"),
    },
    {
        "src": os.path.join(build_dir, "json_config.h"),
        "dst": os.path.join("trustinsoft", "build", "json_config.h"),
    },
]

# --------------------------------------------------------------------------- #
# ---------------------------------- CHECKS --------------------------------- #
# --------------------------------------------------------------------------- #

def check_dir(dir):
    if os.path.isdir(dir):
        print("   > OK! Directory '%s' exists." % dir)
    else:
        exit("Directory '%s' not found." % dir)

def check_file(file):
    if os.path.isfile(file):
        print("   > OK! File '%s' exists." % file)
    else:
        exit("File '%s' not found." % file)

# Initial check.
print("1. Check if needed directories and files exist...")
check_dir("trustinsoft")
check_dir(build_dir)
for file in files_to_copy:
    check_file(file['src'])

# --------------------------------------------------------------------------- #
# -------------------- GENERATE trustinsoft/common.config ------------------- #
# --------------------------------------------------------------------------- #

common_config_path = os.path.join("trustinsoft", "common.config")

def string_of_options(options):
    s = ''
    beginning = True
    for option_prefix in options:
        for option_val in options[option_prefix]:
            if beginning:
                beginning = False # No need for a separator at the beginning.
            else:
                s += ' '
            s += option_prefix + option_val
    return s

def make_common_config():
    # C files.
    c_files = [
        "arraylist.c",
        "json_c_version.c",
        "json_object_iterator.c",
        "json_object.c",
        "json_pointer.c",
        "json_tokener.c",
        "json_util.c",
        "json_visit.c",
        "linkhash.c",
        "printbuf.c",
        "strerror_override.c",
        "tests/parse_flags.c",
    ]
    # Compilation options.
    compilation_cmd = (
        {
            "-I": [
                "..",
                os.path.join("..", "tests"),
                os.path.join("build"),
            ],
            "-D": [],
            "-U": [],
        }
    )
    # Whole common.config JSON.
    return {
        "files": list(map(lambda file: os.path.join("..", file), c_files)),
        "compilation_cmd": string_of_options(compilation_cmd),
        "val-printf-singleton-pointers": True,
        "val-int-for-pointer-equality": [ "-1", "-2" ],
        "safe-arrays": False,
    }

common_config = make_common_config()
with open(common_config_path, "w") as file:
    print("2. Generate the 'trustinsoft/common.config' file.")
    file.write(string_of_json(common_config))

# --------------------------------------------------------------------------- #
# -------------------------------- tis.config ------------------------------- #
# --------------------------------------------------------------------------- #

tests = (
    [
        {
            "name": "test1", # test1
            "formatted": False,
        },
        {
            "name": "test1", # test1Formatted_plain
            "formatted": True,
            "args": [ "plain" ],
        },
        {
            "name": "test1", # test1Formatted_pretty
            "formatted": True,
            "args": [ "pretty" ],
        },
        {
            "name": "test1", # test1Formatted_spaced
            "formatted": True,
            "args": [ "spaced" ],
        },
        {
            "name": "test1", # test1Formatted_spaced_pretty
            "formatted": True,
            "args": [ "spaced", "pretty" ],
        },
        {
            "name": "test1", # test1Formatted_spaced_pretty_pretty_tab
            "formatted": True,
            "args": [ "spaced", "pretty", "pretty_tab" ],
        },
        {
            "name": "test2", # test2
            "formatted": False,
        },
        {
            "name": "test2", # test2Formatted_plain
            "formatted": True,
            "args": [ "plain" ],
        },
        {
            "name": "test2", # test2Formatted_pretty
            "formatted": True,
            "args": [ "pretty" ],
        },
        {
            "name": "test2", # test2Formatted_spaced
            "formatted": True,
            "args": [ "spaced" ],
        },
        {
            "name": "test2", # test2Formatted_spaced_pretty
            "formatted": True,
            "args": [ "spaced", "pretty" ],
        },
        {
            "name": "test2", # test2Formatted_spaced_pretty_pretty_tab
            "formatted": True,
            "args": [ "spaced", "pretty", "pretty_tab" ],
        },
        { "name": "test4" },
        { "name": "test_cast" },
        { "name": "test_charcase" },
        { "name": "test_compare" },
        { "name": "test_deep_copy" },
        { "name": "test_double_serializer" },
        { "name": "test_float" },
        { "name": "test_int_add" },
        { "name": "test_json_pointer" },
        { "name": "test_locale" },
        { "name": "test_null" },
        {
            "name": "test_object_iterator",
            "args": [ "." ],
        },
        { "name": "test_parse" },
        { "name": "test_parse_int64" },
        { "name": "test_printbuf" },
        { "name": "testReplaceExisting" },
        { "name": "test_set_serializer" },
        { "name": "test_set_value" },
        {
            "name": "test_util_file",
            "args": [ "." ],
            "filesystem": {
                "files": [
                    {
                        "from": "tests/valid.json",
                        "name": "./valid.json"
                    },
                    {
                        "from": "tests/valid_nested.json",
                        "name": "./valid_nested.json"
                    },
                    {
                        "name": "/dev/null"
                    },
                ],
            },
        },
        { "name": "test_visit" },
        {
            "fuzz": "0-10058b8cd9"
        },
        {
            "fuzz": "0-4735d351ed"
        },
        {
            "fuzz": "0-638577393e"
        },
        {
            "fuzz": "1-8e3702d59d"
        },
        {
            "fuzz": "1-fb0eb4ff8c"
        },
    ]
)

def make_test(test):
    if "name" in test:
        name = test["name"]
        if "formatted" in test and test["formatted"]:
            name = test["name"] + ("_".join(["Formatted"] + test["args"]))

        tis_test = (
            {
                "name": name,
                "include": common_config_path,

            }
        )

        if "formatted" in test:
            if test["formatted"]:
                compilation_cmd = { "-D": [ "TEST_FORMATTED" ] }
            else:
                compilation_cmd = { "-U": [ "TEST_FORMATTED" ] }
            tis_test["compilation_cmd"] = string_of_options(compilation_cmd)


        tis_test["files"] = [ os.path.join("tests", test["name"] + ".c") ]

        if "filesystem" in test:
            tis_test["filesystem"] = test["filesystem"]


        if "args" in test:
            tis_test["val-args"] = " " + " ".join(test["args"])

        return tis_test

    if "fuzz" in test:
        tis_test = (
            {
                "name": ("test_fuzz input %s.json" % test["fuzz"]),
                "include": "trustinsoft/common.config",
                "files": [
                    "trustinsoft/test_fuzz.c"
                ],
                "filesystem": {
                    "files": [
                        {
                            "from": ("trustinsoft/fuzz_inputs/%s.json" % test["fuzz"]),
                            "name": "./test.json"
                        }
                    ]
                },
                "val-args": " ./test.json"
            }
        )

        return tis_test

tis_config = list(map(make_test, tests))
with open("tis.config", "w") as file:
    print("3. Generate the tis.config file and test vector files.")
    file.write(string_of_json(tis_config))

# ---------------------------------------------------------------------------- #
# ------------------------------ COPY .h FILES ------------------------------- #
# ---------------------------------------------------------------------------- #

print("5. Copy generated files.")
for file in files_to_copy:
    with open(file['src'], 'r') as f_src:
        os.makedirs(os.path.dirname(file['dst']), exist_ok=True)
        with open(file['dst'], 'w') as f_dst:
            print("   > Copy '%s' to '%s'." % (file['src'], file['dst']))
            shutil.copyfileobj(f_src, f_dst)
