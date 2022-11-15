#-------------------------------------------------------------------------------
# Name:        PageRank
# Purpose:     Implementation of hyperlink-based ranking algorithm for finding 
#              truly useful information on the Web. 
#
# Author:      Sergio Murillo
#
# Created:     4/11/2022
#-------------------------------------------------------------------------------

GRAPH = {}
VALUES = {}
SOURCE = "graph.txt"

def get_graph() -> None:
    """
    Returns the graph in a sorted list
    """
    global VALUES
    
    total = 0
    for node in VALUES:
        total += VALUES[node]

    for node in sorted(VALUES, key=VALUES.get, reverse=True):
        val = VALUES[node]
        print(node, val)
    print ("Total:", total)

def calculate_pagerank(iteration : int, dumping_factor: float = 0.85) -> int:
    """
    Recursive implementation of PageRank, runs until the degree of change 
    between two iterations is 0. Dumping factor with a default value of 0.85 is
    used.
    Returns the number of iterations.
    """
    global GRAPH, VALUES
    sum = {}
    for node in GRAPH:
        sum[node] = 0

    equals = True

    for node in GRAPH:
        if len(GRAPH[node]) == 0:
            for node2 in GRAPH:
                if node2 != node:
                   sum[node2] += VALUES[node] / (len(GRAPH)-1)
        else: 
            for link in GRAPH[node]:
                sum[link] += VALUES[node] / len(GRAPH[node])
    
    for node in sum:
        new_value = ((1 - dumping_factor) / len(GRAPH)) + (dumping_factor * sum[node])
        if round(VALUES[node], 3) != round(new_value, 3):
            equals = False
        VALUES[node] = new_value
    
    if (not equals):
        return calculate_pagerank(iteration+1)
    else:
        return iteration

def inicialize_graph() -> None:
    """
    Initializes the value of all nodes in the network to the same value.
    """
    global GRAPH

    for node in GRAPH:
        VALUES[node] = 1 / len(GRAPH)

def read_graph(file_name=SOURCE) -> None:
    """
    Read the initial graph from a .txt
    """
    global GRAPH
    with open(file_name, "r") as file:
        for line in file:
            try:
                line = line.replace(" ", "").strip().split(",")
                GRAPH[line[0]] = line[1:]
            except:
                GRAPH[line] = []
                
def main() -> None:
    """
    It reads the initial data of a graph from a .txt file and performs the 
    PageRank algorithm by counting the number of iterations until the value of 
    the nodes does not change.
    Prints the value of all sorted nodes on the screen.
    """
    read_graph()
    inicialize_graph()
    iterations = calculate_pagerank(1)
    print("Iterations:", iterations)
    get_graph()

if __name__ == '__main__':
    main()
