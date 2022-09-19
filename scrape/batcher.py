import os
from itertools import zip_longest
import multiprocessing as mp
import threading as th
import queue
from tqdm import tqdm


'''
Source: https://docs.python.org/3/library/itertools.html
Collect data into non-overlapping fixed-length chunks or blocks

grouper('ABCDEFG', 3, fillvalue='x') --> ABC DEF Gxx
grouper('ABCDEFG', 3, incomplete='strict') --> ABC DEF ValueError
grouper('ABCDEFG', 3, incomplete='ignore') --> ABC DEF

inputs:
iterable   (iterable)
n          (int)
*          (*)
incomplete (string)
fillvalue  (any)

outputs:

'''
def grouper(iterable, n, *, incomplete='fill', fillvalue=None):
    args = [iter(iterable)] * n
    if incomplete == 'fill':
        return zip_longest(*args, fillvalue=fillvalue)
    if incomplete == 'strict':
        return zip(*args, strict=True)
    if incomplete == 'ignore':
        return zip(*args)
    else:
        raise ValueError('Expected fill, strict, or ignore')
    
    
'''
Wrapper for function to execute in process so can place result in multiprocessing queue

inputs:
func  (Function)              Function that operates on one element of the data and returns a value
task  (*)                     Data to be operated on by func
queue (multiprocessing.Queue) Result queue
'''
def task_wrapper(func, task, queue):
    return queue.put(func(task))


'''
inputs:
data     (list)     List of data to process
func     (Function) Function that operates on one element of the data and returns a value
use_tqdm (bool)     True if uses tqdm, else False

outputs:
results (list) Processed data
'''
def batch_process(data, func, use_tqdm=True):
    q = mp.Queue()
    results = []
    grouped = grouper(data, os.cpu_count())
    
    with tqdm(total=len(data)) as pbar:
        for batch in grouped:
            procs = [mp.Process(target=task_wrapper, args=(func, task, q,)) for task in batch]
            for p in procs: p.start(); p.join()
            
            while(not q.empty()):
                results.append(q.get())

            pbar.update(len(batch))
            
    return results


def batch_thread(data, func, threads=8, use_tqdm=True):
    q = queue.Queue()
    results = []
    grouped = grouper(data, threads)
    
    with tqdm(total=len(data)) as pbar:
        for batch in grouped:
            tasks = [th.Thread(target=task_wrapper, args=(func, task, q,)) for task in batch]
            for t in tasks: t.start(); t.join()
            
            while(not q.empty()):
                results.append(q.get())
            
            pbar.update(len(batch))
            
    return results