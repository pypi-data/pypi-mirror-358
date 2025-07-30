"""Defines the math task Data Transfer Objects."""

from dataclasses import dataclass

from wse_exercises.base.task import Task


@dataclass
class MathTaskConfig:
    """Math task config."""

    min_value: int
    max_value: int

    def __post_init__(self) -> None:
        """Validate after object initialization."""
        self._check_min_leq_max()

    def _check_min_leq_max(self) -> 'MathTaskConfig':
        """Check that the minimum value is greater than the maximum."""
        if self.min_value > self.max_value:
            raise ValueError('The minimum value is greater than the maximum')
        return self


@dataclass(frozen=True)
class MathTaskConditions:
    """Math task conditions."""

    operand_1: int
    operand_2: int


@dataclass(frozen=True)
class MathTextTaskQuestion:
    """Math text task question."""

    text: str


@dataclass(frozen=True)
class MathTextTaskAnswer:
    """Math text task answer."""

    text: str


class SimpleMathTask(
    Task[
        MathTaskConfig,
        MathTaskConditions,
        MathTextTaskQuestion,
        MathTextTaskAnswer,
    ]
):
    """Base simple math task with text question/answer.

    :param config: Contains the min and max values of the operands.
    :param conditions: Contain the first and second operand values.
    :param question: The text representation of question.
    :param answer: The text representation of answer.
    :param exercise_name: Exercise name.
    :param created: The data and time of task creation.
    :param error_msg: The task creation error message.
    """
