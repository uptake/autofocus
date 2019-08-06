#!/bin/bash

# guarantee script exits with non-zero code
# the first time any of these commands fail
set -e

flake8 autofocus tests

black autofocus tests --check
