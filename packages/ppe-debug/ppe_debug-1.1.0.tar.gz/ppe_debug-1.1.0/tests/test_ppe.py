import pytest
from ppe import ppe_debug


def test_custom_message():
    @ppe_debug
    def test_func():
        x = 10 + 5  ## Adding two numbers
        return x

    result = test_func()
    assert result == 15


def test_statement_echo():
    @ppe_debug
    def test_func():
        x = 10 + 5  ## -
        return x

    result = test_func()
    assert result == 15


def test_variable_inspection():
    @ppe_debug
    def test_func():
        a = 1  ## @a
        b = 2  ## @after:b
        c = a + b  ## @before:a,b
        d = 10  ## @before:d
        return c

    result = test_func()
    assert result == 3


def test_try_wrap():
    @ppe_debug
    def test_func():
        x = 10 / 0  ## try: is division by zero okay?
        x = 20 / 0  ## try:
        x = 10 / 2  ## try: division by two
        return x

    result = test_func()
    assert result == 5


def test_checkpoint():
    @ppe_debug
    def test_func():
        x = 10 + 5  ## checkpoint: inside test_func
        y = x + 5  ## checkpoint:
        return y

    result = test_func()
    assert result == 20


## Integration test for combined annotations
@ppe_debug
def analyze_trip(distance, time):
    total_distance = distance  ## checkpoint: trip analyzer started
    total_time = time  ## @after: total_distance, total_time

    avg_speed = total_distance / total_time  ## try: calculate average speed

    status = "ok" if avg_speed < 80 else "impossible"  ## -

    return avg_speed, status  ## @before: avg_speed, status

def test_combined_annotations():
    result = analyze_trip(100, 2)
    assert result == (50, "ok")