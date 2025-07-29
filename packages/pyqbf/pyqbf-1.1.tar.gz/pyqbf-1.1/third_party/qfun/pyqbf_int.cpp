#include <CLI11.hpp>
#include "qtypes.h"
#include "litset.h"
#include "rareqs.h"
#include "aig.h"
#include "options.h"
#include "pyqbf_int.h"

/*-------------------------------Prefix-------------------------------*/
void* pyqbf_qfun_create_prefix(){
    return new Prefix();
}

void pyqbf_qfun_prefix_add_quant(void* ptr, int value){
    if(value == 0)
        return;
    Prefix* prefix = (Prefix*)ptr;
    QuantifierType quant_type = value < 0 ? QuantifierType::UNIVERSAL : QuantifierType::EXISTENTIAL;
    if(prefix->size() == 0 || prefix->back().first != quant_type){
        VarVector varvec;
        varvec.push_back((Minisat::Var)(abs(value)));
        prefix->emplace_back(quant_type, varvec);
    }
    else
        prefix->back().second.push_back(abs(value));
}

void pyqbf_qfun_destroy_prefix(void* ptr){
    delete (Prefix*)ptr;
}

/*-------------------------------CNF-------------------------------*/
void* pyqbf_qfun_create_cnf(){
    return new CNF();
}

void pyqbf_qfun_cnf_add(void* ptr, vector<int>* clause){
    CNF* cnf = (CNF*)ptr;
    std::vector<Lit> qfun_clause;
    for(int lit : *clause)
        qfun_clause.push_back(Minisat::mkLit(abs(lit), lit < 0));
    cnf->push_back(LitSet::mk(qfun_clause));
}

void pyqbf_qfun_destroy_cnf(void* ptr){
    delete (CNF*)ptr;
}



/*-------------------------------Solver-------------------------------*/
static void block_move(const Move& wm, Rareqs* ps) {
    LiteralVector blocking_clause;
    for (Var v : ps->get_free()) {
        const lbool vv = qfun::eval(v, wm);
        if (vv == l_Undef) continue;
        blocking_clause.push_back(vv == l_False ? mkLit(v) : ~mkLit(v));
    }
    LitSet blc = LitSet::mk(blocking_clause);
    ps->strengthen(blc);
}

static int run_solver(const Options& options,Rareqs* ps) {
    const bool w=ps->wins();
    const bool r=(ps->quantifier_type()==EXISTENTIAL) == w;
    if (w) {
        Move wm;
        while (1) {
            wm.clear();
            ps->get_move(wm);
            if (!options.get_win_mv_enum()) break;
            block_move(wm, ps);
            if (!ps->wins()) 
                break;            
        }
    }
    return r ? 10 : 20;
}

static void build_options(CLI::App& app, Options& options)
{
    app.add_option("file_name", options.file_name,
                   "Input file name, use - (dash) or empty for stdin.")
        ->default_val("-");
    app.add_flag("-a, !--no-a", options.accum, "Accumulate strategies.")
        ->default_val(true);
    app.add_flag("-c, !--no-c", options.cyclic, "Cyclic magic function.")
        ->default_val(true);
    app.add_flag("-p, !--no-p", options.proximity, "Use proximity.")
        ->default_val(true);
    app.add_flag("-r, !--no-r", options.rndmodel, "Randomize models.")
        ->default_val(false);
    app.add_flag("-s, !--no-s", options.sample, "Initial sampling.")
        ->default_val(true);
    app.add_flag("-l, !--no-l", options.learn, "Use learning.")
        ->default_val(true);
    app.add_flag("-E, !--no-enum", options.win_mv_enum,
                 "Enumerated winning moves for top-level.")
        ->default_val(false);
    app.add_option("-S, --seed", options.seed, "Random seed.")->default_val(7);
    app.add_option("-b, --blocking", options.blocking,
                   "Clause blocking for quant levels <LEV>.")
        ->default_val(7);
    app.add_option("-i, --interval", options.interval, "Learning interval.")
        ->default_val(64);
    app.add_option("-n, --initial", options.initial,
                   "Initial refinement for quant levels <LEV>.")
        ->default_val(4);
    app.add_flag("-v", options.verbose, "Add verbosity.")->default_val(0);
}

bool pyqbf_qfun_solve(void* prefix_ptr, void* clause_ptr)
{
    Prefix* prefix = (Prefix*)prefix_ptr;
    CNF* clauses = (CNF*)clause_ptr;
    // prepare nonexpert options (simulate as if input was received from stdout)
    const int nargc = 7;
    char* nargv[nargc];
    nargv[0] = strdup("-");
    nargv[1] = strdup("-caps");
    nargv[2] = strdup("-i64");
    nargv[3] = strdup("-n4");
    nargv[4] = strdup("-b4");
    nargv[5] = strdup("-S4");
    nargv[6] = strdup("-");
    Options options;
    CLI::App app("qfun non-CNF QBF solver.");
    build_options(app, options);
    CLI11_PARSE(app, nargc, nargv);

    AigFactory factory;
    AigUtil au(factory);
    QAigFla qf;
    qf.pref = *prefix;
    qf.matrix = au.convert(*clauses);  
    
    auto ps = Rareqs::make_solver(options, factory, qf.pref, qf.matrix);
    int result = run_solver(options, ps);
    
    return result == 10;
}