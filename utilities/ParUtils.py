from multiprocessing import Pool
from functools import reduce
import time

class ParUtils:

    @staticmethod
    def par_map(func, iterable):
        """
        Parallel map function.
        """
        time_start1 = time.time()
        p = Pool()
        time_end1 = time.time()

        time_start2 = time.time()
        list = p.map(func, iterable)
        time_end2 = time.time()

        print("Pool start: ", time_end1 - time_start1)
        print("p.map: ", time_end2 - time_start2)
        return list

    @staticmethod
    def par_reduce(associative_func, iterable):
        """
        Parallel reduce function. It requires the function to be associative.
        """
        return ParUtils._apply_parallel(reduce, associative_func, iterable)
            
    @staticmethod
    def par_filter(predicate, iterable):
        """
        Parallel filter function. 
        """
        return ParUtils._apply_parallel(filter, predicate, iterable)

    @staticmethod
    def _apply_parallel(iterfunc, func, iterable):
        """
        Applies the function (lambda x : iterfunc(func, x)) to chunks of 
        the iterable, then applies func to the intermediate results. 
        This function is used to factorize the code of par_reduce and par_filter.
        """
        with Pool() as p:
            chunks = ParUtils._get_chunks(p._processes, iterable)
            intermediate_result = p.map(lambda x : iterfunc(func, x), chunks)
            return iterfunc(func, intermediate_result)

    @staticmethod
    def _get_chunks(cpu_count, iterable):
        chunk_size = (len(iterable) + cpu_count - 1) // cpu_count
        return [iterable[i:i + chunk_size] for i in range(0, len(iterable), chunk_size)]
    