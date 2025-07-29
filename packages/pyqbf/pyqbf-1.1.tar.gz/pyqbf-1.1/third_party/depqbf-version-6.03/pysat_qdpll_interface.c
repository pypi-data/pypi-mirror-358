#include "qdpll_internals.h"
#include "qdpll_config.h"
#include "pysat_qdpll_interface.h"


void qdpll_get_stats(QDPLL* qdpll, struct pysat_depqbf_stats* stats)
{
    #if COMPUTE_STATS
    stats->decisions = qdpll->stats.decisions;
    stats->propagations = qdpll->stats.propagations;
    stats->restarts = qdpll->state.num_restarts;
    #else
    stats->decisions = 0;
    stats->propagations = 0;
    stats->restarts = qdpll->state.num_restarts;
    #endif    
}