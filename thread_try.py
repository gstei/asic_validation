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
    thread1 = threading.Thread(target=foo, args=('world1!',))
    thread2 = threading.Thread(target=foo2, args=('world2!',))

    thread1.start()
    thread2.start()

    thread1.join()
    thread2.join()
if 1: #does not work
    import threading
    import time

    def foo(bar):
        print('hello {}'.format(bar))
        time.sleep(10)
        return 'foo1'

    def foo2(bar):
        print('hello {}'.format(bar))
        time.sleep(20)
        return 'foo2'

    # Create two threads
    thread1 = threading.Thread(target=foo, args=('world1!',))
    thread2 = threading.Thread(target=foo2, args=('world2!',))

    # Start the threads
    thread1.start()
    thread2.start()

    # Wait for both threads to finish
    thread1.join()
    thread2.join()

    # Retrieve the return values from the threads
    result1 = thread1.result
    result2 = thread2.result

    print("Results from threads:")
    print("Thread 1:", result1)
    print("Thread 2:", result2)