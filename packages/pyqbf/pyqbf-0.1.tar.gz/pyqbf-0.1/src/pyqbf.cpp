#include <nanobind/stl/vector.h>  //optional header for converting python list to std::vector
#include <nanobind/stl/string.h>  //optional header for converting python str to std::string
#include <nanobind/stl/unordered_map.h> //optional header for converting python dict to std::unordered_map
#include "pyqbf.hpp"
#include "preprocessor.hpp"

namespace pyqbf {

  const int SOLVER_DEPQBF = 1;
  // const int SOLVER_QUANTOR = 2;
  const int SOLVER_QUTE = 3;
  const int SOLVER_RAREQS = 4;
  const int SOLVER_QFUN = 5;
  const int SOLVER_QUAPI = 6;
  const int SOLVER_CAQE = 7;

  SolverManager manager;

    SolverManager::~SolverManager() {
    //Clean-up
    for(auto& it : this->solvers)
      it.second.reset();    
  }

  int SolverManager::add(std::shared_ptr<solver> solver){
    int id = next_id++;
    solvers[id] = solver;
    return id;
  }

  void SolverManager::remove(int id){
    auto it = solvers.find(id);
    if(it != solvers.end()){
      (*it).second.reset();
      solvers.erase(it);
    }
  }

  std::shared_ptr<solver> SolverManager::get_solver(int id){
      auto it = this->solvers.find(id);
      if(it == this->solvers.end())
        throw std::runtime_error("Backend-Id " + std::to_string(id) + " does not belong to a registered solver!");      
      return it->second;
  }

  void dump(nb::object py)
  {
    PCNF x(py);
    std::cout << x.prefix().size() << "[";
    for(auto p : x.prefix())
      std::cout << p << " ";
    std::cout << "]" << std::endl;

    std::cout << x.clauses().size() << "[";
    for(literal l : x.clauses()) 
      std::cout << l << " ";
    std::cout << "]" << std::endl;
    std::cout << x.nv() << std::endl;
  }

  bool solve(nb::object py)
  {
    PCNF formula(py);
    depqbf solver;
    solver.load(formula);
    return solver.solve();
  }

  bool solve(nb::object py, int backend_id)
  {
    PCNF formula(py);
    std::shared_ptr<solver> s = manager.get_solver(backend_id);
    s.get()->load(formula);
    bool result = s.get()->solve();
    return result;
  }


  int init_solver(int solver_id)
 {
    std::shared_ptr<solver> s;

    switch (solver_id)
    {
    case SOLVER_QUTE:
      s = std::make_shared<qute>();
      break;

    case SOLVER_RAREQS:
      s = std::make_shared<rareqs>();
      break;

    case SOLVER_QFUN:
      s = std::make_shared<qfun>();
      break;

    case SOLVER_DEPQBF:
      s = std::make_shared<depqbf>();
      break;
    default:
      throw std::runtime_error("Illegal solver id! " + std::to_string(solver_id) + " does not describe a valid solver id!");
    }

    int id = manager.add(s);

    return id;
  }

  void release_solver(int backend_id){
    manager.remove(backend_id);
  }

 void configure(int backend_id, std::string configure_str){
    auto solver = manager.get_solver(backend_id);
    if(solver != nullptr)
      return solver->configure(configure_str);
}

  std::unordered_map<std::string, int>&  get_stats(int backend_id, std::unordered_map<std::string, int>& target){
    auto solver = manager.get_solver(backend_id);
    if(solver != nullptr)
      solver->get_stats(target);
    return target;
  }

  int get_assignment(int backend_id, int var){
      auto solver = manager.get_solver(backend_id);
      if(solver != nullptr)
        return solver->get_assignment(var);
      return 0;
  }


  std::shared_ptr<incremental_solver> safe_get_incremental_solver(int backend_id){
    auto solver = manager.get_solver(backend_id);
    if (!solver.get()->is_incremental())
      throw std::runtime_error("Solver with id " + std::to_string(backend_id) + " was requested as incremental but does not refer to an incremental solver!");
    return std::dynamic_pointer_cast<incremental_solver>(solver);
  }

  void quant_incremental(const int var, int backend_id){
    auto solver = safe_get_incremental_solver(backend_id);
    if(solver != nullptr)  
      solver.get()->quant(var);
  }

  void add_incremental(const LitVector& clause, int backend_id){
    auto solver = safe_get_incremental_solver(backend_id);
    if(solver.get() == nullptr)  
      return;

    for(auto lit : clause)
      solver.get()->add(lit);
    solver.get()->add(0);
  }

  void load_incremental(nb::object py, int backend_id){
    auto solver = safe_get_incremental_solver(backend_id);
    if(solver.get() == nullptr)  
      return;
    PCNF formula(py);
    solver.get()->load(formula);
  }

  bool solve_incremental(int backend_id){
    auto solver = safe_get_incremental_solver(backend_id);
    if(solver.get() == nullptr)
      return false;
    else
      return solver.get()->solve();
  }

  void reset_incremental(int backend_id){
    auto solver = safe_get_incremental_solver(backend_id);
    if(solver.get() != nullptr)
      solver.get()->reset();
  }

  void push_incremental(int backend_id){
    auto solver = safe_get_incremental_solver(backend_id);
    if(solver.get() != nullptr)
      solver.get()->push();
  }

  void pop_incremental(int backend_id){
    auto solver = safe_get_incremental_solver(backend_id);
    if(solver.get() != nullptr)
      solver.get()->pop();
  }

  void assume_incremental(int backend_id, int var){
    auto solver = safe_get_incremental_solver(backend_id);
    if(solver.get() != nullptr)
      solver.get()->assume(var);
  }

  int init_quapi(std::string solver_path){ 
    std::shared_ptr<quapi> solver = std::make_shared<quapi>(solver_path);      
    int id = manager.add(solver);
    return id;
  }

  int init_quapi_with_preset(int solver_id){
    std::shared_ptr<quapi> solver;
    switch (solver_id)
    {
    case SOLVER_CAQE: 
      solver = quapi_with_caqe(); 
      break;

    case SOLVER_DEPQBF:
      solver = quapi_with_depqbf();
      break;

    // case SOLVER_QUANTOR:
    //   solver = quapi_with_quantor();
    //   break;

    case SOLVER_QUTE:
      solver = quapi_with_qute();
      break;

    case SOLVER_RAREQS:
      solver = quapi_with_rareqs();
      break;      

    case SOLVER_QFUN:
      solver = quapi_with_qfun();
      break;

    default:
      throw std::runtime_error("Solver type with id " + std::to_string(solver_id) + " is currently not available as preset for QuAPI!");
    }
    int id = manager.add(solver);
    return id;
  }

  void instantiate_quapi(int backend_id, int max_assumptions, nb::object py, bool allow_missing_universals){
    std::shared_ptr<quapi> solver = std::dynamic_pointer_cast<quapi>(safe_get_incremental_solver(backend_id));
    if(solver.get() != nullptr)  
    {
      PCNF formula(py);
      solver.get()->instantiate_solver(max_assumptions, formula, allow_missing_universals);
    }
  }

  void assume_quapi(int backend_id, int assumption){
    std::shared_ptr<quapi> solver = std::dynamic_pointer_cast<quapi>(safe_get_incremental_solver(backend_id));
    if(solver.get() != nullptr)  
      solver.get()->assume(assumption);    
  }

  bool solve_quapi(int backend_id)
  {
    std::shared_ptr<quapi> solver = std::dynamic_pointer_cast<quapi>(safe_get_incremental_solver(backend_id));
    if(solver.get() == nullptr)      
      return false;    
    else
      return solver.get()->solve();
    
  }

  void release_quapi(int backend_id){
    release_solver(backend_id);
  }

  int preprocess(nb::object py, nb::object target)
  {
    PCNF formula(py);
    bloqqer b;
    b.load(formula);
    auto result =  b.solve();

    PCNF result_formula(target);
    b.get_formula(result_formula);
    setattr(target, "nv", nb::int_(result_formula.nv_));  //write back to the python object
    return result;
  }

  int preprocess_with_trace(nb::object py, nb::object target, std::string qrat_file){
    PCNF formula(py);
    bloqqer b;
    b.set_qrat(qrat_file);
    b.load(formula);
    auto result =  b.solve();

    PCNF result_formula(target);
    b.get_formula(result_formula);
    setattr(target, "nv", nb::int_(result_formula.nv_));  //write back to the python object
    return result;
  }


  nb::list pcnf_to_lit_list(nb::object py)
  {
    PCNF formula(py);   
    nb::list values;
    
    for(literal l : formula.clauses())
      values.append(l);
    
    return values;
  }

  void init_module(std::string location){
    pyqbf::quapi_scriptlocation = location;
  }

}

NB_MODULE(pyqbf_cpp, m) {
  m.attr("SOLVER_DEPQBF") = pyqbf::SOLVER_DEPQBF;
  // m.attr("SOLVER_QUANTOR") = pyqbf::SOLVER_QUANTOR;
  m.attr("SOLVER_QUTE") = pyqbf::SOLVER_QUTE;
  m.attr("SOLVER_RAREQS") = pyqbf::SOLVER_RAREQS;
  m.attr("SOLVER_QFUN") = pyqbf::SOLVER_QFUN;
  m.attr("SOLVER_QUAPI") = pyqbf::SOLVER_QUAPI;
  m.attr("SOLVER_CAQE") = pyqbf::SOLVER_CAQE;

  m.def("dump", &pyqbf::dump);
  m.def("init_solver", &pyqbf::init_solver);
  m.def("release_solver", &pyqbf::release_solver);
  m.def("configure", &pyqbf::configure);
  m.def("get_stats", &pyqbf::get_stats);
  m.def("get_assignment", &pyqbf::get_assignment);
  m.def("solve", nb::overload_cast<nb::object>(&pyqbf::solve));
  m.def("solve", nb::overload_cast<nb::object, int>(&pyqbf::solve));

  m.def("load_incremental", &pyqbf::load_incremental);
  m.def("quant_incremental", &pyqbf::quant_incremental);
  m.def("add_incremental", &pyqbf::add_incremental);
  m.def("reset_incremental", &pyqbf::reset_incremental);
  m.def("push_incremental", &pyqbf::push_incremental);
  m.def("pop_incremental", &pyqbf::pop_incremental);
  m.def("assume_incremental", &pyqbf::assume_incremental);
  m.def("solve_incremental", &pyqbf::solve_incremental);

  m.def("init_quapi", &pyqbf::init_quapi);
  m.def("init_quapi_with_preset", &pyqbf::init_quapi_with_preset);
  m.def("instantiate_quapi", &pyqbf::instantiate_quapi);
  m.def("assume_quapi", &pyqbf::assume_quapi);
  m.def("solve_quapi", &pyqbf::solve_quapi);
  m.def("release_quapi", &pyqbf::release_quapi);

  m.def("preprocess", &pyqbf::preprocess);
  m.def("preprocess_with_trace", &pyqbf::preprocess_with_trace);
  m.def("pcnf_to_lit_list", &pyqbf::pcnf_to_lit_list);
  m.def("init_module", &pyqbf::init_module);
}
