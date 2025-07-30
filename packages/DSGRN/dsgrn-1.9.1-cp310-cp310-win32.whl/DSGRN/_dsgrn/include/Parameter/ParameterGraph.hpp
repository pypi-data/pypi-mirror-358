/// ParameterGraph.hpp
/// Shaun Harker
/// 2015-05-24
///
/// Marcio Gameiro
/// 2024-12-01

#pragma once

#ifndef INLINE_IF_HEADER_ONLY
#define INLINE_IF_HEADER_ONLY
#endif

#include "ParameterGraph.h"

INLINE_IF_HEADER_ONLY ParameterGraph::
ParameterGraph ( void ) {
  data_ . reset ( new ParameterGraph_ );
}

INLINE_IF_HEADER_ONLY ParameterGraph::
ParameterGraph ( Network const& network ) {
  assign ( network );
}

INLINE_IF_HEADER_ONLY void ParameterGraph::
assign ( Network const& network ) {
  std::string path = configuration() -> get_path() + "/logic";
  data_ . reset ( new ParameterGraph_ );
  data_ -> network_ = network;
  data_ -> reorderings_ = 1;
  data_ -> fixedordersize_ = 1;
  // Load the logic files one by one.
  uint64_t D = data_ -> network_ . size ();
  for ( uint64_t d = 0; d < D; ++ d ) {
    uint64_t n = data_ -> network_ . inputs ( d ) . size ();
    // Treat the no out edge case as one out edge
    uint64_t m = data_ -> network_ . outputs ( d ) . size () ? data_ -> network_ . outputs ( d ) . size () : 1;
    data_ -> order_place_bases_ . push_back ( _factorial ( m ) );
    data_ -> reorderings_ *= data_ -> order_place_bases_ . back ();
    std::vector<std::vector<uint64_t>> const& logic_struct = data_ -> network_ . logic ( d );
    std::stringstream ss;
    ss << path << "/" << n <<  "_" << m;
    if ( data_ -> network_ . parameter_type ( d ) == 'D' ) {        // If DSGRN (D) parameter
      for ( auto const& p : logic_struct ) ss <<  "_" << p.size();
    } else if ( data_ -> network_ . parameter_type ( d ) == 'B' ) { // If Boolean (B) parameter
      ss <<  "_B";
    } else { // Multi-Boolean (M) parameter
      ss <<  "_MB";
    }
    if ( data_ -> network_ . essential ( d ) ) ss << "_E";
    ss << ".dat";
    //std::cout << "Acquiring logic data in " << ss.str() << "\n";
    std::vector<std::string> hex_codes;
    std::ifstream infile ( ss.str() );
    if ( not infile . good () ) {
      throw std::runtime_error ( "Error: Could not find logic resource " + ss.str() + ".\n");
    }
    std::string line;
    std::unordered_map<std::string,uint64_t> hx;
    uint64_t counter = 0;
    while ( std::getline ( infile, line ) ) {
      hex_codes . push_back ( line );
      hx [ line ] = counter;
      ++counter;
    }
    infile . close ();
    data_ -> factors_ . push_back ( hex_codes );
    data_ -> factors_inv_ . push_back ( hx );
    data_ -> logic_place_bases_ . push_back ( hex_codes . size () );
    data_ -> fixedordersize_ *= hex_codes . size ();
    //std::cout << d << ": " << hex_codes . size () << " factorial(" << m << ")=" << _factorial ( m ) << "\n";
  }
  data_ -> size_ = data_ -> fixedordersize_ * data_ -> reorderings_;
  // construction of place_values_ used in method index
  data_ -> logic_place_values_ . resize ( D, 0 );
  data_ -> order_place_values_ . resize ( D, 0 );
  data_ -> logic_place_values_ [ 0 ] = 1;
  data_ -> order_place_values_ [ 0 ] = 1;
  for ( uint64_t i = 1; i < D; ++ i ) {
    data_ -> logic_place_values_ [ i ] = data_ -> logic_place_bases_ [ i - 1 ] *
                                   data_ -> logic_place_values_ [ i - 1 ];
    data_ -> order_place_values_ [ i ] = data_ -> order_place_bases_ [ i - 1 ] *
                                  data_ -> order_place_values_ [ i - 1 ];
  }
}

INLINE_IF_HEADER_ONLY uint64_t ParameterGraph::
size ( void ) const {
  return data_ -> size_;
}

INLINE_IF_HEADER_ONLY uint64_t ParameterGraph::
dimension ( void ) const {
  return network().size();
}

INLINE_IF_HEADER_ONLY uint64_t ParameterGraph::
logicsize ( uint64_t i ) const {
  return data_ -> logic_place_bases_ [ i ];
}

INLINE_IF_HEADER_ONLY uint64_t ParameterGraph::
ordersize ( uint64_t i ) const {
  return data_ -> order_place_bases_ [ i ];
}

INLINE_IF_HEADER_ONLY std::vector<std::string> const& ParameterGraph::
factorgraph ( uint64_t i ) const {
  return data_ -> factors_[i];
}

INLINE_IF_HEADER_ONLY Parameter ParameterGraph::
parameter ( uint64_t index ) const {
  //std::cout << data_ -> "ParameterGraph::parameter( " << index << " )\n";
  if ( index >= size () ) {
    throw std::runtime_error ( "ParameterGraph::parameter Index out of bounds");
  }
  uint64_t logic_index = index % data_ -> fixedordersize_;
  uint64_t order_index = index / data_ -> fixedordersize_;

  uint64_t D = data_ -> network_ . size ();
  std::vector<uint64_t> logic_indices;
  for ( uint64_t d = 0; d < D; ++ d ) {
    uint64_t i = logic_index % data_ -> logic_place_bases_ [ d ];
    logic_index /= data_ -> logic_place_bases_ [ d ];
    logic_indices . push_back ( i );
  }
  std::vector<uint64_t> order_indices;
  for ( uint64_t d = 0; d < D; ++ d ) {
    uint64_t i = order_index % data_ -> order_place_bases_ [ d ];
    order_index /= data_ -> order_place_bases_ [ d ];
    order_indices . push_back ( i );
  }

  std::vector<LogicParameter> logic;
  std::vector<OrderParameter> order;
  for ( uint64_t d = 0; d < D; ++ d ) {
    uint64_t n = data_ -> network_ . inputs ( d ) . size ();
    // Treat the no out edge case as one out edge
    uint64_t m = data_ -> network_ . outputs ( d ) . size () ? data_ -> network_ . outputs ( d ) . size () : 1;
    std::string hex_code = data_ -> factors_ [ d ] [ logic_indices[d] ];
    LogicParameter logic_param ( n, m, hex_code );
    OrderParameter order_param ( m, order_indices[d] );
    logic . push_back ( logic_param );
    order . push_back ( order_param );
  }
  Parameter result ( logic, order, data_ -> network_ );
  return result;
}

INLINE_IF_HEADER_ONLY uint64_t ParameterGraph::
index ( Parameter const& p ) const {
  // Obtain logic and order information
  std::vector<LogicParameter> const& logic = p . logic ( );
  std::vector<OrderParameter> const& order = p . order ( );

  // Construct Logic indices
  std::vector<uint64_t> logic_indices;
  uint64_t D = data_ -> network_ . size ();
  for ( uint64_t d = 0; d < D; ++d ) {
    std::string hexcode = logic [ d ] . hex ( );
    auto it = data_ -> factors_inv_[d] . find ( hexcode );
    if ( it != data_ -> factors_inv_[d] . end ( )  ) {
      logic_indices . push_back ( it -> second );
    } else {
      return -1;
    }
  }

  // Construct Order indices
  std::vector<uint64_t> order_indices;
  for ( uint64_t d = 0; d < D; ++ d ) {
    order_indices . push_back ( order[d].index() );
  }

  // Construct index
  uint64_t logic_index = 0;
  uint64_t order_index = 0;
  for ( uint64_t d = 0; d < D; ++ d ) {
    logic_index += data_ -> logic_place_values_[d] * logic_indices[d];
    order_index += data_ -> order_place_values_[d] * order_indices[d];
  }
  uint64_t index = order_index * data_ -> fixedordersize_ + logic_index;

  return (index < size()) ? index : -1;
}

INLINE_IF_HEADER_ONLY std::vector<uint64_t> ParameterGraph::
adjacencies ( const uint64_t myindex, std::string const& type ) const {
  // The default value for type is "", which uses the default type "pre"
  std::string adj_type = type.empty() ? "pre" : type;
  if ( not ( adj_type == "pre" or adj_type == "fixedorder" or adj_type == "codim1" ) ) {
    throw std::runtime_error ( "Invalid adjacency type!" );
  }
  std::vector<uint64_t> output;
  Parameter p = parameter ( myindex );
  std::vector<LogicParameter> logics = p . logic ( );
  std::vector<OrderParameter> orders = p . order ( );

  uint64_t D = data_ -> network_ . size ( );

  std::vector<LogicParameter> logicsTmp = logics;
  std::vector<OrderParameter> ordersTmp = orders;

  // Check if order adjacency correspond to a co-dim 1 boundary
  auto codim1_adj_order = [&]( OrderParameter op_adj, uint64_t d ) {
    // Get permutations for this and adjacent order parameters
    std::vector<uint64_t> op_perm = orders [ d ] . permutation ( );
    std::vector<uint64_t> adj_perm = op_adj . permutation ( );
    // Get indices of permuted thresholds (should be 2)
    std::vector<uint64_t> perm_thres;
    for ( uint64_t i = 0; i < op_perm . size (); ++ i ) {
      if ( not ( op_perm [i] == adj_perm [i] ) ) {
        perm_thres . push_back (i);
      }
    }
    // Number of permuted thresholds should be 2
    if ( not ( perm_thres . size () == 2 ) ) {
      throw std::runtime_error ( "Invalid adjacent order!" );
    }
    // Now check if adjacent order if a co-dim 1 order
    // Indices of the swapped thresholds
    uint64_t j0 = perm_thres [0];
    uint64_t j1 = perm_thres [1];
    // Get input/output sizes information
    uint64_t n = data_ -> network_ . inputs ( d ) . size ();
    uint64_t m = data_ -> network_  . outputs ( d ) . size ();
    uint64_t N = ( 1LL << n );
    // The adjacent order is a co-dim 1 order if there is no
    // input combination (p_i) in between the two thresholds
    // that got swapped. This is true if both thresholds
    // produce the same signs for all input combinations.
    for ( uint64_t i = 0; i < N; ++ i ) {
      // Return false if signs differ
      if ( logics [d] ( i * m + j0 ) != logics [d] ( i * m + j1 ) ) {
        return false;
      }
    }
    return true;
  };

  // Compute adjacent order parameters if needed
  // For type fixedorder do not want adjacent orders
  if ( not ( type == "fixedorder" ) ) {
    for ( uint64_t d = 0; d < D; ++d ) {
      std::vector<OrderParameter> op_adjacencies = orders [ d ] . adjacencies ( );
      if ( op_adjacencies.size() > 0 ) {
        for ( auto op_adj : op_adjacencies ) {
          // Check if adj order is co-dim 1 for type codim1
          if ( ( type == "codim1" ) and ( not codim1_adj_order ( op_adj, d ) ) )
            continue;
          // Add adjacency order to list of adjacent parameters
          orders [ d ] = op_adj;
          Parameter adj_p ( logics, orders, data_ -> network_ );
          uint64_t index_adj = ParameterGraph::index ( adj_p );
          if ( index_adj != -1 ) { output . push_back ( index_adj ); }
          orders [ d ] = ordersTmp [ d ];
        }
      }
    }
  }
  // Compute adjacent logic parameters
  for ( uint64_t d = 0; d < D; ++d ) {
    std::vector<LogicParameter> lp_adjacencies = logics [ d ] . adjacencies ( );
    for ( auto lp_adj : lp_adjacencies ) {
      if ( data_ -> factors_inv_[d] . count ( lp_adj . hex ( ) ) == 0 ) { continue; }
      logics [ d ] = lp_adj;
      Parameter adj_p ( logics, orders, data_ -> network_ );
      uint64_t index_adj = ParameterGraph::index ( adj_p );
      if ( index_adj != -1 ) { output . push_back ( index_adj ); }
      logics [ d ] = logicsTmp [ d ];
    }
  }
  std::sort ( output . begin ( ), output . end ( ) );
  return output;
}

INLINE_IF_HEADER_ONLY Network const ParameterGraph::
network ( void ) const {
  return data_ -> network_;
}

INLINE_IF_HEADER_ONLY std::ostream& operator << ( std::ostream& stream, ParameterGraph const& pg ) {
  stream <<  "(ParameterGraph: "<< pg.size() << " parameters, "
         << pg.network().size() << " nodes)";
  return stream;
}

INLINE_IF_HEADER_ONLY uint64_t ParameterGraph::
fixedordersize ( void ) const {
  return data_ -> fixedordersize_;
}

INLINE_IF_HEADER_ONLY uint64_t ParameterGraph::
reorderings ( void ) const {
  return data_ -> reorderings_;
}

INLINE_IF_HEADER_ONLY uint64_t ParameterGraph::
_factorial ( uint64_t m ) const {
  static const std::vector<uint64_t> table =
    { 1, 1, 2, 6, 24, 120, 720, 5040, 40320, 362880};
  if ( m < 10 ) return table [ m ]; else return m * _factorial ( m - 1 );
}
