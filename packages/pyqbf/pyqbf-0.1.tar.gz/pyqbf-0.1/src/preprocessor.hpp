#pragma once

#include <string>
#include "defs.hpp"
#include "pcnf.hpp"
extern "C"{
    #include <bloqqer.h>
}


namespace pyqbf {
    class preprocessor{
        public:
        virtual void quant(int v) = 0;
        virtual void add(int l) = 0;
        
        virtual void load(PCNF& f){
            for(int v : f.prefix()) {
                quant(v);
            }
            for(int l : f.clauses()) {
                add(l);
            }
        }
        
        virtual int solve() = 0;
        // virtual PCNF& preprocessed() = 0;
    };

    class bloqqer : public preprocessor{
        std::string trace;
        bool qratTracing = false;    
    public:
        bloqqer();
        ~bloqqer() = default;

        virtual void load(PCNF& f) override;
        virtual void quant(int v) override;
        virtual void add(int l) override;
        void get_formula(PCNF& f);
        void set_qrat(std::string);
        
        virtual int solve() override;
        // virtual PCNF& preprocessed() override;
    };
}