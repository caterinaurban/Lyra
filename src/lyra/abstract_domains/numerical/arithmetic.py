from abc import ABCMeta, abstractmethod

from lyra.abstract_domains.lattice import Lattice


class ArithmeticMixin(Lattice, metaclass=ABCMeta):
    """Mixin that adds a arithmetic operations to a lattice."""

    @abstractmethod
    def _neg(self) -> 'ArithmeticMixin':
        """Negation of a default lattice elements.

        :return: current lattice element modified to be its negation

        """

    def neg(self) -> 'ArithmeticMixin':
        """Negation of a lattice elements.

        :return: current lattice element modified to be its negation

        """
        if self.is_bottom():
            return self
        else:
            return self._neg()

    @abstractmethod
    def _add(self, other: 'ArithmeticMixin') -> 'ArithmeticMixin':
        """Addition between two default lattice elements.

        :param other: other lattice element
        :return: current lattice element modified to be the sum of the two lattice elements

        """

    def add(self, other: 'ArithmeticMixin') -> 'ArithmeticMixin':
        """Addition between two lattice elements.

        :param other: other lattice element
        :return: current lattice element modified to be the sum of the two lattice elements

        """
        if self.is_bottom():
            return self
        elif other.is_bottom():
            return self.replace(other)
        else:
            return self._add(other)

    @abstractmethod
    def _sub(self, other: 'ArithmeticMixin') -> 'ArithmeticMixin':
        """Subtraction between two default lattice elements.

        :param other: other lattice element
        :return: current lattice element modified to be the difference between the two lattice elements

        """

    def sub(self, other: 'ArithmeticMixin') -> 'ArithmeticMixin':
        """Subtraction between two lattice elements.

        :param other: other lattice element
        :return: current lattice element modified to be the difference between the two lattice elements

        """
        if self.is_bottom():
            return self
        elif other.is_bottom():
            return self.replace(other)
        else:
            return self._sub(other)

    @abstractmethod
    def _mult(self, other: 'ArithmeticMixin') -> 'ArithmeticMixin':
        """Multiplication between two default lattice elements.

        :param other: other lattice element
        :return: current lattice element modified to be the product of the two lattice elements

        """

    def mult(self, other: 'ArithmeticMixin') -> 'ArithmeticMixin':
        """Multiplication between two lattice elements.

        :param other: other lattice element
        :return: current lattice element modified to be the product of the two lattice elements

        """
        if self.is_bottom():
            return self
        elif other.is_bottom():
            return self.replace(other)
        else:
            return self._mult(other)
