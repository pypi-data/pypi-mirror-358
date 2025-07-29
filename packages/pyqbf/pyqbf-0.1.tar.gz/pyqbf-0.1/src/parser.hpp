#pragma once
#include <string>
#include <iostream>
#include <algorithm>
#include "pcnf.hpp" 

#define END_CONDITON (current != EOF && current != 0) 

namespace pyqbf {
    class qdimacs_parser{
        FILE* handle;
        PCNF& formula;
        int errors = 0;
        char current;

        inline void next(){
            if(END_CONDITON)
                current = fgetc(this->handle);                                
        }   

        inline void check(char expected) {
            if(current != expected){
                printf("Parser error! Expected %c but got %c\n", expected, current);
                errors++; 
            }
            next();
        }

        inline void skip_whitespaces(){
            bool valid = true;
            do{
                switch (this->current)
                {
                case ' ': case '\t': case '\n':
                    next();
                    break;
                
                default:
                    valid = false;
                    break;
                }
            }
            while(valid);
        }

        inline void read_name(){
            bool valid = true;
            buffer.clear();
            do{
                switch (current)
                {
                    case 'a': case 'b': case 'c': case 'd': case 'e': case 'f':
                    case 'g': case 'h': case 'i': case 'j': case 'k': case 'l':
                    case 'm': case 'n': case 'o': case 'p': case 'q': case 'r':
                    case 's': case 't': case 'u': case 'v': case 'w': case 'x':
                    case 'y': case 'z':
                    case 'A': case 'B': case 'C': case 'D': case 'E': case 'F':
                    case 'G': case 'H': case 'I': case 'J': case 'K': case 'L':
                    case 'M': case 'N': case 'O': case 'P': case 'Q': case 'R':
                    case 'S': case 'T': case 'U': case 'V': case 'W': case 'X':
                    case 'Y': case 'Z':
                    buffer += current;
                    next();
                    break;
                
                default:
                    valid = false;
                    break;
                }
            } while(valid);
        }

        inline void read_number(){
            bool valid = true;
            buffer.clear();
            do{
                switch (current)
                {
                    case '0': case '1': case '2': case '3': case '4': case '5':
                    case '6': case '7': case '8': case '9': case '-':
                    buffer += current;
                    next();
                    break;
                
                default:
                    valid = false;
                    break;
                }
            } while(valid);
        }

        void parse_header(){
            skip_whitespaces();
            check('p');
            skip_whitespaces();
            read_name();
            if(buffer != "cnf"){
                printf("Parser error! Expected cnf but got %s", buffer.c_str());
                errors++;
            }
            skip_whitespaces();
            read_number();      //var count
            this->formula.nv_ = std::stoi(buffer);
            skip_whitespaces();
            read_number();      //clause count
            skip_whitespaces();
        }

        void parse_quantifier(){
            int quant = current == 'a' ? -1 : 1;
            next(); skip_whitespaces();
            bool valid = true;
            int number = 0;
            do {
                read_number();
                number = stoi(buffer);
                if(number != 0)
                    this->formula.prefix_.append(number * quant);
                else
                    valid = false;
                skip_whitespaces();
            }while(valid);
            skip_whitespaces();
        }

        void parse_clause(){
            nb::list clause;
            bool valid = true;
            int number = 0;
            do {
                skip_whitespaces();
                read_number();
                if(buffer.size() == 0)  //terminate if no number was found
                    break;
                number = stoi(buffer);
                if(number != 0){
                    clause.append(number);
                    this->formula.nv_ = std::max(number, this->formula.nv_);
                }
                else{
                    valid = false;
                    this->formula.clauses_.append(clause);
                }
            }while(valid);
            skip_whitespaces();
        }

    public:
        qdimacs_parser(FILE* fp, PCNF& formula) : handle(fp), formula(formula) { buffer.reserve(16); }
        std::string buffer;

        void parse(){
            next();
            parse_header();
            while(current == 'a' || current == 'e')
                parse_quantifier();            
            while(END_CONDITON)
                parse_clause();            
        }
    };
}