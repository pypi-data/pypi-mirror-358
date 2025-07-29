import libcst as cst
from .utils import has_docstring


class FunctionAndClassCollector(cst.CSTVisitor):
    """
    A CSTVisitor that collects the names of functions and classes from a CST tree.
    """
    def __init__(self, force, update=False):
        """
        Initializes the FunctionAndClassCollector.

        Args:
          force (bool): Whether to force the collection of functions and classes even if they have docstrings.
          update (bool): Whether to update the collection of functions and classes if they have docstrings.
        """
        self.functions = []
        self.classes = []
        self.force = force
        self.update = update
        self.current_class = None

    def visit_FunctionDef(self, node: cst.FunctionDef) -> None:
        """
        Visits a FunctionDef node and adds its name to the list of functions if it does not have a docstring or if `force` or `update` is `True`.

        Args:
          node (cst.FunctionDef): The FunctionDef node to visit.
        """
        name = (
            f"{self.current_class}.{node.name.value}"
            if self.current_class
            else node.name.value
        )
        if self.force:
            self.functions.append(name)
        elif has_docstring(node) and self.update:
            self.functions.append(name)
        elif not has_docstring(node) and not self.update:
            self.functions.append(name)

    def visit_ClassDef(self, node: cst.ClassDef) -> None:
        """
        Visits a ClassDef node and adds its name to the list of classes if it does not have a docstring or if `force` or `update` is `True`. Also sets the current class name for nested function collection.

        Args:
          node (cst.ClassDef): The ClassDef node to visit.
        """
        self.current_class = node.name.value
        if self.force:
            self.classes.append(node.name.value)
        elif has_docstring(node) and self.update:
            self.classes.append(node.name.value)
        elif not has_docstring(node) and not self.update:
            self.classes.append(node.name.value)
        # self.visit_ClassDef(node)  # Call the superclass method to continue the visit

    def leave_ClassDef(self, node: cst.ClassDef) -> None:
        """
        Resets the current class name when leaving a ClassDef node.
        """
        self.current_class = None


def get_node_names(tree, force, update=False):
    """
    Gets the names of functions and classes from a CST tree.

    Args:
      tree (cst.CSTNode): The CST tree to traverse.
      force (bool): Whether to force the collection of functions and classes even if they have docstrings.
      update (bool, optional): Whether to update the collection of functions and classes if they have docstrings. Defaults to False.

    Returns:
      list[str]: A list of function and class names.
    """
    collector = FunctionAndClassCollector(force, update)
    tree.visit(collector)
    return collector.classes + collector.functions
