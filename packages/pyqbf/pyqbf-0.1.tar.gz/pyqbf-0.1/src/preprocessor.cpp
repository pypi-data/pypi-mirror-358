#include <dlfcn.h>
#include <vector>
#include <algorithm>
#include "preprocessor.hpp"
#include "parser.hpp"


namespace pyqbf{

    bloqqer::bloqqer(){
        bloqqer_reset();
    }

    void bloqqer::load(PCNF& f){
        bloqqer_init(f.nv(), f.clauses_.size());
        preprocessor::load(f);    
    }

    void bloqqer::quant(int v){
        bloqqer_decl_var(v);
    }
    void bloqqer::add(int l){
        bloqqer_add(l);
    }

    int bloqqer::solve(){
        if(this->qratTracing)        
            pyqbf_bloqqer_open_qrat(this->trace.c_str());
        
        int result = bloqqer_preprocess();
        if(this->qratTracing)
            pyqbf_bloqqer_close_qrat();

        return result;
    }

    static void bloqqer_iter_scope_callback(int v, void* target){
        PCNF* formula = (PCNF*)target;
        formula->prefix_.append(v);
        formula->nv_ = std::max(formula->nv_, v);
    }

    static bool bloqqer_iter_scope_clause_ended = true;    //utility variable for iterating over clauses
    static void bloqqer_iter_lit_callback(int v, void* target){
        PCNF* formula = (PCNF*)target;
        if(bloqqer_iter_scope_clause_ended){
            formula->clauses_.append(nb::list());
            bloqqer_iter_scope_clause_ended = false;
        }
        
        if(v == 0)
            bloqqer_iter_scope_clause_ended = true;        
        else{
            nb::list clause = formula->clauses_[formula->clauses_.size() - 1];
            clause.append(nb::int_(v));
        }
    }

    void bloqqer::get_formula(PCNF& f)
    {       
        pyqbf_bloqqer_iter_scopes(bloqqer_iter_scope_callback, &f);
        bloqqer_iter_scope_clause_ended = true;
        pyqbf_bloqqer_iter_clauses(bloqqer_iter_lit_callback, &f);
    }

    void bloqqer::set_qrat(std::string filename){
        // bloqqer_set_option((char*)("--qrat=" + filename).c_str());
        this->trace = filename;
        this->qratTracing = true;
    }
}