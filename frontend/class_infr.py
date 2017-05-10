import frontend.z3_types as z3_types
import frontend.z3_axioms as axioms
from frontend.context import Context


class Class(Context):
    def __init__(self, name, parent_context=None):
        super().__init__(parent_context)
        self.name = name

    def get_attr_type(self, attr):
        if attr in self.types_map:
            return self.types_map[attr]
        else:
            raise NameError("Name {} is not defined.".format(attr))

    def delete_type(self, var_name):
        if var_name in self.types_map:
            del self.types_map[var_name]
        else:
            raise NameError("Name {} is not defined.".format(var_name))


class Instance:
    def __init__(self, cls):
        self.cls = cls

    def get_attribute_type(self, attr):
        try:
            return self.cls.get_attr_type(attr)
        except NameError:
            raise AttributeError("{} object has no attribute {}".format(self.cls.name, attr))

    def assign_attr(self, attr, t):
        try:
            attr_type = self.get_attribute_type(attr)
            if isinstance(attr_type, z3_types.z3.DatatypeRef):
                if isinstance(t, z3_types.z3.DatatypeRef):
                    z3_types.solver.add(axioms.assignment(attr_type, t))
        except AttributeError:
            if isinstance(t, z3_types.z3.DatatypeRef):
                attr_type = z3_types.new_z3_const("attr")
                z3_types.solver.add(axioms.assignment(attr_type, t))
                self.cls.set_type(attr, attr_type)
            else:
                self.cls.set_type(attr, t)

    def delete_attr(self, attr):
        try:
            self.cls.delete_type(attr)
        except NameError:
            raise AttributeError("{} object has no attribute {}".format(self.cls.name, attr))
