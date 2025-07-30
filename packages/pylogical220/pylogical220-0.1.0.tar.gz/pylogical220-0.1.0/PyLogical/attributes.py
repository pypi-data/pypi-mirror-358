class LogicalAttribute:
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"{self.__class__.__name__}({self.value})"


class Inverted(LogicalAttribute):
    def result(self):
        return not self.value


class IsTruthy(LogicalAttribute):
    def result(self):
        return bool(self.value)


class IsFalsy(LogicalAttribute):
    def result(self):
        return not bool(self.value)


class IsNone(LogicalAttribute):
    def result(self):
        return self.value is None


class IsNotNone(LogicalAttribute):
    def result(self):
        return self.value is not None


class IsEven(LogicalAttribute):
    def result(self):
        return isinstance(self.value, int) and self.value % 2 == 0


class IsOdd(LogicalAttribute):
    def result(self):
        return isinstance(self.value, int) and self.value % 2 != 0


class IsPositive(LogicalAttribute):
    def result(self):
        return isinstance(self.value, (int, float)) and self.value > 0


class IsNegative(LogicalAttribute):
    def result(self):
        return isinstance(self.value, (int, float)) and self.value < 0


class IsZero(LogicalAttribute):
    def result(self):
        return self.value == 0


class IsEmpty(LogicalAttribute):
    def result(self):
        return hasattr(self.value, '__len__') and len(self.value) == 0


class IsNotEmpty(LogicalAttribute):
    def result(self):
        return hasattr(self.value, '__len__') and len(self.value) > 0


class IsType(LogicalAttribute):
    def __init__(self, value, expected_type):
        super().__init__(value)
        self.expected_type = expected_type

    def result(self):
        return isinstance(self.value, self.expected_type)


class Equals(LogicalAttribute):
    def __init__(self, value, target):
        super().__init__(value)
        self.target = target

    def result(self):
        return self.value == self.target


class NotEquals(LogicalAttribute):
    def __init__(self, value, target):
        super().__init__(value)
        self.target = target

    def result(self):
        return self.value != self.target


class IsSubset(LogicalAttribute):
    def __init__(self, value, container):
        super().__init__(value)
        self.container = container

    def result(self):
        return set(self.value).issubset(set(self.container))


class IsSuperset(LogicalAttribute):
    def __init__(self, value, subset):
        super().__init__(value)
        self.subset = subset

    def result(self):
        return set(self.value).issuperset(set(self.subset))
