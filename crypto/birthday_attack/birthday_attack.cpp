#include <cstddef>
#include <cstdint>
#include <iostream>
#include <random>

#include "hash.hpp"


int main(int argc, char const *argv[]) {
    std::cout << "Attempting birthday attack ..." << std::endl;

    std::random_device rd;
    uint64_t x0 = rd();

    std::cout << "Trying to find cycle with x0 = " << std::hex << x0 << " ..." << std::endl;

    uint64_t y = x0;
    uint64_t z = x0;
    size_t i = 0;

    do {
        i++;
        y = prf(y);
        z = prf(prf(z));
    } while(y != z);

    std::cout << "Found cycle in iteration " << std::dec << i << " with hash value " << std::hex << y << std::endl;
    std::cout << "Now trying to recover collision ..." << std::endl;

    z = y;
    y = x0;

    for(size_t j = 0; j < i; j++) {
        uint64_t h_y = prf(y);
        uint64_t h_z = prf(z);
        if(h_y == h_z) {
            std::cout << "Found collision: H(" << std::hex << y << ") = H(" << std::hex << z << ") = " << std::hex << h_y << std::endl;
            return 0;
        }
        y = h_y;
        z = h_z;
    }

    return 1;
}
