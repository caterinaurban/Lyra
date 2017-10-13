# https://github.com/justmarkham/DAT8/blob/master/code/03_python_homework_chipotle.py


def main(filename):
    import csv


    with open(filename, mode='rU') as f:
        file_nested_list = [row for row in csv.reader(f, delimiter='\t')]

    # MAD: len(file_nested_list) > 0
    header = file_nested_list[0]
    data = file_nested_list[1:]

    print(data)
    # MAD: len(data) > 0
    print(data[0])
    # MAD: length of a row in data > 4
    # MAD: the fifth element of each in row in data must be slicable
    print([row[4][1:-1] for row in data])

    num_orders = len(set([row[0] for row in data]))
    prices = [float(row[4][1:-1]) for row in data]
    # MAD: num_order cannot be zero => len(data) > 0
    round(sum(prices) / num_orders, 2)

    sodas = []
    for row in data:
        if 'Canned' in row[2]:
            # MAD: len(row) > 3
            # MAD: the third element of each in row in data must be slicable
            sodas.append(row[3][1:-1])

    # MAD: len(row) > 3
    # MAD: the third element of each in row in data must be slicable
    sodas = [row[3][1:-1] for row in data if 'Canned' in row[2]]
    unique_sodas = set(sodas)

    burrito_count = 0
    topping_count = 0
    for row in data:
        # MAD: len(row) > 2
        if 'Burrito' in row[2]:
            burrito_count += 1
            topping_count += (row[3].count(',') + 1)
    # MAD: burrito_count != 0 => len(data) > 0 and there must be a row with 'Burrito' in row[2]
    round(topping_count / float(burrito_count), 2)

    chips = {}
    for row in data:
        if 'Chips' in row[2]:
            if row[2] not in chips:
                # row[1] must be int
                chips[row[2]] = int(row[1])
            else:
                # row[1] must be int
                chips[row[2]] += int(row[1])

    from collections import defaultdict
    dchips = defaultdict(int)
    for row in data:
        if 'Chips' in row[2]:
            dchips[row[2]] += int(row[1])

if __name__ == '__main__':
    main('chipotle.tsv')
    #main('chipotle_few_elems.tsv')
    #main('chipotle_no_burrito.tsv')