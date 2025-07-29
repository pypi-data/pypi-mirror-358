"""
Core functionality for the graphlib package.
"""
from typing import Optional

from relationalai.early_access.builder import Concept, Relationship
from relationalai.early_access.builder import Integer, Float
from relationalai.early_access.builder import where, define, count, sum, not_, min, union
from relationalai.early_access.builder import avg
from relationalai.early_access.builder.std.math import abs, natural_log

class Graph():
    def __init__(self,
            *,
            directed: bool,
            weighted: bool,
            aggregator: Optional[str] = None,
        ):
        assert isinstance(directed, bool), "The `directed` argument must be a boolean."
        assert isinstance(weighted, bool), "The `weighted` argument must be a boolean."
        self.directed = directed
        self.weighted = weighted

        assert isinstance(aggregator, type(None)), "Weight aggregation not yet supported."
        # TODO: In the hopefully not-too-distant future, this argument will
        #   allow the user to specify whether and how to aggregate weights
        #   for multi-edges that exist at the user interface (Edge) level
        #   to construct the internal edge/weight list representation.
        #   The `str` type is just a placeholder; it should be something else.

        # Introduce Node and Edge concepts.
        Node = Concept("Node")
        Edge = Concept("Edge")
        Edge.src = Relationship("{edge:Edge} has source {src:Node}")
        Edge.dst = Relationship("{edge:Edge} has destination {dst:Node}")
        Edge.weight = Relationship("{edge:Edge} has weight {weight:Float}")
        self.Node = Node
        self.Edge = Edge

        # TODO: Require that each Edge has an Edge.src.
        # TODO: Require that each Edge has an Edge.dst.
        # TODO: If weighted, require that each Edge has an Edge.weight.
        # TODO: If not weighted, require that each Edge does not have an Edge.weight.

        # TODO: Suppose that type checking should in future restrict `src` and
        #   `dst` to be `Node`s, but at the moment we may need a require for that.
        # TODO: Suppose that type checking should in future restrict `weight` to be
        #   `Float`s, but at the moment we may need a require for that.

        # TODO: Transform Node and Edge into underlying edge-/weight-list representation.
        # NOTE: Operate under the assumption that `Node` contains all
        #   possible nodes, i.e. we can use the `Node` Concept directly as
        #   the node list. Has the additional benefit of allowing relationships
        #   (for which it makes sense) to be properties of `Node` rather than standalone.
        self._define_edge_relationships()
 
        self._define_num_nodes_relationship()
        self._define_num_edges_relationship()

        self._define_neighbor_relationships()
        self._define_count_neighbor_relationships()
        self._define_common_neighbor_relationship()
        self._define_count_common_neighbor_relationship()

        self._define_degree_relationships()
        self._define_weighted_degree_relationships()

        self._define_degree_centrality_relationship()

        self._define_reachable_from()

        # Helper relationship for preferential attachment.
        self._define_isolated_node_relationship()

        self._define_preferential_attachment_relationship()

        # Helper relationships for triangle functionality.
        self._define_no_loop_edge_relationship()
        self._define_oriented_edge_relationship()
        self._define_reversed_oriented_edge_relationship()

        self._define_triangle_count_relationship()
        self._define_unique_triangle_relationship()
        self._define_num_triangles_relationship()
        self._define_triangle_relationship()

        # Helper relationships for local clustering coefficient.
        self._define_degree_no_self_relationship()

        self._define_local_clustering_coefficient_relationship()
        self._define_average_clustering_coefficient_relationship()
        self._define_adamic_adar_relationship()

        self._define_weakly_connected_component()

        self._define_distance_relationship()

    def _define_edge_relationships(self):
        """
        Define the self._edge and self._weight relationships,
        consuming the Edge concept's `src`, `dst`, and `weight` relationships.
        """
        self._edge = Relationship("{src:Node} has edge to {dst:Node}")
        self._weight = Relationship("{src:Node} has edge to {dst:Node} with weight {weight:Float}")

        Edge = self.Edge
        if self.directed and self.weighted:
            define(
                self._weight(Edge.src, Edge.dst, Edge.weight),
                self._edge(Edge.src, Edge.dst)
            )
        elif self.directed and not self.weighted:
            define(
                self._weight(Edge.src, Edge.dst, 1.0),
                self._edge(Edge.src, Edge.dst)
            )
        elif not self.directed and self.weighted:
            define(
                self._weight(Edge.src, Edge.dst, Edge.weight),
                self._weight(Edge.dst, Edge.src, Edge.weight),
                self._edge(Edge.src, Edge.dst),
                self._edge(Edge.dst, Edge.src)
            )
        elif not self.directed and not self.weighted:
            define(
                self._weight(Edge.src, Edge.dst, 1.0),
                self._weight(Edge.dst, Edge.src, 1.0),
                self._edge(Edge.src, Edge.dst),
                self._edge(Edge.dst, Edge.src)
            )

    def _define_num_nodes_relationship(self):
        """Define the self._num_nodes relationship."""
        self._num_nodes = Relationship("The graph has {num_nodes:Integer} nodes")
        define(self._num_nodes(count(self.Node) | 0))

    def _define_num_edges_relationship(self):
        """Define the self._num_edges relationship."""
        self._num_edges = Relationship("The graph has {num_edges:Integer} edges")

        src, dst = self.Node.ref(), self.Node.ref()

        if self.directed:
            define(self._num_edges(count(src, dst, self._edge(src, dst)) | 0))
        elif not self.directed:
            define(self._num_edges(count(src, dst, self._edge(src, dst), src <= dst) | 0))
            # TODO: Generates an UnresolvedOverload warning from the typer.
            #   Should be sorted out by improvements in the typer (to allow
            #   comparisons between instances of concepts).


    def _define_neighbor_relationships(self):
        """Define the self.[in,out]neighbor relationships."""
        self._neighbor = Relationship("{src:Node} has neighbor {dst:Node}")
        self._inneighbor = Relationship("{dst:Node} has inneighbor {src:Node}")
        self._outneighbor = Relationship("{src:Node} has outneighbor {dst:Node}")

        src, dst = self.Node.ref(), self.Node.ref()
        where(self._edge(src, dst)).define(self._neighbor(src, dst), self._neighbor(dst, src))
        where(self._edge(dst, src)).define(self._inneighbor(src, dst))
        where(self._edge(src, dst)).define(self._outneighbor(src, dst))
        # Note that these definitions happen to work for both
        # directed and undirected graphs due to `edge` containing
        # each edge's symmetric partner in the undirected case.

    def _define_count_neighbor_relationships(self):
        """
        Define the self._count_[in,out]neighbor relationships.
        Note that these relationships differ from corresponding
        [in,out]degree relationships in that they yield empty
        rather than zero absent [in,out]neighbors.
        Primarily for internal consumption.
        """
        self._count_neighbor = Relationship("{src:Node} has neighbor count {count:Integer}")
        self._count_inneighbor = Relationship("{dst:Node} has inneighbor count {count:Integer}")
        self._count_outneighbor = Relationship("{src:Node} has outneighbor count {count:Integer}")

        src, dst = self.Node.ref(), self.Node.ref()
        where(self._neighbor(src, dst)).define(self._count_neighbor(src, count(dst).per(src)))
        where(self._inneighbor(dst, src)).define(self._count_inneighbor(dst, count(src).per(dst)))
        where(self._outneighbor(src, dst)).define(self._count_outneighbor(src, count(dst).per(src)))


    def _define_common_neighbor_relationship(self):
        """Define the self._common_neighbor relationship."""
        self._common_neighbor = Relationship("{node_a:Node} and {node_b:Node} have common neighbor {node_c:Node}")

        node_a, node_b, node_c = self.Node.ref(), self.Node.ref(), self.Node.ref()
        where(self._neighbor(node_a, node_c), self._neighbor(node_b, node_c)).define(self._common_neighbor(node_a, node_b, node_c))

    def _define_count_common_neighbor_relationship(self):
        """Define the self._count_common_neighbor relationship."""
        self._count_common_neighbor = Relationship("{node_a:Node} and {node_b:Node} have common neighbor count {count:Integer}")

        node_a, node_b, node_c = self.Node.ref(), self.Node.ref(), self.Node.ref()
        where(self._common_neighbor(node_a, node_b, node_c)).define(self._count_common_neighbor(node_a, node_b, count(node_c).per(node_a, node_b)))


    def _define_degree_relationships(self):
        """Define the self._[in,out]degree relationships."""
        self._degree = Relationship("{node:Node} has degree {count:Integer}")
        self._indegree = Relationship("{node:Node} has indegree {count:Integer}")
        self._outdegree = Relationship("{node:Node} has outdegree {count:Integer}")

        incount, outcount = Integer.ref(), Integer.ref()

        where(
            self.Node,
            _indegree := where(self._count_inneighbor(self.Node, incount)).select(incount) | 0,
        ).define(self._indegree(self.Node, _indegree))

        where(
            self.Node,
            _outdegree := where(self._count_outneighbor(self.Node, outcount)).select(outcount) | 0,
        ).define(self._outdegree(self.Node, _outdegree))

        if self.directed:
            where(
                self._indegree(self.Node, incount),
                self._outdegree(self.Node, outcount),
            ).define(self._degree(self.Node, incount + outcount))
        elif not self.directed:
            neighcount = Integer.ref()
            where(
                self.Node,
                _degree := where(self._count_neighbor(self.Node, neighcount)).select(neighcount) | 0,
            ).define(self._degree(self.Node, _degree))

    def _define_reachable_from(self):
        """Define the self.reachable_from relationship"""
        self._reachable_from = Relationship("{node_a:Node} reaches {node_b:Node}")

        node_a, node_b, node_c = self.Node.ref(), self.Node.ref(), self.Node.ref()
        define(self._reachable_from(node_a, node_a))
        define(self._reachable_from(node_a, node_c)).where(self._reachable_from(node_a, node_b), self._edge(node_b, node_c))


    def _define_weighted_degree_relationships(self):
        """Define the self._weighted_[in,out]degree relationships."""
        self._weighted_degree = Relationship("{node:Node} has weighted degree {weight:Float}")
        self._weighted_indegree = Relationship("{node:Node} has weighted indegree {weight:Float}")
        self._weighted_outdegree = Relationship("{node:Node} has weighted outdegree {weight:Float}")

        src, dst = self.Node.ref(), self.Node.ref()
        inweight, outweight = Float.ref(), Float.ref()

        where(
            self.Node,
            _weighted_indegree := sum(src, inweight).per(self.Node).where(self._weight(src, self.Node, inweight)) | 0.0,
        ).define(self._weighted_indegree(self.Node, _weighted_indegree))

        where(
            self.Node,
            _weighted_outdegree := sum(dst, outweight).per(self.Node).where(self._weight(self.Node, dst, outweight)) | 0.0,
        ).define(self._weighted_outdegree(self.Node, _weighted_outdegree))

        if self.directed:
            where(
                self._weighted_indegree(self.Node, inweight),
                self._weighted_outdegree(self.Node, outweight),
            ).define(self._weighted_degree(self.Node, inweight + outweight))
        elif not self.directed:
            weight = Float.ref()
            where(
                self.Node,
                _weighted_degree := sum(dst, weight).per(self.Node).where(self._weight(self.Node, dst, weight)) | 0.0,
            ).define(self._weighted_degree(self.Node, _weighted_degree))


    def _define_degree_centrality_relationship(self):
        """Define the self._degree_centrality relationship."""
        self._degree_centrality = Relationship("{node:Node} has {degree_centrality:Float}")

        degree = Integer.ref()
        weighted_degree = Float.ref()

        # A single isolated node has degree centrality zero.
        where(
            self._num_nodes(1),
            self._degree(self.Node, 0)
        ).define(self._degree_centrality(self.Node, 0.0))

        # A single non-isolated node has degree centrality one.
        where(
            self._num_nodes(1),
            self._degree(self.Node, degree),
            degree > 0
        ).define(self._degree_centrality(self.Node, 1.0))

        # General case, i.e. with more than one node.
        num_nodes = Integer.ref()
        if self.weighted:
            where(
                self._num_nodes(num_nodes),
                num_nodes > 1,
                self._weighted_degree(self.Node, weighted_degree)
            ).define(self._degree_centrality(self.Node, weighted_degree / (num_nodes - 1.0)))
        elif not self.weighted:
            where(
                self._num_nodes(num_nodes),
                num_nodes > 1,
                self._degree(self.Node, degree)
            ).define(self._degree_centrality(self.Node, degree / (num_nodes - 1.0)))


    def _define_isolated_node_relationship(self):
        """Define the self._isolated_node (helper, non-public) relationship."""
        self._isolated_node = Relationship("{node:Node} is isolated")

        dst = self.Node.ref()
        where(
            self.Node,
            not_(self._neighbor(self.Node, dst))
        ).define(self._isolated_node(self.Node))

    def _define_preferential_attachment_relationship(self):
        """Define the self._preferential_attachment relationship."""
        self._preferential_attachment = Relationship("{node_u:Node} and {node_v:Node} have preferential attachment score {score:Integer}")

        node_u, node_v = self.Node.ref(), self.Node.ref()
        count_u, count_v = Integer.ref(), Integer.ref()

        # NOTE: We consider isolated nodes separately to maintain
        #   the dense behavior of preferential attachment.

        # Case where node u is isolated, and node v is any node: score 0.
        where(
            self._isolated_node(node_u),
            self.Node(node_v),
        ).define(self._preferential_attachment(node_u, node_v, 0))

        # Case where node u is any node, and node v is isolated: score 0.
        where(
            self.Node(node_u),
            self._isolated_node(node_v)
        ).define(self._preferential_attachment(node_u, node_v, 0))

        # Case where neither node is isolated: score is count_neighbor[u] * count_neighbor[v].
        where(
            self._count_neighbor(node_u, count_u),
            self._count_neighbor(node_v, count_v)
        ).define(self._preferential_attachment(node_u, node_v, count_u * count_v))

    def _define_weakly_connected_component(self):
        """Defines the self.weakly_connected_component relationship"""
        self._weakly_connected_component = Relationship("{node:Node} is in the connected component {id:Node}")

        node, node_v, component = self.Node.ref(), self.Node.ref(), self.Node.ref()
        node, component = union(
            # A node starts with itself as the component id.
            where(node == component).select(node, component),
            # Recursive case.
            where(self._weakly_connected_component(node, component), self._neighbor(node, node_v)).select(node_v, component)
        )
        define(self._weakly_connected_component(node, min(component).per(node)))

    def _define_no_loop_edge_relationship(self):
        """Define the self._no_loop_edge (helper, non-public) relationship."""
        self._no_loop_edge = Relationship("{src:Node} has nonloop edge to {dst:Node}")

        src, dst = self.Node.ref(), self.Node.ref()
        where(
            self._edge(src, dst),
            src != dst
        ).define(self._no_loop_edge(src, dst))

    def _define_oriented_edge_relationship(self):
        """Define the self._oriented_edge (helper, non-public) relationship."""
        self._oriented_edge = Relationship("{src:Node} has oriented edge to {dst:Node}")

        src, dst = self.Node.ref(), self.Node.ref()
        where(
            self._edge(src, dst),
            src < dst
        ).define(self._oriented_edge(src, dst))

    def _define_reversed_oriented_edge_relationship(self):
        """Define the self._reversed_oriented_edge (helper, non-public) relationship."""
        self._reversed_oriented_edge = Relationship("{src:Node} has reversed oriented edge to {dst:Node}")

        src, dst = self.Node.ref(), self.Node.ref()
        where(
            self._edge(src, dst),
            src > dst
        ).define(self._reversed_oriented_edge(src, dst))


    def _define_triangle_count_relationship(self):
        """Define self._triangle_count relationship."""
        self._triangle_count = Relationship("{node:Node} belongs to {count:Integer} triangles")

        where(
            self.Node,
            _count := self._nonzero_triangle_count_fragment(self.Node) | 0
        ).define(self._triangle_count(self.Node, _count))

    def _nonzero_triangle_count_fragment(self, node):
        """
        Helper function that returns a fragment, specifically a count
        of the number of triangles containing the given node.
        """
        node_a, node_b = self.Node.ref(), self.Node.ref()

        if self.directed:
            # For directed graphs, count triangles with any circulation.
            # For example, count both (1-2-3-1) and (1-3-2-1) as triangles.
            return count(node_a, node_b).per(node).where(
                self._no_loop_edge(node, node_a),
                self._no_loop_edge(node_a, node_b),
                self._no_loop_edge(node_b, node)
            )
        else:
            # For undirected graphs, count triangles with a specific circulation.
            # For example, count (1-2-3-1) but not (1-3-2-1) as a triangle.
            return count(node_a, node_b).per(node).where(
                self._no_loop_edge(node, node_a),
                self._oriented_edge(node_a, node_b),
                self._no_loop_edge(node, node_b)
            )


    def _define_unique_triangle_relationship(self):
        """Define self._unique_triangle relationship."""
        self._unique_triangle = Relationship("{node_a:Node} and {node_b:Node} and {node_c:Node} form unique triangle")

        node_a, node_b, node_c = self.Node.ref(), self.Node.ref(), self.Node.ref()

        where(
            self._unique_triangle_fragment(node_a, node_b, node_c)
        ).define(self._unique_triangle(node_a, node_b, node_c))

    def _unique_triangle_fragment(self, node_a, node_b, node_c):
        """
        Helper function that returns a fragment, specifically a where clause
        constraining the given triplet of nodes to unique triangles in the graph.
        """
        if self.directed:
            return where(
                self._oriented_edge(node_a, node_b),
                self._no_loop_edge(node_b, node_c),
                self._reversed_oriented_edge(node_c, node_a)
            )
        else:
            return where(
                self._oriented_edge(node_a, node_b),
                self._oriented_edge(node_b, node_c),
                self._oriented_edge(node_a, node_c)
            )


    def _define_num_triangles_relationship(self):
        """Define self._num_triangles relationship."""
        self._num_triangles = Relationship("The graph has {num_triangles:Integer} triangles")

        _num_triangles = Integer.ref()
        node_a, node_b, node_c = self.Node.ref(), self.Node.ref(), self.Node.ref()

        where(
            _num_triangles := count(
                node_a, node_b, node_c
            ).where(
                self._unique_triangle_fragment(node_a, node_b, node_c)
            ) | 0,
        ).define(self._num_triangles(_num_triangles))

    def _define_triangle_relationship(self):
        """Define self._triangle relationship."""
        self._triangle = Relationship("{node_a:Node} and {node_b:Node} and {node_c:Node} form a triangle")

        a, b, c = self.Node.ref(), self.Node.ref(), self.Node.ref()

        if self.directed:
            where(self._unique_triangle(a, b, c)).define(self._triangle(a, b, c))
            where(self._unique_triangle(b, c, a)).define(self._triangle(a, b, c))
            where(self._unique_triangle(c, a, b)).define(self._triangle(a, b, c))
        else:
            where(self._unique_triangle(a, b, c)).define(self._triangle(a, b, c))
            where(self._unique_triangle(a, c, b)).define(self._triangle(a, b, c))
            where(self._unique_triangle(b, a, c)).define(self._triangle(a, b, c))
            where(self._unique_triangle(b, c, a)).define(self._triangle(a, b, c))
            where(self._unique_triangle(c, a, b)).define(self._triangle(a, b, c))
            where(self._unique_triangle(c, b, a)).define(self._triangle(a, b, c))


    def _define_degree_no_self_relationship(self):
        """
        Define self._degree_no_self relationship
        (non-public helper for local clustering coefficient).
        """
        self._degree_no_self = Relationship("{node:Node} has degree excluding self loops {num:Integer}")

        node, neighbor = self.Node.ref(), self.Node.ref()
        where(
            self.Node(node),
            _dns := count(neighbor).per(node).where(self._no_loop_edge(node, neighbor)) | 0,
        ).define(self._degree_no_self(node, _dns))

    def _define_local_clustering_coefficient_relationship(self):
        """
        Define self._local_clustering_coefficient relationship.
        Note that local_clustering_coefficient only applies to undirected graphs.
        """
        self._local_clustering_coefficient = Relationship("{node:Node} has local clustering coefficient {coefficient:Float}")

        if self.directed:
            return

        node = self.Node.ref()
        degree_no_self = Integer.ref()
        triangle_count = Integer.ref()
        where(
            node,
            _lcc := where(
                self._degree_no_self(node, degree_no_self),
                self._triangle_count(node, triangle_count),
                degree_no_self > 1
            ).select(
                2.0 * triangle_count / (degree_no_self * (degree_no_self - 1.0))
            ) | 0.0,
        ).define(self._local_clustering_coefficient(node, _lcc))

    def _define_average_clustering_coefficient_relationship(self):
        """
        Define self._average_clustering_coefficient relationship.
        Note that average_clustering_coefficient only applies to undirected graphs.
        """
        self._average_clustering_coefficient = Relationship("The graph has average clustering coefficient {coefficient:Float}")

        if self.directed:
            return

        node = self.Node.ref()
        coefficient = Float.ref()
        where(
            _avg_coefficient := avg(node, coefficient).where(
                    self._local_clustering_coefficient(node, coefficient)
                ) | 0.0
        ).define(self._average_clustering_coefficient(_avg_coefficient))

    def _define_distance_relationship(self):
        """Define self._distance relationship."""
        if not self.weighted:
            self._distance = Relationship("{node_u:Node} and {node_v:Node} have a distance of {d:Integer}")
            node_u, node_v, node_n, d1 = self.Node.ref(), self.Node.ref(), self.Node.ref(), Integer.ref()
            node_u, node_v, d = union(
                where(node_u == node_v, d1 == 0).select(node_u, node_v, d1), # Base case.
                where(self._edge(node_n, node_v),
                      d2 := self._distance(node_u, node_n, Integer) + 1).select(node_u, node_v, d2) # Recursive case.
            )
            define(self._distance(node_u, node_v, min(d).per(node_u, node_v)))
        else:
            self._distance = Relationship("{node_u:Node} and {node_v:Node} have a distance of {d:Float}")
            node_u, node_v, node_n, w, d1 = self.Node.ref(), self.Node.ref(),\
                self.Node.ref(), Float.ref(), Float.ref()
            node_u, node_v, d = union(
                where(node_u == node_v, d1 == 0.0).select(node_u, node_v, d1), # Base case.
                where(self._weight(node_n, node_v, w), d2 := self._distance(node_u, node_n, Float) + abs(w))\
                .select(node_u, node_v, d2) # Recursive case.
            )
            define(self._distance(node_u, node_v, min(d).per(node_u, node_v)))

    def _define_adamic_adar_relationship(self):
        """Define self._adamic_adar relationship."""
        self._adamic_adar = Relationship("{node_u:Node} and {node_v:Node} have adamic adar score {score:Float}")

        node_u, node_v, common_neighbor = self.Node.ref(), self.Node.ref(), self.Node.ref()
        neighbor_count = Integer.ref()

        where(
            _score := sum(common_neighbor, 1.0 / natural_log(neighbor_count)).per(node_u, node_v).where(
                self._common_neighbor(node_u, node_v, common_neighbor),
                self._count_neighbor(common_neighbor, neighbor_count),
            )
        ).define(self._adamic_adar(node_u, node_v, _score))


    # Public accessor methods for private relationships.
    def num_nodes(self): return self._num_nodes
    def num_edges(self): return self._num_edges

    def neighbor(self): return self._neighbor
    def inneighbor(self): return self._inneighbor
    def outneighbor(self): return self._outneighbor

    def count_neighbor(self): return self._count_neighbor
    def count_inneighbor(self): return self._count_inneighbor
    def count_outneighbor(self): return self._count_outneighbor

    def common_neighbor(self): return self._common_neighbor
    def count_common_neighbor(self): return self._count_common_neighbor

    def degree(self): return self._degree
    def indegree(self): return self._indegree
    def outdegree(self): return self._outdegree

    def weighted_degree(self): return self._weighted_degree
    def weighted_indegree(self): return self._weighted_indegree
    def weighted_outdegree(self): return self._weighted_outdegree

    def degree_centrality(self): return self._degree_centrality

    def reachable_from(self): return self._reachable_from

    def preferential_attachment(self): return self._preferential_attachment

    def triangle_count(self): return self._triangle_count
    def unique_triangle(self): return self._unique_triangle
    def num_triangles(self): return self._num_triangles
    def triangle(self): return self._triangle

    def local_clustering_coefficient(self):
        if self.directed:
            # TODO: Eventually make this error more similar to
            #   the corresponding error emitted from the pyrel graphlib wrapper.
            raise NotImplementedError(
                "Local clustering coefficient is not applicable to directed graphs"
            )
        return self._local_clustering_coefficient

    def average_clustering_coefficient(self):
        if self.directed:
            raise NotImplementedError(
                "Average clustering coefficient is not applicable to directed graphs"
            )
        return self._average_clustering_coefficient

    def weakly_connected_component(self): return self._weakly_connected_component

    def distance(self): return self._distance
    def adamic_adar(self): return self._adamic_adar
