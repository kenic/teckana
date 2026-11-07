#!/bin/sh
set -eu
cd "$(dirname "$0")"
xcrun clang -O2 -Wall -Wextra -fobjc-arc -Wno-deprecated-declarations \
  -framework Foundation mecabra_candidates.m -o mecabra_candidates
