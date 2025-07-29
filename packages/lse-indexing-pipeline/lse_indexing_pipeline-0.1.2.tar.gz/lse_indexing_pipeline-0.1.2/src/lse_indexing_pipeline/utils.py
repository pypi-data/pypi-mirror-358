import time
from functools import wraps


def timeit(label: str = "⏱️ 실행 시간"):
    """
    함수 실행 시간을 측정하고 출력합니다.
    Args:
        label (str): 출력에 사용될 라벨.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            result = func(*args, **kwargs)
            end = time.time()
            print(f"{label}: {end - start:.2f}초")
            return result

        return wrapper

    return decorator
