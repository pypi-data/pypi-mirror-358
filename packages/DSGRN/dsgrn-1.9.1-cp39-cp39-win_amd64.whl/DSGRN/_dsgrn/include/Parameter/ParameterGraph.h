/// ParameterGraph.h
/// Shaun Harker
/// 2015-05-24
///
/// Marcio Gameiro
/// 2021-01-30

#pragma once 

#include "common.h"

#include "Parameter/Network.h"
#include "Parameter/Parameter.h" 
#include "Parameter/Configuration.h" 

struct ParameterGraph_;

class ParameterGraph {
public:
  /// constructor
  ParameterGraph ( void );

  /// ParameterGraph
  ///   Assign a network to the parameter graph
  ///   Search in path for logic .dat files
  ParameterGraph ( Network const& network );

  /// assign
  ///   Assign a network to the parameter graph
  ///   Search in path for logic .dat files
  void
  assign ( Network const& network );

  /// size
  ///   Return the number of parameters
  uint64_t
  size ( void ) const;

  /// dimension
  ///   Return the number of nodes in the network
  ///   (i.e. the dimension of the phase space)
  uint64_t 
  dimension ( void ) const;

  /// logicsize
  ///   Given a network node 0 <= i < dimension(), 
  ///   Return the size of the factor graph associated
  ///   with network node i (for some fixed output edge ordering)
  uint64_t
  logicsize ( uint64_t i ) const;

  /// ordersize
  ///   Given a network node 0 <= i < dimension(), 
  ///   returns the number of output edge orderings
  ///   network().outputs().size() !
  uint64_t
  ordersize ( uint64_t i ) const;

  /// factorgraph
  ///   Return the list of hex-code strings
  ///   representing the logic parameters of the ith
  ///   ith factor graph
  std::vector<std::string> const& 
  factorgraph ( uint64_t i ) const;
  
  /// parameter
  ///   Return the parameter associated with an index
  Parameter
  parameter ( uint64_t index ) const;

  /// index
  ///   Return the index associated with a parameter
  ///   If the parameter presented is invalid, return -1
  uint64_t
  index ( Parameter const& p ) const;

  /// adjacencies
  ///   Return the adjacent parameter indices of the given type
  ///   to a given parameter index. The default type is used if
  ///   type is not specified.
  std::vector<uint64_t>
  adjacencies ( uint64_t const index, std::string const& type = "" ) const;

  /// network
  ///   Return network
  Network const
  network ( void ) const;

  /// fixedordersize
  ///   Return the number of parameters
  ///   for a fixed ordering
  uint64_t
  fixedordersize ( void ) const;

  /// reorderings
  ///   Return of reorderings
  ///   Note: size() = fixedordersize()*reorderings()
  uint64_t
  reorderings ( void ) const;

  /// operator <<
  ///   Stream out information about parameter graph.
  friend std::ostream& operator << ( std::ostream& stream, ParameterGraph const& pg );

private:
  std::shared_ptr<ParameterGraph_> data_;
  uint64_t _factorial ( uint64_t m ) const;
};

struct ParameterGraph_ {
  Network network_;
  uint64_t size_;
  uint64_t reorderings_;
  uint64_t fixedordersize_;
  std::vector<uint64_t> logic_place_values_;
  std::vector<uint64_t> order_place_values_;
  std::vector<std::vector<std::string>> factors_;
  std::vector<std::unordered_map<std::string,uint64_t>> factors_inv_;
  std::vector<uint64_t> logic_place_bases_;
  std::vector<uint64_t> order_place_bases_;
};

/// Python Bindings

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
namespace py = pybind11;

inline void
ParameterGraphBinding (py::module &m) {
  py::class_<ParameterGraph, std::shared_ptr<ParameterGraph>>(m, "ParameterGraph")
    .def(py::init<>())
    .def(py::init<Network const&>())
    .def("size", &ParameterGraph::size)
    .def("dimension", &ParameterGraph::dimension)
    .def("logicsize", &ParameterGraph::logicsize)
    .def("ordersize", &ParameterGraph::ordersize)
    .def("factorgraph", &ParameterGraph::factorgraph)
    .def("parameter", &ParameterGraph::parameter)    
    .def("index", &ParameterGraph::index)
    .def("adjacencies", &ParameterGraph::adjacencies, py::arg("index"), py::arg("type") = "")
    .def("network", &ParameterGraph::network)
    .def("fixedordersize", &ParameterGraph::fixedordersize)
    .def("reorderings", &ParameterGraph::reorderings)
    .def("__str__", [](ParameterGraph * lp){ std::stringstream ss; ss << *lp; return ss.str(); })
    .def(py::pickle(
    [](ParameterGraph const& p) { // __getstate__
        /* Return a tuple that fully encodes the state of the object */
        return py::make_tuple(p.network());
    },
    [](py::tuple t) { // __setstate__
        if (t.size() != 1)
            throw std::runtime_error("Unpickling ParameterGraph object: Invalid state!");
        /* Create a new C++ instance */
        return ParameterGraph(t[0].cast<Network>());
    }));
}
