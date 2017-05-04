from Base import Net,Node
import re


def parse_file(file_name):
    f = open(file_name)
    net_list = f.readlines()
    net_list_object = {}
    numbers_pattern = re.compile('^[0-9]')

    for line in net_list:
        if line[0] != '+':
            net_list_object[line.split()[0]] = [block for block in line.split()[1:] if ((block == '0' or (not re.match(numbers_pattern, block))) and (block[0:3] != "TC=") and (block[0:6] != "PARAMS"))]

    reverse_list_object = {};

    for key in net_list_object.keys():
        for block in net_list_object[key]:
            if block in reverse_list_object:
                reverse_list_object[block].append(key)
            else:
                reverse_list_object[block] = []
                reverse_list_object[block].append(key)
    nodes = []
    nets = []

    for key in reverse_list_object.keys():
        nets.append(Net(id=key))
        for block in reverse_list_object[key]:
            if block not in nodes:
                nodes.append(Node(id=block))
            nets[-1].add_node(nodes[nodes.index(block)])
    # for net in nets:
    #     print(net)
    # print("\r\n\r\n")
    return nets, nodes
