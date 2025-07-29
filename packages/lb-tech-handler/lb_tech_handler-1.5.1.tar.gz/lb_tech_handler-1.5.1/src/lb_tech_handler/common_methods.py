import timeit

def timed_execution(func):
    """This is a decorator to time the execution time of a function

    Example:
        @timed_execution
        def test_api():
            response = requests.get("https://api.learnbasics.fun/testing?name=test")

    Args:
        func (_type_): Function to be timed
    """

    def wrapper(*args, **kwargs):
        start_time = timeit.default_timer()
        result = func(*args, **kwargs)
        end_time = timeit.default_timer()
        execution_time = end_time - start_time
        print(f"Execution time for {func.__name__}: {execution_time} seconds")
        return result
    
    return wrapper