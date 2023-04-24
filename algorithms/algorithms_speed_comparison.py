from algorithms.algorithm1_v2 import main as alg1
from algorithms.algorithm1_v3 import main as alg2


for count in (100, 200, 300, 400, 500, 600, 700, 800, 900, 1000):
    print(f"COUNT: {count}")
    result_alg1 = alg1(application_count=count, lm=3, mu=1, sg=1)
    result_alg2 = alg2(application_count=count, lm=3, mu=1, sg=1)
    print("A1: ", result_alg1["number_of_iterations"], result_alg1["algorithm_working_time"])
    print("A2: ", result_alg2["number_of_iterations"], result_alg2["algorithm_working_time"])
    c_iter = result_alg1["number_of_iterations"] / result_alg2["number_of_iterations"]
    c_time = result_alg1["algorithm_working_time"] / result_alg2["algorithm_working_time"]
    print(f"iter_coefficients: {c_iter}, time_coefficients: {c_time}")
    print()
