#include <dlfcn.h>
#include <stdlib.h>
#include <filesystem>
#include <nanobind/nanobind.h>

//depqbf
extern "C"{
    #include <pysat_qdpll_interface.h>
}

#include "solver.hpp"

#define STRINGIFY(x) #x    
#define XSTRINGIFY(x) STRINGIFY(x)
#ifdef QUAPI_PRELOAD_SO_PATH
    //Expand Makro received from CMake to quoted string
    #define STR_QUAPI_PRELOAD_SO_PATH XSTRINGIFY(QUAPI_PRELOAD_SO_PATH)
#endif
#ifdef QUAPI_CAQE_EXE_PATH
    #define STR_QUAPI_CAQE_EXE_PATH XSTRINGIFY(QUAPI_CAQE_EXE_PATH)
#endif
#ifdef QUAPI_DEPQBF_EXE_PATH
    #define STR_QUAPI_DEPQBF_EXE_PATH XSTRINGIFY(QUAPI_DEPQBF_EXE_PATH)
#endif
#ifdef QUAPI_QUTE_EXE_PATH
    #define STR_QUAPI_QUTE_EXE_PATH XSTRINGIFY(QUAPI_QUTE_EXE_PATH)
#endif
#ifdef QUAPI_RAREQS_EXE_PATH
    #define STR_QUAPI_RAREQS_EXE_PATH XSTRINGIFY(QUAPI_RAREQS_EXE_PATH)
#endif
#ifdef QUAPI_QFUN_EXE_PATH
    #define STR_QUAPI_QFUN_EXE_PATH XSTRINGIFY(QUAPI_QFUN_EXE_PATH)
#endif

#define NOT_AVAILABLE(solver, func) throw std::runtime_error("The " XSTRINGIFY(func) "-operation is not available for " XSTRINGIFY(solver) "!")


namespace pyqbf
{
    std::string quapi_scriptlocation = "";

    static bool file_exists(const char* path) {
        struct stat buffer;
        return (stat(path, &buffer) == 0);
    }

    static std::string find_fallback_path(std::string folder_prefix, std::string target){        
        std::string possible_paths[] = {
            target,
            "./" + target,
            "../" + target,
            folder_prefix + "/" + target,
            "../" + folder_prefix + "/build/" + target,
            "./" + folder_prefix + "/" + target,
            "../" + folder_prefix + "/" + target,
            "./third_party/" + folder_prefix + "/" + target,
            "~/" + folder_prefix + "/build/" + target,
            "/usr/local/lib/" + target,
            "/usr/lib/" + target
        };

        for(auto path : possible_paths)
        {
            if(file_exists(path.c_str()))
                return path;
        }
        return "";
    }
    


    /*------------------------------------------------------------------------*/
    void depqbf::qdpll_deleter::operator()(QDPLL *q) {
        qdpll_delete(q);
    }

    depqbf::depqbf()
    {
        handle.reset(qdpll_create());   
    }

    void depqbf::quant(int var) {
        if(curq_ == 0){  //No open scope
            qdpll_new_scope(handle.get(), var < 0 ? QDPLL_QTYPE_FORALL : QDPLL_QTYPE_EXISTS);
            #ifdef LOG_API_USAGE
            std::cerr << "qdpll_new_scope(" << (var < 0 ? QDPLL_QTYPE_FORALL : QDPLL_QTYPE_EXISTS) << ")" << std::endl;
            #endif
        }
        else if((curq_ < 0) != (var < 0))
        {
            qdpll_add(handle.get(), 0);         //close scope
            qdpll_new_scope(handle.get(), var < 0 ? QDPLL_QTYPE_FORALL : QDPLL_QTYPE_EXISTS);            
            #ifdef LOG_API_USAGE
            std::cerr << "qdpll_add(0)" << std::endl;
            std::cerr << "qdpll_new_scope(" << (var < 0 ? QDPLL_QTYPE_FORALL : QDPLL_QTYPE_EXISTS) << ")" << std::endl;
            #endif
        }
        curq_ = var < 0 ? -1 : 1;
        qdpll_add(handle.get(), abs(var));
        #ifdef LOG_API_USAGE
            std::cerr << "qdpll_add(" << abs(var) << ")" << std::endl;
        #endif
    }
    void depqbf::add(int l) {
        if(curq_ != 0)
        {
            qdpll_add(handle.get(), 0);         //close scope 
            #ifdef LOG_API_USAGE
                std::cerr << "qdpll_add(0)" << std::endl;
            #endif
            curq_ = 0;
        }
        qdpll_add(handle.get(), l);
        #ifdef LOG_API_USAGE
            std::cerr << "qdpll_add("<< l <<")" << std::endl;
        #endif
    }

    bool depqbf::solve()
    {
        if(this->assumptions.size() != 0){
            for(auto assumption : this->assumptions){
                qdpll_assume(handle.get(), assumption);
                #ifdef LOG_API_USAGE
                    std::cerr << "qdpll_assume(" << assumption << ")" << std::endl;
                #endif
            }
            this->assumptions.clear();
        }
        #ifdef LOG_API_USAGE
            std::cerr << "qdpll_sat()" << std::endl;
        #endif
        return qdpll_sat(handle.get()) == QDPLL_RESULT_SAT;
    }

    void depqbf::assume(int var)
    {
        if(this->is_loaded()){
            qdpll_assume(handle.get(), var);
            #ifdef LOG_API_USAGE
                std::cerr << "qdpll_assume(" << var << ")" << std::endl;
            #endif
        }
        else
            this->assumptions.push_back(var);
    }

    void depqbf::reset(){
        qdpll_reset(handle.get());
        #ifdef LOG_API_USAGE
            std::cerr << "qdpll_reset()" << std::endl;
        #endif
    }

    void depqbf::push(){
        qdpll_push(handle.get());
        #ifdef LOG_API_USAGE
            std::cerr << "qdpll_push()" << std::endl;
        #endif
    }

    void depqbf::pop(){
        qdpll_pop(handle.get());
        #ifdef LOG_API_USAGE
            std::cerr << "qdpll_pop()" << std::endl;
        #endif        
    }

    int depqbf::get_assignment(int var)
    {
        #ifdef LOG_API_USAGE
            std::cerr << "qdpll_get_value(" << var <<")" << std::endl;
        #endif
        return qdpll_get_value(handle.get(), var) * var;
    }

    void depqbf::configure(std::string configure_str)
    {
        qdpll_configure(handle.get(), (char*) configure_str.c_str());
        #ifdef LOG_API_USAGE
            std::cerr << "qdpll_configure(" << configure_str <<")" << std::endl;
        #endif
    }

    void depqbf::get_stats(std::unordered_map<std::string, int>& target){
        struct pysat_depqbf_stats stats;
        qdpll_get_stats(handle.get(), &stats);
        #ifdef LOG_API_USAGE
            std::cerr << "qdpll_get_states()" << std::endl;
        #endif
        
        target["restarts"] = stats.restarts;
		target["conflicts"] = 0; // no conflicts in qdpll algorithm
		target["decisions"] = stats.decisions;
		target["propagations"] = stats.propagations;
    }

    /*------------------------------------------------------------------------*/
    qute::qute() {}

    std::string qute::configuration_value_or_default(std::string key, std::string default_value){
        if(this->configuration.find(key) != this->configuration.end())
            return this->configuration[key];
        else
            return default_value;
    }

    bool qute::configuration_flag(std::string key) {
        return this->configuration.find(key) != this->configuration.end();
    }

    void qute::quant(int var) {
        if (var == 0 )
            return;
        if(handle)
            handle->addVariable(std::to_string(abs(var)), var < 0 ?  'a' : 'e', false); //QTYPE_FORALL='a' ,QTYPE_EXISTS='e'
        //https://github.com/fslivovsky/qute/blob/master/src/parser.cc
        //Line 128
    }

    void qute::add(int l) {
        if(!handle)
            return;

        if(l == 0){
            handle->addConstraint(tmp_clause_, Qute::ConstraintType::clauses);
            tmp_clause_.clear();
        }
        else
            tmp_clause_.push_back(Qute::mkLiteral(abs(l), l > 0));        
    }

    void qute::configure(std::string str){
        auto pos = str.find("=");
        if(pos == std::string::npos)
            this->set_configuration_value(str, "");
        else
            this->set_configuration_value(str.substr(0, pos), str.substr(pos + 1));
    }

    void qute::get_stats(std::unordered_map<std::string, int>& target){NOT_AVAILABLE(qute, get_stats); (void)target;}
    int qute::get_assignment(int v) { NOT_AVAILABLE(QuAPI, get_assignment); (void)v; return 0;}

    void qute::set_configuration_value(std::string key, std::string value) {
        this->configuration[key] = value;
    }

    bool qute::solve()
    {
        auto solver = std::make_shared<Qute::QCDCL_solver>(1e52);     
        solving = true;
        bool result = false;
        try{
            solver->options.trace = this->configuration_flag("--trace");
            solver->tracer = nullptr;
            std::unique_ptr<Qute::Tracer> tracer;
            if(solver->options.trace) {
                tracer = std::make_unique<Qute::SimpleTracer>(*solver);
                solver->tracer = tracer.get();
            }

            Qute::ConstraintDB constraint_database(*solver, 
                solver->options.trace,  //trace
                0.999,  //constraint activity decay
                std::stoi(this->configuration_value_or_default("--initial-clause-DB-size", "4000")),   //initial clause DB size
                std::stoi(this->configuration_value_or_default("--initial-term-DB-size", "500")),     //initial term DB size
                4000,   //clause DB increment
                500,    //term DB increment
                0.5,    //clause removal ratio
                0.5,    //term removal ratio
                false,  //use activity threshold
                1,      //constraint activity inc
                2       //LBD threshold
            );
            solver->constraint_database = &constraint_database;

            auto debug_helper = Qute::DebugHelper(*solver);
            solver->debug_helper = &debug_helper;

            auto variable_data_store = Qute::VariableDataStore(*solver);
            solver->variable_data_store = &variable_data_store;
            
            std::unique_ptr<Qute::DependencyManagerWatched> dependency_manager = std::make_unique<Qute::DependencyManagerWatched>(*solver, 
                "all",  //dependency learning
                "off"   //out of order decisions
            );
            
            solver->dependency_manager = dependency_manager.get();

            std::unique_ptr<Qute::DecisionHeuristic> decision_heuristic;
            std::string dependency_learning_argument = this->configuration_value_or_default("--dependency-learning", "all");
            std::string decision_heuristic_argument = this->configuration_value_or_default("--decision-heuristic", "VMTF");

            if(dependency_learning_argument == "off")
                decision_heuristic = std::make_unique<Qute::DecisionHeuristicVMTFprefix>(*solver, 
                    this->configuration_flag("--no-phase-saving")
                );
            else if(decision_heuristic_argument == "VMTF")
                decision_heuristic = std::make_unique<Qute::DecisionHeuristicVMTFdeplearn>(*solver,
                    this->configuration_flag("--no-phase-saving")
                );            
            else if (decision_heuristic_argument == "VSIDS"){
                std::string tiebreak_argument = this->configuration_value_or_default("--tiebreak", "arbitrary");
                bool tiebreak_scores = tiebreak_argument != "arbitrary";
                bool use_secondary_occurrences = tiebreak_argument == "more-secondary" || tiebreak_argument == "fewer-secondary";
                bool prefer_fewer_occurrences = tiebreak_argument == "fewer-primary" || tiebreak_argument == "fewer-secondary";
                decision_heuristic = std::make_unique<Qute::DecisionHeuristicVSIDSdeplearn>(*solver,
                    this->configuration_flag("--no-phase-saving"),
                    std::stod(this->configuration_value_or_default("--var-activity-decay", "0.95")),
                    std::stod(this->configuration_value_or_default("--var-activity-inc", "1")),                                                        
                    tiebreak_scores,
                    use_secondary_occurrences,
                    prefer_fewer_occurrences
                );
            }
            else if(decision_heuristic_argument == "SGDB")
                decision_heuristic = std::make_unique<Qute::DecisionHeuristicSGDB>(*solver,
                    this->configuration_flag("--no-phase-saving"),
                    std::stod(this->configuration_value_or_default("--initial-learning-rate", "0.8")),
                    std::stod(this->configuration_value_or_default("--learning-rate-decay", "2e-6")),
                    std::stod(this->configuration_value_or_default("--learning-rate-minimum", "0.12")),
                    std::stod(this->configuration_value_or_default("--lambda-factor", "0.1"))
                );
            else
                throw std::runtime_error("Illegal decision heuristic for qute: " + decision_heuristic_argument);
            solver->decision_heuristic = decision_heuristic.get();

            Qute::DecisionHeuristic::PhaseHeuristicOption phase_heuristic = Qute::DecisionHeuristic::PhaseHeuristicOption::PHFALSE;
            auto phase_heuristic_argument = this->configuration_value_or_default("--phase-heuristic", "false");
            if (phase_heuristic_argument == "qtype") 
                phase_heuristic = Qute::DecisionHeuristic::PhaseHeuristicOption::QTYPE;
            else if (phase_heuristic_argument == "watcher")
                phase_heuristic = Qute::DecisionHeuristic::PhaseHeuristicOption::WATCHER;
            else if (phase_heuristic_argument == "random")
                phase_heuristic = Qute::DecisionHeuristic::PhaseHeuristicOption::RANDOM;
            else if (phase_heuristic_argument == "false")
                phase_heuristic = Qute::DecisionHeuristic::PhaseHeuristicOption::PHFALSE;
            else if (phase_heuristic_argument == "true")
                phase_heuristic = Qute::DecisionHeuristic::PhaseHeuristicOption::PHTRUE;
            else if (phase_heuristic_argument == "invJW")
                phase_heuristic = Qute::DecisionHeuristic::PhaseHeuristicOption::INVJW;
            else
                throw std::runtime_error("Illegal phase heuristic for qute: " + phase_heuristic_argument);            

            solver->decision_heuristic->setPhaseHeuristic(phase_heuristic);

            std::unique_ptr<Qute::RestartScheduler> restart_scheduler;
            std::string restart_argument = this->configuration_value_or_default("--restarts", "inner-outer");
            if(restart_argument == "off")
                restart_scheduler = std::make_unique<Qute::RestartSchedulerNone>();
            else if(restart_argument == "inner-outer")
                restart_scheduler = std::make_unique<Qute::RestartSchedulerInnerOuter>(
                    std::stol(this->configuration_value_or_default("--inner-restart-distance", "100")), 
                    std::stol(this->configuration_value_or_default("--outer-restart-distance", "100")),
                    std::stod(this->configuration_value_or_default("--restart-multiplier", "1.1"))
                );
            else if (restart_argument == "luby")
                restart_scheduler = std::make_unique<Qute::RestartSchedulerLuby>(
                    std::stol(this->configuration_value_or_default("--luby-restart-multiplier", "50"))
                );
            else if (restart_argument == "EMA")
                restart_scheduler = std::make_unique<Qute::RestartSchedulerEMA>(
                    std::stod(this->configuration_value_or_default("--alpha", "2e-5")),
                    std::stol(this->configuration_value_or_default("--minimum-distance", "20")),
                    std::stod(this->configuration_value_or_default("--threshold-factor", "1.4"))
                );
            else
                throw std::runtime_error("Illegal restart manager for qute: " + restart_argument);

            //NOTE: Restart scheduler Inner Outer is not working due to source having multiple definition of Qute::RestartSchedulerInnerOuter::notifyConflict(Qute::ConstraintType)
            solver->restart_scheduler = restart_scheduler.get();

            Qute::StandardLearningEngine learning_engine(*solver,
                "off"   //rrs
            );
            solver->learning_engine= &learning_engine;
            
            //WARNING, for some reason the base class "Propagator" does not have a virtual destructor, thus it will cause address sanitization issues if used
            std::unique_ptr<Qute::WatchedLiteralPropagator> propagator = std::make_unique<Qute::WatchedLiteralPropagator>(*solver);
            solver->propagator = propagator.get();


            this->handle = solver;
            solver::load(*this->formula);   //now load formula to solver

            std::unique_ptr<Qute::ModelGenerator> model_generator = std::make_unique<Qute::ModelGeneratorSimple>(*solver); 
            solver->model_generator = model_generator.get(); 
            
            result = solver->solve() == Qute::l_True;
            this->handle.reset();
        }
        catch(const std::exception& e){
            solving = false;
            throw;
        }
        solving = false;

        return result;
    }

    /*------------------------------------------------------------------------*/
    void rareqs::rareqs_deleter::operator()(RASolverIt *q) {
        delete q;
    }

    void rareqs::quant(int var)
    {
        if (var == 0 )
            return;
        auto varq = var < 0 ? QuantifierType::UNIVERSAL : QuantifierType::EXISTENTIAL;
        if(prefix.size() == 0)
        {
            Quantification q;
            q.first = varq;
            prefix_vars.push_back(abs(var));
            prefix.push_back(q);
        }
        else if(prefix.back().first != varq){
            prefix.back().second = VarVector(prefix_vars);
            prefix_vars.clear();
            Quantification q;
            q.first = varq;
            prefix_vars.push_back(abs(var));
            prefix.push_back(q);
        }
        else
            prefix_vars.push_back(abs(var));
    }

    void rareqs::add(int var)
    {
        if(var == 0)
        {
            cnf.push_back(LitSet(clause_vars));
            clause_vars.clear();
        }
        else{
            // clause_vars.push_back(mkLit(var));
            clause_vars.push_back(var>0 ? mkLit(abs(var)) : ~mkLit(abs(var)));
            max_id = max(max_id, abs(var));
        }
    }

    void rareqs::configure(std::string str){NOT_AVAILABLE(rareqs, configure); (void)str;}
    void rareqs::get_stats(std::unordered_map<std::string, int>& target){NOT_AVAILABLE(rareqs, get_stats); (void)target;}
    int rareqs::get_assignment(int v) { NOT_AVAILABLE(QuAPI, get_assignment); (void)v; return 0;}

    bool rareqs::solve()
    {
        //push the last remnants if necessary
        if (prefix_vars.size() != 0)
        {
            prefix.back().second = VarVector(prefix_vars);
            prefix_vars.clear();
        }
        
        //HOTFIX: Free variables are only partially supported. There has to be at least one variable in the prefix
        //        Thus, if the prefix is empty, we will just add the existentially quantified variable with id 1
        if(prefix.size() == 0){
            Quantification q;
            q.first = EXISTENTIAL;
            q.second = VarVector({1});
            prefix.push_back(q);
        }

        Fla fla;
        build_fla(prefix,cnf, fla);
        RASolverIt s((Var)max_id, prefix, cnf, false);  //unit is 0 on default
        const bool win = s.solve();
        const bool sat = fla.q==EXISTENTIAL ? win : !win;
        return sat;
    }


    /*------------------------------------------------------------------------*/
    qfun::qfun()
    {
        this->prefix_handle = pyqbf_qfun_create_prefix();    
        this->cnf_handle = pyqbf_qfun_create_cnf();
    }

    void qfun::quant(int x)
    {
        if(this->prefix_handle)
            pyqbf_qfun_prefix_add_quant(this->prefix_handle, x);
    }

    void qfun::push_clause()
    {
        if(this->cnf_handle)
            pyqbf_qfun_cnf_add(this->cnf_handle, &(this->clause_vars));
        this->clause_vars.clear();
    }


    void qfun::add(int x)
    {
        if(x == 0)
            this->push_clause();
        else
            clause_vars.push_back(x);        
    }

    void qfun::configure(std::string str){NOT_AVAILABLE(qfun, configure); (void)str;}
    void qfun::get_stats(std::unordered_map<std::string, int>& target){NOT_AVAILABLE(qfun, get_stats); (void)target;}
    int qfun::get_assignment(int v) { NOT_AVAILABLE(QuAPI, get_assignment); (void)v; return 0;}

    bool qfun::solve()
    {
        bool result = false;
        if(!this->clause_vars.empty())
            this->push_clause();
        result = pyqbf_qfun_solve(this->prefix_handle, this->cnf_handle);
        return result;
    }
    
    qfun::~qfun()
    {
        if(this->prefix_handle)
            pyqbf_qfun_destroy_prefix(this->prefix_handle);
        if(this->cnf_handle)
            pyqbf_qfun_destroy_cnf(this->cnf_handle);
    }

/*------------------------------------------------------------------------*/
    quapi::quapi(std::string solver_path) : solver_path(solver_path) { }

    void quapi::quant(int x)
    {
        if(this->solver_handle.get() != nullptr)
            quapi_shield::quapi_quantify(this->solver_handle.get(), x);
    }
    void quapi::add(int x) 
    {
        if(this->solver_handle.get() != nullptr)
            quapi_shield::quapi_add(this->solver_handle.get(), x);
    }

    int quapi::getReturnCode(){
        int result = quapi_shield::quapi_solve(this->solver_handle.get());
        if(result != 10 && result != 20)
            throw std::runtime_error("QuAPI returned code " + std::to_string(result) + "!");
        return result;
    }   

    void quapi::set_preload_lib_envvar(){
        const char* preload_so_paths[] = {
            "./libquapi_preload.so",
            "../libquapi_preload.so",
            "../quapi/build/libquapi_preload.so",
            "./quapi/libquapi_preload.so",
            "./third_party/quapi/libquapi_preload.so",
            "./_deps/quapi-build/libquapi_preload.so",
            "~/quapi/build/libquapi_preload.so",
            "/usr/local/lib/libquapi_preload.so",
            "/usr/lib/libquapi_preload.so"
        };
        std::string error_msg;
        #ifdef QUAPI_PRELOAD_SO_PATH            
            char origin_name[] = STR_QUAPI_PRELOAD_SO_PATH;            
            char* space_pos = strchr(origin_name, ' ');
            if(space_pos != NULL){
                error_msg = "WARNING: Executable path contains space-characters! This is currently not supported by pyqbf.";
            }
            else if(file_exists((quapi_scriptlocation + "/" STR_QUAPI_PRELOAD_SO_PATH).c_str())){
                setenv("QUAPI_PRELOAD_PATH", (quapi_scriptlocation + "/" STR_QUAPI_PRELOAD_SO_PATH).c_str(), true);    
                return;
            }
        #else
            error_msg = "Cannot retrive path of libquapi_preload.so, preprocessor variable does not exist!";
        #endif

        bool exists = false;
        for(auto path : preload_so_paths){
            exists = file_exists(path);
            if(exists) break;
        }

        if(!exists)
        {
            char* lib_env = getenv("PYQBF_QUAPI_PRELOAD_TEST_LIBRARY");
            exists = lib_env && file_exists(lib_env);
            if(exists)
                setenv("QUAPI_PRELOAD_PATH", lib_env, true);
        }

        if(!exists){
            std::cerr << error_msg
                      << "In order to still use QuAPI, please make sure the \"libquapi_preload.so\" is available at one of the following locations:" << std::endl;
            for(auto path : preload_so_paths)
                std::cerr << path << std::endl;
        }
                    
    }

    void quapi::instantiate_solver(int max_assumption_count, PCNF& formula, bool allow_missing_universials){
        set_preload_lib_envvar();
        // setenv("QUAPI_DEBUG", "1", true);
        // setenv("QUAPI_TRACE", "1", true);
            
        if(allow_missing_universials)
            setenv("QUAPI_ALLOW_MISSING_UNIVERSAL_ASSUMPTIONS", "1", true);
        else
            unsetenv("QUAPI_ALLOW_MISSING_UNIVERSAL_ASSUMPTIONS");

        const char** argv = (const char**)malloc((this->executable_argv.size() + 2) * sizeof(char*));        
        argv[0] = (char*) this->solver_path.c_str();
        int idx = 1;
        std::vector<char*> cleanup;
        for(auto arg : this->executable_argv){
            char* str = (char*)calloc(arg.size() + 1, sizeof(char));
            memcpy(str, arg.c_str(), arg.size());
            cleanup.push_back(str);
            argv[idx++] = str;
        }        
        argv[idx] = nullptr;
        this->solver_handle.reset(quapi_shield::quapi_init(
            (char*) this->solver_path.c_str(),  //path
            argv,                               //argv
            nullptr,                            //envp
            formula.nv(),                       //litcount
            formula.clauses_.size(),            //clausecount
            max_assumption_count,               //maxassumptions
            nullptr,                            //SAT_regex
            nullptr                             //UNSAT_regex
            ));        
        if(!this->solver_handle)
            throw std::runtime_error("Unable to initialize QuAPI!\n");                    
        this->load(formula);
    }

    void quapi::assume(int v) 
    {
        if(this->solver_handle.get() != nullptr) {
            if(!quapi_shield::quapi_assume(this->solver_handle.get(), v))
                std::cerr << "WARNING! Function quapi_assume(" << v << ") returned false!";
        }
    }

    void quapi::configure(std::string str){
        this->executable_argv.push_back(str);
    }

    void quapi::reset() { NOT_AVAILABLE(QuAPI, reset); }
    void quapi::push() { NOT_AVAILABLE(QuAPI, push); }
    void quapi::pop() { NOT_AVAILABLE(QuAPI, pop); }
    int quapi::get_assignment(int v) { NOT_AVAILABLE(QuAPI, get_assignment); (void)v; return 0;}
    void quapi::get_stats(std::unordered_map<std::string, int>& target){NOT_AVAILABLE(quapi, get_stats); (void)target;}

    std::shared_ptr<quapi> quapi_with_caqe(){
        #ifdef QUAPI_CAQE_EXE_PATH        
            std::string path = quapi_scriptlocation + "/" STR_QUAPI_CAQE_EXE_PATH;
            if (file_exists(path.c_str()))
                return std::make_shared<quapi>(path);
        #endif
        auto candidate = find_fallback_path("caqe", "pyqbf_caqe");
        if(candidate == ""){            
            char* exe_env = getenv("PYQBF_CAQE_TEST_EXECUTABLE");
            if(exe_env && file_exists(exe_env))
                return std::make_shared<quapi>(exe_env);            
            else
                throw std::runtime_error("Cannot locate caqe executable!");
        }
        else
            return std::make_shared<quapi>(candidate);
    }

    std::shared_ptr<quapi> quapi_with_depqbf(){
        #ifdef QUAPI_DEPQBF_EXE_PATH
        std::string path = quapi_scriptlocation + "/" STR_QUAPI_DEPQBF_EXE_PATH;
            if (file_exists(path.c_str()))
                return std::make_shared<quapi>(path);
        #endif
        auto candidate = find_fallback_path("depqbf", "pyqbf_depqbf");
        if(candidate == ""){            
            char* exe_env = getenv("PYQBF_DEPQBF_TEST_EXECUTABLE");
            std::cout << "DEPQBF-ENV: " << exe_env << std::endl;
            if(exe_env && file_exists(exe_env)){
                return std::make_shared<quapi>(exe_env);            
            }
            else
                throw std::runtime_error("Cannot locate depqbf executable!");
        }
        else
            return std::make_shared<quapi>(candidate);
    }

    std::shared_ptr<quapi> quapi_with_qute(){
        #ifdef QUAPI_QUTE_EXE_PATH
            std::string path = quapi_scriptlocation + "/" STR_QUAPI_QUTE_EXE_PATH;
            if (file_exists(path.c_str()))
                return std::make_shared<quapi>(path);
        #endif
        auto candidate = find_fallback_path("qute", "pyqbf_qute");
        if(candidate == ""){            
            char* exe_env = getenv("PYQBF_QUTE_TEST_EXECUTABLE");
            if(exe_env && file_exists(exe_env))
                return std::make_shared<quapi>(exe_env);            
            else
                throw std::runtime_error("Cannot locate qute executable!");
        }
        else
            return std::make_shared<quapi>(candidate);
    }

    std::shared_ptr<quapi> quapi_with_rareqs(){
        #ifdef QUAPI_RAREQS_EXE_PATH        
            std::string path = quapi_scriptlocation + "/" STR_QUAPI_RAREQS_EXE_PATH;
            if (file_exists(path.c_str()))
                return std::make_shared<quapi>(path);
        #endif
        auto candidate = find_fallback_path("rareqs", "pyqbf_rareqs");
        if(candidate == ""){            
            char* exe_env = getenv("PYQBF_RAREQS_TEST_EXECUTABLE");
            if(exe_env && file_exists(exe_env))
                return std::make_shared<quapi>(exe_env);            
            else
                throw std::runtime_error("Cannot locate rareqs executable!");
        }
        else
            return std::make_shared<quapi>(candidate);
    }
    
      std::shared_ptr<quapi> quapi_with_qfun(){
        #ifdef QUAPI_QFUN_EXE_PATH     
            std::string path = quapi_scriptlocation + "/" STR_QUAPI_QFUN_EXE_PATH;
            if (file_exists(path.c_str()))
                return std::make_shared<quapi>(path);
        #endif
        auto candidate = find_fallback_path("qfun", "pyqbf_qfun");
        if(candidate == ""){            
            char* exe_env = getenv("PYQBF_QFUN_TEST_EXECUTABLE");
            if(exe_env && file_exists(exe_env))
                return std::make_shared<quapi>(exe_env);            
            else
                throw std::runtime_error("Cannot locate qfun executable!");
        }
        else
            return std::make_shared<quapi>(candidate);
    }
}
