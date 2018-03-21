#include <cstddef>

#include "hash.hpp"


/*
 * Example hash function we want to find collisions for.
 */
uint64_t prf(uint64_t x) {
    uint64_t shifts[] = {13,37,9,12,25,18,3,49};
    uint64_t y = x;
    uint64_t z = 0xecc9d62ede0e3ddd;
    for(size_t i = 0; i < 8; i++) {
        y = y^z;
        z = (((z+y)<<shifts[i])|((z+y)>>(64-shifts[i])));
    }
    return y^z;
}
