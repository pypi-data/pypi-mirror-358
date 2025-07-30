"""Defines base class for task."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Generic

from wse_exercises.core.mathem.enums import Exercises

from .interface import AnswerT, QuestionT, TaskConditionsT, TaskConfigT


@dataclass(frozen=True)
class Task(
    Generic[
        TaskConfigT,
        TaskConditionsT,
        QuestionT,
        AnswerT,
    ],
):
    """Base class for DTO exercise task."""

    config: TaskConfigT
    conditions: TaskConditionsT
    question: QuestionT
    answer: AnswerT
    exercise_name: Exercises
    created: datetime = field(default_factory=datetime.now)
    error_msg: str = field(default='', compare=False)
