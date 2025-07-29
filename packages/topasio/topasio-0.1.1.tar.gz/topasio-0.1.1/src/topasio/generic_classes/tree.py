


class Node:
    def __init__(self, name, parent=None):
        self.name = name
        self.isgroup = False
        self.expand = None
        self.children = []
        self.parent = parent

        if parent is not None:
            parent.add_child(self)

    def add_child(self, child_node):
        self.children.append(child_node)

    def print(self, prefix=""):
        print(f"{prefix}{self.name}")
        for child in self.children:
            child.print(prefix + "  ")

    def printAsDir(self, prefix=""):
        print(*list(self.iterateAsDir()), sep="\n")

    def isLeaf(self):
        return len(self.children) == 0

    def isParentOfChain(self):
        if self.isLeaf():
            return True
        
        if len(self.children) == 1:
            return self.children[0].isParentOfChain()

        return False
    
    def getChainAbove(self):
        if self.parent is not None:
            yield self.parent.name
            yield from self.parent.getChainAbove()

    def iterate(self):
        yield self
        for child in self.children:
            yield from child.iterate()

    def iterateAsDir(self, prefix=""):
        yield f"{prefix}{self.name}/"
        for child in self.children:
            yield from child.iterateAsDir(prefix=prefix + self.name + "/")


    def find(self, name):
        if self.name == name:
            return self
        for child in self.children:
            found = child.find(name)
            if found is not None:
                return found
        return None