#pragma once
#include <iostream>
#include <memory>
#include <vector>
#include <unordered_map>

#include "defs.hpp"
#include "pcnf.hpp"

extern "C" {    
#include <qdpll.h>       //DepQBF
}

//qute
#include <qcdcl.hh>      
#include <simple_tracer.hh>
#include <watched_literal_propagator.hh>
#include <standard_learning_engine.hh>
#include <dependency_manager_watched.hh>
#include <variable_data.hh>
#include <decision_heuristic_VMTF_deplearn.hh>
#include <decision_heuristic_VMTF_prefix.hh>
#include <decision_heuristic_VSIDS_deplearn.hh>
#include <decision_heuristic_SGDB.hh>
#include <constraint_DB.hh>
#include <restart_scheduler_none.hh>
#include <restart_scheduler_inner_outer.hh>
#include <restart_scheduler_ema.hh>
#include <restart_scheduler_luby.hh>
#include <debug_helper.hh>
#include <model_generator_simple.hh>

//rareqs
#include <qtypes.hh>
#include <RASolverIt.hh>

//quapi
namespace quapi_shield{
//Name confilict of "struct gzFile_s" with <zlib> included by minisat included by rareqs via qtypes => resolve by putting it into different namespace
#include <quapi/quapi.h>
}
struct QDPLL;

//qfun
#include <pyqbf_int.h>

namespace pyqbf {
    //Global variable for the script-location of quapi
    extern std::string quapi_scriptlocation;

    class solver {
    public:
        virtual ~solver() = default;
        virtual void quant(int v) = 0;
        virtual void add(int l) = 0;

        virtual void load(PCNF& f) {
            for(int v : f.prefix()) {
                quant(v);
            }
            for(int l : f.clauses()) {
                add(l);
            }
        }

        virtual inline bool is_incremental(){ return false; }
        virtual void configure(std::string) = 0;
        virtual void get_stats(std::unordered_map<std::string, int>&) = 0;
        virtual int get_assignment(int v) = 0;
        virtual bool solve() = 0;
    };

    class incremental_solver : public solver{
        private:
            bool loaded = false;
            int iteration = 0;
        protected:
            std::vector<int> assumptions;
        public:
        virtual ~incremental_solver() = default;

        inline bool is_loaded() {return loaded;}
        virtual void load(PCNF& f){
            if(is_loaded())
                std::cerr << "Cannot load a PNF formula twice!" << std::endl;
            else
                solver::load(f);
        }
        virtual void assume(int v) = 0;
        virtual void reset() = 0;
        virtual void push() = 0;
        virtual void pop() = 0;        
        virtual inline bool is_incremental(){return true;}
    };


    class depqbf : public incremental_solver {
    private:
        struct qdpll_deleter {
            void operator()(QDPLL*);
        };
        int curq_  = 0;           //current quantifier

	    std::unique_ptr<QDPLL, qdpll_deleter> handle;
    public:
        depqbf();
        virtual ~depqbf() = default;
        virtual void quant(int) override;
        virtual void add(int) override;
        virtual void assume(int) override;
        virtual void reset() override;
        virtual void push() override;
        virtual void pop() override;
        virtual void configure(std::string) override;
        virtual void get_stats(std::unordered_map<std::string, int>&) override;
        virtual int get_assignment(int) override;
        bool solve();
    };

    class qute : public solver {
        private:
        bool solving = false;
        PCNF* formula = nullptr;

        std::shared_ptr<Qute::QCDCL_solver> handle;
        std::vector<Qute::Literal> tmp_clause_;
        std::unordered_map<std::string, std::string> configuration;

        std::string configuration_value_or_default(std::string, std::string);
        bool configuration_flag(std::string);

        public:
        qute();
        virtual ~qute() = default;        
        virtual inline void load(PCNF& f) override {    //lazy loading due to late instantiation
            formula = &f;
        }
        
        virtual void quant(int) override;
        virtual void add(int) override;
        virtual void configure(std::string) override;
        virtual void get_stats(std::unordered_map<std::string, int>&) override;
        virtual int get_assignment(int) override;
        void set_configuration_value(std::string, std::string);
        bool solve();
    };

     class rareqs : public solver{
        private:
         struct rareqs_deleter{
             void operator()(RASolverIt*);
         };
         std::vector<Var> prefix_vars;
         Prefix prefix;
         CNF cnf;
         std::vector<Lit> clause_vars;
         int max_id = 0;
         std::unique_ptr<RASolverIt, rareqs_deleter> handle;
        public:
         virtual ~rareqs() = default;
         virtual void quant(int x) override;
         virtual void add(int x) override;
         virtual void configure(std::string) override;
         virtual void get_stats(std::unordered_map<std::string, int>&) override;
         virtual int get_assignment(int) override;
         bool solve() override;
     };

     class qfun: public solver{
        private:
        void* prefix_handle;
        void* cnf_handle;
        std::vector<int> clause_vars;

        void push_clause();

        public: 
         qfun();
         virtual ~qfun();
         virtual void quant(int x) override;
         virtual void add(int x) override;
         virtual void configure(std::string) override;
         virtual void get_stats(std::unordered_map<std::string, int>&) override;
         virtual int get_assignment(int) override;
         bool solve() override;
     };

    class quapi : public incremental_solver{
        private:
          std::string solver_path;
          quapi_shield::QuAPISolver solver_handle;
          std::vector<int> assumptions;
          std::vector<std::string> executable_argv;
          bool solving = false;

          void set_preload_lib_envvar();

        public:
          quapi(std::string);
          virtual ~quapi() = default;
          virtual void quant(int x) override;
          virtual void add(int x) override;
          inline virtual bool solve() override {return this->getReturnCode() == 10;}
          int getReturnCode();
          void instantiate_solver(int max_assumption_count, PCNF& formula, bool allow_missing_universials);

          virtual void assume(int v) override;
          virtual void reset() override;
          virtual void push() override;
          virtual void pop() override;
          virtual int get_assignment(int v) override;
          virtual void configure(std::string) override;
          virtual void get_stats(std::unordered_map<std::string, int>&) override;
    };

    std::shared_ptr<quapi> quapi_with_caqe();
    std::shared_ptr<quapi> quapi_with_depqbf();
    std::shared_ptr<quapi> quapi_with_qute();
    std::shared_ptr<quapi> quapi_with_rareqs();
    std::shared_ptr<quapi> quapi_with_qfun();

}