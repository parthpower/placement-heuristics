# -*- coding: utf-8 -*-
"""
Created on Thu Mar 16 10:33:50 2017

@author: Parth
"""

from sys import argv
import numpy as np
import Base
from Base import Node, Net, Board
import matplotlib.pyplot as plt
import copy
import svgwrite
import threading
import atexit
from netlist_parser import parse_file

nets_or = []
nodes_or = []


def show_graph():
    # b = Board(0, nets, min_cost_placement, 12, 12)
    print('\n\r\n')
    # print(b)

    for i in range(len(min_cost_placement)):
        nodes_or[i].pos = min_cost_placement[i].pos
        print(nodes_or[i])
    print("MIN COST %d" % min_cost)
    svg_draw_board(min_cost_placement, nets, BOX_W, BOX_H, "BEST.svg", str(min_cost),NODE_C_=NODE_C,NET_C_=NET_C)
    plt.plot(cost_list)
    plt.show()
    while True:
        plt.pause(1)
    return 0


atexit.register(show_graph)


def svg_draw_board(nodes, nets, w, h, svg_name="netList.svg", txt="HI", H=50, W=50, spacing_x=5, spacing_y=5,NODE_C_ = 50,NET_C_=50):
    """

    :type nets: list
    :param nets:
    :type nodes: list
    """
    w2 = float(W) / 2
    h2 = float(H) / 2

    svg_doc = svgwrite.Drawing(filename=svg_name, size=((W + spacing_y) * w + 100, (H + spacing_x) * h + 100,))
    # add nodes

    svg_doc.add(svg_doc.rect(insert=(0, 0), size=((W * w, H * h)), stroke_width="1", stroke="blue", fill="none"))

    node_color_space = np.linspace(0, 255, NODE_C_)
    net_color_space = np.linspace(0, 255, NET_C_)

    for node in nodes:
        x = node.pos[0]
        y = node.pos[1]
        svg_doc.add(svg_doc.rect(insert=(W * x, H * y), size=(W, H), stroke_width="1", stroke="black",
                                 fill=svgwrite.rgb(int(node_color_space[node.id]), 0, 100)))

    # add nets
    for net in nets:
        for i in range(1, len(net)):
            x1 = net.nodeList[i - 1].pos[0]
            y1 = net.nodeList[i - 1].pos[1]
            x2 = net.nodeList[i].pos[0]
            y2 = net.nodeList[i].pos[1]

            svg_doc.add(svgwrite.shapes.Line((x1 * W + w2, y1 * H + h2), (x2 * W + w2, y2 * H + h2), stroke_width=2,
                                             stroke=svgwrite.rgb(int(net_color_space[net.id]),
                                                                 int(net_color_space[net.id]), 0)))
    svg_doc.add(svg_doc.text(txt, insert=((H + spacing_x) * h, (W * spacing_y) * w)))
    svg_doc.save()


def svg_draw_board_2(nodes, nets, w, h, svg_name="netList.svg", txt="HI", H=50, W=50, spacing_x=5, spacing_y=5,NODE_C_ = 10,NET_C_=10):
    """

    :type nets: list
    :param nets:
    :type nodes: list
    """
    w2 = float(W) / 2
    h2 = float(H) / 2

    svg_doc = svgwrite.Drawing(filename=svg_name, size=((W + spacing_y) * w + 100, (H + spacing_x) * h + 100,))
    # add nodes

    svg_doc.add(svg_doc.rect(insert=(0, 0), size=((W * w, H * h)), stroke_width="1", stroke="blue", fill="none"))

    node_color_space = np.linspace(0, 255, NODE_C_)
    net_color_space = np.linspace(0, 255, NET_C_)

    for node in nodes:
        x = node.pos[0]
        y = node.pos[1]
        svg_doc.add(svg_doc.rect(insert=(W * x, H * y), size=(W, H), stroke_width="1", stroke="black",
                                 fill=svgwrite.rgb(int(node_color_space[node.id]), 0, 100)))

    # add nets
    for net in nets:
        for i in range(1, len(net)):
            x1 = Base.get_node_by_id(net[i - 1], nodes).pos[0]
            y1 = Base.get_node_by_id(net[i - 1], nodes).pos[1]
            x2 = Base.get_node_by_id(net[i],nodes).pos[0]
            y2 = Base.get_node_by_id(net[i],nodes).pos[1]

            svg_doc.add(svgwrite.shapes.Line((x1 * W + w2, y1 * H + h2), (x2 * W + w2, y2 * H + h2), stroke_width=2,
                                             stroke=svgwrite.rgb(int(net_color_space[nets.index(net)]),
                                                                 int(net_color_space[nets.index(net)]), 0)))
    svg_doc.add(svg_doc.text(txt, insert=((H + spacing_x) * h, (W * spacing_y) * w)))
    svg_doc.save()



NODE_C = 7
NET_C = 5
BOX_W = 10
BOX_H = 10
T = 10000
M = 10000
alfa = 0.998
beta = 1.001
Final_T = 100

ERR_CONSTRAIN = 0.1
cost_list = []
nodes = []
nets = []
min_cost_placement = []
min_cost = 0


if __name__ == "__main__":

    if len(argv) < 11:
        print("Usage:%s #node #net width height initTemp finalTemp M alfa beta err_const")
        NODE_C = 150
        NET_C = 250
        BOX_H = 10
        BOX_W = 10
        T = 10000
        M = 10000
        alfa = 0.998
        beta = 1.001
        Final_T = 100
        ERR_CONSTRAIN = 0.001
    else:
        NODE_C = int(argv[1])
        NET_C = int(argv[2])
        BOX_W = int(argv[3])
        BOX_H = int(argv[4])
        T = float(argv[5])
        Final_T = float(argv[6])
        M = int(argv[7])
        alfa = float(argv[8])
        beta = float(argv[9])
        ERR_CONSTRAIN = float(argv[10])

    # board matrix
    # for i in range(NODE_C):
    #     nodes.append(Node((0, 0), i))
    #
    # for i in range(NET_C):
    #     nets.append(Net(i))
    #     itr = np.random.randint(2, 5)
    #     for j in range(itr):
    #         n_id = np.random.randint(NODE_C)
    #         if not nets[i].has(nodes[n_id]):
    #             nets[i].add_node(nodes[n_id])


    nets_or, nodes_or = parse_file("orcadNetlist.txt")
    nets = copy.deepcopy(nets_or)
    nodes = copy.deepcopy(nodes_or)

    i = 0

    for n in nodes:
        n.id = i
        i += 1
        n_tmp = []
        for netIdOld in n.netIds:
            n_tmp.append(nets_or.index(netIdOld))
        n.netIds = copy.copy(n_tmp)

    i = 0
    for n in nets:
        n.id = i
        i += 1
        n_tmp = copy.deepcopy(n.nodeList)
        n.nodeList = []
        for node in n_tmp:
            n.nodeList.append(nodes[nodes_or.index(node)])
    NODE_C = len(nodes)
    NET_C = len(nets)
    ################# END ORCAD NETLIST PARSING##################
    c = 0
    for net in nets:
        c += len(net) - 1
    print("LOWER BOUND:%d" % c)
    Base.random_place_board(nodes, BOX_W, BOX_H)
    cost = Base.get_total_cost(nets)
    min_cost = cost
    min_cost_placement = copy.deepcopy(nodes)
    # svg_draw_board(nodes, nets, BOX_W, BOX_H, svg_name="Init" + "_" + str(cost) + ".svg", txt=str(cost))
    svg_draw_board(nodes, nets, BOX_W, BOX_H, svg_name="Init.svg", txt=str(cost),NODE_C_=NODE_C,NET_C_=NET_C)
    itr = 0
    while T > Final_T:
        # if float(min_cost - c) / 100 / c < ERR_CONSTRAIN * 0.01:
        #     break
        # Metropolis
        for i in range(int(M)):
            itr += 1
            n1 = np.random.choice(nodes)
            n1_pos = copy.copy(n1.pos)

            rn_pos = (np.random.randint(BOX_W), np.random.randint(BOX_H))
            while rn_pos == n1.pos:
                rn_pos = (np.random.randint(BOX_W), np.random.randint(BOX_H))

            n2 = Base.find_node_at(rn_pos, nodes)
            if not n2:  # Swap with empty place
                n1.pos = rn_pos
                nd = False
            else:
                Base.swap(n1, n2)
                nd = True
            new_cost = Base.get_total_cost(nets)
            h = new_cost - cost

            # Store Minimum cost
            if cost < min_cost:
                min_cost = cost

                min_cost_placement = copy.deepcopy(nodes)
                svg_draw_board(min_cost_placement, nets, BOX_W, BOX_H, "BEST.svg", str(min_cost),NODE_C_=NODE_C,NET_C_=NET_C)
            # Good solution
            if h < 0:
                cost = new_cost
            else:
                # Bad solution
                rn = np.random.rand()
                if rn <= np.exp(-1 * h / T):
                    # Reject with probability
                    if nd:
                        Base.swap(n1, n2)
                    else:
                        n1.pos = n1_pos
                else:
                    cost = new_cost

            cost_list.append(cost)
            if min_cost == c:
                break
            if len(cost_list) % 100 == 0:
                print("%d T:%f MIN:%d Current COST:%d\r" % (len(cost_list), T, min_cost, cost), end='\r')
                # t = threading.Thread(target=svg_draw_board,
                #					args=(nodes, nets, BOX_W, BOX_H, "currentNet.svg", str(cost)))
                # args=(nodes, nets, BOX_W, BOX_H, str(itr) + "_" + str(cost) + ".svg", str(cost)))
                # t.daemon = True
                # t.start()

        T *= alfa
        M *= beta
    # b = Board(0, nets, min_cost_placement, 12, 12)
    svg_draw_board(min_cost_placement, nets, BOX_W, BOX_H, "BEST.svg", str(min_cost),NODE_C_=NODE_C,NET_C_=NET_C)
    print('\n\r\n')
    # print(b)
    print(min_cost)
    for i in range(len(min_cost_placement)):
        nodes_or[i].pos = min_cost_placement[i].pos
        print(nodes_or[i])
    print("MIN COST %d" % min_cost)

    plt.plot(cost_list)
    plt.show()
    while True:
        plt.pause(1)
