import src.home.recommendation_service as recommendation_service

def create_child_nodes(root_node, childs):
        for term in childs: 
            new_node = recommendation_service.Node(term,term)
            root_node.add_child(new_node)

class TestRescomendationService:
    def test_safe_is_empty_list(self):
        tree = recommendation_service.Tree()
        root_node = recommendation_service.Node(0,'Root')
        tree.set_root(root_node)
        create_child_nodes(root_node,['A','B','C'])
        node_A = tree.get_node_by_name(root_node,'A')
        create_child_nodes(node_A,['D','E','F'])
        tree.display_tree(root_node)
    def test_levels(self):
        tree = recommendation_service.Tree()
        root_node = recommendation_service.Node(0,'Root')
        tree.set_root(root_node)
        create_child_nodes(root_node,['A','B'])
        node_A = tree.get_node_by_name(root_node,'A')
        create_child_nodes(node_A,['C'])
        node_C = tree.get_node_by_name(root_node,'C')
        create_child_nodes(node_C,['D'])
        node_B = tree.get_node_by_name(root_node,'B')
        create_child_nodes(node_B,['E'])
        tree.display_tree(root_node)
        print(tree.calculate_depth(root_node))
        print (list(range(1, tree.calculate_depth(root_node) + 1)))
        wtree = tree.build_wtree(root_node,1,[])
        print (wtree)


