"""Insert a tree into beast xml file."""

from lxml import etree
from ete4 import Tree

from phynalysis.trees import prune_tree


def insert_tree(args):
    # read tree
    newick_data = args.tree.read_text()
    tree = Tree(newick_data)

    # read and parse template
    template = etree.parse(args.xml)
    root = template.getroot()

    # read type set
    type_set = root.find(".//typeSet[@id='type_set']")
    type_dict = dict(
        map(
            lambda s: s.strip().split("="),
            type_set.text.replace("\n", "").split(","),
        )
    )
    types = set(type_dict.keys())

    # check if all nodes are in the tree
    nodes = set(node.name for node in tree.traverse() if node.name)
    if types - nodes:
        print(f"{types - nodes} are missing from tree before pruning.")

    tree = prune_tree(tree, types)

    nodes = set(node.name for node in tree.traverse() if node.name)
    if types - nodes:
        print(f"{types - nodes} are missing from tree after pruning.")

    if nodes - types:
        print(f"{nodes - types} are missing from type set after pruning.")

    # find and update init element
    init_element = root.find(".//init")

    if init_element.attrib["spec"].endswith("StructuredCoalescentMultiTypeTree"):
        init_element.text = etree.CDATA(tree.write())
        init_element.attrib["spec"] = "MultiTypeTreeFromUntypedNewick"
    else:
        new_element = etree.Element(
            "init",
            {
                "spec": "beast.base.evolution.tree.TreeParser",
                "id": "tree",
                "IsLabelledNewick": "true",
                "adjustTipHeights": "false",
                "taxa": "@alignment",
                "newick": tree.write(),
            },
        )
        init_element.getparent().replace(init_element, new_element)

    # remove any tree element from xml
    tree_element = root.find(".//tree")
    if tree_element is not None:
        tree_element.getparent().remove(tree_element)

    # overwrite xml
    xml_data = etree.tostring(root, pretty_print=True).decode("utf-8")
    with open(args.xml, "w") as xml_file:
        xml_file.write(xml_data)
