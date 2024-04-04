import time

import concurrent.futures

if 0:
    def foo(bar):
        print('hello {}'.format(bar))
        time.sleep(10)
        return 'foo1'

    def foo2(bar):
        print('hello {}'.format(bar))
        time.sleep(20)
        return 'foo2'

    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(foo, 'world1!')
        future2 = executor.submit(foo2, 'world2!')

    return_value = future.result()
    return_value2 = future2.result()

    print(return_value)
    print(return_value2)
