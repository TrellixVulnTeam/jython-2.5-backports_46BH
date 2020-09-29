# Test for Moody and White k-components algorithm
from nose.tools import assert_equal, assert_true, raises, assert_greater_equal
import networkx as nx
from networkx.algorithms.connectivity.kcomponents import (
    build_k_number_dict,
    _consolidate,
)

##
# A nice synthetic graph
##


def torrents_and_ferraro_graph():
    # Graph from https://arxiv.org/pdf/1503.04476v1 p.26
    G = nx.convert_node_labels_to_integers(
        nx.grid_graph([5, 5]),
        label_attribute='labels',
    )
    rlabels = nx.get_node_attributes(G, 'labels')
    labels = dict((v, k) for k, v in rlabels.items())

    for nodes in [(labels[(0, 4)], labels[(1, 4)]),
                  (labels[(3, 4)], labels[(4, 4)])]:
        new_node = G.order() + 1
        # Petersen graph is triconnected
        P = nx.petersen_graph()
        G = nx.disjoint_union(G, P)
        # Add two edges between the grid and P
        G.add_edge(new_node + 1, nodes[0])
        G.add_edge(new_node, nodes[1])
        # K5 is 4-connected
        K = nx.complete_graph(5)
        G = nx.disjoint_union(G, K)
        # Add three edges between P and K5
        G.add_edge(new_node + 2, new_node + 11)
        G.add_edge(new_node + 3, new_node + 12)
        G.add_edge(new_node + 4, new_node + 13)
        # Add another K5 sharing a node
        G = nx.disjoint_union(G, K)
        nbrs = G[new_node + 10]
        G.remove_node(new_node + 10)
        for nbr in nbrs:
            G.add_edge(new_node + 17, nbr)
        # This edge makes the graph biconnected; it's
        # needed because K5s share only one node.
        G.add_edge(new_node + 16, new_node + 8)

    for nodes in [(labels[(0, 0)], labels[(1, 0)]),
                  (labels[(3, 0)], labels[(4, 0)])]:
        new_node = G.order() + 1
        # Petersen graph is triconnected
        P = nx.petersen_graph()
        G = nx.disjoint_union(G, P)
        # Add two edges between the grid and P
        G.add_edge(new_node + 1, nodes[0])
        G.add_edge(new_node, nodes[1])
        # K5 is 4-connected
        K = nx.complete_graph(5)
        G = nx.disjoint_union(G, K)
        # Add three edges between P and K5
        G.add_edge(new_node + 2, new_node + 11)
        G.add_edge(new_node + 3, new_node + 12)
        G.add_edge(new_node + 4, new_node + 13)
        # Add another K5 sharing two nodes
        G = nx.disjoint_union(G, K)
        nbrs = G[new_node + 10]
        G.remove_node(new_node + 10)
        for nbr in nbrs:
            G.add_edge(new_node + 17, nbr)
        nbrs2 = G[new_node + 9]
        G.remove_node(new_node + 9)
        for nbr in nbrs2:
            G.add_edge(new_node + 18, nbr)
    return G


@raises(nx.NetworkXNotImplemented)
def test_directed():
    G = nx.gnp_random_graph(10, 0.2, directed=True)
    nx.k_components(G)


# Helper function
def _check_connectivity(G, k_components):
    for k, components in k_components.items():
        if k < 3:
            continue
        # check that k-components have node connectivity >= k.
        for component in components:
            C = G.subgraph(component)
            K = nx.node_connectivity(C)
            assert_greater_equal(K, k)


def test_torrents_and_ferraro_graph():
    G = torrents_and_ferraro_graph()
    result = nx.k_components(G)
    _check_connectivity(G, result)

    # In this example graph there are 8 3-components, 4 with 15 nodes
    # and 4 with 5 nodes.
    assert_equal(len(result[3]), 8)
    assert_equal(len([c for c in result[3] if len(c) == 15]), 4)
    assert_equal(len([c for c in result[3] if len(c) == 5]), 4)
    # There are also 8 4-components all with 5 nodes.
    assert_equal(len(result[4]), 8)
    assert_true(all(len(c) == 5 for c in result[4]))


def test_random_gnp():
    G = nx.gnp_random_graph(50, 0.2)
    result = nx.k_components(G)
    _check_connectivity(G, result)


def test_shell():
    constructor = [(20, 80, 0.8), (80, 180, 0.6)]
    G = nx.random_shell_graph(constructor)
    result = nx.k_components(G)
    _check_connectivity(G, result)


def test_configuration():
    deg_seq = nx.random_powerlaw_tree_sequence(100, tries=5000)
    G = nx.Graph(nx.configuration_model(deg_seq))
    G.remove_edges_from(nx.selfloop_edges(G))
    result = nx.k_components(G)
    _check_connectivity(G, result)


def test_karate():
    G = nx.karate_club_graph()
    result = nx.k_components(G)
    _check_connectivity(G, result)


def test_karate_component_number():
    karate_k_num = {
        0: 4, 1: 4, 2: 4, 3: 4, 4: 3, 5: 3, 6: 3, 7: 4, 8: 4, 9: 2,
        10: 3, 11: 1, 12: 2, 13: 4, 14: 2, 15: 2, 16: 2, 17: 2,
        18: 2, 19: 3, 20: 2, 21: 2, 22: 2, 23: 3, 24: 3, 25: 3,
        26: 2, 27: 3, 28: 3, 29: 3, 30: 4, 31: 3, 32: 4, 33: 4
    }
    G = nx.karate_club_graph()
    k_components = nx.k_components(G)
    k_num = build_k_number_dict(k_components)
    assert_equal(karate_k_num, k_num)


def test_davis_southern_women():
    G = nx.davis_southern_women_graph()
    result = nx.k_components(G)
    _check_connectivity(G, result)


def test_davis_southern_women_detail_3_and_4():
    solution = {
        3: [set([
            'Nora Fayette',
            'E10',
            'Myra Liddel',
            'E12',
            'E14',
            'Frances Anderson',
            'Evelyn Jefferson',
            'Ruth DeSand',
            'Helen Lloyd',
            'Eleanor Nye',
            'E9',
            'E8',
            'E5',
            'E4',
            'E7',
            'E6',
            'E1',
            'Verne Sanderson',
            'E3',
            'E2',
            'Theresa Anderson',
            'Pearl Oglethorpe',
            'Katherina Rogers',
            'Brenda Rogers',
            'E13',
            'Charlotte McDowd',
            'Sylvia Avondale',
            'Laura Mandeville',
        ]),
        ],
        4: [set([
            'Nora Fayette',
            'E10',
            'Verne Sanderson',
            'E12',
            'Frances Anderson',
            'Evelyn Jefferson',
            'Ruth DeSand',
            'Helen Lloyd',
            'Eleanor Nye',
            'E9',
            'E8',
            'E5',
            'E4',
            'E7',
            'E6',
            'Myra Liddel',
            'E3',
            'Theresa Anderson',
            'Katherina Rogers',
            'Brenda Rogers',
            'Charlotte McDowd',
            'Sylvia Avondale',
            'Laura Mandeville',
        ]),
        ],
    }
    G = nx.davis_southern_women_graph()
    result = nx.k_components(G)
    for k, components in result.items():
        if k < 3:
            continue
        assert_true(len(components) == len(solution[k]))
        for component in components:
            assert_true(component in solution[k])


def test_set_consolidation_rosettacode():
    # Tests from http://rosettacode.org/wiki/Set_consolidation
    def list_of_sets_equal(result, solution):
        assert_equal(
            set([frozenset(s) for s in result]),
            set([frozenset(s) for s in solution])
        )
    question = [set(['A', 'B']), set(['C', 'D'])]
    solution = [set(['A', 'B']), set(['C', 'D'])]
    list_of_sets_equal(_consolidate(question, 1), solution)
    question = [set(['A', 'B']), set(['B', 'C'])]
    solution = [set(['A', 'B', 'C'])]
    list_of_sets_equal(_consolidate(question, 1), solution)
    question = [set(['A', 'B']), set(['C', 'D']), set(['D', 'B'])]
    solution = [set(['A', 'C', 'B', 'D'])]
    list_of_sets_equal(_consolidate(question, 1), solution)
    question = [set(['H', 'I', 'K']), set(['A', 'B']), set(['C', 'D']), set(['D', 'B']), set(['F', 'G', 'H'])]
    solution = [set(['A', 'C', 'B', 'D']), set(['G', 'F', 'I', 'H', 'K'])]
    list_of_sets_equal(_consolidate(question, 1), solution)
    question = [set(['A', 'H']), set(['H', 'I', 'K']), set(['A', 'B']), set(['C', 'D']), set(['D', 'B']), set(['F', 'G', 'H'])]
    solution = [set(['A', 'C', 'B', 'D', 'G', 'F', 'I', 'H', 'K'])]
    list_of_sets_equal(_consolidate(question, 1), solution)
    question = [set(['H', 'I', 'K']), set(['A', 'B']), set(['C', 'D']), set(['D', 'B']), set(['F', 'G', 'H']), set(['A', 'H'])]
    solution = [set(['A', 'C', 'B', 'D', 'G', 'F', 'I', 'H', 'K'])]
    list_of_sets_equal(_consolidate(question, 1), solution)