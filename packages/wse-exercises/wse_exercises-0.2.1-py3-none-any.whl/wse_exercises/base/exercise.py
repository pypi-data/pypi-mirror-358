"""Defines base exercise class."""

from dataclasses import dataclass

from wse_exercises.core.mathem.enums import Exercises


@dataclass
class ExerciseConfig:
    """Exercise base config."""


@dataclass
class TaskRequest:
    """Request an exercise with a given configuration.

    :param Exercises name: Exercise name.
    :param ExerciseConfig config: Exercise configuration.
    """

    name: Exercises
    config: ExerciseConfig
