"""Defines the math task Data Transfer Objects."""

from typing import Any

from pydantic import BaseModel, validator

from wse_exercises.base.task import Task, TaskConfig


class MathTaskConfig(TaskConfig):
    """Math task config."""

    min_value: int
    max_value: int

    @classmethod
    @validator('max_value')
    def check_min_less_than_max(
        cls,
        value: str,
        values: dict[str, Any],
    ) -> str:
        """Check that the minimum value is greater than the maximum."""
        if 'min_value' in values and value <= values['min_value']:
            raise ValueError('max_value must be greater than min_value')
        return value


class MathTaskConditions(BaseModel):
    """Math task conditions."""

    operand_1: int
    operand_2: int


class MathTextTaskQuestion(BaseModel):
    """Math text task question."""

    text: str


class MathTextTaskAnswer(BaseModel):
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

    config: MathTaskConfig
    conditions: MathTaskConditions
    question: MathTextTaskQuestion
    answer: MathTextTaskAnswer
