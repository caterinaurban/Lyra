import ast

source_string = 'a = b[2]; a = b[5]; a = b[3]; a = b[1]; a = b[6]; b = t.split(\',\'); t = input()'
input_string = '1,2,3,4,5,6,7,8'


class ListAbs:
    def __init__(self, left, value, right):
        self.left = left
        self.value = value
        self.right = right
        self.delimiter = ' '

    @classmethod
    def defaultinit(cls):
        return cls(0, 'T', 'len')

    def __str__(self):
        s = ''
        if type(self.left) is ListAbs :
            left_str = self.left.__str__()
            s = s + left_str
        else:
            s = s + ('{%s}' % self.left)
        s = s + ' %s ' % self.value
        if type(self.right) is ListAbs :
            right_str = self.right.__str__()
            s = s + right_str
        else:
            s = s + ('{%s}' % self.right)
        return s

    # {0} T {len} -> split 1 -> {0} T {1} T {len}?
    #             -> split i -> {0} T {i}? T {len}?
    # {0} T {N} T {len} -> split 1 -> {0} T {1} T {N}? T {len}?
    #                   -> split 2 -> {0} T {N} T {len}? AND {0} T {2} T {len}?
    def split(self, new_value):
        try:
            number = int(new_value)
            if type(self.left) is ListAbs:
                if self.left.split(number):
                    return True
            else:
                number_left = int(self.left)
                if number_left == number:
                    return True
                elif number_left > number:
                    self.left = ListAbs(number, self.value, number_left)
                    return True
            if type(self.right) is ListAbs:
                if self.right.split(number):
                    return True
            else:
                if self.right == 'len':
                    self.right = ListAbs(number, self.value, self.right)
                    return True
                number_right = int(self.right)
                if number_right == number:
                    return True
                elif number_right > number:
                    self.right = ListAbs(number, self.value, number_right)
                    return True
        except ValueError:
            raise NotImplementedError('case value is not number')
        return False

    def get_assumption(self, index):
        if type(self.left) is ListAbs:
            assumption = self.left.get_assumption(index)
            if assumption is not None:
                return assumption
        elif self.left == index:
            return self.value
        if type(self.right) is ListAbs:
            assumption = self.right.get_assumption(index)
            if assumption is not None:
                return assumption
        elif self.right == 'len':
            return self.value
        elif self.right > index:
            return self.value

    def get_min_length(self):
        if type(self.right) is ListAbs:
            return self.right.get_min_length()
        elif self.right != 'len':
            return self.right
        elif type(self.left) is ListAbs:
            return self.left.get_min_lingth()
        return self.left


class MyVisitor(ast.NodeVisitor):

    # done with a first analaysis of what kind of variables exist
    arrays = {'b': ListAbs.defaultinit(), 'LINES' : ListAbs.defaultinit()}
    inputcounter = 0

    def generic_visit(self, node):
        ast.NodeVisitor.generic_visit(self, node)

    def visit_Subscript(self, node):
        array_name = ast.NodeVisitor.visit(self, node.value)
        index_value = ast.NodeVisitor.visit(self, node.slice)
        curr_list_abs = self.arrays[array_name]
        curr_list_abs.split(index_value)

    def visit_Name(self, node):
        return node.id

    def visit_Num(self, node):
        return node.n

    def visit_Index(self, node):
        return ast.NodeVisitor.visit(self, node.value)

    def visit_Assign(self, node):
        assign_to = ast.NodeVisitor.visit(self, node.targets[0])
        assign_right = ast.NodeVisitor.visit(self, node.value)
        if assign_right is not None:
            if assign_right == 'input':
                self.arrays['input%d' % self.inputcounter] = self.arrays.pop(assign_to)
                self.inputcounter += 1
            delimiter = assign_right.split(':')
            if delimiter[0] == 'delimiter':
                self.arrays[assign_to].delimiter = delimiter[1]
            if len(delimiter) >= 4 and delimiter[2] == 'name':
                self.arrays[delimiter[3]] = self.arrays.pop(assign_to)

    def visit_Attribute(self, node):
        return

    def visit_Call(self, node):
        if type(node.func) is ast.Attribute:
            if node.func.attr == 'split':
                return 'delimiter:,:name:t'
        elif type(node.func) is ast.Name:
            if node.func.id == 'split':
                return 'delimiter:,'
            if node.func.id == 'input':
                return 'input'


vis = MyVisitor()
print('arrays before:')
for array in vis.arrays:
    print('%s: ' % array, end='')
    print(vis.arrays[array])
source = ast.parse(source_string)

print('--- start analaysis')

vis.visit(source)
print('arrays after:')
for array in vis.arrays:
    print('%s: ' % array, end='')
    print(vis.arrays[array])

print('--- start checking')

for line_number, input_line in enumerate(input_string.split(';')):
    print('--- checking line', line_number, 'with input', input_line)
    list_abs = vis.arrays['input%d' % line_number]
    print('--- found list abstraction', list_abs)
    delimiter = list_abs.delimiter
    print('--- found delimiter', delimiter)
    input_values = input_line.split(delimiter)
    min_length_assumption = list_abs.get_min_length()
    if len(input_values) < min_length_assumption:
        print('ERROR line', line_number+1, ': expected at least', min_length_assumption,
              'elements splitted by', '"%s"' % delimiter,
              'instead found', len(input_values), 'elements')
    else:
        for ind, value in enumerate(input_values):
            assumption = list_abs.get_assumption(ind)
            print('--- checking assumption', assumption, 'for value', value, 'at index', ind)