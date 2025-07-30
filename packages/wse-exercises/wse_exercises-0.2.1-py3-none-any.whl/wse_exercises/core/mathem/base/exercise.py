"""Defines the base logic for creation a math exercises."""

import logging
from dataclasses import dataclass
from typing import Any, ClassVar, Type

from wse_exercises.base.exercise import (
    ExerciseConfig,
    TaskRequest,
)
from wse_exercises.core.mathem.base.services import OperandGenerator
from wse_exercises.core.mathem.enums import Exercises
from wse_exercises.core.mathem.exceptions import OperandGeneratorError
from wse_exercises.core.mathem.task import (
    MathTaskConditions,
    MathTaskConfig,
    MathTextTaskAnswer,
    MathTextTaskQuestion,
    SimpleMathTask,
)

from .task_factory import BaseMathTaskComponentFactory

logger = logging.getLogger(__name__)

MIN_VALUE = 1
MAX_VALUE = 9


@dataclass
class SimpleMathExerciseConfig(ExerciseConfig):
    """Exercise config Data-Transfer-Object."""

    min_value: int = MIN_VALUE
    max_value: int = MAX_VALUE


@dataclass
class SimpleMathTaskRequest(TaskRequest):
    """Request a simple math exercise with a given configuration."""

    config: SimpleMathExerciseConfig


class BaseSimpleCalculationExercise:
    """Defines a base logic of simple calculation exercise creation.

    Control exercise task creation with:
    - `task_factory`, create question and answer for exercise type;
    - `operand_generator`, get random or exact calculation operands;
    - `config`, set min and max calculation operand value range for
       random generator or as exact operands.
    """

    exercise_name: ClassVar[Exercises]
    task_factory: ClassVar[Type[BaseMathTaskComponentFactory]]

    def __init__(
        self,
        operand_generator: OperandGenerator,
        config: SimpleMathExerciseConfig | dict[str, Any] | None = None,
    ) -> None:
        """Construct the task creation."""
        # Initialize exercise config
        self._set_config(config)

        # Set up operand generator
        self._operand_generator = operand_generator

    def create_task(
        self,
        config: SimpleMathExerciseConfig | dict[str, Any] | None = None,
    ) -> SimpleMathTask:
        """Create simple calculation task."""
        if config is not None:
            self._set_config(config)
        elif self._config is None:
            raise AttributeError('Exercise config is not defined')

        self._generate_operands()
        self._create_components()
        task_dto = self._create_task_dto()
        return task_dto

    # Utility methods

    def _set_config(
        self,
        config: SimpleMathExerciseConfig | dict[str, Any] | None,
    ) -> None:
        """Update exercise configuration with validation."""
        if isinstance(config, dict):
            self._config = SimpleMathExerciseConfig(**config)
        elif isinstance(config, SimpleMathExerciseConfig):
            self._config = config
        else:
            raise

        # If config is None, keep existing configuration.
        self._init_value_range()

    def _init_value_range(self) -> None:
        self._min_value = self._config.min_value
        self._max_value = self._config.max_value

    def _generate_operands(self) -> None:
        """Generate task operands."""
        self._operand_generator.set_values(self._min_value, self._max_value)

        try:
            self._operand_1 = self._operand_generator.generate()
            self._operand_2 = self._operand_generator.generate()

        except OperandGeneratorError as e:
            logger.error(
                'Operand generation failed: %s. '
                'Using fallback values: min_value=%d, max_value=%d',
                str(e),
                self._min_value,
                self._max_value,
            )
            # Fallback to minimal possible values
            # to keep system operational
            self._operand_1 = self._min_value
            self._operand_2 = self._min_value

        except Exception as e:
            logger.critical(
                'Unexpected error during operand generation: %s',
                str(e),
                exc_info=True,
            )
            # Critical fallback to prevent complete failure
            self._operand_1 = 1
            self._operand_2 = 1

    def _create_components(self) -> None:
        """Create simple math task component DTO (question/answer)."""
        self._question = self.task_factory.create_question(
            self._operand_1, self._operand_2
        )
        self._answer = self.task_factory.create_answer(
            self._operand_1, self._operand_2
        )

    def _create_task_dto(self) -> SimpleMathTask:
        """Create simple math task Data Transfer Object."""
        return SimpleMathTask(
            config=MathTaskConfig(
                min_value=self._min_value,
                max_value=self._max_value,
            ),
            conditions=MathTaskConditions(
                operand_1=self._operand_1,
                operand_2=self._operand_2,
            ),
            question=MathTextTaskQuestion(
                text=self._question,
            ),
            answer=MathTextTaskAnswer(
                text=self._answer,
            ),
            exercise_name=self.exercise_name,
        )
