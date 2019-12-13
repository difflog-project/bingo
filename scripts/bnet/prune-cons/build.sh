#!/usr/bin/env bash

set -e

g++ -std=c++11 -O3 -march=native -Wall -Wextra -Werror prune-cons.cpp -o prune-cons
g++ -std=c++11 -O3 -march=native -Wall -Wextra -Werror prune-cons-unopt.cpp -o prune-cons-unopt
# clang++ -std=c++11 -g -Wall -Wextra -Werror prune-cons.cpp -o prune-cons
