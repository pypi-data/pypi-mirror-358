from halib import *


@console_log
def this_function():
    pprint(np.random.rand(3, 3))
    print("Hello, World!")
    inspect(np.random.rand(3, 3))


this_function()

# with ConsoleLog('custom msg'):
#     pprint(np.random.rand(3, 3))
