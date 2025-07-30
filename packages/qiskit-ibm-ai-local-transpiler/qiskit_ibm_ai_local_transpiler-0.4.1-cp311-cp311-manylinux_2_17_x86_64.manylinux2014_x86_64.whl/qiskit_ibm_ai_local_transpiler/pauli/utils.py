import random
import networkx as nx

from numpy import pi as np_pi, random as np_random

from qiskit import QuantumCircuit
from qiskit.quantum_info import Operator, process_fidelity
from qiskit.circuit.library.standard_gates import (
    CXGate,
    HGate,
    IGate,
    RXGate,
    RYGate,
    RZGate,
    SGate,
    SXGate,
    XGate,
    YGate,
    ZGate,
)

# ---------------------------------------------------------------------
# Coupling maps and permutations
# ---------------------------------------------------------------------

coupling_maps = {
    "4qL": [[0, 1], [1, 2], [2, 3]],
    "4qT": [[0,1], [1,2], [1,3]],
    "5qL": [[0,1], [1,2], [2,3], [3,4]],
    "5qT": [[0,1], [1,2], [2,3], [1,4]],
    "6qL": [[0,1], [1,2], [2,3], [3,4], [4,5]],
    "6qT": [[0,1], [1,2], [1,3], [3,4], [4,5]],
    "6qY": [[0,1], [1,2], [2,3], [1,4], [4,5]],
}

PAULI_COUPLING_MAPS_BY_HASHES_DICT = {
    nx.weisfeiler_lehman_graph_hash(nx.Graph(cmap)): cmap 
    for cmap in coupling_maps.values()
    }


def get_random_rotations(
    num_qubits, num_rots, valid_rots=["X", "Y", "Z", "I"], seed=42
):
    rng = np_random.RandomState(seed=seed)
    rots = []
    for _ in range(num_rots):
        rot = ["I"] * num_qubits
        while "".join(rot) == "I" * num_qubits:
            rot = []
            for _ in range(num_qubits):
                rot.append(rng.choice(valid_rots))
        rots.append("".join(rot))
    return rots


base_gate_dict = {
    "h": HGate,
    "s": SGate,
    "z": ZGate,
    "x": XGate,
    "y": YGate,
    # "z": YGate,
    "sx": SXGate,
    "cx": CXGate,
    "i": IGate,
    "rx": RXGate,
    "ry": RYGate,
    "rz": RZGate,
}
allowed_gates = ["cx", "x", "y", "z", "s", "sx", "h"]
allowed_rots = ["rx", "ry", "rz"]

def apply_random_gate(num_qubits, qc):
    gate = random.choice(allowed_gates)
    match gate:
        case "cx":
            qubits = tuple(random.sample(range(num_qubits), k=2))
            qc.cx(*qubits)
        case "x" | "y" | "z" | "s" | "sx" | "h":
            qubit = (random.choice(range(num_qubits)),)
            qc.append(base_gate_dict[gate](), qubit)


def apply_random_rot(num_qubits, qc):
    gate = random.choice(allowed_rots)
    match gate:
        case "rx" | "ry" | "rz":
            qubit = (random.choice(range(num_qubits)),)
            angle = random.uniform(-np_pi, np_pi)
            qc.append(base_gate_dict[gate](angle), qubit)

def get_random_pauli_network(num_qubits, depth=3, rot_p=0.5, max_rots=10, seed=42):
    random.seed(seed)
    qc = QuantumCircuit(num_qubits)
    rotations = 0
    while qc.depth() < depth and rotations <= max_rots:
        if random.uniform(0, 1) > rot_p:
            apply_random_gate(num_qubits, qc)
        else:
            if rotations == max_rots:
                continue
            apply_random_rot(num_qubits, qc)
            rotations += 1
    return qc

def check_synthesized_pauli(
    original_qc: QuantumCircuit, synthesized_qc: QuantumCircuit
):
    return process_fidelity(Operator(original_qc), Operator(synthesized_qc)) > 0.999