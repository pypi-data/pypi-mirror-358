"""Defines mathematical exercises.

>>> from wse_exercises import (
...     AddingExercise,
...     ExactOperandGenerator,
... )
>>> from wse_exercises import SimpleMathExerciseConfig
>>> config = SimpleMathExerciseConfig(min_value=2, max_value=9)
>>> exercise = AddingExercise(
...     operand_generator=ExactOperandGenerator(),
...     config={'min_value': 2, 'max_value': 9},
... )
>>> task = exercise.create_task()
>>> task.question.text
'2 + 9'
>>> task.answer.text
'11'
"""

from .base.exercise import BaseSimpleCalculationExercise
from .enums import Exercises
from .task_factories import (
    AddingTaskFactoryBase,
    DivisionTaskFactoryBase,
    MultiplicationTaskFactoryBase,
    SubtractionTaskFactoryBase,
)


class AddingExercise(BaseSimpleCalculationExercise):
    """Adding exercise."""

    exercise_name = Exercises.ADDING
    task_factory = AddingTaskFactoryBase


class DivisionExercise(BaseSimpleCalculationExercise):
    """Division exercise."""

    exercise_name = Exercises.DIVISION
    task_factory = DivisionTaskFactoryBase


class MultiplicationExercise(BaseSimpleCalculationExercise):
    """Multiplication exercise."""

    exercise_name = Exercises.MULTIPLICATION
    task_factory = MultiplicationTaskFactoryBase


class SubtractionExercise(BaseSimpleCalculationExercise):
    """Subtraction exercise."""

    exercise_name = Exercises.SUBTRACTION
    task_factory = SubtractionTaskFactoryBase


if __name__ == '__main__':
    import doctest

    doctest.testmod()
