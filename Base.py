# -*- coding: utf-8 -*-
"""
@author Parth Parikh
"""

##Simulated Annealing
import numpy as np
from numpy.random import randint
import matplotlib.pyplot as plt


class Node:
    def __init__(self, pos=(0, 0), id=0,locked=False):
        self.pos = pos
        self.id = id
        self.netIds = list()
        self.locked = locked

    def get_degree(self):
        return len(self.netIds)

    def get_x(self):
        return self.pos[0]

    def get_y(self):
        return self.pos[1]

    def get_distance(self, node):
        return abs(self.pos[0] - node.pos[0]) + abs(self.pos[1] - node.pos[1])

    def __str__(self):
        return str(str(self.id) + ':(' + str(self.pos[0]) + ',' + str(self.pos[1]) + ')')

    def __int__(self):
        return self.id

    def __eq__(self, i):
        return self.id == i


class Net:
    def __init__(self, id=0):
        self.id = id
        self.nodeList = list()

    def add_node(self, node):
        self.nodeList.append(node)
        node.netIds.append(self.id)

    def add_nodes_from(self, node_list):
        for node in node_list:
            self.nodeList.append(node)

    def remove_node(self, node_id):
        self.nodeList.remove(node_id)

    def has(self, node_id):
        return node_id in self.nodeList

    def get_cost(self):
        max_x = 0
        max_y = 0
        for node in self.nodeList:
            x = node.pos[0]
            y = node.pos[0]
            if x > max_x:
                max_x = x
            if y > max_y:
                max_y = y
        return max_x + max_y

    def __len__(self):
        return len(self.nodeList)

    def __str__(self):
        string = str(self.id) + ':\n'
        for node in self.nodeList:
            string = string + '\t' + str(node) + '\n'
        return string

    def __eq__(self, other):
        return self.id == other

class Board:
    def __init__(self, id=0, nets=[], nodes=[], width=0, height=0):
        self.width = width
        self.height = height
        self.nets = nets
        self.id = id
        self.nodes = nodes

    def add_net(self, net):
        self.nets.append(net)

    def add_node(self, node):
        self.nodes.append(node)

    def get_cost(self):
        cost = 0
        for net in self.nets:
            cost = cost + net.get_cost()
        return cost

    def is_empty(self, pos):
        for node in self.nodes:
            if pos == node.pos:
                return False
        return True

    def __str__(self):
        string = str(self.id) + ":\n"
        for net in self.nets:
            string = string + str(net)
        return string


def is_pos_empty(pos, nodeList):
    for node in nodeList:
        if pos == node.pos:
            return False
    return True


def get_total_cost(nets):
    cost = 0
    for net in nets:
        cost += net.get_cost()
    return cost


def random_place_board(nodeList, width, height, debug=False):
    for node in nodeList:
        n_x = 0
        n_y = 0
        while not is_pos_empty((n_x, n_y), nodeList):
            n_x = randint(width)
            n_y = randint(height)
        if debug:
            print("NODE:%d at (%d,%d)" % (node.id, n_x, n_y))
        node.pos = (n_x, n_y)
    return nodeList


def swap(n1: Node, n2: Node) -> None:
    pos = n1.pos
    n1.pos = n2.pos
    n2.pos = pos


def draw_board(nodeList):
    """

    :type nodeList: list
    """
    x = []
    y = []
    area = []
    for node in nodeList:
        x.append(node.pos[0])
        y.append(node.pos[1])
        area.append(np.pi * node.get_degree())

    plt.scatter(x, y, s=area)
    plt.show()

def find_node_at(pos,nodeList):
    for node in nodeList:
        if node.pos == pos:
            return node
    return False


def get_connected_nodes(n,nets):
    """

    :param n:
    :return:
    """
    connected_nodes = []

    for i in n.netIds:
        net = nets[i]
        for nd in net.nodeList:
            if nd not in connected_nodes and nd != n:
                connected_nodes.append(nd)
    return connected_nodes


def find_nearby_unlocked(pos, node_list, width, height ):
    # Find nearby empty place
    x = pos[0]
    y = pos[1]

    w = 0
    h = 0
    while True:
        W_L = x - w
        W_R = x + w
        H_U = y + h
        H_D = y - h

        if W_L<0:
            W_L = 0
        if W_R>width-1:
            W_R = width - 1
        if H_U>height-1:
            H_U = height -1
        if H_D<0:
            H_D = 0
        w += 1
        h += 1

        scan_x = range(W_L,W_R+1)
        scan_y = range(H_D, H_U+1)

        for i in scan_x:
            for j in [H_D,H_U]:
                a = find_node_at((i,j),node_list)
                if not a:
                    return i,j
                if not a.locked:
                    return i,j

        for i in [W_R,W_L]:
            for j in scan_y:
                a = find_node_at((i,j),node_list)
                if not a:
                    return i,j
                if not a.locked:
                    return i,j
        if W_R == width-1 and W_L == 0 and H_U == height-1 and H_D == 0:
            break
    return False


def unlock_all_nodes(nodes):
    for i in nodes:
        i.locked = False


def get_node_by_id(id,nodes):
    for i in nodes:
        if i.id == id:
            return i
    return False


def get_total_cost_nodes(nets,nodes):
    cost = 0
    for net in nets:
        x_max = 0
        y_max = 0
        for node_id in net:
            node = get_node_by_id(node_id,nodes)
            if node.get_x() > x_max:
                x_max = node.get_x()
            if node.get_y() > y_max:
                y_max = node.get_y()
        cost += x_max + y_max
    return cost


def get_fitness(nets, nodes):
    return 1/float(1+get_total_cost_nodes(nets, nodes))
