#pragma once 

#include <iostream>
#include <iterator>
#include <unordered_map>
#include <nanobind/nanobind.h>
#include "defs.hpp"
#include "pcnf.hpp"
#include "solver.hpp"

namespace pyqbf {

    class SolverManager{
        int next_id = 1;
        std::unordered_map<int, std::shared_ptr<solver>> solvers;
        public:
            ~SolverManager();
            int add(std::shared_ptr<solver> solver);
            void remove(int);
            std::shared_ptr<solver> get_solver(int);
    };
}