#!/bin/bash

# guarantee script exits with non-zero code
# the first time any of these commands fail
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
$DIR/common_checks.sh

pytest
