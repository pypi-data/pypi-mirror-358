#include <vector>
using namespace std;

/*-------------------------------Prefix-------------------------------*/
void* pyqbf_qfun_create_prefix();

void pyqbf_qfun_prefix_add_quant(void* ptr, int value);

void pyqbf_qfun_destroy_prefix(void* ptr);

/*-------------------------------CNF-------------------------------*/
void* pyqbf_qfun_create_cnf();

void pyqbf_qfun_cnf_add(void* ptr, vector<int>* clause);

void pyqbf_qfun_destroy_cnf(void* ptr);



/*-------------------------------Solver-------------------------------*/
bool pyqbf_qfun_solve(void* prefix_ptr, void* clause_ptr);