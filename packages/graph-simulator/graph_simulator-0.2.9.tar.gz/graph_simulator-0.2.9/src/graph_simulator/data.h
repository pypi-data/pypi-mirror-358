#ifndef DATA_H
#define DATA_H

#include <map>
#include <vector>
#include <string>
#include <variant>
#include <yaml-cpp/yaml.h>
#include <iostream> // Include for debugging

// 1(X> 1) * 1(Y<3) * (1 + 2 * R * X + 1 * Z)
class Node {
public:
    const int time_step;
    const std::string name;
    float value;
    std::vector<Node*> parents;
    // TODO: Consider using setters and getters for value,parents.
    Node(int time_step, const std::string& name) : time_step(time_step), name(name), value(0.0f) {}
};

// Define a hash function for std::tuple<int, std::string>
struct PairHash {
    template <typename T1, typename T2>
    std::size_t operator()(const std::pair<T1, T2>& p) const {
        auto h1 = std::hash<T1>{}(p.first);
        auto h2 = std::hash<T2>{}(p.second);
        return h1 ^ (h2 << 1); // Combining hashes
    }
};

class Variable {
public:
    int lag;
    std::string name;
    float value;

    Variable(int lag, const std::string& name) : lag(lag), name(name) {
        value = 0.0f;
    }

    // Method to return a string in the format "int_name"
    std::string get_name() const {
        return std::to_string(lag) + "_" + name;
    }
};

// TODO: Observation should hold variables. 
class Observation {
public:
    // Method to add data for a specific lag
    void add_lag_data(int lag, const std::map<std::string, float>& lag_data) {
        data[lag] = lag_data;
    }

    // Method to get data for a specific lag
    const std::map<std::string, float>& get_lag_data(int lag) const {
        return data.at(lag);
    }

    // Method to get value for lag and variable
    const float& get_variable_value(int lag, const std::string& name) const {
        auto lag_it = data.find(lag);
        if (lag_it != data.end()) {
            auto var_it = lag_it->second.find(name);
            if (var_it != lag_it->second.end()) {
                return var_it->second;
            } else {
                throw std::runtime_error("Variable name not found in observation data.");
            }
        } else {
            throw std::runtime_error("Lag not found in observation data.");
        }
    }

    // Method to get all data
    const std::map<int, std::map<std::string, float>>& get_all_data() const {
        return data;
    }

private:
    std::map<int, std::map<std::string, float>> data;  // Store data for each lag
};

// Indicator class
class Indicator {
public:
    std::string type;
    Variable variable;
    std::variant<float, Variable> threshold;

    // Constructor that takes a YAML node
    Indicator(const YAML::Node& node)
        : variable(node["variable"].begin()->first.as<int>(), node["variable"].begin()->second.as<std::string>()) {
        type = node["type"].as<std::string>();

        if (node["threshold"].IsScalar()) {
            threshold = node["threshold"].as<float>();
        } else {
            auto thresh_node = node["threshold"].begin();
            threshold = Variable(thresh_node->first.as<int>(), thresh_node->second.as<std::string>());
        }
    }
};

class GreaterThanValue {
    public:
        std::string type;
        std::map<int, std::map<std::string, float>> variable;
        float threshold;

        GreaterThanValue(const YAML::Node& node) : type(node["type"].as<std::string>()), threshold(node["threshold"].as<float>()) {
            for (const auto& var : node["variable"]) {
                int key = var.first.as<int>();
                std::map<std::string, float> value = var.second.as<std::map<std::string, float>>();
                variable[key] = value;
            }
        }
};

// Term class to encapsulate individual terms
class Term {
public:
    float intercept;
    float value;
    std::vector<Indicator> indicators;
    std::map<int, std::vector<std::string>> variables;

    // Default constructor
    Term() : intercept(0.0f), value(0.0f) {}

    // Constructor that takes a YAML node
    Term(const YAML::Node& node) {
        if (node["intercept"]) {
            intercept = node["intercept"].as<float>();
        } else {
            // std::cerr << "Missing 'intercept' key in YAML node" << std::endl;
            intercept = 0.0f; // Default value
        }

        if (node["value"]) {
            value = node["value"].as<float>();
        } else {
            // std::cerr << "Missing 'value' key in YAML node" << std::endl;
            value = 0.0f; // Default value
        }

        if (node["indicators"] && node["indicators"].IsSequence()) {
            for (const auto& indicator_node : node["indicators"]) {
                indicators.emplace_back(indicator_node);
            }
        } else {
            // std::cerr << "Missing or null 'indicators' key in YAML node" << std::endl;
            indicators = {}; // Initialize to an empty vector
        }

        if (node["variables"] && node["variables"].IsMap()) {
            for (const auto& var : node["variables"]) {
                int key = var.first.as<int>();
                std::vector<std::string> value = var.second.as<std::vector<std::string>>();
                variables[key] = value;
            }
        } else {
            variables = {}; 
            // std::cerr << "Missing or null 'variables' key in YAML node" << std::endl;
        }
    }
};

// TermsContainer class to encapsulate a collection of terms
class TermsContainer {
public:
    std::vector<Term> terms;

    // Default constructor
    TermsContainer() = default;

    // Constructor that takes a YAML node
    TermsContainer(const YAML::Node& node) {
        for (const auto& term : node) {
            terms.emplace_back(term);
        }
    }

    auto begin() const { return terms.begin(); }
    auto end() const { return terms.end(); }

};

class Data {
public:
    // Method to add data for a specific time step
    void add_time_step_data(int time_step, const std::map<std::string, float>& time_step_data) {
        data[time_step] = time_step_data;
    }

    // Method to get data for a specific time step
    std::map<std::string, float> get_time_step_data(int time_step) const {
        return data.at(time_step);
    }

    // Method to get all data
    std::map<int, std::map<std::string, float>> get_all_data() const {
        return data;
    }

    // Method to convert data to a list of dictionaries
    std::vector<std::map<std::string, float>> to_list_of_dicts() const {
        std::vector<std::map<std::string, float>> list_of_dicts;
        for (const auto& [time_step, time_step_data] : data) {
            list_of_dicts.push_back(time_step_data);
        }
        return list_of_dicts;
    }

private:
    std::map<int, std::map<std::string, float>> data;  // Store data for each time step
};

#endif // DATA_H