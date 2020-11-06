#! /usr/bin/env python3

# This script regenerates TrustInSoft CI configuration.

# Run from the root of the JSON-C project:
# $ python3 trustinsoft/regenerate.py

import re # sub
import json # dumps, load
import os # path, makedirs
import binascii # hexlify
import shutil # copyfileobj
import glob # iglob

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
def make_simple_copy_file(filename):
    return (
        {
            "src": os.path.join(build_dir, filename),
            "dst": os.path.join("trustinsoft", "build", filename),
        }
    )

files_to_copy = [
    make_simple_copy_file("apps_config.h"),
    make_simple_copy_file("config.h"),
    make_simple_copy_file("json_config.h"),
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
    elts = []
    for opt_prefix in options: # e.g. opt_prefix == "-D"
        for opt_value in options[opt_prefix]: # e.g. opt_value == "HAVE_OPEN"
            elts.append(opt_prefix + opt_value) # e.g. "-DHAVE_OPEN"
    return " ".join(elts)

def make_common_config():
    # C files.
    c_files = (
        sorted(glob.iglob("*.c", recursive=False)) +
        [ os.path.join("tests", "parse_flags.c") ]
    )
    # Compilation options.
    compilation_cmd = (
        {
            "-I": [
                os.path.join("build"),
                "..",
                os.path.join("..", "tests"),
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
            "test": "test1",
            "formatted": False,
        },
        {
            "test": "test1",
            "formatted": True,
            "args": [ "plain" ],
        },
        {
            "test": "test1",
            "formatted": True,
            "args": [ "pretty" ],
        },
        {
            "test": "test1",
            "formatted": True,
            "args": [ "spaced" ],
        },
        {
            "test": "test1",
            "formatted": True,
            "args": [ "spaced", "pretty" ],
        },
        {
            "test": "test1",
            "formatted": True,
            "args": [ "spaced", "pretty", "pretty_tab" ],
        },
        {
            "test": "test2",
            "formatted": False,
        },
        {
            "test": "test2",
            "formatted": True,
            "args": [ "plain" ],
        },
        {
            "test": "test2",
            "formatted": True,
            "args": [ "pretty" ],
        },
        {
            "test": "test2",
            "formatted": True,
            "args": [ "spaced" ],
        },
        {
            "test": "test2",
            "formatted": True,
            "args": [ "spaced", "pretty" ],
        },
        {
            "test": "test2",
            "formatted": True,
            "args": [ "spaced", "pretty", "pretty_tab" ],
        },
        { "test": "test4" },
        { "test": "test_cast" },
        { "test": "test_charcase" },
        { "test": "test_compare" },
        { "test": "test_deep_copy" },
        { "test": "test_double_serializer" },
        { "test": "test_float" },
        { "test": "test_int_add" },
        { "test": "test_json_pointer" },
        { "test": "test_locale" },
        { "test": "test_null" },
        {
            "test": "test_object_iterator",
            "args": [ "." ],
        },
        { "test": "test_parse" },
        { "test": "test_parse_int64" },
        { "test": "test_printbuf" },
        { "test": "testReplaceExisting" },
        { "test": "test_set_serializer" },
        { "test": "test_set_value" },
        {
            "test": "test_util_file",
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
        { "test": "test_visit" },
        { "fuzz": "0-10058b8cd9" },
        { "fuzz": "0-4735d351ed" },
        { "fuzz": "0-638577393e" },
        { "fuzz": "1-8e3702d59d" },
        { "fuzz": "1-fb0eb4ff8c" },
    ]
)

fuzz_input_dir = os.path.join("trustinsoft", "fuzz_inputs")

def make_test(test):
    if "test" in test:
        name_elts = [ test["test"] ]
        if "formatted" in test:
            if test["formatted"]:
                name_elts.append("formatted")
            if "args" in test:
                name_elts += test["args"]
        name = " ".join(name_elts)

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

        tis_test["files"] = [ os.path.join("tests", test["test"] + ".c") ]

        if "filesystem" in test:
            tis_test["filesystem"] = test["filesystem"]

        if "args" in test:
            tis_test["val-args"] = " " + " ".join(test["args"])

        return tis_test

    if "fuzz" in test:
        fuzz_filename = test["fuzz"] + ".json"
        tis_test = (
            {
                "name": ("test_fuzz input " + fuzz_filename),
                "include": common_config_path,
                "files": [
                     os.path.join("trustinsoft", "test_fuzz.c")
                ],
                "filesystem": {
                    "files": [
                        {
                            "from": os.path.join(fuzz_input_dir, fuzz_filename),
                            "name": "test.json"
                        }
                    ]
                },
                "val-args": " test.json"
            }
        )

        return tis_test

tis_config = list(map(make_test, tests))
with open("tis.config", "w") as file:
    print("3. Generate the tis.config file and test vector files.")
    file.write(string_of_json(tis_config))

# --------------------------------------------------------------------------- #
# ------------------------------ COPY .h FILES ------------------------------ #
# --------------------------------------------------------------------------- #

print("5. Copy generated files.")
for file in files_to_copy:
    with open(file['src'], 'r') as f_src:
        os.makedirs(os.path.dirname(file['dst']), exist_ok=True)
        with open(file['dst'], 'w') as f_dst:
            print("   > Copy '%s' to '%s'." % (file['src'], file['dst']))
            shutil.copyfileobj(f_src, f_dst)
