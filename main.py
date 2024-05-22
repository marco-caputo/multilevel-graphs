# import multilevel_graphs.utilities.par_utils as pu
# import time

def square(x):
    return [[x*i] for i in range(10)]



if __name__ == '__main__':
    print({1, 2, 3} == {3, 2, 1})
    '''
    input1 = range(1000)
    input2 = range(10000)
    input3 = range(1000000)

    print("\n TIME 1")
    pu.ParUtils.par_map(square, input1)
    print("\n TIME 2")
    time1 = time.time()
    map(square, input1)
    time2 = time.time()
    print("Time with map: ", time2 - time1)

    print("\n\n TIME 1")
    pu.ParUtils.par_map(square, input2)
    print("\n TIME 2")
    time1 = time.time()
    map(square, input2)
    time2 = time.time()
    print("Time with map: ", time2 - time1)

    print("\n\n TIME 1")
    pu.ParUtils.par_map(square, input3)
    print("\n TIME 2")
    time1 = time.time()
    map(square, input3)
    time2 = time.time()
    print("Time with map: ", time2 - time1)
    #print("Time with par_map: ", end_time1 - start_time1)
    #print("Time with map: ", end_time2 - start_time2)
    '''