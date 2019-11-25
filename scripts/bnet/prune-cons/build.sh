#!/usr/bin/env bash

if [[ $HOSTNAME =~ "fir" || $HOSTNAME =~ "ae249" ]]; then
   g++ -std=c++11 -O3 -I $BASE_DIR/libs/boost_1_61_0 -march=native -Wall -Wextra -Werror prune-cons.cpp -o prune-cons
   g++ -std=c++11 -O3 -I $BASE_DIR/libs/boost_1_61_0 -march=native -Wall -Wextra -Werror prune-cons-unopt.cpp -o prune-cons-unopt
else
   g++ -std=c++11 -O3 -march=native -Wall -Wextra -Werror prune-cons.cpp -o prune-cons
   g++ -std=c++11 -O3 -march=native -Wall -Wextra -Werror prune-cons-unopt.cpp -o prune-cons-unopt
fi
# clang++ -std=c++11 -g -Wall -Wextra -Werror prune-cons.cpp -o prune-cons

exit $?
