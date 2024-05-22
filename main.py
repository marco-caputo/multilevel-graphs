import utilities.ParUtils as pu
import time

def square(x):
    return x * 7

print("\n TIME 1")
pu.ParUtils.par_map(square, range(1000))

print("\n\n TIME 1")
pu.ParUtils.par_map(square, range(10000))

print("\n\n TIME 1")
pu.ParUtils.par_map(square, range(10000000))



#print("Time with par_map: ", end_time1 - start_time1)
#print("Time with map: ", end_time2 - start_time2)