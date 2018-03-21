# Birthday Attack

Implementation of the birthday attack against hash functions, according to https://www.cs.umd.edu/~jkatz/imc/hash-erratum.pdf

This is a C++ implementation (for performance reasons and compatibility), which can find collisions for 64-bit pseudorandom functions.


## Usage

Provide the targeted hash function in file `hash.cpp`, following the simple interface described in `hash.hpp` (see `hash.sample.cpp` for an example). Then just run `make` and execute `./birthday_attack` afterwards.
