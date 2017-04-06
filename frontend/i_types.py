from abc import ABCMeta
from frontend.context import Context
import os


class SubtypesTree:
    __file_name = "classes_subtypes.txt"

    def __init__(self):
        """Initialize the tree with the text file

        The tree is represented by an adjacency list,
        where each directed edge between node x and y
        denotes that x is a subtype of y.

        The subtype relationship is reflexive and transitive.
        """
        base_path = os.path.dirname(__file__)
        file_path = os.path.abspath(os.path.join(base_path, SubtypesTree.__file_name))
        self.tree = {}
        for line in open(file_path):
            line = line.strip()
            if line.startswith("#") or len(line) == 0:
                continue
            t1, t2 = line.split()
            if t1 in self.tree:
                self.tree[t1].append(t2)
            else:
                self.tree[t1] = [t2]

    def __reachable(self, current, target, visited):
        if current in visited or (current not in self.tree):
            return False
        if current == target:
            return True

        visited.add(current)
        for adjacent in self.tree[current]:
            if self.__reachable(adjacent, target, visited):
                return True
        return False

    def reachable(self, source, target):
        """Check if node2 is reachable from node1"""
        return self.__reachable(source, target, set())


subtypes_tree = SubtypesTree()


class Type():
    """This class is the top-parent of all possible inferred types of a Python program.
    Every type has its own class that inherits this class.
    """
    def is_subtype(self, t):
        return isinstance(self, type(t))

    def get_name(self):
        if hasattr(self, 'name'):
            return self.name
        return "Type"

    # Two types are considered identical if their names exactly match.
    def __eq__(self, other):
        return self.get_name() == other.get_name()

    def __hash__(self):
        return hash(self.get_name())

    def __repr__(self):
        return self.get_name()


class TObject(Type):
    """This class is the top-parent of all possible inferred types of a Python program.
    Every type has its own class that inherits this class.
    """
    def __init__(self):
        self.name = "object"

    def is_subtype(self, t):
        return isinstance(self, type(t))


class TClass(TObject):
    """Type given to a user defined class.

    Attributes:
        name (str): Class name.
        context (Context): Contains a mapping between variables and types within the scope of this class.
    """

    def __init__(self, name, context=Context()):
        super().__init__()
        self.name = name
        self.context = context

    def is_subtype(self, t):
        if not isinstance(t, TClass):
            return False
        return subtypes_tree.reachable(self.name, t.name)

    def get_name(self):
        # TODO implement after classes inference
        return ""


class TNone(TObject):
    def __init__(self):
        super().__init__()
        self.name = "None"


class TNumber(TObject):
    def __init__(self):
        super().__init__()
        self.strength = -1
        self.name = "Number"


class TInt(TNumber):
    def __init__(self):
        super().__init__()
        self.strength = 1
        self.name = "int"


class TBool(TInt):
    def __init__(self):
        super().__init__()
        self.strength = 0
        self.name = "bool"


class TFloat(TNumber):
    def __init__(self):
        super().__init__()
        self.strength = 2
        self.name = "float"


class TComplex(TNumber):
    def __init__(self):
        super().__init__()
        self.strength = 3
        self.name = "complex"


class Generic(list, Type):
    """
    Class used to control possible values for variables

    When list or tuples are used as domains, they are automatically
    converted to an instance of that class.
    """

    def __eq__(self, other):
        return self.get_name() == other.get_name()

    def __hash__(self):
        return hash(self.get_name())

    def get_name(self):
        return "Generic" + str(self)

    def __init__(self, set, variable=None, constraint_problem=None):
        """
        @param set: Set of values that the given variables may assume
        @type  set: set of objects comparable by equality
        """
        list.__init__(self, set)
        self._hidden = []
        self._states = []
        self.constraint_problem = constraint_problem
        self.variable = variable

    def has_supertype(self, t):
        """Check if this Generic has a supertype for t"""
        for ti in self:
            if t.is_subtype(ti):
                return True
        return False

    def narrow(self, domain_filter):
        """Narrow the domain of this Generic
        Example:
            x = Domain([Type()])
            x.narrow([TNumber(), TSequence()]) --> x = Domain([TNumber, TSequence])
            x.narrow([TBool()]) --> x = Domain([TBool()])
        """
        to_remove = []
        to_add = []
        for t in self:
            keep = True
            has_sup = False
            for t2 in domain_filter:
                if t2.is_subtype(t):
                    keep = False
                    if t2 not in to_add:
                        to_add.append(t2)
                elif t.is_subtype(t2):
                    has_sup = True
            if (not keep) or (not has_sup):
                to_remove.append(t)
        for t in to_add:
            self.append(t)
        for t in to_remove:
            self.remove(t)

        if len(self) == 0:
            raise ValueError("Narrowed domain is empty.")

        self.constraint_problem.setDomain(self.variable, self)

    def resetState(self):
        """
        Reset to the original domain state, including all possible values
        """
        self.extend(self._hidden)
        del self._hidden[:]
        del self._states[:]

    def pushState(self):
        """
        Save current domain state

        Variables hidden after that call are restored when that state
        is popped from the stack.
        """
        self._states.append(len(self))

    def popState(self):
        """
        Restore domain state from the top of the stack

        Variables hidden since the last popped state are then available
        again.
        """
        diff = self._states.pop() - len(self)
        if diff:
            self.extend(self._hidden[-diff:])
            del self._hidden[-diff:]

    def hideValue(self, value):
        """
        Hide the given value from the domain

        After that call the given value won't be seen as a possible value
        on that domain anymore. The hidden value will be restored when the
        previous saved state is popped.

        @param value: Object currently available in the domain
        """
        list.remove(self, value)
        self._hidden.append(value)


class TSequence(TObject):
    def __init__(self):
        super().__init__()
        self.name = "Sequence"


class TMutableSequence(TSequence):
    def __init__(self):
        super().__init__()
        self.name = "MutableSequence"


class TImmutableSequence(TSequence):
    def __init__(self):
        super().__init__()
        self.name = "Immutable Sequence"


class TString(TImmutableSequence):
    def __init__(self):
        super().__init__()
        self.name = "str"


class TBytesString(TImmutableSequence):
    def __init__(self):
        super().__init__()
        self.name = "bytes"


class TList(TMutableSequence):
    """Type given to homogeneous lists.

    Attributes:
        type (Type): Type of the list elements
    """

    def __init__(self, t=Generic([Type()])):
        super().__init__()
        self.type = t
        self.name = "list"

    def is_subtype(self, t):
        if isinstance(t, Generic) and t.has_supertype(self):
            return True
        if type(t) in [TObject, TMutableSequence, TSequence, Type]:
            return True
        return isinstance(t, TList) and self.type.get_name() == t.type.get_name()

    def get_name(self):
        return "{}[{}]".format(self.name, self.type.get_name())


class TTuple(TImmutableSequence):
    """Type given to a tuple.

    Attributes:
        types ([Type]): Types of the tuple elements.
    """

    def __init__(self, t):
        super().__init__()
        self.types = t
        self.name = "tuple"

    def is_subtype(self, t):
        if isinstance(t, Generic) and t.has_supertype(self):
            return True
        if type(t) in [TObject, TImmutableSequence, TSequence, Type]:
            return True
        if not isinstance(t, TTuple):
            return False
        if len(self.types) != len(t.types):
            return False
        for i in range(len(self.types)):
            if not self.types[i].is_subtype(t.types[i]):
                return False
        return True

    def get_name(self):
        types_names = [t.get_name() for t in self.types]
        return "{}({})".format(self.name, ",".join(types_names))

    def get_possible_tuple_slicings(self):
        """Returns a union type of all possible slicings of this tuple

        For example:
            t = (1, "string", 2.5)

            t.get_possible_tuple_slicings() will return the following
            Union{Tuple(Int), Tuple(Int,String), Tuple(Int,String,Float), Tuple(String),
                    Tuple(String,Float), Tuple(Float), Tuple()}

        """
        slices = {TTuple([])}
        for i in range(len(self.types)):
            for j in range(i + 1, len(self.types) + 1):
                slices.add(TTuple(self.types[i:j]))
        return UnionTypes(slices)


class TIterator(TObject):
    """Type given to an iterator.

    Attributes:
        type (Type): Type of the iterator.
    """

    def __init__(self, t=Generic([Type()])):
        super().__init__()
        self.type = t

    def is_subtype(self, t):
        if isinstance(t, Generic) and t.has_supertype(self):
            return True
        if type(t) in [TObject, Type]:
            return True
        return isinstance(t, TIterator) and isinstance(self.type, type(t.type))

    def get_name(self):
        return "Iterator({})".format(self.type.get_name())


class TDictionary(TObject):
    """Type given to a dictionary, whose keys are of the same type, and values are of the same type.

    Attributes:
        key_type (Type): Type of the dictionary keys.
        value_type (Type): Type of the dictionary values.
    """

    def __init__(self, t_k=Generic([Type()]), t_v=Generic([Type()])):
        super().__init__()
        self.key_type = t_k
        self.value_type = t_v
        self.name = "dict"

    def is_subtype(self, t):
        if isinstance(t, Generic) and t.has_supertype(self):
            return True
        if type(t) in [TObject, Type]:
            return True
        return (isinstance(t, TDictionary) and isinstance(self.key_type, type(t.key_type))
                and isinstance(self.value_type, type(t.value_type)))

    def get_name(self):
        return "{}({}:{})".format(self.name, self.key_type.get_name(), self.value_type.get_name())


class TSet(TObject):
    """Type given to homogeneous sets"""

    def __init__(self, t=Generic([Type()])):
        super().__init__()
        self.type = t
        self.name = "set"

    def is_subtype(self, t):
        if isinstance(t, Generic) and t.has_supertype(self):
            return True
        if type(t) in [TObject, Type]:
            return True
        return isinstance(t, TSet) and self.type.is_subtype(t.type)

    def get_name(self):
        return "{}({})".format(self.name, self.type.get_name())


class TFunction(TObject):
    """Type given to a function.

    Attributes:
        return_type (Type): Type of the function return value.
        arg_types ([Type]): A list of types for the function arguments.
    """

    def __init__(self, t_r, t_a):
        super().__init__()
        self.return_type = t_r
        self.arg_types = t_a
        self.name = "function"

    def is_subtype(self, t):
        if isinstance(t, Generic) and t.has_supertype(self):
            return True
        if type(t) in [TObject, Type]:
            return True
        if not isinstance(t, TFunction):
            return False
        if len(self.arg_types) != len(t.arg_types):
            return False
        if not self.return_type.is_subtype(t.return_type):
            return False
        for i in range(len(self.arg_types)):
            if not t.arg_types[i].is_subtype(self.arg_types[i]):
                return False
        return True

    def get_name(self):
        args_types_names = [t.get_name() for t in self.arg_types]
        return "{}({}) --> {}".format(self.name, ",".join(args_types_names), self.return_type.get_name())


class UnionTypes(Type):
    """Type given to variables that are inferred to have a range of types.

    Attributes:
        types (set{Type}): An unordered set of possible types.
    """

    def __init__(self, t=set()):
        super().__init__()
        self.types = set()
        if isinstance(t, TObject):
            self.union(t)
        else:
            for ti in t:
                self.union(ti)

    def is_subtype(self, t):
        if len(self.types) == 1:
            unique_type = list(self.types)[0]
            if unique_type.is_subtype(t):
                return True
        if not isinstance(t, UnionTypes):
            return False
        for m_t in self.types:  # look for a supertype in t.types for every type in self.types
            found_supertype = False
            for t_t in t.types:
                if m_t.is_subtype(t_t):
                    found_supertype = True
                    break
            if not found_supertype:
                return False

        return True

    def get_name(self):
        types_names = sorted([t.get_name() for t in self.types])
        return "Union{{{}}}".format(",".join(types_names))

    def union(self, other_type):
        """Add other types to the union"""
        if isinstance(other_type, UnionTypes):
            for t in other_type.types:
                self.union(t)
        else:
            to_remove = set()
            for t in self.types:
                if other_type.is_subtype(t):  # Ignore union if supertype already exists in the set
                    return
                elif t.is_subtype(other_type):  # Remove subtypes of added type
                    to_remove.add(t)
            for t in to_remove:
                self.types.remove(t)
            self.types.add(other_type)
