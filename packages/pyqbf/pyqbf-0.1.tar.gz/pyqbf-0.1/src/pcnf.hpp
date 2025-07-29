#pragma once

#include <nanobind/nanobind.h>

namespace nb = nanobind;

namespace pyqbf {
    class literal_iterator
    {
    nb::detail::fast_iterator it;

    public:
    literal_iterator(nb::detail::fast_iterator it)
        : it(it)
        {}

    using iterator_category = std::forward_iterator_tag;
    using difference_type   = nb::detail::fast_iterator::difference_type;
    using value_type        = literal;
    using pointer           = literal*;  // or also value_type*
    using reference         = literal&;  // or also value_type&

    literal_iterator operator++()        { it++; return *this; }
    literal_iterator operator++(int)     { literal_iterator self(*this); ++(*this); return self; }
    literal          operator*()         { return nb::cast<literal>(*it); }
    
    friend bool operator== (const literal_iterator& a, const literal_iterator& b) { return a.it == b.it; };
    friend bool operator!= (const literal_iterator& a, const literal_iterator& b) { return a.it != b.it; };  
    };

    class clause_iterator
    {
        public:
        nb::detail::fast_iterator it;
        nb::detail::fast_iterator clause_it = 0;
        nb::detail::fast_iterator end;

        inline nb::list get_current() { //current clause
            return nb::cast<nb::list>(*it); 
        }  

        public:
        clause_iterator(nb::detail::fast_iterator it, nb::detail::fast_iterator end) : it(it), end(end) {
            if(it != end){
                auto current = nb::cast<nb::list>(*it);
                clause_it = current.begin();
            }
        }

        using iterator_category = std::forward_iterator_tag;
        using difference_type   = nb::detail::fast_iterator::difference_type;
        using value_type        = literal;
        using pointer           = literal*;  // or also value_type*
        using reference         = literal&;  // or also value_type&

        clause_iterator operator++() { 
            if(it == end)
                return *this;
            if(clause_it == get_current().end())
            {
                it++; 
                if(it == end){
                    clause_it = 0;
                    return *this;
                }
                clause_it = get_current().begin();
            }
            else
                clause_it++;
            return *this; 
        }
        clause_iterator operator++(int) { clause_iterator self(*this); ++(*this); return self; }
        literal operator*() { 
            if(it == end || clause_it == get_current().end())
                return 0;
            else 
                return  nb::cast<literal>(*clause_it); 
        }
        
        friend bool operator== (const clause_iterator& a, const clause_iterator& b) { return a.it == b.it && a.clause_it == b.clause_it; };
        friend bool operator!= (const clause_iterator& a, const clause_iterator& b) { return a.it != b.it || a.clause_it != b.clause_it; };  
    };

    struct PCNF
    {
    nb::list prefix_;
    nb::list clauses_;
    int nv_;  

    PCNF(nb::object py)
    {
        prefix_ = nb::cast<nb::list>(getattr(py, "prefix"));
        clauses_ = nb::cast<nb::list>(getattr(py, "clauses"));
        nv_ = nb::cast<int>(getattr(py, "nv"));
    }

    struct prefix_accessor {
        PCNF &self;
        explicit prefix_accessor(PCNF &p) : self(p) {}

        literal_iterator begin() {return literal_iterator(self.prefix_.begin());}  
        literal_iterator end() {return literal_iterator(self.prefix_.end());}  
        inline size_t size(){return self.prefix_.size();}
    };
    struct clauses_accessor {
        PCNF &self;
        explicit clauses_accessor(PCNF &p) : self(p) {}

        clause_iterator begin() {return clause_iterator(self.clauses_.begin(), self.clauses_.end());}  
        clause_iterator end() {return clause_iterator(self.clauses_.end(), self.clauses_.end());}  
        inline size_t size() {return self.clauses_.size();}
    };

    prefix_accessor prefix() { return prefix_accessor(*this); }
    clauses_accessor clauses() { return clauses_accessor(*this); }
    inline int nv() {return this->nv_;}
    };
}