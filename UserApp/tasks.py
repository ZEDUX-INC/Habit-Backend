import random
from typing import Sequence
from celery import shared_task


@shared_task
def add(x: int, y: int) -> int:
    return x + y


@shared_task(name='multiply_two_numbers')
def mul(x: int, y: int) -> int:
    total = x * (y * random.randint(3, 100))
    return total


@shared_task(name='sum_list_numbers')
def xsum(numbers: Sequence[int]) -> int:
    return sum(numbers)
