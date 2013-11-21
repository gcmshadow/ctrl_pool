#!/usr/bin/env python

# To run:
#
#    mpiexec -n <number of nodes> /path/to/demoPool.py"
#

import math
def test1(cache, data, *args, **kwargs):
    result = math.sqrt(data)
    print "Store: %s" % ("present" if hasattr(cache, "p") else "absent")
    cache.result = result
    cache.args = args
    cache.kwargs = kwargs
    return result

def test2(cache, data, *args, **kwargs):
    result = math.sqrt(data)
    print "%d: %f vs %f ; %s vs %s ; %s vs %s ; %s" % (cache.comm.rank, cache.result, result, cache.args,
                                                       args, cache.kwargs, kwargs, hasattr(cache, "p"))
    return None

from hsc.pipe.base.pool import startPool, Pool, Debugger, Comm

# Here's how to enable debugging messages from the pool
Debugger().enabled = True

pool = startPool()

dataList = map(float, range(10))

def context1():
    pool1 = Pool()
    pool1.storeSet(p=1)

    print "Calculating [sqrt(x) for x in %s]" % dataList
    print "And checking for 'p' in our pool"
    print pool1.map(test1, True, dataList, "foo", foo="bar")
    pool1.clearCache()

# Now let's say we're somewhere else and forgot to hold onto pool1
def context2():
    fruit = ["tomato", "tomahtoe"]
    veges = {"potato": "potahtoe"}
    pool2 = Pool()
    # We inherit a pool with 'p' in it --- it's the same pool as before
    pool2.storeDel("p") # Now there's no 'p' in our pool...
    print pool2.mapNoBalance(test1, True, dataList, *fruit, **veges)
    pool2.storeSet(p=2)
    pool2.storeClear()
    print pool2.mapToPrevious(test2, dataList, *fruit, **veges)

context1()
context2()

Pool().exit() # This is important, to bring everything down nicely; or the wheels will just keep turning
# Can do stuff here, just not use any MPI because the slaves have exited.
# If you want the slaves, then pass "killSlaves=False" to startPool(); they'll emerge after startPool().
print "Done."

