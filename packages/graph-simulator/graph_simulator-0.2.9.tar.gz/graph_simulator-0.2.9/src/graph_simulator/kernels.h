#ifndef KERNELS_H
#define KERNELS_H

#include <vector>
#include <map>
#include <string>
#include <stdexcept>
#include <random>
#include <cmath>
#include <yaml-cpp/yaml.h>
#include <memory>
#include "data.h"
#include <iostream>

// Base class for kernels
class Kernel {
public:
    virtual ~Kernel() = default;
    virtual float kernel_predict(const int time_step) const = 0;

    // Constructor that takes kernel parameters and node_map
    Kernel(const YAML::Node& kernel_params, const std::unordered_map<std::pair<int, std::string>, Node*, PairHash>& node_map) 
        : kernel_params(kernel_params), node_map(node_map), noise(0), terms(kernel_params["terms"]) {
        if (kernel_params["sample_domain"]) {
            sample_domain = kernel_params["sample_domain"].as<std::vector<float>>();
        }

        if (kernel_params["noise"]) {
            noise = kernel_params["noise"].as<float>();
        }
    }

    float predict(const int time_step) const {
        if (noise > 0) {
            // Create a random number generator
            std::random_device rd;
            std::mt19937 gen(rd());
            std::uniform_real_distribution<> dist(0.0, 1.0);

            // Generate a random number and compare with noise probability
            if (dist(gen) < noise) {
                return sample();
            }
        }

        return kernel_predict(time_step);
    }

    float sample() const {
        if (sample_domain.empty()) {
            throw std::runtime_error("sample_domain is empty");
        }

        // Create a random number generator
        std::random_device rd;
        std::mt19937 gen(rd());

        // Create a uniform distribution to pick a random index
        std::uniform_int_distribution<> dist(0, sample_domain.size() - 1);

        // Sample an index from the distribution
        int index = dist(gen);

        // Return the corresponding element from the sample_domain
        return sample_domain[index];
    }

    // Method to compute linear predictor
    float linear_predictor(const int time_step) const {
        float value = 0;
        // Loop over each term in the TermsContainer
        for (const auto& term : terms) {
            float term_value = 1.0f;  // Initialize term value to 1 for multiplication

            // Loop over each variable in the term
            value += term_predictor(term, time_step);
        }

        return value;
    }

    float term_predictor(const Term& term, const int time_step) const {
        // Check indicators (if any are present)
        if (!check_indicators(term.indicators, time_step)) {
            return 0;
        }

        // TODO: Refactor this to a separate function
        float output = term.intercept;  // Start with the intercept

        float value = term.value;  // Start with the term value
        // Loop over each variable in the term
        for (const auto& [lag, vars] : term.variables) {
            for (const auto& var : vars) {
                auto it = node_map.find(std::make_pair(time_step - lag, var));
                if (it != node_map.end()) {
                    value *= it->second->value;
                }
            }
        }

        output += value;  // Add the term value to the total value

        return output;
    }

    bool check_indicators(const std::vector<Indicator>& indicators, const int time_step) const {
        for (const auto& indicator : indicators) {
            if (!indicator_predictor(indicator, time_step)) {
                return false;
            }
        }
        return true;
    }

    float indicator_predictor(const Indicator& indicator, const int time_step) const {

        auto key = std::make_pair(time_step - indicator.variable.lag, indicator.variable.name);

        float variable_value = node_map.at(key)->value;

        if (indicator.type == "greater_than_value") {
            if (variable_value <= std::get<float>(indicator.threshold)) {
                return false;
            }
        } else if (indicator.type == "equal_to") {
            if (variable_value != std::get<float>(indicator.threshold)) {
                return false;
            }
        } else if (indicator.type == "greater_or_equal_than_value") {
            if (variable_value < std::get<float>(indicator.threshold)) {
                return false;
            }
        } else if (indicator.type == "greater_than_variable") {
            const auto& threshold_variable = std::get<Variable>(indicator.threshold);
            float threshold_value = node_map.at(std::make_pair(time_step - threshold_variable.lag, threshold_variable.name))->value;

            if (variable_value <= threshold_value) {
                return false;
            }
        } else {
            throw std::invalid_argument("Indicator type not supported.");
        }

        return true;
    }

    bool is_sample_domain_set() const {
        return !sample_domain.empty();
    }

    std::vector<float> sample_domain;
    TermsContainer terms;

protected:
    YAML::Node kernel_params;  // Store the kernel parameters
    const std::unordered_map<std::pair<int, std::string>, Node*, PairHash>& node_map; // Reference to node_map
    float noise;
};

// Derived class for uniform kernel
class UniformKernel : public Kernel {
public:
    std::vector<float> probs;

    // Constructor that takes kernel parameters and node_map
    UniformKernel(const YAML::Node& kernel_params, const std::unordered_map<std::pair<int, std::string>, Node*, PairHash>& node_map) 
        : Kernel(kernel_params, node_map) {
        if (!kernel_params["sample_domain"]) {
            throw std::invalid_argument("UniformKernel must contain 'sample_domain'");
        }

        if (kernel_params["probs"]) {
            probs = kernel_params["probs"].as<std::vector<float>>();
        } else {
            // Default probabilities if not specified
            probs = std::vector<float>(sample_domain.size(), 1.0f / sample_domain.size());
        }
    }

    float kernel_predict(const int time_step) const override {
        // Create a random number generator
        std::random_device rd;
        std::mt19937 gen(rd());

        // Create a discrete distribution to pick a random index based on probs
        std::discrete_distribution<> dist(probs.begin(), probs.end());

        // Sample an index from the distribution
        int index = dist(gen);

        // Return the corresponding element from the domain
        return sample_domain[index];
    }
};

// Derived class for linear kernel
class LinearKernel : public Kernel {
public:
    // Constructor that takes kernel parameters and node_map
    LinearKernel(const YAML::Node& kernel_params, const std::unordered_map<std::pair<int, std::string>, Node*, PairHash>& node_map) 
        : Kernel(kernel_params, node_map) {
        if (!kernel_params["sample_domain"]) {
            throw std::invalid_argument("LinearKernel must contain 'sample_domain'");
        }

        if (!kernel_params["lower_bound"]) {
            throw std::invalid_argument("LinearKernel must contain 'lower_bound'");
        } else {
            lower_bound = kernel_params["lower_bound"].as<float>();
        }

        if (!kernel_params["upper_bound"]) {
            throw std::invalid_argument("LinearKernel must contain 'upper_bound'");
        } else {
            upper_bound = kernel_params["upper_bound"].as<float>();
        }
    }

    float kernel_predict(const int time_step) const override {
        float output = linear_predictor(time_step);
        
        if (output < lower_bound) {
            return lower_bound;
        } else if (output > upper_bound) {
            return upper_bound;
        }

        return output;
    }

private:
    float lower_bound;
    float upper_bound;
};

// Derived class for poisson kernel
class PoissonKernel : public Kernel {
public:
    Term limit;  // Declare limit as TermsContainer

    // Constructor that takes kernel parameters and node_map
    PoissonKernel(const YAML::Node& kernel_params, const std::unordered_map<std::pair<int, std::string>, Node*, PairHash>& node_map) 
        : Kernel(kernel_params, node_map), limit(kernel_params["limit"]) {
        if (limit.value > 0) {
            sample_domain.resize(static_cast<size_t>(limit.value) + 1);
        } else {
            sample_domain.resize(static_cast<size_t>(10) + 1); // arbitrary value
        }
        std::iota(sample_domain.begin(), sample_domain.end(), 0);
    }

    float kernel_predict(const int time_step) const override {
        // Create a random number generator
        std::random_device rd;
        std::mt19937 gen(rd());

        // Compute the mean (mu) using the linear predictor
        float mu = std::exp(linear_predictor(time_step));

        // Create a Poisson distribution with mean mu
        std::poisson_distribution<> d(mu);

        // Sample from the Poisson distribution
        float output = d(gen);

        // Apply the limit if specified
        if (limit.value > 0) {
            float current_value = 1;
            for (const auto& [lag, vars] : limit.variables) {
                for (const auto& var : vars) {
                    current_value *= node_map.at(std::make_pair(time_step - lag, var))->value;
                }
            }
            if (current_value + output > limit.value) {
                output = limit.value - current_value;
            }
        }

        return output;
    }
};

// Derived class for poisson kernel
class BinomialKernel : public Kernel {
    int dim;

public:
    // Constructor that takes kernel parameters and node_map
    BinomialKernel(const YAML::Node& kernel_params, const std::unordered_map<std::pair<int, std::string>, Node*, PairHash>& node_map) 
        : Kernel(kernel_params, node_map), dim(kernel_params["dim"].as<int>()) {

        sample_domain.resize(static_cast<size_t>(dim) + 1);
        std::iota(sample_domain.begin(), sample_domain.end(), 0);
    }

    float kernel_predict(const int time_step) const override {
        // Create a random number generator
        std::random_device rd;
        std::mt19937 gen(rd());

        // Compute the mean (mu) using the linear predictor
        float expit_val = std::exp(linear_predictor(time_step));
        float p = expit_val / (1 + expit_val);

        // Create a binomial distribution with n trials and probability p
        std::binomial_distribution<> d(dim, p);

        // Sample from the binomial distribution
        float output = d(gen);

        return output;
    }
};

// Derived class for mixed kernel
class MixedKernel: public Kernel {
public:
    MixedKernel(const YAML::Node& node, const std::unordered_map<std::pair<int, std::string>, Node*, PairHash>& node_map) 
        : Kernel(node, node_map) {
        noise = node["noise"].as<float>();
        if (!kernel_params["mixed_probs"]) {
            throw std::invalid_argument("MixedKernel must contain 'mixed_probs'");
        } else {
            mixed_probs = node["mixed_probs"].as<std::vector<float>>();
        }

        const YAML::Node& kernels_nodes = node["kernels"];
        for (const auto& kernel_node : kernels_nodes) {
            std::string kernel_type = kernel_node["type"].as<std::string>();
            if (kernel_type == "linear") {
                kernels.push_back(std::make_unique<LinearKernel>(kernel_node, node_map));
            } else if (kernel_type == "poisson") {
                kernels.push_back(std::make_unique<PoissonKernel>(kernel_node, node_map));
            } else {
                throw std::invalid_argument("Kernel type not supported: " + kernel_type);
            }
        }
    }

    float kernel_predict(const int time_step) const override {
        // Create a random number generator
        std::random_device rd;
        std::mt19937 gen(rd());

        // Create a discrete distribution to pick a random index based on mixed_probs
        std::discrete_distribution<> dist(mixed_probs.begin(), mixed_probs.end());

        // Sample an index from the distribution
        int index = dist(gen);

        // Call kernel_predict on the chosen kernel
        return kernels[index]->predict(time_step);
    }

private:
    float noise;
    std::vector<float> mixed_probs;
    std::vector<std::unique_ptr<Kernel>> kernels;
};

// Derived class for uniform kernel
class ConstantKernel : public Kernel {
public:
    float value;

    // Constructor that takes kernel parameters and node_map
    ConstantKernel(const YAML::Node& kernel_params, const std::unordered_map<std::pair<int, std::string>, Node*, PairHash>& node_map) 
        : Kernel(kernel_params, node_map), value(kernel_params["value"].as<float>()) {

        sample_domain = {value};

    }

    float kernel_predict(const int time_step) const override {
        return value;
    }
};

#endif // KERNELS_H