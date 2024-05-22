import multilevel_graphs.utilities.par_utils as pu
import time


def square(x):
    return x * x


if __name__ == '__main__':
    input3 = range(10000000)

    start_time1 = time.time()
    pu.ParUtils.par_map(square, input3)
    end_time1 = time.time()
    start_time2 = time.time()
    map(square, input3)
    end_time2 = time.time()
    print("Time with par_map: ", end_time1 - start_time1)
    print("Time with map: ", end_time2 - start_time2)
