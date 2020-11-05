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

# tis_config = make_tis_config_and_generate_test_vector_files()
# with open("tis.config", "w") as file:
#     print("3. Generate the tis.config file and test vector files.")
#     file.write(string_of_json(tis_config))

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
