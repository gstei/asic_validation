
"""This is an exmample of how to use the concurrent.futures module to run functions in parallel.

Returns:
    _type_: _description_
"""

import time

import concurrent.futures

if 0:
    def foo(bar):
        """
        This function prints a greeting message and sleeps for 10 seconds.

        Args:
            bar (str): The name to be included in the greeting message.

        Returns:
            str: The string 'foo1'.
        """
        print('hello {}'.format(bar))
        time.sleep(10)
        return 'foo1'

    def foo2(bar):
        """
        This function prints a greeting message and sleeps for 20 seconds.

        Args:
            bar (str): The name to be included in the greeting message.

        Returns:
            str: The string 'foo2'.
        """
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
