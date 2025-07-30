/// Network.hpp
/// Shaun Harker
/// 2015-05-22
///
/// Marcio Gameiro
/// 2024-12-01

#pragma once

#ifndef INLINE_IF_HEADER_ONLY
#define INLINE_IF_HEADER_ONLY
#endif

#include "Network.h"

INLINE_IF_HEADER_ONLY Network::
Network ( void ) {
  data_ . reset ( new Network_ );
}

INLINE_IF_HEADER_ONLY Network::
Network ( std::string const& s, std::string const& edge_blowup ) {
  // The default value for edge_blowup is "", which uses the default "neg"
  std::string e_blowup = edge_blowup.empty() ? "neg" : edge_blowup;
  // Remove leading and trailing whitespaces of e_blowup
  e_blowup = std::regex_replace(e_blowup, std::regex("^ +| +$|( ) +"), "$1");
  // Transform all letters of e_blowup to lower case
  std::transform(e_blowup.begin(), e_blowup.end(), e_blowup.begin(), ::tolower);
  // Check if edge blowup flag e_blowup is valid
  if ( not ( e_blowup == "neg" or e_blowup == "pos" or e_blowup == "all" or e_blowup == "none" ) ) {
    throw std::runtime_error ( "Invalid edge blowup flag!" );
  }
  // Create the network
  data_ . reset ( new Network_ );
  // The default is to blowup negative self-edges only
  // Change the default values if necessary
  if ( e_blowup == "pos" ) {
    // Blowup positive self-edges only
    data_ -> pos_edge_blowup_ = true;
    data_ -> neg_edge_blowup_ = false;
  }
  if ( e_blowup == "all" ) {
    // Blowup all self-edges
    data_ -> pos_edge_blowup_ = true;
    data_ -> neg_edge_blowup_ = true;
  }
  if ( e_blowup == "none" ) {
    // Do not blowup self-edges
    data_ -> pos_edge_blowup_ = false;
    data_ -> neg_edge_blowup_ = false;
  }
  assign(s);
}

INLINE_IF_HEADER_ONLY void Network::
assign ( std::string const& s ) {
  auto colon = s.find(':');
  if ( colon != std::string::npos ) {
    data_ -> specification_ = s;
    _parse ( _lines () );
  } else {
    load(s);
  }
}

INLINE_IF_HEADER_ONLY void Network::
load ( std::string const& filename ) {
  std::ifstream infile ( filename );
  if ( not infile . good () ) {
    throw std::runtime_error ( "Problem loading network specification file " + filename );
  }
  std::string line;
  while ( std::getline ( infile, line ) ) {
    data_ -> specification_ += line + '\n';
  }
  infile . close ();
  _parse ( _lines () );
}

INLINE_IF_HEADER_ONLY uint64_t Network::
size ( void ) const {
  return data_ ->  name_by_index_ . size ();
}

INLINE_IF_HEADER_ONLY uint64_t Network::
index ( std::string const& name ) const {
  return data_ ->  index_by_name_ . find ( name ) -> second;
}

INLINE_IF_HEADER_ONLY std::string const& Network::
name ( uint64_t index ) const {
  return data_ ->  name_by_index_[index];
}

INLINE_IF_HEADER_ONLY std::vector<uint64_t> const& Network:: 
inputs ( uint64_t index ) const {
  return data_ ->  inputs_[index];
}

INLINE_IF_HEADER_ONLY std::vector<uint64_t> const& Network:: 
outputs ( uint64_t index ) const {
  return data_ ->  outputs_[index];
}

INLINE_IF_HEADER_ONLY std::vector<std::vector<uint64_t>> const& Network::
logic ( uint64_t index ) const {
  return data_ ->  logic_by_index_ [ index ];
}

INLINE_IF_HEADER_ONLY bool Network::
essential ( uint64_t index ) const {
  return data_ -> essential_ [ index ];
}

INLINE_IF_HEADER_ONLY char Network::
parameter_type ( uint64_t index ) const {
  return data_ -> parameter_type_ [ index ];
}

INLINE_IF_HEADER_ONLY bool Network::
interaction ( uint64_t source, uint64_t target ) const {
  return data_ ->  edge_type_ . find ( std::make_pair ( source, target ) ) -> second;
}

INLINE_IF_HEADER_ONLY bool Network::
pos_edge_blowup ( void ) const {
  return data_ -> pos_edge_blowup_;
}

INLINE_IF_HEADER_ONLY bool Network::
neg_edge_blowup ( void ) const {
  return data_ -> neg_edge_blowup_;
}

INLINE_IF_HEADER_ONLY uint64_t Network::
num_thresholds ( uint64_t index ) const {
  return data_ -> num_thresholds_ [ index ];
}

INLINE_IF_HEADER_ONLY uint64_t Network::
order ( uint64_t source, uint64_t target ) const {
  return data_ ->  order_ . find ( std::make_pair ( source, target ) ) -> second;
}

INLINE_IF_HEADER_ONLY  std::vector<uint64_t> Network::
domains ( void ) const {
  std::vector<uint64_t> result;
  for ( auto n_thresholds : data_ -> num_thresholds_ ) {
    result . push_back ( n_thresholds + 1 );
  }
  return result;
}

INLINE_IF_HEADER_ONLY std::string Network::
specification ( void ) const {
  return data_ -> specification_;
}

INLINE_IF_HEADER_ONLY std::string Network::
graphviz ( std::vector<std::string> const& theme ) const {
  std::stringstream result;
  // std::cout << "graphviz. Looping through nodes.\n";
  result << "digraph {\n";
  result << "bgcolor = " << theme[0] << ";";
  for ( uint64_t i = 0; i < size (); ++ i ) {
    result << "\"" << name(i) << "\"" << " [style=filled fillcolor=" << theme[1] << "];\n";
  }
  std::string normalhead ("normal");
  std::string blunthead ("tee");
  // std::cout << "graphviz. Looping through edges.\n";
  for ( uint64_t target = 0; target < size (); ++ target ) {
    std::vector<std::vector<uint64_t>> logic_struct = logic ( target );
    std::reverse ( logic_struct . begin (), logic_struct . end () ); // prefer black
    uint64_t partnum = 0;
    for ( auto const& part : logic_struct ) {
      for ( uint64_t source : part ) {
        // std::cout << "Checking type of edge from " << source << " to " << target << "\n";
        std::string head = interaction(source,target) ? normalhead : blunthead;
        result << "\"" << name(source) << "\" -> \"" << name(target) << "\" [color=" << theme[partnum+2] << " arrowhead=\"" << head << "\"];\n";
      }
      ++ partnum;
      if ( partnum + 2 == theme . size () ) partnum = 0;
    }
  }  
  result << "}\n";
  return result . str ();
}

namespace DSGRN_parse_tools {
  // http://stackoverflow.com/questions/236129/split-a-string-in-c
  INLINE_IF_HEADER_ONLY std::vector<std::string> &split(const std::string &s, char delim, std::vector<std::string> &elems) {
    std::stringstream ss(s);
    std::string item;
    while (std::getline(ss, item, delim)) {
        elems.push_back(item);
    }
    return elems;
  }
  INLINE_IF_HEADER_ONLY std::vector<std::string> split(const std::string &s, char delim) {
    std::vector<std::string> elems;
    split(s, delim, elems);
    return elems;
  }
  INLINE_IF_HEADER_ONLY std::string& removeSpace ( std::string &s ) {
    s.erase(std::remove_if(s.begin(), s.end(), (uint64_t(*)(uint64_t))isspace), s.end());
    return s;
  }
}

/// _lines
///   Open the network file and read it line by line
INLINE_IF_HEADER_ONLY std::vector<std::string> Network::
_lines ( void ) {
  // Remove quote marks if they exist, and convert "\n" substrings to newlines
  std::string & str = data_ -> specification_;
  const std::regex quote_regex("\"", std::regex::basic);
  const std::regex newline_regex("\n", std::regex::basic);
  data_ -> specification_ = std::regex_replace(data_ -> specification_, newline_regex, "\n" );
  data_ -> specification_ = std::regex_replace(data_ -> specification_, quote_regex, "" );

  // Parse the lines
  std::vector<std::string> result;
  std::stringstream spec ( data_ -> specification_ );
  std::string line;
  while ( std::getline ( spec, line ) ) {
    result . push_back ( line );
  }
  return result;
}

/// parse
///   Iterate through lines and produce data structures
INLINE_IF_HEADER_ONLY void Network::
_parse ( std::vector<std::string> const& lines ) {
  using namespace DSGRN_parse_tools;
  std::vector<std::string> logic_strings;
  std::map<std::string, bool> essential_nodes;
  std::map<std::string, char> nodes_parameter_type;
  //std::vector<std::string> constraint_strings;
  // Learn the node names
  for ( auto const& line : lines ) {
    auto splitline = split ( line, ':' );
    if ( splitline . empty () ) continue;
    removeSpace(splitline[0]);
    // Skip if empty string
    if ( splitline[0] == "" ) continue;
    // If begins with . or @, skip
    if ( (splitline[0][0] == '.') || (splitline[0][0] == '@' ) ) continue;
    data_ ->  name_by_index_ . push_back ( splitline[0] );
    // If no logic specified, zero inputs.
    if ( splitline . size () < 2 ) {
      logic_strings . push_back ( " " );
    } else {
      logic_strings . push_back ( splitline[1] );
    }
    //std::cout << line << " has " << splitline.size() << " parts.\n";
    // Default is non-essential and DSGRN (D) parameter
    essential_nodes [ splitline[0] ] = false;
    nodes_parameter_type [ splitline[0] ] = 'D';
    if ( splitline . size () >= 3 ) {
      // Check if essential, Boolean, or multi-Boolean parameter
      removeSpace(splitline[2]);
      for ( char c : splitline[2] ) {
        if ( (c != 'E') && (c != 'B') && (c != 'M') ) {
          throw std::runtime_error ( "Problem parsing network specification file: Invalid parameter type" );
        }
        if ( c == 'E' ) {
          essential_nodes [ splitline[0] ] = true;
          //std::cout << "Marking " << splitline[0] << " as essential \n";
        }
        if ( c == 'B' ) {
          if ( nodes_parameter_type [ splitline[0] ] == 'D' ) {
            nodes_parameter_type [ splitline[0] ] = 'B';
          } else {
            throw std::runtime_error ( "Problem parsing network specification file: Multiple parameter types" );
          }
        }
        if ( c == 'M' ) {
          if ( nodes_parameter_type [ splitline[0] ] == 'D' ) {
          nodes_parameter_type [ splitline[0] ] = 'M';
          } else {
            throw std::runtime_error ( "Problem parsing network specification file: Multiple parameter types" );
          }
        }
      }
    }
  }
  // Index the node names
  uint64_t loop_index = 0;
  data_ -> essential_ . resize ( essential_nodes . size () );
  data_ -> parameter_type_ . resize ( nodes_parameter_type . size () );
  for ( auto const& name : data_ -> name_by_index_ ) {
    data_ -> index_by_name_ [ name ] = loop_index;
    data_ -> essential_ [ loop_index ] = essential_nodes [ name ];
    data_ -> parameter_type_ [ loop_index ] = nodes_parameter_type [ name ];
    ++ loop_index;
  }
  // Learn the logics
  // Trick: ignore everything but node names and +'s. 
  // Example: a + ~ b c d + e  corresponds to (a+~b)(c)(d+e)
  uint64_t target = 0;
  for ( auto const& logic_string : logic_strings ) {
    //std::cout << "Processing " << logic_string << "\n";
    std::vector<std::vector<uint64_t>> logic_struct;
    std::vector<uint64_t> factor;
    std::string token;
    bool parity = true;
    bool appending = true;

    auto flush_factor = [&] () {
      if ( factor . empty () ) return;
      // Put factor into canonical ordering
      std::sort ( factor.begin(), factor.end() );
      logic_struct . push_back ( factor );
      //std::cout << "    Flushing factor ";
      //for ( uint64_t i : factor ) std::cout << name ( i ) << " ";
      //std::cout << "\n";
      factor . clear ();      
    };
    auto flush_token = [&] () {
      if ( token . empty () ) return;
      if ( not appending ) flush_factor ();
      //std::cout << "  Flushing token " << token << "\n";
      if ( data_ -> index_by_name_ . count ( token ) == 0 ) {
        throw std::runtime_error ( "Problem parsing network specification file: " 
                                   "Invalid input variable " + token );
      }
      uint64_t source = data_ ->  index_by_name_ [ token ];
      factor . push_back ( source );
      data_ ->  edge_type_[std::make_pair( source, target )] = parity;
      //std::cout << "Creating edge from " << source << " to " << target << "\n";
      token . clear ();
      appending = false;
      parity = true;
    };
    for ( char c : logic_string ) {
      //std::cout << "Reading character " << c << "\n";
      if ( ( c == '\t' ) || (c == ' ') || (c == '(') || (c == ')') || (c == '+') || (c == '~') ) {
        flush_token ();
      } else {
        token . push_back ( c );
      }
      if ( c == '+' ) { 
        appending = true;
        //std::cout << "  Detected +\n";
      }
      if ( c == '~' ) parity = false;
    }
    flush_token ();
    flush_factor ();
    //std::cout << "The logic_struct formed.\n";
    // Ensure logic_struct is acceptable (no repeats!)
    std::unordered_set<uint64_t> inputs;
    for ( auto const& factor : logic_struct ) {
      //std::cout << "# ";
      for ( auto i : factor ) {
        //std::cout << i << " ";
        if ( inputs . count ( i ) ) {
          throw std::runtime_error ( "Problem parsing network specification file: Repeated inputs in logic" );
        }
        inputs . insert ( i );
      }
    }
    //std::cout << "\n";
    //std::cout << "The logic_struct is acceptable.\n";
    // Compare partitions by (size, max), where size is length and max is maximum index
    auto compare_partition = [](std::vector<uint64_t> const& lhs, std::vector<uint64_t> const& rhs) {
      if ( lhs . size () < rhs . size () ) return true;
      if ( lhs . size () > rhs . size () ) return false;
      uint64_t max_lhs = * std::max_element ( lhs.begin(), lhs.end() );
      uint64_t max_rhs = * std::max_element ( rhs.begin(), rhs.end() );
      if ( max_lhs < max_rhs ) return true;
      if ( max_lhs > max_rhs ) return false;  /* unreachable -> */ return false;
    };
    // Put the logic struct into a canonical ordering.
    std::sort ( logic_struct.begin(), logic_struct.end(), compare_partition );
    data_ -> logic_by_index_ . push_back ( logic_struct );
    //std::cout << "The logic_struct has been incorporated into the network.\n";
    ++ target;
  }
  // Compute inputs and outputs.
  data_ -> inputs_ . resize ( size () );
  data_ -> outputs_ . resize ( size () );
  for ( target = 0; target < size (); ++ target ) {
    for ( auto const& factor : logic ( target ) ) {
      for ( uint64_t source : factor ) {
        data_ -> inputs_[target] . push_back ( source );
        data_ -> outputs_[source] . push_back ( target );
        data_ -> order_[std::make_pair(source,target)] = data_ ->  outputs_[source].size()-1;
      }
    }
  }
  // Set number of thresholds for each node
  data_ -> num_thresholds_ . resize ( size () );
  for ( uint64_t d = 0; d < size (); ++ d ) {
    std::vector<uint64_t> outedges = outputs ( d );
    // Treat the no out edge case as one out edge
    uint64_t m = outedges . size() ? outedges . size() : 1;
    // Get the number of self edges
    uint64_t n_self_edges = std::count( outedges . begin(), outedges . end(), d );
    // Do not count positive self edges if pos_edge_blowup is false
    if ( ( not pos_edge_blowup () ) and ( n_self_edges > 0 ) ) {
      if ( interaction ( d, d ) ) { // If positive self edge
        n_self_edges = 0;
      }
    }
    // Do not count negative self edges if neg_edge_blowup is false
    if ( ( not neg_edge_blowup () ) and ( n_self_edges > 0 ) ) {
      if ( not interaction ( d, d ) ) { // If negative self edge
        n_self_edges = 0;
      }
    }
    // Each self edge creates an additional threshold
    data_ -> num_thresholds_[d] = m + n_self_edges;
  }
  // std::cout << "_parse complete.\n";
}

INLINE_IF_HEADER_ONLY std::ostream& operator << ( std::ostream& stream, Network const& network ) {
  stream << "[";
  bool first1 = true;
  for ( uint64_t v = 0; v < network.size (); ++ v ) {
    if ( first1 ) first1 = false; else stream << ",";
    stream << "[\"" << network.name(v) << "\","; // node
    std::vector<std::vector<uint64_t>> logic_struct = network.logic ( v );
    stream << "["; // logic_struct
    bool first2 = true;
    for ( auto const& part : logic_struct ) {
      if ( first2 ) first2 = false; else stream << ",";
      stream << "["; // factor
      bool first3 = true;
      for ( uint64_t source : part ) {
        if ( first3 ) first3 = false; else stream << ",";
        std::string head = network.interaction(source,v) ? "" : "~";
        stream << "\"" << head << network.name(source) << "\"";
      }
      stream << "]"; // factor
    }
    stream << "],"; // logic_struct
    stream << "["; // outputs
    bool first4 = true;
    for ( uint64_t target : network.outputs ( v ) ) {
      if ( first4 ) first4 = false; else stream << ",";
      stream << "\"" << network.name(target) << "\"";
    }
    stream << "]"; // outputs 
    stream << "]"; // node
  }
  stream << "]"; // network
  return stream;
}
