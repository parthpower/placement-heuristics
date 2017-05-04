from sys import argv
import Base
from Base import Net
from Base import Node, Board
import Base_Test
import numpy as np
import copy
import atexit
import matplotlib.pyplot as plt
import Base_Test
from netlist_parser import parse_file


def show_graph():
    # b = Board(0, nets, min_cost_placement, 12, 12)
    print('\n\r\n')
    # print(b)

    for i in range(len(min_cost_placement)):
        nodes_or[i].pos = min_cost_placement[i].pos
        print(nodes_or[i])
    print("MIN COST %d" % min_cost)
    Base_Test.svg_draw_board(min_cost_placement, nets, BOX_W, BOX_H, "BEST.svg", str(min_cost),NODE_C_=NODE_C,NET_C_=NET_C)
    plt.plot(cost_list)
    plt.show()
    while True:
        plt.pause(1)
    return 0

atexit.register(show_graph)

def round_pos(pos):
    r_x = round(pos[0])
    r_y = round(pos[1])
    if r_x < 0:
        r_x = 0
    if r_y < 0:
        r_y = 0
    return r_x, r_y


def get_xy_point(nd, connected_nodes):
    if len(connected_nodes) == 0:
        return nd.get_x(), nd.get_y()
    x, y = (nd.get_x(), nd.get_y())
    x_b, y_b = (0, 0)

    for n in connected_nodes:
        x_b, y_b = (x_b + abs(x - n.get_x()), y_b + abs(y - n.get_y()))

    x_b, y_b = (float(x_b) / len(connected_nodes), float(y_b) / len(connected_nodes))

    return x_b, y_b


def get_force_vector(nd, connected_nodes):
    x, y = (nd.get_x(), nd.get_y())
    Fx_b, Fy_b = (0, 0)

    for n in connected_nodes:
        Fx_b, Fy_b = (Fx_b + (x - n.get_x()), Fy_b + (y - n.get_y()))

    return Fx_b, Fy_b


def get_max_force_node(nodes):
    max_force_node = nodes[0]
    for i in range(1, len(nodes)):
        if nodes[i]["force_mag"] > max_force_node["force_mag"]:
            max_force_node = nodes[i]
    return max_force_node


def get_force_mag(coordinates):
    return (coordinates[0] ** 2 + coordinates[1] ** 2) ** 0.5


nodes = []
nets = []
cost_list = []
NODE_C = 1000
NET_C = 1000
BOX_W = 100
BOX_H = 100
min_cost_placement = []
min_cost = 0
if __name__ == '__main__':
    debug = False

    if len(argv) < 5:
        print("Usage: FD_Placement.py #node #nets width height error_margin #iterations")
        NODE_C = 1500
        NET_C = 2000
        BOX_W = 13
        BOX_H = 5
        ITR_COUNT = 1000
        ERR_CONSTRAIN = -10000000000000
    else:
        NODE_C = int(argv[1])
        NET_C = int(argv[2])
        BOX_W = int(argv[3])
        BOX_H = int(argv[4])
        ERR_CONSTRAIN = float(argv[5])
        ITR_COUNT = int(argv[6])
    locked_nodes = []

    for i in range(NODE_C):
        nodes.append(Node((0, 0), i))

    for i in range(NET_C):
        nets.append(Net(i))
        itr = np.random.randint(3, 5)
        for j in range(itr):
            n_id = np.random.randint(NODE_C)
            if not nets[i].has(nodes[n_id]):
                nets[i].add_node(nodes[n_id])


################# END ORCAD NETLIST PARSING##################
    nets_or,nodes_or = parse_file("orcadNetlist.txt")
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

    i=0
    for n in nets:
        n.id = i
        i+=1
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
    Base_Test.svg_draw_board(nodes, nets, BOX_W, BOX_H, svg_name="Init_FD.svg", txt=str(cost),NODE_C_=NODE_C,NET_C_=NET_C)
    min_cost = cost
    last_cost = cost
    min_cost_placement = copy.copy(nodes)
    b = Board(nets=nets, nodes=nodes, width=BOX_W, height=BOX_H)
    if debug:
        print(b)

    forces = []
    cost_list = []

    for i in range(ITR_COUNT):
        for node in nodes:
            connected_nodes = Base.get_connected_nodes(node, nets)
            forces.append({
                'force_mag': get_force_mag(get_force_vector(node, connected_nodes)),
                'node': node,
                'zero_pos': get_xy_point(node, connected_nodes)})

        while len(forces) > 0:
            max_force_node = get_max_force_node(forces)
            forces.remove(max_force_node)
            if debug:
                print("MAX_FORCE_NODE:%s : %f" % (max_force_node["node"], max_force_node["force_mag"]))




            # Try Moving it..
            dst_pos = Base.find_nearby_unlocked(round_pos(max_force_node["zero_pos"]), nodes, BOX_W, BOX_H)
            mm = 0
            for n in nodes:
                if n.pos == dst_pos:
                    mm+=1
                if mm > 1:
                    print("!!!!")


            if dst_pos != max_force_node["node"].pos:
                if dst_pos != False:
                    n2 = Base.find_node_at(dst_pos, nodes)
                    if type(n2) == type(False):
                        max_force_node["node"].pos = dst_pos
                        last_op = "Place"
                    else:
                        Base.swap(max_force_node["node"], n2)
                        print("SWAPPED %s %s"%(max_force_node["node"],n2))
                        last_op = "SWAP"
                else:
                    if debug:
                        print("No place to move!")
            mm = 0
            for n in nodes:
                if n.pos == dst_pos:
                    mm+=1
                if mm > 1:
                    print("!!!!")
            max_force_node["node"].locked = True

        Base.unlock_all_nodes(nodes)
        current_cost = Base.get_total_cost(nets)
        cost_list.append(current_cost)
        if current_cost < min_cost:
            min_cost = current_cost
            min_cost_placement = copy.deepcopy(nodes)
            Base_Test.svg_draw_board(min_cost_placement, nets, BOX_W, BOX_H, "BEST_FD.svg", str(min_cost),NODE_C_=NODE_C,NET_C_=NET_C)

        if len(cost_list)%10 == 0:
            print("%d MIN:%d Current COST:%d\r" % (len(cost_list), min_cost, current_cost), end='\r')

        if current_cost == last_cost:
            break

        last_cost = current_cost

        if 100*float(min_cost - c)/c < ERR_CONSTRAIN:
            break

        if min_cost == c:
            break


        #print("%d MIN:%d Current COST:%d" % (len(cost_list),min_cost,current_cost))
    for i in range(len(min_cost_placement)):
        nodes_or[i].pos = min_cost_placement[i].pos
        print(nodes_or[i])
    print("MIN COST %d" % min_cost)
    plt.plot(cost_list)
    plt.show()
    while True:
        plt.pause(1)
