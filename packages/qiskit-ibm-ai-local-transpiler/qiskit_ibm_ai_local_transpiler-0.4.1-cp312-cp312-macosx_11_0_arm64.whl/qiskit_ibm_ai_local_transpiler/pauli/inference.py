# -*- coding: utf-8 -*-

# (C) Copyright 2025 IBM. All Rights Reserved.


"""Synthesize module"""
from typing import Union
import networkx as nx
import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit import Parameter
from qiskit.circuit.library import CXGate
from qiskit.quantum_info import Clifford
from qiskit.transpiler.passes.optimization import InverseCancellation

from qiskit_ibm_ai_local_transpiler import qiskit_ibm_ai_local_transpiler_rs
import logging

from .pauli_network import PauliNetwork
from .utils import (
    coupling_maps,
    check_synthesized_pauli,
)
from ..utils.transpile import (
    check_topology_synthesized_circuit,
    find_symmetries,
)

from ..config.config import AITranspilerConfig

logger = logging.getLogger(__name__)

CONFIG = AITranspilerConfig()

_cxc = InverseCancellation([CXGate()])

def just_clifford(circuit):
    circuit_out = QuantumCircuit.copy_empty_like(circuit)
    for g in circuit:
        if g.operation.name not in {"rx", "ry", "rz"}:
            circuit_out.append(g.operation, g.qubits)
    return circuit_out


def get_angle_param(angle_res, angle_mapping):
    idx, phase = angle_res
    param = angle_mapping[idx]

    param = Parameter(param) if isinstance(param, str) else param
    return phase * param


def to_circuit(synth_out, angles_mapping, original_circuit, num_qubits=None):
    if num_qubits is None:
        num_qubits = max(max(qs) for _, qs, _ in synth_out) + 1
    circuit = QuantumCircuit(num_qubits)
    for gate, qs, param in synth_out:
        if gate == "h":
            circuit.h(qs[0])
        elif gate == "s":
            circuit.s(qs[0])
        elif gate == "sx":
            circuit.sx(qs[0])
        elif gate == "cx":
            circuit.cx(*qs[::-1])
        elif gate == "rx":
            p = get_angle_param(param, angles_mapping)
            circuit.rx(p, qs[0])
        elif gate == "ry":
            p = get_angle_param(param, angles_mapping)
            circuit.ry(p, qs[0])
        elif gate == "rz":
            p = get_angle_param(param, angles_mapping)
            circuit.rz(p, qs[0])
        else:
            raise RuntimeError(f"Gate {gate} not recognized")

    # Phase fixing
    ph_correction = Clifford(
        just_clifford(circuit.inverse().compose(original_circuit))
    ).to_circuit()
    return circuit.compose(ph_correction)


def get_action_perms(perms, act_to_gate):
    act_perms = []
    for p in perms:
        act_perm = [
            act_to_gate.index((g, tuple(p[q] for q in qs))) for g, qs in act_to_gate
        ]
        act_perms.append(act_perm)
    return act_perms


def build_gate_input_list(num_qubits, one_q_gs, two_q_gs, valid_pairs=None):
    """Constructs a list with all possible gates given a gate set and a coupling map"""
    gate_list = []
    # One qubit gates
    for g in one_q_gs:
        for q in range(num_qubits):
            gate_list.append((g, (q,)))

    # Two qubit gates
    for g in two_q_gs:
        for q1 in range(num_qubits):
            for q2 in range(num_qubits):
                if q1 != q2 and (valid_pairs is None or (q1, q2) in valid_pairs):
                    gate_list.append((g, (q1, q2)))
    return gate_list

class PauliInference:
    DEFAULT_N_STEPS = 10
    RL_INFERENCE = None

    def __init__(
        self,
        models_info=CONFIG.ML_PAULI_CONFIG.AVAILABLE_MODELS,
        models_path=CONFIG.ML_PAULI_CONFIG.MODELS_PATH,
    ):
                # Auxiliary structures
        self.model_names = []
        self.model_cmap_hashes = []
        self.model_cmaps = []
        self.model_qubits = []
        self.model_topology = []
        self.model_backends = []
        models_info_rust = []

        act_gates = {}
        valid_perms = {}
        valid_act_perms = {}
        for model in models_info:
            model_name = model["model_name"]
            self.model_names.append(model_name)
            self.model_cmap_hashes.append(model["coupling_map_hash"])
            self.model_qubits.append(model["qubits"])
            self.model_topology.append(model["topology"])
            self.model_backends.append(model["backends"])
            topology = model["topology"]

            # From the env
            cmap = coupling_maps.get(topology)
            cmap += [(q2, q1) for q1, q2 in cmap]
            cmap = list(set([tuple(qbits) for qbits in cmap]))
            self.model_cmaps.append(cmap)
            valid_perms_list = find_symmetries(nx.Graph(cmap))
            valid_perms[model_name] = valid_perms_list
            act_to_gate = build_gate_input_list(
                model["qubits"], ["h", "s", "sx"], ["cx"], cmap
            )
            act_gates[model_name] = act_to_gate

            act_perms = get_action_perms(valid_perms_list, act_to_gate)
            valid_act_perms[model_name] = act_perms

            # Convert all dict values to strings for rust
            model_info_rust = {
                key: str(value) if value else "" for (key, value) in model.items()
            }
            models_info_rust.append(model_info_rust)

        if not PauliInference.RL_INFERENCE:
            PauliInference.RL_INFERENCE = qiskit_ibm_ai_local_transpiler_rs.PauliSynthesis(
                models_info_rust, act_gates, valid_perms, valid_act_perms, models_path
            )


    def synthesize(
        self,
        input_qc: QuantumCircuit,
        model_name: str = None,
        coupling_map_hash: str = None,
        backend: str = None,
        topology: str = None,
        n_qubits: int = None,
        check_result: bool = False,
        n_steps: Union[int, None] = None,
        metrics: tuple = (
            "n_cnots",
            "n_layers_cnots",
            "n_layers",
            "n_gates",
        ),
        keep_layout: bool = True,
    ) -> Union[QuantumCircuit, None]:
        """Synthesize Pauli Network using the RL model"""
        circ_n_qubits = input_qc.num_qubits
        selected_model_id = None
        if (
            coupling_map_hash is not None
            and coupling_map_hash in self.model_cmap_hashes
        ):
            # get the model to use depending on its coupling_map_hash
            selected_model_id = self.model_cmap_hashes.index(coupling_map_hash)
        elif backend is not None:
            # get the model to use depending the backend
            for i, backend_list in enumerate(self.model_backends):
                if backend_list and backend in backend_list:
                    selected_model_id = i
                    break

        # Topology is for now the name of the model
        elif topology is not None and topology in self.model_topology:
            # get the model to use depending the topology
            selected_model_id = self.model_topology.index(topology)
        elif n_qubits is not None and n_qubits in self.model_qubits:
            # get the model to use depending the n_qubits
            # avoid to choose models with topology for regular synthesis
            id_qubits_no_topology = [
                id
                for id, (qubits, topology) in enumerate(
                    zip(self.model_qubits, self.model_topology)
                )
                if topology is None and qubits == n_qubits
            ]
            if id_qubits_no_topology:
                selected_model_id = id_qubits_no_topology[0]
        else:
            # select the model to use depending on the N of qubits used in the permutation circuit
            # avoid to choose models with topology for regular synthesis
            # If there is no model for the current num_qubits without topology,
            # choose the next available (num_qubits +1).
            # So, if we request synthesis for 3 qubits and we only have a 3q model for I topology,
            # better use a model with more qubits but fully fully connected
            id_qubits_no_topology = [
                id
                for id, (qubits, topology) in enumerate(
                    zip(self.model_qubits, self.model_topology)
                )
                if topology is None and qubits >= circ_n_qubits
            ]
            if id_qubits_no_topology:
                selected_model_id = id_qubits_no_topology[0]

        if selected_model_id is None:
            logger.warning(
                "The model selected for inference is not available. Options used: "
                f"backend: {backend}, topology: {topology}, "
                f"coupling_map_hash: {coupling_map_hash}, "
                f"n_qubits: {n_qubits}, circuit n_qubits: {circ_n_qubits} "
            )
            return None
        model_name = self.model_names[selected_model_id]
        model_n_qubits = self.model_qubits[selected_model_id]
        if model_n_qubits < circ_n_qubits:
            logger.warning(
                f"The model selected for inference '{model_name}' cannot synthesize that circuit. "
                f"The model is trained for n_qubits={model_n_qubits} while the "
                f"circuits uses n_qubits={circ_n_qubits} "
            )
            return None

        # We should embed also in the cases of circuits with less qubits
        # than the bakend's or topologies qubits, or the model selected manually
        if model_n_qubits > circ_n_qubits:
            logger.info(
                f"Embedding the circuit from {circ_n_qubits} to {model_n_qubits}"
            )
            input_qc = QuantumCircuit(model_n_qubits).compose(input_qc)

        if n_steps is None:
            n_steps = self.DEFAULT_N_STEPS

        logger.info(
            f"Synthesizing the pauli network using the model {model_name}. "
        )

        logger.debug("Synthesizing circuit")
        pauli_network = PauliNetwork.from_circuit(input_qc)
        # Synth the input
        try:
            gate_list = self.RL_INFERENCE.run(
                self.model_names[selected_model_id],
                10,
                pauli_network.clifford.tableau[:, :-1].T.astype(np.int8).flatten(),
                [p.to_label() for p in pauli_network.rotations],
            )
        except Exception as err:
            raise RuntimeError(f"Inference failed: {err}")

        if len(gate_list) == 0:
            return QuantumCircuit(model_n_qubits)
        rl_circuit = _cxc(
            to_circuit(
                synth_out=gate_list,
                angles_mapping=pauli_network.params,
                original_circuit=input_qc,
                num_qubits=model_n_qubits,
            )
        )
        logger.debug("Circuit synthesized")

        if check_result is True:
            logger.debug("Checking results from synthesis process")
            if not check_synthesized_pauli(input_qc, rl_circuit):
                logger.warning(
                    "The check for synthesized permutation circuit vs the original permutation failed"
                )
                return None

            if topology is not None or backend is not None:
                logger.debug(
                    "Checking if synthesized permutation follows the input topology/backend's topology"
                )
                logger.debug(
                    f"Topology: {model_name}. Coupling map: {self.model_cmaps[selected_model_id]}"
                )
                if not check_topology_synthesized_circuit(
                    rl_circuit,
                    self.model_cmaps[selected_model_id],
                ):
                    logger.warning(
                        "The check to evaluate if synthesized permutation circuit follows the topology failed"
                    )
                    return None
            logger.info("Success. The checks for the synthesis results were successful")
        return rl_circuit
