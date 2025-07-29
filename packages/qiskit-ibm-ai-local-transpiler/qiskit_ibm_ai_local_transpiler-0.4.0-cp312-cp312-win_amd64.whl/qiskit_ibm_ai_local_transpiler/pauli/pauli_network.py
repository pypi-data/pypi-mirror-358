# -*- coding: utf-8 -*-

# (C) Copyright 2022 IBM. All Rights Reserved.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Clifford, Pauli


def make_pauli_string(num_qubits, qubit, pauli_type):
    p = ["I"] * num_qubits
    p[qubit] = pauli_type
    return "".join(p[::-1])


class PauliNetwork:
    @staticmethod
    def from_circuit(circuit):
        circuitb = QuantumCircuit(circuit.num_qubits).compose(circuit)

        rotations = []
        params = []
        clifford = Clifford(np.eye(2 * circuitb.num_qubits, dtype=bool))

        for g in circuitb:
            g_name = g.operation.name
            g_params = g.operation.params
            g_qubits = [q._index for q in g.qubits]

            if g_name in {"rx", "ry", "rz"}:
                p = Pauli(
                    make_pauli_string(
                        circuitb.num_qubits, g_qubits[0], g_name[1].upper()
                    )
                )
                p = p.evolve(clifford)
                rotations.append(p.adjoint())
                params += g_params

            else:
                try:
                    clifford = clifford.compose(g.operation, g_qubits)
                except Exception:
                    raise TypeError(
                        f"Gate {g_name} on qubits {g_qubits} not supported."
                    )

        return PauliNetwork(clifford.adjoint(), rotations, params)

    def __init__(self, clifford: Clifford, rotations: list[Pauli], params: list):
        self.clifford = clifford
        self.rotations = rotations
        self.params = params
