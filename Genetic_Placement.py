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
    # b = Board(0, nets, best_fitness_placement, 12, 12)
    print('\n\r\n')
    for i in range(len(best_fitness_placement["node_list"])):
        nodes_or[i].pos = best_fitness_placement["node_list"][i].pos
        print(nodes_or[i])
    print("MIN COST:%d"%(1/best_fitness - 1))
    Base_Test.svg_draw_board_2(best_fitness_placement["node_list"], net_list2, BOX_W, BOX_H, "BEST_FD.svg", str(1/best_fitness - 1),NODE_C_=NODE_C,NET_C_=NET_C)

    plt.figure()
    plt.plot(average_fitness_list)
    plt.figure()
    plt.plot(1 / np.array(average_fitness_list) - 1)
    plt.show()
    return 0

atexit.register(show_graph)


def get_fitness_list(gen):
    fitness = []
    for g in gen:
        fitness.append(g["fitness"])
    return fitness


def do_cross_over(parent_1, parent_2, width, height):
    n2 = False
    while n2 == False:
        keep_id = []
        nI = Base.find_node_at((np.random.randint(width), np.random.randint(height)), parent_1)
        while nI == False:
            nI = Base.find_node_at((np.random.randint(width), np.random.randint(height)), parent_1)

        keep_id.append(parent_1.index(nI))

        n1 = nI

        n2 = Base.find_node_at(n1.pos, parent_2)
        # Go back get another initial node to get the n2 not empty
        if type(n2) == type(False):
            continue

        p1_index = parent_1.index(n2)  # Index where n2 is located
        n1 = parent_1[p1_index]
        keep_id.append(p1_index)

    while nI != n1:
        n2 = Base.find_node_at(n1.pos, parent_2)
        if n2 == False:
            break
        p1_index = parent_1.index(n2)
        n1 = parent_1[p1_index]
        keep_id.append(p1_index)

    # do swap
    for i in range(len(parent_1)):
        if i not in keep_id:
            tmp = parent_1[i].id
            parent_1[i].id = parent_2[i].id
            parent_2[i].id = tmp


def do_mutation(nodes):
    itr = np.random.randint(len(nodes) / 4)
    for i in range(itr):
        n1 = np.random.choice(nodes)
        n2 = np.random.choice(nodes)
        while n2 == n1:
            n2 = np.random.choice(nodes)
        Base.swap(n1, n2)


NODE_C = 1000
NET_C = 1000
BOX_W = 8
BOX_H = 10
best_fitness_placement = []
best_fitness = 0
average_fitness_list = []

if __name__ == '__main__':
    debug = True
    if len(argv)<9:
        print("USAGE: Genetic_Placement.py #node #net width height #population #generations Prob.Selection "
              "Prob.Mutation")
        NODE_C = 15
        NET_C = 20
        BOX_H = 10
        BOX_W = 10
        N_P = 100
        N_G = 500
        P_S = 0.3
        P_M = 0.02
    else:
        NODE_C = int(argv[1])
        NET_C = int(argv[2])
        BOX_W = int(argv[3])
        BOX_H = int(argv[4])
        N_P = int(argv[5])
        N_G = int(argv[6])
        P_S = float(argv[7])
        P_M = float(argv[8])

    P_C = 1 - P_S

    nodes = []
    nets = []
    net_list2 = []



    # for i in range(NODE_C):
    #     nodes.append(Node((0, 0), i))
    # for i in range(NET_C):
    #     net_list2.append([])
    #     nets.append(Net(i))
    #     itr = np.random.randint(3, 5)
    #     for j in range(itr):
    #         n_id = np.random.randint(NODE_C)
    #         if not nets[i].has(nodes[n_id]):
    #             nets[i].add_node(nodes[n_id])
    #         if nodes[n_id].id not in net_list2[i]:
    #             net_list2[i].append(nodes[n_id].id)
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

        n_tmp = copy.deepcopy(n.nodeList)
        n.nodeList = []
        net_list2.append([])
        for node in n_tmp:
            n.nodeList.append(nodes[nodes_or.index(node)])
            net_list2[i].append(nodes_or.index(node))
        i += 1
    NODE_C = len(nodes)
    NET_C = len(nets)
    ################# END ORCAD NETLIST PARSING##################
    c = 0
    for net in nets:
        c += len(net) - 1
    print("MINIMUM COST:%d" % c)

    generation = []
    for i in range(N_P):
        generation.append({'node_list': copy.deepcopy(Base.random_place_board(nodes, BOX_W, BOX_H)),
                           'fitness': 0})
        generation[-1]["fitness"] = Base.get_fitness(net_list2, generation[-1]["node_list"])

    Base_Test.svg_draw_board_2(generation[0]["node_list"], net_list2, BOX_W, BOX_H, "Init_genetic.svg",
                               str(generation[0]["fitness"]), NET_C_=NET_C, NODE_C_=NODE_C)
    for chromosome in generation:
        if generation.count(chromosome) > 1:
            do_mutation(chromosome["node_list"])

    print("INIT COST:%d" % Base.get_total_cost_nodes(net_list2,generation[0]["node_list"]))

    fitness_list = get_fitness_list(generation)
    average_fitness_list = [np.average(fitness_list)]
    best_fitness = max(fitness_list)
    best_fitness_placement = copy.deepcopy(generation[fitness_list.index(best_fitness)])
    Base_Test.svg_draw_board_2(best_fitness_placement["node_list"], net_list2, BOX_W, BOX_H, "BEST_genetic.svg",
                               str(best_fitness), NET_C_=NET_C, NODE_C_=NODE_C)

    for i in range(N_G):
        next_generation = []
        # Selection
        for chromosome in generation:
            rn = np.random.rand()
            if rn < P_S:
                ftl = np.array(get_fitness_list(generation))
                selected_chromosome = np.random.choice(generation, p=ftl / sum(ftl))
                next_generation.append(selected_chromosome)
                generation.remove(chromosome)

        # Cross Over
        for chromosome in range(int(len(generation) / 2)):
            ftl = np.array(get_fitness_list(generation))
            p1 = np.random.choice(generation, p=ftl / sum(ftl))
            generation.remove(p1)

            ftl = np.array(get_fitness_list(generation))
            p2 = np.random.choice(generation, p=ftl / sum(ftl))

            if p1 == p2 and generation.count(p1) == len(generation):
                break

            while p1 == p2:
                ftl = np.array(get_fitness_list(generation))
                p2 = np.random.choice(generation, p=ftl / sum(ftl))
            generation.remove(p2)
            do_cross_over(p1["node_list"], p2["node_list"], BOX_W, BOX_H)
            next_generation.append(
                {"node_list": p1["node_list"], "fitness": Base.get_fitness(net_list2, p1["node_list"])})
            next_generation.append(
                {"node_list": p2["node_list"], "fitness": Base.get_fitness(net_list2, p2["node_list"])})

        if len(generation) != 0:
            for chromosome in generation:
                next_generation.append(chromosome)
        generation = []

        for chromosome in next_generation:
            rn = np.random.rand()
            if rn < P_M or next_generation.count(chromosome) > 1:
                do_mutation(chromosome["node_list"])

        generation = copy.copy(next_generation)

        fitness_list = get_fitness_list(generation)
        average_fitness_list.append(np.average(fitness_list))
        current_fitness = max(fitness_list)

        if current_fitness > best_fitness:
            best_fitness = current_fitness

            best_fitness_placement = copy.copy(generation[fitness_list.index(best_fitness)])
            Base_Test.svg_draw_board_2(best_fitness_placement["node_list"], net_list2, BOX_W, BOX_H, "BEST_genetic.svg",
                                       str(best_fitness), NET_C_=NET_C, NODE_C_=NODE_C)
            if int(1 / best_fitness - 1) == c:
                break
        # print("%d T:%f MIN:%d Current COST:%d\r" % (len(cost_list), T, min_cost, cost), end='\r')
        # print("GENERATION:%d:Best Fitness:%f MIN COST:%d Avg. Fitness:%f Avg. COST:%d\r" % (
        # i, best_fitness, 1 / best_fitness - 1, average_fitness_list[-1], (1 / average_fitness_list[-1] - 1)))
        print("GENERATION:%d:Best Fitness:%f MIN COST:%d Avg. Fitness:%f Avg. COST:%d\r" % (
            i, best_fitness, 1 / best_fitness - 1, average_fitness_list[-1], (1 / average_fitness_list[-1] - 1)),end='\r')

    print('\n\r\n')
    for i in range(len(best_fitness_placement["node_list"])):
        nodes_or[i].pos = best_fitness_placement["node_list"][i].pos
        print(nodes_or[i])
    print("MIN COST:%d"%(1/best_fitness - 1))

    plt.figure()
    plt.plot(average_fitness_list)
    plt.figure()
    plt.plot(1/np.array(average_fitness_list) - 1)
    plt.show()

    while True:
        plt.pause(1)
