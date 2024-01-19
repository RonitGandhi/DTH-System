import hashlib
import bisect
import threading

class Node:
    def __init__(self, identifier):
        # Unique identifier for the node
        self.identifier = identifier
        # Data stored in the node (in this example, a key-value store)
        self.data = {}
        # Finger table used for efficient key lookup
        self.finger_table = {}

    def find_successor(self, key):
        # Find the successor node responsible for a given key
        if key in self.data:
            return self  # If the key is in the local data, return this node
        successor = self.closest_preceding_node(key)
        return successor.find_successor(key)

    def closest_preceding_node(self, key):
        # Find the closest preceding node in the finger table for a given key
        for i in range(160, 0, -1):
            if self.finger_table[i] and self.in_range(self.finger_table[i].identifier, self.identifier, key):
                return self.finger_table[i]
        return self  # If no closer node is found in the finger table, return this node

    def in_range(self, target, start, end):
        # Check if a target identifier is within a specified range
        if start <= end:
            return start < target <= end
        else:
            return start < target or target <= end

class ChordRing:
    def __init__(self):
        # List to store nodes in the Chord ring
        self.nodes = []
        # Lock to ensure thread safety when modifying the list of nodes
        self.lock = threading.Lock()

    def add_node(self, node):
        # Add a node to the Chord ring
        with self.lock:
            self.nodes.append(node)
            self.nodes.sort(key=lambda x: x.identifier)  # Sort the nodes based on their identifiers

    def hash_key(self, key):
        # Hash a string key to get a numerical identifier
        return int(hashlib.sha1(key.encode()).hexdigest(), 16)

    def find_node(self, key):
        # Find the node responsible for a given key in the Chord ring
        hashed_key = self.hash_key(key)
        with self.lock:
            index = bisect.bisect_left([node.identifier for node in self.nodes], hashed_key) % len(self.nodes)
            return self.nodes[index]

def main():
    # Create a Chord ring
    ring = ChordRing()

    # Create nodes and add them to the ring
    node1 = Node(ring.hash_key("node1"))
    node2 = Node(ring.hash_key("node2"))
    ring.add_node(node1)
    ring.add_node(node2)

    # Find and print the nodes responsible for 'key1' and 'key2'
    print("Node responsible for 'key1':", ring.find_node("key1").identifier)
    print("Node responsible for 'key2':", ring.find_node("key2").identifier)

if __name__ == "__main__":
    main()

