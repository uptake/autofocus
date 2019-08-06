#!/bin/bash

# guarantee script exits with non-zero code
# the first time any of these commands fail
set -e

# Find this file's directory
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
$DIR/common_checks.sh

pytest tests/test_package
