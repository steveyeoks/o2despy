import math
import random
from datetime import timedelta

import numpy as np


class DurationStatisticsConfig:
    def __init__(self, seed):
        random.seed(seed)

    def generate_exponential(self, lambda_parameter):
        if lambda_parameter <= 0:
            raise Exception("Negative lambda not applicable")
        else:
            return random.expovariate(lambda_parameter)

    def generate_normal(self, mean, cv):
        if mean < 0:
            raise Exception("Negative mean not applicable")
        if cv < 0:
            raise Exception("Negative coefficient of variation not applicable for normal distribution")

        if mean == 0:
            return 0
        if cv == 0:
            return mean
        return random.normalvariate(mu=mean, sigma=mean*cv)

    def generate_poisson(self, lambda_parameter):
        """lambda parameter"""
        if lambda_parameter < 0:
            raise Exception("Negative mean not applicable")

        if np.random.poisson(lambda_parameter) != 0:
            return np.random.poisson(lambda_parameter)
        else:
            return 0.000000001

    def generate_geometric(self, mean):
        if mean <= 0:
            raise Exception("Negative mean not applicable")
        else:
            return np.random.geometric(1/mean)

    def generate_uniform(self, mean, cv):
        lowerbound = mean - math.sqrt(3*cv)
        upperbound = mean + math.sqrt(3*cv)

        if lowerbound < 0 or upperbound < 0:
            raise Exception("Negative lowerbound or upperbound is not applicable")

        return np.random.uniform(lowerbound, upperbound)

    def retrive_sku_duration(self):
        distance = 5.0
        speed = 2.5
        dte = timedelta(seconds=distance/speed)
        print('duration is ', dte)
        return dte


if __name__ == '__main__':
    duration_config = DurationStatisticsConfig(10)
    print(duration_config.generate_poisson(5))