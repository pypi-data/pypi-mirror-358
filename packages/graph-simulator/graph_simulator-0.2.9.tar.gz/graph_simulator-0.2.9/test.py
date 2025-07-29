# import time
# import python_example

# sim = python_example.DagSimulator("config/pricing_specs.yaml")
# # sim = python_example.DagSimulator("config/example_1.yaml")
# start_time = time.time()
# sim.run(100000)
# print(time.time() - start_time)


import time
import graph_simulator

sim = graph_simulator.DagSimulator("examples/example_1.yaml")
# sim = python_example.DagSimulator("config/example_1.yaml")
start_time = time.time()

print(len(sim.run(10000)))

print(time.time() - start_time)
