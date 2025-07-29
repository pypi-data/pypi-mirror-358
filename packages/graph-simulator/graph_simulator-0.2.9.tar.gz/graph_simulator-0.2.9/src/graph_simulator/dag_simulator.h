#ifndef DAG_SIMULATOR_H
#define DAG_SIMULATOR_H

#include "kernels.h"
#include "data.h"
#include <iostream>
#include <vector>
#include <map>
#include <string>
#include <stdexcept>
#include <random>
#include <tuple>
#include <yaml-cpp/yaml.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <unordered_set>
#include <queue>
#include <algorithm>

namespace py = pybind11;

class DagSimulator {
public:
    // Constructor that takes a YAML file path
    DagSimulator(const std::string& config_path);
    std::vector<std::map<std::string, float>> run(int steps = 10);
    void print_dependencies(const std::string& key) const;
    void print_node_map() const;

private:
    int time_step;
    std::map<std::string, std::map<int, std::vector<std::string>>> dependencies_map;
    std::vector<Node> graph;
    std::map<std::string, YAML::Node> kernel_params;  // Store the kernel parameters for each key
    std::unordered_map<std::pair<int, std::string>, Node*, PairHash> node_map;
    // std::map<std::string, TermsContainer> terms_map;
    std::map<std::string, std::unique_ptr<Kernel>> kernel_map;
    std::vector<std::string> topo_order;
    
    std::vector<std::map<std::string, float>> collect_data() const;
    void parse_config(const YAML::Node& config);
    void process_node(const std::string& key);
    float compute_value(const std::string& key) const;
    std::vector<Node*> get_parents(const std::map<int, std::vector<std::string>>& deps, const Node* node) const;
    void init_graph(int steps = 5);
    void print_graph() const;
    std::vector<std::string> compute_topological_order() const;
    Observation get_observation(const std::map<int, std::vector<std::string>>& deps, int time_step) const;
    void print_observation(const std::string& node, const Observation& observation) const;
    std::string get_node_name(const std::string& key, int time_step) const;
    size_t calculate_collected_data_size(const Data& collected_data);
};

#endif // DAG_SIMULATOR_H