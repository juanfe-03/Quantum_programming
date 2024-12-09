import numpy as np
from qiskit import QuantumCircuit, ClassicalRegister
from qiskit.quantum_info import Statevector
from qiskit.visualization import plot_histogram
from qiskit_aer import AerSimulator
import matplotlib.pyplot as plt
from qiskit_aer.noise import NoiseModel
from qiskit_ibm_runtime import QiskitRuntimeService
from qiskit import QuantumCircuit, transpile
import random

# Load the IBM Quantum account and select a backend (e.g., 'ibmq_manila')
service = QiskitRuntimeService()
backend = service.backend('ibm_brisbane')
noise_model = NoiseModel.from_backend(backend)


# Helper functions to display statevector information
def print_raw_statevector(state, label):
    print(f"\n{label} (Raw Coefficients):")
    print(state)


def print_statevector(state, label):
    print(f"\n{label}:")
    for i, amplitude in enumerate(state):
        basis_state = f"|{format(i, '05b')[::-1]}>"
        if abs(amplitude) > 0.0001:  # Filter out near-zero amplitudes
            print(f"{amplitude:.4f} {basis_state}")

 # Step 1: Prepare GHZ state for one logical qubit
def prepare_ghz(qc, qubits):
    qc.h(qubits[0])          # Hadamard on first qubit
    qc.cx(qubits[0], qubits[1])  # Entangle first and second qubits
    qc.cx(qubits[0], qubits[2])  # Entangle first and third qubits
def parity_check(qc):
    # Parity checks between system qubits using ancillas (3, 4)
    qc.cx(0, 3)  # Parity check between qubits 0 and 1 with ancilla 3
    qc.cx(1, 3)
    qc.cx(0, 4)  # Parity check between qubits 0 and 2 with ancilla 4
    qc.cx(2, 4)
    # Step 4: Syndrome decoding for 3rd ancillary
    qc.ccx(3, 4, 5)  # Detect and encode error info in ancilla qubit 5
    qc.cx(5,4)
    qc.cx(5,3)
def error_correct(qc):
    parity_check(qc)
    # Correct errors based on syndrome information
    qc.cx(5, 0)  # Correct first qubit if needed
    qc.cx(3, 1)  # Correct second qubit based on ancilla 3
    qc.cx(4, 2)  # Correct third qubit based on ancilla 4



def initialize_circuit():
    # Initialize Quantum Circuit with system and ancilla qubits
    qc = QuantumCircuit(7)
    # creg = ClassicalRegister(6, 'c')
    # qc.add_register(creg)

    # Step 1: Prepare GHZ state for one logical qubit

    # First logical GHZ qubit set
    prepare_ghz(qc, [0, 1, 2])
    return qc
def introduce_random_error(qc):
    # Step 2: Introduce some noise to the system qubits
    bit_error=random.randint(0,2)
    qc.x(bit_error)       # Apply X gate to simulate noise
    return qc
def introduce_purpose_error(qc,bit_error):
    # Step 2: Introduce some noise to the system qubits
    qc.x(bit_error)       # Apply X gate to simulate noise


def execute_and_measure(qc):
    # Final measurement
    qc.draw()
    print(qc)
    qc.measure_all()

    # Transpile the circuit for the AerSimulator
    qc = transpile(qc, basis_gates=noise_model.basis_gates)

    # Create the noisy simulator backend
    simulator = AerSimulator(noise_model=noise_model)

    # Run the simulation
    result = simulator.run(qc).result()
    counts = result.get_counts()

    # Plot and print results
    from qiskit.visualization import plot_histogram
    plot_histogram(counts)
    plt.show()

    # Display the final statevector (without measurements)
    final_state = Statevector.from_instruction(qc.remove_final_measurements(inplace=False))
    print_statevector(final_state, "Final State (Big-Endian Notation)")

    # Display measurement counts
    print("\nMeasurement counts:", counts)
for i in range(3):
    qc = initialize_circuit()
    introduce_purpose_error(qc,i)
    error_correct(qc)
    execute_and_measure(qc)


