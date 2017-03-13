from igraph import Graph as IGraph
from functools import reduce


def edgelist_to_vertices(edgelist):
    return reduce(lambda acc, data: acc.union([data['source'], data['target']]), edgelist, set())


def edgelist_to_igraph(edgelist):
    raw = list(map(lambda x: [x['source'], x['target'], int(x['weight'])], edgelist))
    g = IGraph.TupleList(raw, weights=True, directed=True)
    g.vs['indegree'] = g.degree(mode="in")
    g.vs['outdegree'] = g.degree(mode="out")
    g.vs['label'] = g.vs['name']
    return g


def dicts_to_columns(dicts):
    """
    Given a List of Dictionaries with uniform keys, returns a single Dictionary
    with keys holding a List of values matching the key in the original List.

    [{'name': 'Field Museum', 'location': 'Chicago'},
     {'name': 'Epcot', 'location': 'Orlando'}]
      =>
    {'name': ['Field Museum', 'Epcot'],
     'location': ['Chicago', 'Orlando']}
    """
    keys = dicts[0].keys()
    result = dict((k, []) for k in keys)

    for d in dicts:
        for k, v in d.items():
            result[k] += [v]

    return result


def load(vertices, edges, vertex_name_key='name', vertex_id_key='id', edge_foreign_keys=('source', 'target')):
    """
    Constructs a graph from a list-of-dictionaries representation.

    This representation assumes that vertices and edges are encoded in
    two lists, each list containing a Python dict for each vertex and
    each edge, respectively. A distinguished element of the vertex dicts
    contain a vertex ID which is used in the edge dicts to refer to
    source and target vertices. All the remaining elements of the dicts
    are considered vertex and edge attributes.

    @param vertices: a list of dicts for the vertices.
    @param edges: a list of dicts for the edges.
    @param vertex_name_key: the name of the distinguished key in the dicts
      in the vertex data source that contains the vertex names. Will also be used
      as vertex label.
    @param vertex_id_key: the name of the distinguished key in the dicts
      in the vertex data source that contains a unique identifier for the vertex.
    @param edge_foreign_keys: the name of the attributes in the dicts in C{edges}
      that contain the source and target vertex names.
    @return: IGraph instance with integers for vertex ids, edge sources, and edge targets.
    """
    vertex_data = dicts_to_columns(vertices)
    edge_data = dicts_to_columns(edges)
    n = len(vertices)
    vertex_index = dict(zip(vertex_data[vertex_id_key], range(n)))

    # Iterate over `edges` to create `edge_list`, where every list item is a pair of integers.
    edge_list = list(map(lambda source, target: (vertex_index[source], vertex_index[target]),
                         edge_data[edge_foreign_keys[0]],
                         edge_data[edge_foreign_keys[1]]))

    g = IGraph(n=n, edges=edge_list, directed=True, vertex_attrs=vertex_data, edge_attrs=edge_data)
    g.vs['name'] = g.vs[vertex_name_key]
    g.vs['indegree'] = g.degree(mode="in")
    g.vs['outdegree'] = g.degree(mode="out")
    g.vs['label'] = g.vs[vertex_name_key]
    return g
