#include "dag_simulator.h"
#include <chrono>
using namespace std::chrono;

DagSimulator::DagSimulator(const std::string& config_path) : time_step(0) {
    YAML::Node config = YAML::LoadFile(config_path);
    parse_config(config);

    // Compute topological order
    topo_order = compute_topological_order();

    // Kernel map
    for (const auto& key : kernel_params) {
        std::string kernel_type = kernel_params.at(key.first)["type"].as<std::string>();
        if (kernel_type == "uniform") {
            kernel_map[key.first] = std::make_unique<UniformKernel>(kernel_params.at(key.first), node_map);
        } else if (kernel_type == "linear") {
            kernel_map[key.first] = std::make_unique<LinearKernel>(kernel_params.at(key.first), node_map);
        } else if (kernel_type == "poisson") {
            kernel_map[key.first] = std::make_unique<PoissonKernel>(kernel_params.at(key.first), node_map);
        } else if (kernel_type == "binomial") {
            kernel_map[key.first] = std::make_unique<BinomialKernel>(kernel_params.at(key.first), node_map);
        } else if (kernel_type == "mixed") {
            kernel_map[key.first] = std::make_unique<MixedKernel>(kernel_params.at(key.first), node_map);
        } else if (kernel_type == "constant") {
            kernel_map[key.first] = std::make_unique<ConstantKernel>(kernel_params.at(key.first), node_map);
        } else {
            throw std::invalid_argument("Kernel type not supported: " + kernel_type);
        }

        if (!kernel_map[key.first]->is_sample_domain_set()) {
            throw std::runtime_error("sample_domain is not set for " + kernel_type + " kernel");
        }
    }

    // Reserve spaces
    graph.reserve(1000000);
    node_map.reserve(1000000);
}

std::vector<std::map<std::string, float>> DagSimulator::run(int steps) {
    // Initialize the graph
    init_graph(5);

    // Data collection
    Data collected_data;

    // Run steps
    size_t previous_capacity = graph.capacity();
    for (int i = 0; i <= steps; ++i) {
        // auto start = high_resolution_clock::now();

        for (const auto& key : topo_order) {
            if (dependencies_map.find(key) != dependencies_map.end()) {
                // Construct node
                Node node(time_step, key);

                // Set value
                node.value = kernel_map.at(key)->predict(time_step);

                // Add node to graph
                graph.push_back(node);

                // Add node to node_map
                node_map[std::make_pair(time_step, key)] = &graph.back();
            }
        }

        // Check if the graph vector has been reallocated
        if (graph.capacity() != previous_capacity) {
            std::cout << "Graph vector reallocated. Previous capacity: " << previous_capacity << ", New capacity: " << graph.capacity() << std::endl;
            std:exit(EXIT_FAILURE);
        }

        // auto stop = high_resolution_clock::now();

        // auto duration = duration_cast<microseconds>(stop - start);

        // std::cout << "Time taken by single iteration: "
        //     << duration.count() << " microseconds" << std::endl;


        ++time_step;  // Increment time_step
    }

    return collect_data();
}

// Method to return the data in the graph
std::vector<std::map<std::string, float>> DagSimulator::collect_data() const {
    // Map to group data by time_step
    std::map<int, std::map<std::string, float>> grouped_data;

    // Iterate over the graph to collect data
    for (const auto& node : graph) {
        grouped_data[node.time_step][node.name] = node.value;
    }

    // Convert grouped data to the desired format
    std::vector<std::map<std::string, float>> result;
    result.reserve(grouped_data.size());
    for (const auto& [time_step, data] : grouped_data) {
        result.push_back(data);
    }

    return result;
}

// Method to parse the configuration file
void DagSimulator::parse_config(const YAML::Node& config) {
    for (YAML::const_iterator it = config.begin(); it != config.end(); ++it) {
        std::string key = it->first.as<std::string>();
        // std::cout << "Processing key " << key << std::endl;

        // Kernel parameters
        kernel_params[key] = it->second["kernel"];

        // Dependencies
        YAML::Node dependencies_node = it->second["dependencies"];
        if (dependencies_node.IsNull() || dependencies_node.size() == 0) {
            dependencies_map[key] = {};  // Add an empty entry if dependencies_node is empty
        } else {
            for (YAML::const_iterator dep_it = dependencies_node.begin(); dep_it != dependencies_node.end(); ++dep_it) {
                int time_step = dep_it->first.as<int>();
                std::vector<std::string> dependencies = dep_it->second.as<std::vector<std::string>>();
                dependencies_map[key][time_step] = dependencies;
            }
        }
    }
}

// Method to get parents
std::vector<Node*> DagSimulator::get_parents(const std::map<int, std::vector<std::string>>& deps, const Node* node) const {
    std::vector<Node*> parents;
    for (const auto& [lag, vars] : deps) {  // Loop over each lag in deps
        for (const auto& var : vars) {  // Loop over each var in deps[lag]
            int parent_time_step = node->time_step - lag;
            auto it = node_map.find(std::make_pair(parent_time_step, var));
            if (it != node_map.end()) {
                parents.push_back(it->second);
            }
        }
    }
    return parents;
}

// Method to initialize the graph
void DagSimulator::init_graph(int steps) {

    size_t previous_capacity = graph.capacity();

    // Create nodes
    for (int i = 0; i <= steps; ++i) {
        // std::cout << "Time-step " << time_step << std::endl;
        for (const auto& [key, deps] : dependencies_map) {

            // Construct node
            Node node(time_step, key);

            // Sample value
            node.value = kernel_map.at(key)->sample();

            // Add node to graph
            graph.push_back(node);

            // Check if the graph vector has been reallocated
            if (graph.capacity() != previous_capacity) {
                std::cout << "Graph vector reallocated. Previous capacity: " << previous_capacity << ", New capacity: " << graph.capacity() << std::endl;
                previous_capacity = graph.capacity();
            }

            // Set the map
            node_map[std::make_pair(node.time_step, node.name)] = &graph.back();

        }
        ++time_step;  // Increment time_step
    }

    // Set parents
    for (Node& node : graph) {
        auto deps = dependencies_map[node.name];
        node.parents = get_parents(deps, &node);
    }
}

// Method to compute topological order
std::vector<std::string> DagSimulator::compute_topological_order() const {
    int time_step = 100; // arbitrary time step
    std::vector<std::string> time_step_nodes;
    std::map<std::string, std::vector<std::string>> node_parents;
    std::vector<std::string> topo_order;

    // Compute node_parents from dependencies_map
    for (const auto& [key, deps] : dependencies_map) {
        std::string node = get_node_name(key, time_step);

        std::vector<std::string> parents;
        for (const auto& [lag, vars] : deps) {  // Loop over each lag in deps
            for (const auto& var : vars) {  // Loop over each var in deps[lag]
                std::string parent = get_node_name(var, time_step - lag);
                parents.push_back(parent);
            }
        }

        time_step_nodes.push_back(node);
        node_parents[node] = parents;
    }

    // 1. For all nodes in time_step_nodes, that do not have any parents in time_step_nodes
    // add them to topo_order.
    for (const auto& node : time_step_nodes) {
        bool has_parents_in_time_step_nodes = false;
        for (const auto& parent : node_parents[node]) {
            if (std::find(time_step_nodes.begin(), time_step_nodes.end(), parent) != time_step_nodes.end()) {
                has_parents_in_time_step_nodes = true;
            }
        }
        if (!has_parents_in_time_step_nodes) {
            topo_order.push_back(node);
        }
    }

    // 2. Pop these nodes from time_step_nodes
    for (const auto& node : topo_order) {
        time_step_nodes.erase(std::remove(time_step_nodes.begin(), time_step_nodes.end(), node), time_step_nodes.end());
    }

    // 3. While time_step_nodes is not empty, do the following:
    while (!time_step_nodes.empty()) {
        for (const auto& node : time_step_nodes) {
            if (node.empty()) {
                break;
            }
            //    a. pop all nodes in topo-order from parent nodes.
            for (auto& topo_node: topo_order) {
                node_parents[node].erase(std::remove(node_parents[node].begin(), node_parents[node].end(), topo_node), node_parents[node].end());
            }

            //    b. If there are no parents left in time_step_nodes, add the node to topo_order and pop from time_step_nodes, else continue.
            bool has_parents_in_time_step_nodes = false;
            for (const auto& parent : node_parents[node]) {
                if (std::find(time_step_nodes.begin(), time_step_nodes.end(), parent) != time_step_nodes.end()) {
                    has_parents_in_time_step_nodes = true;
                    break;
                }
            }
            if (!has_parents_in_time_step_nodes) {
                topo_order.push_back(node);
                time_step_nodes.erase(std::remove(time_step_nodes.begin(), time_step_nodes.end(), node), time_step_nodes.end());
            }
        }
    }

    // Replace elements in topo_order to remove the time step part
    for (auto& node : topo_order) {
        size_t pos = node.find('_');
        if (pos != std::string::npos) {
            node = node.substr(0, pos);
        }
    }

    // std::cout << "Topo order:" << std::endl;
    // for (const auto& node : topo_order) {
    //     std::cout << "Node: " << node << std::endl;
    // }

    return topo_order;
}

void DagSimulator::print_dependencies(const std::string& key) const {
    auto it = dependencies_map.find(key);
    if (it != dependencies_map.end()) {
        std::cout << "Dependencies for " << key << ":\n";
        for (const auto& [time_step, deps] : it->second) {
            std::cout << "  Time step " << time_step << ": ";
            for (const auto& dep : deps) {
                std::cout << dep << " ";
            }
            std::cout << std::endl;
        }
    } else {
        std::cout << "Key " << key << " not found in dependencies." << std::endl;
    }
}

void DagSimulator::print_node_map() const {
    std::cout << "Node map:" << std::endl;
    for (const auto& [key, node_ptr] : node_map) {
        auto [time_step, name] = key;
        if (node_ptr) {
            std::cout << "  Key: (" << time_step << ", " << name << "), Name: " << node_ptr->name << " Time-step: " << node_ptr->time_step << " Value: " << node_ptr->value << std::endl;
        } else {
            std::cout << "  Key: (" << time_step << ", " << name << "), Node: nullptr" << std::endl;
        }
    }
}

// Method to print all nodes in the graph
void DagSimulator::print_graph() const {
    std::cout << "Graph nodes:" << std::endl;
    for (const auto& node : graph) {
        std::cout << "Node:" << std::endl;
        std::cout << "  Name: " << node.name << std::endl;
        std::cout << "  Time-step: " << node.time_step << std::endl;
        std::cout << "  Parents: \n";
        if (node.parents.empty()) {
            std::cout << "None";
        } else {
            for (const auto& parent : node.parents) {
                std::cout << "Name: " << parent->name << ", Time-step: " << parent->time_step << "\n";
            }
        }
        std::cout << std::endl;
    }
}

// Method to get observation
// Observation DagSimulator::get_observation(const std::map<int, std::vector<std::string>>& deps, int time_step) const {
//     Observation observation;
//     for (const auto& [lag, vars] : deps) {
//         std::map<std::string, float> values;
//         for (const auto& var : vars) {
//             Node* node = node_map.at(std::make_pair(time_step - lag, var));
//             if (node == nullptr) {
//                 throw std::runtime_error("Parent node " + var + " not found in node_map.");
//             }
//             values[var] = node->value;  // Use var as the key instead of parent_node
//         }
//         observation.add_lag_data(lag, values);
//     }
//     return observation;
// }

// Method to print observation
// void DagSimulator::print_observation(const std::string& node, const Observation& observation) const {
//     std::cout << "Observation for node " << node << ":\n";
//     for (const auto& [lag, values] : observation.get_all_data()) {
//         std::cout << "  Lag " << lag << ":\n";
//         for (const auto& [var, value] : values) {
//             std::cout << "    " << var << ": " << value << "\n";  // Use var instead of parent_node
//         }
//     }
// }

// Method to get node name
std::string DagSimulator::get_node_name(const std::string& key, int time_step) const {
    return key + "_" + std::to_string(time_step);
}

// Function to calculate the size of a map
size_t calculate_map_size(const std::map<std::string, float>& m) {
    size_t size = sizeof(m);
    for (const auto& [key, value] : m) {
        size += sizeof(key) + key.capacity() + sizeof(value);
    }
    return size;
}

// Function to calculate the size of collected_data
size_t DagSimulator::calculate_collected_data_size(const Data& collected_data) {
    size_t size = sizeof(collected_data);
    for (const auto& [time_step, time_step_data] : collected_data.get_all_data()) {
        size += sizeof(time_step) + calculate_map_size(time_step_data);
    }
    return size;
}

PYBIND11_MODULE(graph_simulator, handle) {
    handle.doc() = "This is the DAG Simulator module";
    py::class_<DagSimulator>(handle, "DagSimulator")
        .def(py::init<const std::string&>())
        .def("run", &DagSimulator::run, py::arg("steps") = 10)
        .def("print_dependencies", &DagSimulator::print_dependencies);
}