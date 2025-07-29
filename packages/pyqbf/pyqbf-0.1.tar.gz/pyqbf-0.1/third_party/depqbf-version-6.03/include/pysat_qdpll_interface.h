#include <qdpll.h>

//As the normal interface of qdpll.h does not provide the possibility to retrieve stats, this interface will expose them

struct pysat_depqbf_stats{
    int decisions;
    int restarts;
    int propagations;
};


void qdpll_get_stats(QDPLL*, struct pysat_depqbf_stats*);