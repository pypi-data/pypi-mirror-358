"""Defines the calculation exercise components."""

from .base.task_factory import BaseMathTaskComponentFactory


class AddingTaskFactoryBase(BaseMathTaskComponentFactory):
    """Create simple adding task."""

    @classmethod
    def create_question(cls, op1: int, op2: int) -> str:
        """Create a question to a simple math adding task."""
        return f'{op1} + {op2}'

    @classmethod
    def create_answer(cls, op1: int, op2: int) -> str:
        """Create an answer to a simple math adding task."""
        return str(op1 + op2)


class DivisionTaskFactoryBase(BaseMathTaskComponentFactory):
    """Create simple division task."""

    @classmethod
    def create_question(cls, op1: int, op2: int) -> str:
        """Create a question to a simple math division task."""
        return f'{op1 * op2} : {op2}'

    @classmethod
    def create_answer(cls, op1: int, op2: int) -> str:
        """Create an answer to a simple math division task."""
        return str(op1)


class MultiplicationTaskFactoryBase(BaseMathTaskComponentFactory):
    """Create simple multiplication task."""

    @classmethod
    def create_question(cls, op1: int, op2: int) -> str:
        """Create a question to a simple math multiplication task."""
        return f'{op1} x {op2}'

    @classmethod
    def create_answer(cls, op1: int, op2: int) -> str:
        """Create an answer to a simple math multiplication task."""
        return str(op1 * op2)


class SubtractionTaskFactoryBase(BaseMathTaskComponentFactory):
    """Create simple subtraction task."""

    @classmethod
    def create_question(cls, op1: int, op2: int) -> str:
        """Create a question to a simple math subtraction task."""
        return f'{op1} - {op2}'

    @classmethod
    def create_answer(cls, op1: int, op2: int) -> str:
        """Create an answer to a simple math subtraction task."""
        return str(op1 - op2)
