CXX=clang++
CXXFLAGS=-std=gnu++11 -Wall -O3

.PHONY: all
all: birthday_attack

birthday_attack: birthday_attack.cpp hash.cpp
	$(CXX) $(CXXFLAGS) -o $@ $?

.PHONY: clean
clean:
	rm -f birthday_attack
