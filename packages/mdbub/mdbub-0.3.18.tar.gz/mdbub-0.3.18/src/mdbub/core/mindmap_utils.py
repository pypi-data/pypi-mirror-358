from typing import List

from .mindmap import MindMapNode


def get_node_by_path(root: MindMapNode, path: List[int]) -> MindMapNode:
    node = root
    for idx in path:
        node = node.children[idx]
    return node


def get_breadcrumbs(root: MindMapNode, path: List[int]) -> List[str]:
    node = root
    labels = [node.label]
    for idx in path:
        node = node.children[idx]
        labels.append(node.label)
    return labels


def add_child(node: MindMapNode, label: str = "New Child") -> MindMapNode:
    child = MindMapNode(label)
    node.children.append(child)
    return child


def add_sibling(
    parent: MindMapNode, idx: int, label: str = "New Sibling"
) -> MindMapNode:
    sibling = MindMapNode(label)
    parent.children.insert(idx + 1, sibling)
    return sibling
