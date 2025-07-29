from collections.abc import Mapping, Sequence
from typing import Annotated, overload

from numpy.typing import ArrayLike
import scipy

from . import gate as gate
import scaluq.scaluq_core


class StateVector:
    r"""
    Vector representation of quantum state.

    Qubit index is start from 0. If the i-th value of the vector is $a_i$, the state is $\sum_i a_i \ket{i}$.

    Given `n_qubits: int`, construct with bases $\ket{0\dots 0}$ holding `n_qubits` number of qubits.

    Examples:
        >>> state1 = StateVector(2)
        >>> print(state1)
         *** Quantum State ***
         * Qubit Count : 2
         * Dimension   : 4
         * State vector : 
        00: (1,0)
        01: (0,0)
        10: (0,0)
        11: (0,0)
    """

    def __init__(self, n_qubits: int) -> None:
        r"""
        Construct with specified number of qubits.

        Vector is initialized with computational basis $\ket{0\dots0}$.

        Args:
            n_qubits (int):
                number of qubits

        Examples:
            >>> state1 = StateVector(2)
            >>> print(state1)
             *** Quantum State ***
             * Qubit Count : 2
             * Dimension   : 4
             * State vector : 
            00: (1,0)
            01: (0,0)
            10: (0,0)
            11: (0,0)
        """

    @staticmethod
    def Haar_random_state(n_qubits: int, seed: int | None = None) -> StateVector:
        """
        Construct :class:`StateVector` with Haar random state.

        Args:
            n_qubits (int):
                number of qubits

            seed (int | None, optional):
                random seed

                If not specified, the value from random device is used.

        Examples:
            >>> state = StateVector.Haar_random_state(2)
            >>> print(state.get_amplitudes())
            [(-0.3188299516496241+0.6723250989136779j), (-0.253461343768224-0.22430415678425403j), (0.24998142919420457+0.33096908710840045j), (0.2991187916479724+0.2650813322096342j)]
            >>> print(StateVector.Haar_random_state(2).get_amplitudes()) # If seed is not specified, generated vector differs.
            [(-0.49336775961196616-0.3319437726884906j), (-0.36069529482031787+0.31413708595210815j), (-0.3654176892043237-0.10307602590749808j), (-0.18175679804035652+0.49033467421609994j)]
            >>> print(StateVector.Haar_random_state(2, 0).get_amplitudes())
            [(0.030776817573663098-0.7321137912473642j), (0.5679070655936114-0.14551095055034327j), (-0.0932995615041323-0.07123201881040941j), (0.15213024630399696-0.2871374092016799j)]
            >>> print(StateVector.Haar_random_state(2, 0).get_amplitudes()) # If same seed is specified, same vector is generated.
            [(0.030776817573663098-0.7321137912473642j), (0.5679070655936114-0.14551095055034327j), (-0.0932995615041323-0.07123201881040941j), (0.15213024630399696-0.2871374092016799j)]
        """

    @staticmethod
    def uninitialized_state(n_qubits: int) -> StateVector:
        """
        Construct :class:`StateVector` without initializing.

        Args:
            n_qubits (int):
                number of qubits
        """

    def set_amplitude_at(self, index: int, value: complex) -> None:
        """
        Manually set amplitude at one index.

        Args:
            index (int):
                index of state vector

                This is read as binary.k-th bit of index represents k-th qubit.

            value (complex):
                amplitude value to set at index

        Examples:
            >>> state = StateVector(2)
            >>> state.get_amplitudes()
            [(1+0j), 0j, 0j, 0j]
            >>> state.set_amplitude_at(2, 3+1j)
            >>> state.get_amplitudes()
            [(1+0j), 0j, (3+1j), 0j]

        Notes:
            If you want to get amplitudes at all indices, you should use :meth:`.load`.
        """

    def get_amplitude_at(self, index: int) -> complex:
        """
        Get amplitude at one index.

        Args:
            index (int):
                index of state vector

                This is read as binary. k-th bit of index represents k-th qubit.

        Returns:
            complex:
                Amplitude at specified index

        Examples:
            >>> state = StateVector(2)
            >>> state.load([1+2j, 3+4j, 5+6j, 7+8j])
            >>> state.get_amplitude_at(0)
            (1+2j)
            >>> state.get_amplitude_at(1)
            (3+4j)
            >>> state.get_amplitude_at(2)
            (5+6j)
            >>> state.get_amplitude_at(3)
            (7+8j)

        Notes:
            If you want to get amplitudes at all indices, you should use :meth:`.get_amplitudes`.
        """

    def set_zero_state(self) -> None:
        r"""
        Initialize with computational basis $\ket{00\dots0}$.

        Examples:
            >>> state = StateVector.Haar_random_state(2)
            >>> state.get_amplitudes()
            [(-0.05726462181150916+0.3525270165415515j), (0.1133709060491142+0.3074930854078303j), (0.03542174692996924+0.18488950377672345j), (0.8530024105558827+0.04459332470844164j)]
            >>> state.set_zero_state()
            >>> state.get_amplitudes()
            [(1+0j), 0j, 0j, 0j]
        """

    def set_zero_norm_state(self) -> None:
        """
        Initialize with 0 (null vector).

        Examples:
            >>> state = StateVector(2)
            >>> state.get_amplitudes()
            [(1+0j), 0j, 0j, 0j]
            >>> state.set_zero_norm_state()
            >>> state.get_amplitudes()
            [0j, 0j, 0j, 0j]
        """

    def set_computational_basis(self, basis: int) -> None:
        r"""
        Initialize with computational basis \ket{\mathrm{basis}}.

        Args:
            basis (int):
                basis as integer format ($0 \leq \mathrm{basis} \leq 2^{\mathrm{n\_qubits}}-1$)

        Examples:
            >>> state = StateVector(2)
            >>> state.set_computational_basis(0) # |00>
            >>> state.get_amplitudes()
            [(1+0j), 0j, 0j, 0j]
            >>> state.set_computational_basis(1) # |01>
            >>> state.get_amplitudes()
            [0j, (1+0j), 0j, 0j]
            >>> state.set_computational_basis(2) # |10>
            >>> state.get_amplitudes()
            [0j, 0j, (1+0j), 0j]
            >>> state.set_computational_basis(3) # |11>
            >>> state.get_amplitudes()
            [0j, 0j, 0j, (1+0j)]
        """

    def get_amplitudes(self) -> list[complex]:
        r"""
        Get all amplitudes as `list[complex]`.

        Returns:
            list[complex]:
                amplitudes of list with len $2^{\mathrm{n\_qubits}}$

        Examples:
            >>> state = StateVector(2)
            >>> state.get_amplitudes()
            [(1+0j), 0j, 0j, 0j]
        """

    def n_qubits(self) -> int:
        """
        Get num of qubits.

        Returns:
            int:
                num of qubits

        Examples:
            >>> state = StateVector(2)
            >>> state.n_qubits()
            2
        """

    def dim(self) -> int:
        r"""
        Get dimension of the vector ($=2^\mathrm{n\_qubits}$).

        Returns:
            int:
                dimension of the vector

        Examples:
            >>> state = StateVector(2)
            >>> state.dim()
            4
        """

    def get_squared_norm(self) -> float:
        r"""
        Get squared norm of the state. $\braket{\psi|\psi}$.

        Returns:
            float:
                squared norm of the state

        Examples:
            >>> v = [1+2j, 3+4j, 5+6j, 7+8j]
            >>> state = StateVector(2)
            >>> state.load(v)
            >>> state.get_squared_norm()
            204.0>>> sum([abs(a)**2 for a in v])
            204.0
        """

    def normalize(self) -> None:
        r"""
        Normalize state.

        Let $\braket{\psi|\psi} = 1$ by multiplying constant.

        Examples:
            >>> v = [1+2j, 3+4j, 5+6j, 7+8j]
            >>> state = StateVector(2)
            >>> state.load(v)
            >>> state.normalize()
            >>> state.get_amplitudes()
            [(0.07001400420140048+0.14002800840280097j), (0.21004201260420147+0.28005601680560194j), (0.3500700210070024+0.42008402520840293j), (0.4900980294098034+0.5601120336112039j)]
            >>> norm = state.get_squared_norm()**.5
            >>> [a / norm for a in v][(0.07001400420140048+0.14002800840280097j), (0.21004201260420147+0.28005601680560194j), (0.3500700210070024+0.42008402520840293j), (0.4900980294098034+0.5601120336112039j)]
        """

    def get_zero_probability(self, index: int) -> float:
        r"""
        Get the probability to observe $\ket{0}$ at specified index.

        **State must be normalized.**

        Args:
            index (int):
                qubit index to be observed

        Returns:
            float:
                probability to observe $\ket{0}$

        Examples:
            >>> v = [1 / 6**.5, 2j / 6**.5 * 1j, -1 / 6**.5, -2j / 6**.5]
            >>> state = StateVector(2)
            >>> state.load(v)
            >>> state.get_zero_probability(0)
            0.3333333333333334
            >>> state.get_zero_probability(1)
            0.8333333333333336
            >>> abs(v[0])**2+abs(v[2])**2
            0.3333333333333334
            >>> abs(v[0])**2+abs(v[1])**2
            0.8333333333333336
        """

    def get_marginal_probability(self, measured_values: Sequence[int]) -> float:
        """
        Get the marginal probability to observe as given.

        **State must be normalized.**

        Args:
            measured_values (list[int]):
                list with len n_qubits.

                `0`, `1` or :attr:`.UNMEASURED` is allowed for each elements. `0` or `1` shows the qubit is observed and the value is got. :attr:`.UNMEASURED` shows the the qubit is not observed.

        Returns:
            float:
                probability to observe as given

        Examples:
            >>> v = [1/4, 1/2, 0, 1/4, 1/4, 1/2, 1/4, 1/2]
            state = StateVector(3)
            >>> state.load(v)
            >>> state.get_marginal_probability([0, 1, StateVector.UNMEASURED])
            0.0625
            >>> abs(v[2])**2 + abs(v[6])**2
            0.0625
        """

    def get_entropy(self) -> float:
        r"""
        Get the entropy of the vector.

        **State must be normalized.**

        Returns:
            float:
                entropy

        Examples:
            >>> v = [1/4, 1/2, 0, 1/4, 1/4, 1/2, 1/4, 1/2]
            >>> state = StateVector(3)
            >>> state.load(v)
            >>> state.get_entropy()
            2.5000000000000497
            >>> sum(-abs(a)**2 * math.log2(abs(a)**2) for a in v if a != 0)
            2.5

        Notes:
            The result of this function differs from qulacs. This is because scaluq adopted 2 for the base of log in the definition of entropy $\sum_i -p_i \log p_i$ however qulacs adopted e.
        """

    def add_state_vector_with_coef(self, coef: complex, state: StateVector) -> None:
        r"""
        Add other state vector with multiplying the coef and make superposition.

        $\ket{\mathrm{this}}\leftarrow\ket{\mathrm{this}}+\mathrm{coef} \ket{\mathrm{state}}$.

        Args:
            coef (complex):
                coefficient to multiply to `state`

            state (:class:`StateVector`):
                state to be added

        Examples:
            >>> state1 = StateVector(1)
            >>> state1.load([1, 2])
            >>> state2 = StateVector(1)
            >>> state2.load([3, 4])
            >>> state1.add_state_vector_with_coef(2j, state2)
            >>> state1.get_amplitudes()
            [(1+6j), (2+8j)]
        """

    def multiply_coef(self, coef: complex) -> None:
        r"""
        Multiply coef.

        $\ket{\mathrm{this}}\leftarrow\mathrm{coef}\ket{\mathrm{this}}$.

        Args:
            coef (complex):
                coefficient to multiply

        Examples:
            >>> state = StateVector(1)
            >>> state.load([1, 2])
            >>> state.multiply_coef(2j)
            >>> state.get_amplitudes()
            [2j, 4j]
        """

    def sampling(self, sampling_count: int, seed: int | None = None) -> list[int]:
        r"""
        Sampling state vector independently and get list of computational basis

        Args:
            sampling_count (int):
                how many times to apply sampling

            seed (int | None, optional):
                random seed

                If not specified, the value from random device is used.

        Returns:
            list[int]:
                result of sampling

                list of `sampling_count` length. Each element is in $[0,2^{\mathrm{n\_qubits}})$

        Examples:
             >>> state = StateVector(2)
            >>> state.load([1/2, 0, -3**.5/2, 0])
            >>> state.sampling(8) 
            [0, 2, 2, 2, 2, 0, 0, 2]
        """

    def to_string(self) -> str:
        r"""
        Information as `str`.

        Returns:
            str:
                information as str

        Examples:
            >>> state = StateVector(1)
            >>> state.to_string()
            ' *** Quantum State ***\n * Qubit Count : 1\n * Dimension   : 2\n * State vector : \n0: (1,0)\n1: (0,0)\n'
        """

    def load(self, other: Sequence[complex]) -> None:
        r"""
        Load amplitudes of `Sequence`

        Args:
            other (collections.abc.Sequence[complex]):
                list of complex amplitudes with len $2^{\mathrm{n_qubits}}$
        """

    def __str__(self) -> str:
        """
        Information as `str`.

        Same as :meth:`.to_string()`
        """

    UNMEASURED: int = ...
    """
    Constant used for `StateVector::get_marginal_probability` to express the the qubit is not measured.
    """

    def to_json(self) -> str:
        """
        Information as json style.

        Returns:
            str:
                information as json style

        Examples:
            >>> state = StateVector(1)
            >>> state.to_json()
            '{"amplitudes":[{"imag":0.0,"real":1.0},{"imag":0.0,"real":0.0}],"n_qubits":1}'
        """

    def load_json(self, json_str: str) -> None:
        """Read an object from the JSON representation of the state vector."""

class StateVectorBatched:
    r"""
    Batched vector representation of quantum state.

    Qubit index starts from 0. If the amplitudes of $\ket{b_{n-1}\dots b_0}$ are $b_i$, the state is $\sum_i b_i 2^i$.

    Given `batch_size: int, n_qubits: int`, construct a batched state vector with specified batch size and qubits.

    Given `other: StateVectorBatched`, Construct a batched state vector by copying another batched state.

    Examples:
        >>> states = StateVectorBatched(3, 2)
        >>> print(states)
        Qubit Count : 2
        Dimension : 4
        --------------------
        Batch_id : 0
        State vector : 
          00 : (1,0)
          01 : (0,0)
          10 : (0,0)
          11 : (0,0)
        --------------------
        Batch_id : 1
        State vector : 
          00 : (1,0)
          01 : (0,0)
          10 : (0,0)
          11 : (0,0)
        --------------------
        Batch_id : 2
        State vector : 
          00 : (1,0)
          01 : (0,0)
          10 : (0,0)
          11 : (0,0)
    """

    @overload
    def __init__(self, batch_size: int, n_qubits: int) -> None:
        """
        Construct batched state vector with specified batch size and qubits.

        Args:
            batch_size (int):
                Number of batches.

            n_qubits (int):
                Number of qubits in each state vector.

        Examples:
            >>> states = StateVectorBatched(3, 2)
            >>> print(states)
            Qubit Count : 2
            Dimension : 4
            --------------------
            Batch_id : 0
            State vector : 
              00 : (1,0)
              01 : (0,0)
              10 : (0,0)
              11 : (0,0)
            --------------------
            Batch_id : 1
            State vector : 
              00 : (1,0)
              01 : (0,0)
              10 : (0,0)
              11 : (0,0)
            --------------------
            Batch_id : 2
            State vector : 
              00 : (1,0)
              01 : (0,0)
              10 : (0,0)
              11 : (0,0)
        """

    @overload
    def __init__(self, other: StateVectorBatched) -> None:
        """
        Construct a batched state vector by copying another batched state.

        Args:
            other (StateVectorBatched):
                The batched state vector to copy.
        """

    def n_qubits(self) -> int:
        """
        Get the number of qubits in each state vector.

        Returns:
            int:
                The number of qubits.
        """

    def dim(self) -> int:
        r"""
        Get the dimension of each state vector (=$2^{\mathrm{n\_qubits}}$).

        Returns:
            int:
                The dimension of the vector.
        """

    def batch_size(self) -> int:
        """
        Get the batch size (number of state vectors).

        Returns:
            int:
                The batch size.
        """

    def set_state_vector(self, state: StateVector) -> None:
        """
        Set all state vectors in the batch to the given state.

        Args:
            state (StateVector):
                State to set for all batches.
        """

    def set_state_vector_at(self, batch_id: int, state: StateVector) -> None:
        """
        Set the state vector at a specific batch index.

        Args:
            batch_id (int):
                Index in batch to set.

            state (StateVector):
                State to set at the specified index.
        """

    def get_state_vector_at(self, batch_id: int) -> StateVector:
        """
        Get the state vector at a specific batch index.

        Args:
            batch_id (int):
                Index in batch to get.

        Returns:
            StateVector:
                The state vector at the specified batch index.
        """

    def set_zero_state(self) -> None:
        """Initialize all states to |0...0⟩."""

    def set_computational_basis(self, basis: int) -> None:
        """
        Set all states to the specified computational basis state.

        Args:
            basis (int):
                Index of the computational basis state.
        """

    def set_zero_norm_state(self) -> None:
        """Set all amplitudes to zero."""

    def set_Haar_random_state(self, set_same_state: bool, seed: int | None = None) -> None:
        """
        Initialize with Haar random states.

        Args:
            batch_size (int):
                Number of states in batch.

            n_qubits (int):
                Number of qubits per state.

            set_same_state (bool):
                Whether to set all states to the same random state.

            seed (int, optional):
                Random seed (default: random).
        """

    @staticmethod
    def Haar_random_state(batch_size: int, n_qubits: int, set_same_state: bool, seed: int | None = None) -> StateVectorBatched:
        """
        Construct :class:`StateVectorBatched` with Haar random state.

        Args:
            batch_size (int):
                Number of states in batch.

            n_qubits (int):
                Number of qubits per state.

            set_same_state (bool):
                Whether to set all states to the same random state.

            seed (int, optional):
                Random seed (default: random).

        Returns:
            StateVectorBatched:
                New batched state vector with random states.
        """

    @staticmethod
    def uninitialized_state(batch_size: int, n_qubits: int) -> StateVectorBatched:
        """
        Construct :class:`StateVectorBatched` without initializing.

        Args:
            batch_size (int):
                Number of states in batch.

            n_qubits (int):
                number of qubits
        """

    def get_squared_norm(self) -> list[float]:
        """
        Get squared norm for each state in the batch.

        Returns:
            list[float]:
                List of squared norms.
        """

    def normalize(self) -> None:
        """Normalize all states in the batch."""

    def get_zero_probability(self, target_qubit_index: int) -> list[float]:
        """
        Get probability of measuring |0⟩ on specified qubit for each state.

        Args:
            target_qubit_index (int):
                Index of qubit to measure.

        Returns:
            list[float]:
                Probabilities for each state in batch.
        """

    def get_marginal_probability(self, measured_values: Sequence[int]) -> list[float]:
        """
        Get marginal probabilities for specified measurement outcomes.

        Args:
            measured_values (list[int]):
                Measurement configuration.

        Returns:
            list[float]:
                Probabilities for each state in batch.
        """

    def get_entropy(self) -> list[float]:
        """
        Calculate von Neumann entropy for each state.

        Returns:
            list[float]:
                Entropy values for each state.
        """

    def sampling(self, sampling_count: int, seed: int | None = None) -> list[list[int]]:
        """
        Sample from the probability distribution of each state.

        Args:
            sampling_count (int):
                Number of samples to take.

            seed (int, optional):
                Random seed (default: random).

        Returns:
            list[list[int]]:
                Samples for each state in batch.
        """

    def add_state_vector_with_coef(self, coef: complex, states: StateVectorBatched) -> None:
        """
        Add another batched state vector multiplied by a coefficient.

        Args:
            coef (complex):
                Coefficient to multiply with states.

            states (StateVectorBatched):
                States to add.
        """

    def multiply_coef(self, coef: complex) -> None:
        """
        Multiply all states by a coefficient.

        Args:
            coef (complex):
                Coefficient to multiply.
        """

    def load(self, states: Sequence[Sequence[complex]]) -> None:
        """
        Load amplitudes for all states in batch.

        Args:
            states (list[list[complex]]):
                Amplitudes for each state.
        """

    def get_amplitudes(self) -> list[list[complex]]:
        """
        Get amplitudes of all states in batch.

        Returns:
            list[list[complex]]:
                Amplitudes for each state.
        """

    def copy(self) -> StateVectorBatched:
        """
        Create a deep copy of this batched state vector.

        Returns:
            StateVectorBatched:
                New copy of the states.
        """

    def to_string(self) -> str:
        """
        Get string representation of the batched states.

        Returns:
            str:
                String representation of states.

        Examples:
            >>> states = StateVectorBatched.Haar_random_state(2, 3, False)
            >>> print(states.to_string())
             Qubit Count : 3 
            Dimension : 8
            --------------------
            Batch_id : 0
            State vector : 
              000 : (-0.135887,-0.331815)
              001 : (-0.194471,0.108649)
              010 : (-0.147649,-0.329848)
              011 : (-0.131489,0.131093)
              100 : (-0.262069,0.198882)
              101 : (-0.0797319,-0.313087)
              110 : (-0.140573,-0.0577208)
              111 : (0.181703,0.622905)
            --------------------
            Batch_id : 1
            State vector : 
              000 : (-0.310841,0.342973)
              001 : (0.16157,-0.216366)
              010 : (-0.301031,0.2286)
              011 : (-0.430187,-0.341108)
              100 : (0.0126325,0.169034)
              101 : (0.356303,0.033349)
              110 : (-0.184462,-0.0361127)
              111 : (0.224724,-0.160959)
        """

    def __str__(self) -> str:
        """
        Get string representation of the batched states.

        Returns:
            str:
                String representation of states.
        """

    def to_json(self) -> str:
        """
        Convert states to JSON string.

        Returns:
            str:
                JSON representation of states.

        Examples:
            >>> states = StateVectorBatched.Haar_random_state(2, 3, False)
            >>> print(states.to_json())
            {"batch_size":2,"batched_amplitudes":[{"amplitudes":[{"imag":-0.06388485770655017,"real":-0.18444457531249306},{"imag":-0.19976277833680336,"real":0.02688995276721736},{"imag":-0.10325202586347756,"real":0.34750392103639344},{"imag":-0.08316405642178114,"real":-0.13786630724295332},{"imag":-0.12472230847944885,"real":0.14554495925352498},{"imag":-0.26280362129148116,"real":0.11742521097266628},{"imag":-0.2624948420923217,"real":0.020338934511145986},{"imag":0.03692345644121347,"real":0.7573990906654825}]},{"amplitudes":[{"imag":-0.042863543360962014,"real":0.2002535190582227},{"imag":-0.26105089098208206,"real":0.033791318581512894},{"imag":-0.5467139724228703,"real":0.23960667554139148},{"imag":-0.1008220536735562,"real":0.3431287916056916},{"imag":0.26552531402802715,"real":-0.06501035752577479},{"imag":0.11913162732583721,"real":0.47146654843051494},{"imag":-0.1877230034941065,"real":0.04062968177663162},{"imag":-0.16209817213481867,"real":-0.1737591400014162}]}],"n_qubits":3}
        """

    def load_json(self, json_str: str) -> None:
        """
        Load states from JSON string.

        Args:
            json_str (str):
                JSON string to load from.
        """

class Gate:
    """
    General class of QuantumGate.

    Notes
    	Downcast to required to use gate-specific functions.
    """

    @overload
    def __init__(self, arg: Gate) -> None:
        """Downcast from Gate."""

    @overload
    def __init__(self, arg: Gate) -> None:
        """Just copy shallowly."""

    @overload
    def __init__(self, arg: IGate, /) -> None:
        """Upcast from `IGate`."""

    @overload
    def __init__(self, arg: GlobalPhaseGate, /) -> None:
        """Upcast from `GlobalPhaseGate`."""

    @overload
    def __init__(self, arg: XGate, /) -> None:
        """Upcast from `XGate`."""

    @overload
    def __init__(self, arg: YGate, /) -> None:
        """Upcast from `YGate`."""

    @overload
    def __init__(self, arg: ZGate, /) -> None:
        """Upcast from `ZGate`."""

    @overload
    def __init__(self, arg: HGate, /) -> None:
        """Upcast from `HGate`."""

    @overload
    def __init__(self, arg: SGate, /) -> None:
        """Upcast from `SGate`."""

    @overload
    def __init__(self, arg: SdagGate, /) -> None:
        """Upcast from `SdagGate`."""

    @overload
    def __init__(self, arg: TGate, /) -> None:
        """Upcast from `TGate`."""

    @overload
    def __init__(self, arg: TdagGate, /) -> None:
        """Upcast from `TdagGate`."""

    @overload
    def __init__(self, arg: SqrtXGate, /) -> None:
        """Upcast from `SqrtXGate`."""

    @overload
    def __init__(self, arg: SqrtXdagGate, /) -> None:
        """Upcast from `SqrtXdagGate`."""

    @overload
    def __init__(self, arg: SqrtYGate, /) -> None:
        """Upcast from `SqrtYGate`."""

    @overload
    def __init__(self, arg: SqrtYdagGate, /) -> None:
        """Upcast from `SqrtYdagGate`."""

    @overload
    def __init__(self, arg: P0Gate, /) -> None:
        """Upcast from `P0Gate`."""

    @overload
    def __init__(self, arg: P1Gate, /) -> None:
        """Upcast from `P1Gate`."""

    @overload
    def __init__(self, arg: RXGate, /) -> None:
        """Upcast from `RXGate`."""

    @overload
    def __init__(self, arg: RYGate, /) -> None:
        """Upcast from `RYGate`."""

    @overload
    def __init__(self, arg: RZGate, /) -> None:
        """Upcast from `RZGate`."""

    @overload
    def __init__(self, arg: U1Gate, /) -> None:
        """Upcast from `U1Gate`."""

    @overload
    def __init__(self, arg: U2Gate, /) -> None:
        """Upcast from `U2Gate`."""

    @overload
    def __init__(self, arg: U3Gate, /) -> None:
        """Upcast from `U3Gate`."""

    @overload
    def __init__(self, arg: SwapGate, /) -> None:
        """Upcast from `SwapGate`."""

    @overload
    def __init__(self, arg: SparseMatrixGate, /) -> None:
        """Upcast from `SparseMatrixGate`."""

    @overload
    def __init__(self, arg: DenseMatrixGate, /) -> None:
        """Upcast from `DenseMatrixGate`."""

    @overload
    def __init__(self, arg: PauliGate, /) -> None:
        """Upcast from `PauliGate`."""

    @overload
    def __init__(self, arg: PauliRotationGate, /) -> None:
        """Upcast from `PauliRotationGate`."""

    def gate_type(self) -> scaluq.scaluq_core.GateType:
        """Get gate type as `GateType` enum."""

    def target_qubit_list(self) -> list[int]:
        """Get target qubits as `list[int]`. **Control qubits are not included.**"""

    def control_qubit_list(self) -> list[int]:
        """Get control qubits as `list[int]`."""

    def operand_qubit_list(self) -> list[int]:
        """Get target and control qubits as `list[int]`."""

    def target_qubit_mask(self) -> int:
        """Get target qubits as mask. **Control qubits are not included.**"""

    def control_qubit_mask(self) -> int:
        """Get control qubits as mask."""

    def operand_qubit_mask(self) -> int:
        """Get target and control qubits as mask."""

    def get_inverse(self) -> Gate:
        """Generate inverse gate as `Gate` type. If not exists, return None."""

    @overload
    def update_quantum_state(self, state_vector: StateVector) -> None:
        """
        Apply gate to `state_vector`. `state_vector` in args is directly updated.
        """

    @overload
    def update_quantum_state(self, states: StateVectorBatched) -> None:
        """Apply gate to `states`. `states` in args is directly updated."""

    def get_matrix(self) -> Annotated[ArrayLike, dict(dtype='complex128', shape=(None, None), order='C')]:
        """Get matrix representation of the gate."""

    def to_string(self) -> str:
        """Get string representation of the gate."""

    def __str__(self) -> str:
        """Get string representation of the gate."""

    def to_json(self) -> str:
        """Get JSON representation of the gate."""

    def load_json(self, json_str: str) -> None:
        """Read an object from the JSON representation of the gate."""

    def phase(self) -> float:
        r"""Get `phase` property. The phase is represented as $\gamma$."""

class IGate:
    """
    Specific class of Pauli-I gate.

    Notes
    	Upcast is required to use gate-general functions (ex: add to Circuit).
    """

    @overload
    def __init__(self, arg: Gate, /) -> None:
        """Downcast from Gate."""

    @overload
    def __init__(self, arg: Gate, /) -> None: ...

    def gate_type(self) -> scaluq.scaluq_core.GateType:
        """Get gate type as `GateType` enum."""

    def target_qubit_list(self) -> list[int]:
        """Get target qubits as `list[int]`. **Control qubits are not included.**"""

    def control_qubit_list(self) -> list[int]:
        """Get control qubits as `list[int]`."""

    def operand_qubit_list(self) -> list[int]:
        """Get target and control qubits as `list[int]`."""

    def target_qubit_mask(self) -> int:
        """Get target qubits as mask. **Control qubits are not included.**"""

    def control_qubit_mask(self) -> int:
        """Get control qubits as mask."""

    def operand_qubit_mask(self) -> int:
        """Get target and control qubits as mask."""

    def get_inverse(self) -> Gate:
        """Generate inverse gate as `Gate` type. If not exists, return None."""

    @overload
    def update_quantum_state(self, state_vector: StateVector) -> None:
        """
        Apply gate to `state_vector`. `state_vector` in args is directly updated.
        """

    @overload
    def update_quantum_state(self, states: StateVectorBatched) -> None:
        """Apply gate to `states`. `states` in args is directly updated."""

    def get_matrix(self) -> Annotated[ArrayLike, dict(dtype='complex128', shape=(None, None), order='C')]:
        """Get matrix representation of the gate."""

    def to_string(self) -> str:
        """Get string representation of the gate."""

    def __str__(self) -> str:
        """Get string representation of the gate."""

    def to_json(self) -> str:
        """Get JSON representation of the gate."""

    def load_json(self, json_str: str) -> None:
        """Read an object from the JSON representation of the gate."""

class GlobalPhaseGate:
    r"""
    Specific class of gate, which rotate global phase, represented as $e^{i\gamma}I$.

    Notes
    	Upcast is required to use gate-general functions (ex: add to Circuit).
    """

    @overload
    def __init__(self, arg: Gate, /) -> None:
        """Downcast from Gate."""

    @overload
    def __init__(self, arg: Gate, /) -> None: ...

    def gate_type(self) -> scaluq.scaluq_core.GateType:
        """Get gate type as `GateType` enum."""

    def target_qubit_list(self) -> list[int]:
        """Get target qubits as `list[int]`. **Control qubits are not included.**"""

    def control_qubit_list(self) -> list[int]:
        """Get control qubits as `list[int]`."""

    def operand_qubit_list(self) -> list[int]:
        """Get target and control qubits as `list[int]`."""

    def target_qubit_mask(self) -> int:
        """Get target qubits as mask. **Control qubits are not included.**"""

    def control_qubit_mask(self) -> int:
        """Get control qubits as mask."""

    def operand_qubit_mask(self) -> int:
        """Get target and control qubits as mask."""

    def get_inverse(self) -> Gate:
        """Generate inverse gate as `Gate` type. If not exists, return None."""

    @overload
    def update_quantum_state(self, state_vector: StateVector) -> None:
        """
        Apply gate to `state_vector`. `state_vector` in args is directly updated.
        """

    @overload
    def update_quantum_state(self, states: StateVectorBatched) -> None:
        """Apply gate to `states`. `states` in args is directly updated."""

    def get_matrix(self) -> Annotated[ArrayLike, dict(dtype='complex128', shape=(None, None), order='C')]:
        """Get matrix representation of the gate."""

    def to_string(self) -> str:
        """Get string representation of the gate."""

    def __str__(self) -> str:
        """Get string representation of the gate."""

    def to_json(self) -> str:
        """Get JSON representation of the gate."""

    def load_json(self, json_str: str) -> None:
        """Read an object from the JSON representation of the gate."""

class XGate:
    """
    Specific class of Pauli-X gate.

    Notes
    	Upcast is required to use gate-general functions (ex: add to Circuit).
    """

    @overload
    def __init__(self, arg: Gate, /) -> None:
        """Downcast from Gate."""

    @overload
    def __init__(self, arg: Gate, /) -> None: ...

    def gate_type(self) -> scaluq.scaluq_core.GateType:
        """Get gate type as `GateType` enum."""

    def target_qubit_list(self) -> list[int]:
        """Get target qubits as `list[int]`. **Control qubits are not included.**"""

    def control_qubit_list(self) -> list[int]:
        """Get control qubits as `list[int]`."""

    def operand_qubit_list(self) -> list[int]:
        """Get target and control qubits as `list[int]`."""

    def target_qubit_mask(self) -> int:
        """Get target qubits as mask. **Control qubits are not included.**"""

    def control_qubit_mask(self) -> int:
        """Get control qubits as mask."""

    def operand_qubit_mask(self) -> int:
        """Get target and control qubits as mask."""

    def get_inverse(self) -> Gate:
        """Generate inverse gate as `Gate` type. If not exists, return None."""

    @overload
    def update_quantum_state(self, state_vector: StateVector) -> None:
        """
        Apply gate to `state_vector`. `state_vector` in args is directly updated.
        """

    @overload
    def update_quantum_state(self, states: StateVectorBatched) -> None:
        """Apply gate to `states`. `states` in args is directly updated."""

    def get_matrix(self) -> Annotated[ArrayLike, dict(dtype='complex128', shape=(None, None), order='C')]:
        """Get matrix representation of the gate."""

    def to_string(self) -> str:
        """Get string representation of the gate."""

    def __str__(self) -> str:
        """Get string representation of the gate."""

    def to_json(self) -> str:
        """Get JSON representation of the gate."""

    def load_json(self, json_str: str) -> None:
        """Read an object from the JSON representation of the gate."""

class YGate:
    """
    Specific class of Pauli-Y gate.

    Notes
    	Upcast is required to use gate-general functions (ex: add to Circuit).
    """

    @overload
    def __init__(self, arg: Gate, /) -> None:
        """Downcast from Gate."""

    @overload
    def __init__(self, arg: Gate, /) -> None: ...

    def gate_type(self) -> scaluq.scaluq_core.GateType:
        """Get gate type as `GateType` enum."""

    def target_qubit_list(self) -> list[int]:
        """Get target qubits as `list[int]`. **Control qubits are not included.**"""

    def control_qubit_list(self) -> list[int]:
        """Get control qubits as `list[int]`."""

    def operand_qubit_list(self) -> list[int]:
        """Get target and control qubits as `list[int]`."""

    def target_qubit_mask(self) -> int:
        """Get target qubits as mask. **Control qubits are not included.**"""

    def control_qubit_mask(self) -> int:
        """Get control qubits as mask."""

    def operand_qubit_mask(self) -> int:
        """Get target and control qubits as mask."""

    def get_inverse(self) -> Gate:
        """Generate inverse gate as `Gate` type. If not exists, return None."""

    @overload
    def update_quantum_state(self, state_vector: StateVector) -> None:
        """
        Apply gate to `state_vector`. `state_vector` in args is directly updated.
        """

    @overload
    def update_quantum_state(self, states: StateVectorBatched) -> None:
        """Apply gate to `states`. `states` in args is directly updated."""

    def get_matrix(self) -> Annotated[ArrayLike, dict(dtype='complex128', shape=(None, None), order='C')]:
        """Get matrix representation of the gate."""

    def to_string(self) -> str:
        """Get string representation of the gate."""

    def __str__(self) -> str:
        """Get string representation of the gate."""

    def to_json(self) -> str:
        """Get JSON representation of the gate."""

    def load_json(self, json_str: str) -> None:
        """Read an object from the JSON representation of the gate."""

class ZGate:
    """
    Specific class of Pauli-Z gate.

    Notes
    	Upcast is required to use gate-general functions (ex: add to Circuit).
    """

    @overload
    def __init__(self, arg: Gate, /) -> None:
        """Downcast from Gate."""

    @overload
    def __init__(self, arg: Gate, /) -> None: ...

    def gate_type(self) -> scaluq.scaluq_core.GateType:
        """Get gate type as `GateType` enum."""

    def target_qubit_list(self) -> list[int]:
        """Get target qubits as `list[int]`. **Control qubits are not included.**"""

    def control_qubit_list(self) -> list[int]:
        """Get control qubits as `list[int]`."""

    def operand_qubit_list(self) -> list[int]:
        """Get target and control qubits as `list[int]`."""

    def target_qubit_mask(self) -> int:
        """Get target qubits as mask. **Control qubits are not included.**"""

    def control_qubit_mask(self) -> int:
        """Get control qubits as mask."""

    def operand_qubit_mask(self) -> int:
        """Get target and control qubits as mask."""

    def get_inverse(self) -> Gate:
        """Generate inverse gate as `Gate` type. If not exists, return None."""

    @overload
    def update_quantum_state(self, state_vector: StateVector) -> None:
        """
        Apply gate to `state_vector`. `state_vector` in args is directly updated.
        """

    @overload
    def update_quantum_state(self, states: StateVectorBatched) -> None:
        """Apply gate to `states`. `states` in args is directly updated."""

    def get_matrix(self) -> Annotated[ArrayLike, dict(dtype='complex128', shape=(None, None), order='C')]:
        """Get matrix representation of the gate."""

    def to_string(self) -> str:
        """Get string representation of the gate."""

    def __str__(self) -> str:
        """Get string representation of the gate."""

    def to_json(self) -> str:
        """Get JSON representation of the gate."""

    def load_json(self, json_str: str) -> None:
        """Read an object from the JSON representation of the gate."""

class HGate:
    """
    Specific class of Hadamard gate.

    Notes
    	Upcast is required to use gate-general functions (ex: add to Circuit).
    """

    @overload
    def __init__(self, arg: Gate, /) -> None:
        """Downcast from Gate."""

    @overload
    def __init__(self, arg: Gate, /) -> None: ...

    def gate_type(self) -> scaluq.scaluq_core.GateType:
        """Get gate type as `GateType` enum."""

    def target_qubit_list(self) -> list[int]:
        """Get target qubits as `list[int]`. **Control qubits are not included.**"""

    def control_qubit_list(self) -> list[int]:
        """Get control qubits as `list[int]`."""

    def operand_qubit_list(self) -> list[int]:
        """Get target and control qubits as `list[int]`."""

    def target_qubit_mask(self) -> int:
        """Get target qubits as mask. **Control qubits are not included.**"""

    def control_qubit_mask(self) -> int:
        """Get control qubits as mask."""

    def operand_qubit_mask(self) -> int:
        """Get target and control qubits as mask."""

    def get_inverse(self) -> Gate:
        """Generate inverse gate as `Gate` type. If not exists, return None."""

    @overload
    def update_quantum_state(self, state_vector: StateVector) -> None:
        """
        Apply gate to `state_vector`. `state_vector` in args is directly updated.
        """

    @overload
    def update_quantum_state(self, states: StateVectorBatched) -> None:
        """Apply gate to `states`. `states` in args is directly updated."""

    def get_matrix(self) -> Annotated[ArrayLike, dict(dtype='complex128', shape=(None, None), order='C')]:
        """Get matrix representation of the gate."""

    def to_string(self) -> str:
        """Get string representation of the gate."""

    def __str__(self) -> str:
        """Get string representation of the gate."""

    def to_json(self) -> str:
        """Get JSON representation of the gate."""

    def load_json(self, json_str: str) -> None:
        """Read an object from the JSON representation of the gate."""

class SGate:
    r"""
    Specific class of S gate, represented as $\begin{bmatrix} 1 & 0 \\ 0 & i \end{bmatrix}$.

    Notes
    	Upcast is required to use gate-general functions (ex: add to Circuit).
    """

    @overload
    def __init__(self, arg: Gate, /) -> None:
        """Downcast from Gate."""

    @overload
    def __init__(self, arg: Gate, /) -> None: ...

    def gate_type(self) -> scaluq.scaluq_core.GateType:
        """Get gate type as `GateType` enum."""

    def target_qubit_list(self) -> list[int]:
        """Get target qubits as `list[int]`. **Control qubits are not included.**"""

    def control_qubit_list(self) -> list[int]:
        """Get control qubits as `list[int]`."""

    def operand_qubit_list(self) -> list[int]:
        """Get target and control qubits as `list[int]`."""

    def target_qubit_mask(self) -> int:
        """Get target qubits as mask. **Control qubits are not included.**"""

    def control_qubit_mask(self) -> int:
        """Get control qubits as mask."""

    def operand_qubit_mask(self) -> int:
        """Get target and control qubits as mask."""

    def get_inverse(self) -> Gate:
        """Generate inverse gate as `Gate` type. If not exists, return None."""

    @overload
    def update_quantum_state(self, state_vector: StateVector) -> None:
        """
        Apply gate to `state_vector`. `state_vector` in args is directly updated.
        """

    @overload
    def update_quantum_state(self, states: StateVectorBatched) -> None:
        """Apply gate to `states`. `states` in args is directly updated."""

    def get_matrix(self) -> Annotated[ArrayLike, dict(dtype='complex128', shape=(None, None), order='C')]:
        """Get matrix representation of the gate."""

    def to_string(self) -> str:
        """Get string representation of the gate."""

    def __str__(self) -> str:
        """Get string representation of the gate."""

    def to_json(self) -> str:
        """Get JSON representation of the gate."""

    def load_json(self, json_str: str) -> None:
        """Read an object from the JSON representation of the gate."""

class SdagGate:
    """
    Specific class of inverse of S gate.

    Notes
    	Upcast is required to use gate-general functions (ex: add to Circuit).
    """

    @overload
    def __init__(self, arg: Gate, /) -> None:
        """Downcast from Gate."""

    @overload
    def __init__(self, arg: Gate, /) -> None: ...

    def gate_type(self) -> scaluq.scaluq_core.GateType:
        """Get gate type as `GateType` enum."""

    def target_qubit_list(self) -> list[int]:
        """Get target qubits as `list[int]`. **Control qubits are not included.**"""

    def control_qubit_list(self) -> list[int]:
        """Get control qubits as `list[int]`."""

    def operand_qubit_list(self) -> list[int]:
        """Get target and control qubits as `list[int]`."""

    def target_qubit_mask(self) -> int:
        """Get target qubits as mask. **Control qubits are not included.**"""

    def control_qubit_mask(self) -> int:
        """Get control qubits as mask."""

    def operand_qubit_mask(self) -> int:
        """Get target and control qubits as mask."""

    def get_inverse(self) -> Gate:
        """Generate inverse gate as `Gate` type. If not exists, return None."""

    @overload
    def update_quantum_state(self, state_vector: StateVector) -> None:
        """
        Apply gate to `state_vector`. `state_vector` in args is directly updated.
        """

    @overload
    def update_quantum_state(self, states: StateVectorBatched) -> None:
        """Apply gate to `states`. `states` in args is directly updated."""

    def get_matrix(self) -> Annotated[ArrayLike, dict(dtype='complex128', shape=(None, None), order='C')]:
        """Get matrix representation of the gate."""

    def to_string(self) -> str:
        """Get string representation of the gate."""

    def __str__(self) -> str:
        """Get string representation of the gate."""

    def to_json(self) -> str:
        """Get JSON representation of the gate."""

    def load_json(self, json_str: str) -> None:
        """Read an object from the JSON representation of the gate."""

class TGate:
    r"""
    Specific class of T gate, represented as $\begin{bmatrix} 1 & 0 \\ 0 &e^{i \pi/4} \end{bmatrix}$.

    Notes
    	Upcast is required to use gate-general functions (ex: add to Circuit).
    """

    @overload
    def __init__(self, arg: Gate, /) -> None:
        """Downcast from Gate."""

    @overload
    def __init__(self, arg: Gate, /) -> None: ...

    def gate_type(self) -> scaluq.scaluq_core.GateType:
        """Get gate type as `GateType` enum."""

    def target_qubit_list(self) -> list[int]:
        """Get target qubits as `list[int]`. **Control qubits are not included.**"""

    def control_qubit_list(self) -> list[int]:
        """Get control qubits as `list[int]`."""

    def operand_qubit_list(self) -> list[int]:
        """Get target and control qubits as `list[int]`."""

    def target_qubit_mask(self) -> int:
        """Get target qubits as mask. **Control qubits are not included.**"""

    def control_qubit_mask(self) -> int:
        """Get control qubits as mask."""

    def operand_qubit_mask(self) -> int:
        """Get target and control qubits as mask."""

    def get_inverse(self) -> Gate:
        """Generate inverse gate as `Gate` type. If not exists, return None."""

    @overload
    def update_quantum_state(self, state_vector: StateVector) -> None:
        """
        Apply gate to `state_vector`. `state_vector` in args is directly updated.
        """

    @overload
    def update_quantum_state(self, states: StateVectorBatched) -> None:
        """Apply gate to `states`. `states` in args is directly updated."""

    def get_matrix(self) -> Annotated[ArrayLike, dict(dtype='complex128', shape=(None, None), order='C')]:
        """Get matrix representation of the gate."""

    def to_string(self) -> str:
        """Get string representation of the gate."""

    def __str__(self) -> str:
        """Get string representation of the gate."""

    def to_json(self) -> str:
        """Get JSON representation of the gate."""

    def load_json(self, json_str: str) -> None:
        """Read an object from the JSON representation of the gate."""

class TdagGate:
    """
    Specific class of inverse of T gate.

    Notes
    	Upcast is required to use gate-general functions (ex: add to Circuit).
    """

    @overload
    def __init__(self, arg: Gate, /) -> None:
        """Downcast from Gate."""

    @overload
    def __init__(self, arg: Gate, /) -> None: ...

    def gate_type(self) -> scaluq.scaluq_core.GateType:
        """Get gate type as `GateType` enum."""

    def target_qubit_list(self) -> list[int]:
        """Get target qubits as `list[int]`. **Control qubits are not included.**"""

    def control_qubit_list(self) -> list[int]:
        """Get control qubits as `list[int]`."""

    def operand_qubit_list(self) -> list[int]:
        """Get target and control qubits as `list[int]`."""

    def target_qubit_mask(self) -> int:
        """Get target qubits as mask. **Control qubits are not included.**"""

    def control_qubit_mask(self) -> int:
        """Get control qubits as mask."""

    def operand_qubit_mask(self) -> int:
        """Get target and control qubits as mask."""

    def get_inverse(self) -> Gate:
        """Generate inverse gate as `Gate` type. If not exists, return None."""

    @overload
    def update_quantum_state(self, state_vector: StateVector) -> None:
        """
        Apply gate to `state_vector`. `state_vector` in args is directly updated.
        """

    @overload
    def update_quantum_state(self, states: StateVectorBatched) -> None:
        """Apply gate to `states`. `states` in args is directly updated."""

    def get_matrix(self) -> Annotated[ArrayLike, dict(dtype='complex128', shape=(None, None), order='C')]:
        """Get matrix representation of the gate."""

    def to_string(self) -> str:
        """Get string representation of the gate."""

    def __str__(self) -> str:
        """Get string representation of the gate."""

    def to_json(self) -> str:
        """Get JSON representation of the gate."""

    def load_json(self, json_str: str) -> None:
        """Read an object from the JSON representation of the gate."""

class SqrtXGate:
    r"""
    Specific class of sqrt(X) gate, represented as $\frac{1}{\sqrt{2}} \begin{bmatrix} 1+i & 1-i\\ 1-i & 1+i \end{bmatrix}$.

    Notes
    	Upcast is required to use gate-general functions (ex: add to Circuit).
    """

    @overload
    def __init__(self, arg: Gate, /) -> None:
        """Downcast from Gate."""

    @overload
    def __init__(self, arg: Gate, /) -> None: ...

    def gate_type(self) -> scaluq.scaluq_core.GateType:
        """Get gate type as `GateType` enum."""

    def target_qubit_list(self) -> list[int]:
        """Get target qubits as `list[int]`. **Control qubits are not included.**"""

    def control_qubit_list(self) -> list[int]:
        """Get control qubits as `list[int]`."""

    def operand_qubit_list(self) -> list[int]:
        """Get target and control qubits as `list[int]`."""

    def target_qubit_mask(self) -> int:
        """Get target qubits as mask. **Control qubits are not included.**"""

    def control_qubit_mask(self) -> int:
        """Get control qubits as mask."""

    def operand_qubit_mask(self) -> int:
        """Get target and control qubits as mask."""

    def get_inverse(self) -> Gate:
        """Generate inverse gate as `Gate` type. If not exists, return None."""

    @overload
    def update_quantum_state(self, state_vector: StateVector) -> None:
        """
        Apply gate to `state_vector`. `state_vector` in args is directly updated.
        """

    @overload
    def update_quantum_state(self, states: StateVectorBatched) -> None:
        """Apply gate to `states`. `states` in args is directly updated."""

    def get_matrix(self) -> Annotated[ArrayLike, dict(dtype='complex128', shape=(None, None), order='C')]:
        """Get matrix representation of the gate."""

    def to_string(self) -> str:
        """Get string representation of the gate."""

    def __str__(self) -> str:
        """Get string representation of the gate."""

    def to_json(self) -> str:
        """Get JSON representation of the gate."""

    def load_json(self, json_str: str) -> None:
        """Read an object from the JSON representation of the gate."""

class SqrtXdagGate:
    r"""
    Specific class of inverse of sqrt(X) gate, represented as $\frac{1}{\sqrt{2}} \begin{bmatrix} 1-i & 1+i\\ 1+i & 1-i \end{bmatrix}$.

    Notes
    	Upcast is required to use gate-general functions (ex: add to Circuit).
    """

    @overload
    def __init__(self, arg: Gate, /) -> None:
        """Downcast from Gate."""

    @overload
    def __init__(self, arg: Gate, /) -> None: ...

    def gate_type(self) -> scaluq.scaluq_core.GateType:
        """Get gate type as `GateType` enum."""

    def target_qubit_list(self) -> list[int]:
        """Get target qubits as `list[int]`. **Control qubits are not included.**"""

    def control_qubit_list(self) -> list[int]:
        """Get control qubits as `list[int]`."""

    def operand_qubit_list(self) -> list[int]:
        """Get target and control qubits as `list[int]`."""

    def target_qubit_mask(self) -> int:
        """Get target qubits as mask. **Control qubits are not included.**"""

    def control_qubit_mask(self) -> int:
        """Get control qubits as mask."""

    def operand_qubit_mask(self) -> int:
        """Get target and control qubits as mask."""

    def get_inverse(self) -> Gate:
        """Generate inverse gate as `Gate` type. If not exists, return None."""

    @overload
    def update_quantum_state(self, state_vector: StateVector) -> None:
        """
        Apply gate to `state_vector`. `state_vector` in args is directly updated.
        """

    @overload
    def update_quantum_state(self, states: StateVectorBatched) -> None:
        """Apply gate to `states`. `states` in args is directly updated."""

    def get_matrix(self) -> Annotated[ArrayLike, dict(dtype='complex128', shape=(None, None), order='C')]:
        """Get matrix representation of the gate."""

    def to_string(self) -> str:
        """Get string representation of the gate."""

    def __str__(self) -> str:
        """Get string representation of the gate."""

    def to_json(self) -> str:
        """Get JSON representation of the gate."""

    def load_json(self, json_str: str) -> None:
        """Read an object from the JSON representation of the gate."""

class SqrtYGate:
    r"""
    Specific class of sqrt(Y) gate, represented as $\frac{1}{\sqrt{2}} \begin{bmatrix} 1+i & -1-i \\ 1+i & 1+i \end{bmatrix}$.

    Notes
    	Upcast is required to use gate-general functions (ex: add to Circuit).
    """

    @overload
    def __init__(self, arg: Gate, /) -> None:
        """Downcast from Gate."""

    @overload
    def __init__(self, arg: Gate, /) -> None: ...

    def gate_type(self) -> scaluq.scaluq_core.GateType:
        """Get gate type as `GateType` enum."""

    def target_qubit_list(self) -> list[int]:
        """Get target qubits as `list[int]`. **Control qubits are not included.**"""

    def control_qubit_list(self) -> list[int]:
        """Get control qubits as `list[int]`."""

    def operand_qubit_list(self) -> list[int]:
        """Get target and control qubits as `list[int]`."""

    def target_qubit_mask(self) -> int:
        """Get target qubits as mask. **Control qubits are not included.**"""

    def control_qubit_mask(self) -> int:
        """Get control qubits as mask."""

    def operand_qubit_mask(self) -> int:
        """Get target and control qubits as mask."""

    def get_inverse(self) -> Gate:
        """Generate inverse gate as `Gate` type. If not exists, return None."""

    @overload
    def update_quantum_state(self, state_vector: StateVector) -> None:
        """
        Apply gate to `state_vector`. `state_vector` in args is directly updated.
        """

    @overload
    def update_quantum_state(self, states: StateVectorBatched) -> None:
        """Apply gate to `states`. `states` in args is directly updated."""

    def get_matrix(self) -> Annotated[ArrayLike, dict(dtype='complex128', shape=(None, None), order='C')]:
        """Get matrix representation of the gate."""

    def to_string(self) -> str:
        """Get string representation of the gate."""

    def __str__(self) -> str:
        """Get string representation of the gate."""

    def to_json(self) -> str:
        """Get JSON representation of the gate."""

    def load_json(self, json_str: str) -> None:
        """Read an object from the JSON representation of the gate."""

class SqrtYdagGate:
    r"""
    Specific class of inverse of sqrt(Y) gate, represented as $\frac{1}{\sqrt{2}} \begin{bmatrix} 1-i & 1-i\\ -1+i & 1-i \end{bmatrix}$.

    Notes
    	Upcast is required to use gate-general functions (ex: add to Circuit).
    """

    @overload
    def __init__(self, arg: Gate, /) -> None:
        """Downcast from Gate."""

    @overload
    def __init__(self, arg: Gate, /) -> None: ...

    def gate_type(self) -> scaluq.scaluq_core.GateType:
        """Get gate type as `GateType` enum."""

    def target_qubit_list(self) -> list[int]:
        """Get target qubits as `list[int]`. **Control qubits are not included.**"""

    def control_qubit_list(self) -> list[int]:
        """Get control qubits as `list[int]`."""

    def operand_qubit_list(self) -> list[int]:
        """Get target and control qubits as `list[int]`."""

    def target_qubit_mask(self) -> int:
        """Get target qubits as mask. **Control qubits are not included.**"""

    def control_qubit_mask(self) -> int:
        """Get control qubits as mask."""

    def operand_qubit_mask(self) -> int:
        """Get target and control qubits as mask."""

    def get_inverse(self) -> Gate:
        """Generate inverse gate as `Gate` type. If not exists, return None."""

    @overload
    def update_quantum_state(self, state_vector: StateVector) -> None:
        """
        Apply gate to `state_vector`. `state_vector` in args is directly updated.
        """

    @overload
    def update_quantum_state(self, states: StateVectorBatched) -> None:
        """Apply gate to `states`. `states` in args is directly updated."""

    def get_matrix(self) -> Annotated[ArrayLike, dict(dtype='complex128', shape=(None, None), order='C')]:
        """Get matrix representation of the gate."""

    def to_string(self) -> str:
        """Get string representation of the gate."""

    def __str__(self) -> str:
        """Get string representation of the gate."""

    def to_json(self) -> str:
        """Get JSON representation of the gate."""

    def load_json(self, json_str: str) -> None:
        """Read an object from the JSON representation of the gate."""

class P0Gate:
    r"""
    Specific class of projection gate to $\ket{0}$.

    Notes:
    	This gate is not unitary.

    Notes
    	Upcast is required to use gate-general functions (ex: add to Circuit).
    """

    @overload
    def __init__(self, arg: Gate, /) -> None:
        """Downcast from Gate."""

    @overload
    def __init__(self, arg: Gate, /) -> None: ...

    def gate_type(self) -> scaluq.scaluq_core.GateType:
        """Get gate type as `GateType` enum."""

    def target_qubit_list(self) -> list[int]:
        """Get target qubits as `list[int]`. **Control qubits are not included.**"""

    def control_qubit_list(self) -> list[int]:
        """Get control qubits as `list[int]`."""

    def operand_qubit_list(self) -> list[int]:
        """Get target and control qubits as `list[int]`."""

    def target_qubit_mask(self) -> int:
        """Get target qubits as mask. **Control qubits are not included.**"""

    def control_qubit_mask(self) -> int:
        """Get control qubits as mask."""

    def operand_qubit_mask(self) -> int:
        """Get target and control qubits as mask."""

    def get_inverse(self) -> Gate:
        """Generate inverse gate as `Gate` type. If not exists, return None."""

    @overload
    def update_quantum_state(self, state_vector: StateVector) -> None:
        """
        Apply gate to `state_vector`. `state_vector` in args is directly updated.
        """

    @overload
    def update_quantum_state(self, states: StateVectorBatched) -> None:
        """Apply gate to `states`. `states` in args is directly updated."""

    def get_matrix(self) -> Annotated[ArrayLike, dict(dtype='complex128', shape=(None, None), order='C')]:
        """Get matrix representation of the gate."""

    def to_string(self) -> str:
        """Get string representation of the gate."""

    def __str__(self) -> str:
        """Get string representation of the gate."""

    def to_json(self) -> str:
        """Get JSON representation of the gate."""

    def load_json(self, json_str: str) -> None:
        """Read an object from the JSON representation of the gate."""

class P1Gate:
    r"""
    Specific class of projection gate to $\ket{1}$.

    Notes:
    	This gate is not unitary.

    Notes
    	Upcast is required to use gate-general functions (ex: add to Circuit).
    """

    @overload
    def __init__(self, arg: Gate, /) -> None:
        """Downcast from Gate."""

    @overload
    def __init__(self, arg: Gate, /) -> None: ...

    def gate_type(self) -> scaluq.scaluq_core.GateType:
        """Get gate type as `GateType` enum."""

    def target_qubit_list(self) -> list[int]:
        """Get target qubits as `list[int]`. **Control qubits are not included.**"""

    def control_qubit_list(self) -> list[int]:
        """Get control qubits as `list[int]`."""

    def operand_qubit_list(self) -> list[int]:
        """Get target and control qubits as `list[int]`."""

    def target_qubit_mask(self) -> int:
        """Get target qubits as mask. **Control qubits are not included.**"""

    def control_qubit_mask(self) -> int:
        """Get control qubits as mask."""

    def operand_qubit_mask(self) -> int:
        """Get target and control qubits as mask."""

    def get_inverse(self) -> Gate:
        """Generate inverse gate as `Gate` type. If not exists, return None."""

    @overload
    def update_quantum_state(self, state_vector: StateVector) -> None:
        """
        Apply gate to `state_vector`. `state_vector` in args is directly updated.
        """

    @overload
    def update_quantum_state(self, states: StateVectorBatched) -> None:
        """Apply gate to `states`. `states` in args is directly updated."""

    def get_matrix(self) -> Annotated[ArrayLike, dict(dtype='complex128', shape=(None, None), order='C')]:
        """Get matrix representation of the gate."""

    def to_string(self) -> str:
        """Get string representation of the gate."""

    def __str__(self) -> str:
        """Get string representation of the gate."""

    def to_json(self) -> str:
        """Get JSON representation of the gate."""

    def load_json(self, json_str: str) -> None:
        """Read an object from the JSON representation of the gate."""

class RXGate:
    r"""
    Specific class of X rotation gate, represented as $e^{-i\frac{\theta}{2}X}$.

    Notes
    	Upcast is required to use gate-general functions (ex: add to Circuit).
    """

    @overload
    def __init__(self, arg: Gate, /) -> None:
        """Downcast from Gate."""

    @overload
    def __init__(self, arg: Gate, /) -> None: ...

    def gate_type(self) -> scaluq.scaluq_core.GateType:
        """Get gate type as `GateType` enum."""

    def target_qubit_list(self) -> list[int]:
        """Get target qubits as `list[int]`. **Control qubits are not included.**"""

    def control_qubit_list(self) -> list[int]:
        """Get control qubits as `list[int]`."""

    def operand_qubit_list(self) -> list[int]:
        """Get target and control qubits as `list[int]`."""

    def target_qubit_mask(self) -> int:
        """Get target qubits as mask. **Control qubits are not included.**"""

    def control_qubit_mask(self) -> int:
        """Get control qubits as mask."""

    def operand_qubit_mask(self) -> int:
        """Get target and control qubits as mask."""

    def get_inverse(self) -> Gate:
        """Generate inverse gate as `Gate` type. If not exists, return None."""

    @overload
    def update_quantum_state(self, state_vector: StateVector) -> None:
        """
        Apply gate to `state_vector`. `state_vector` in args is directly updated.
        """

    @overload
    def update_quantum_state(self, states: StateVectorBatched) -> None:
        """Apply gate to `states`. `states` in args is directly updated."""

    def get_matrix(self) -> Annotated[ArrayLike, dict(dtype='complex128', shape=(None, None), order='C')]:
        """Get matrix representation of the gate."""

    def to_string(self) -> str:
        """Get string representation of the gate."""

    def __str__(self) -> str:
        """Get string representation of the gate."""

    def to_json(self) -> str:
        """Get JSON representation of the gate."""

    def load_json(self, json_str: str) -> None:
        """Read an object from the JSON representation of the gate."""

    def angle(self) -> float:
        """Get `angle` property."""

class RYGate:
    r"""
    Specific class of Y rotation gate, represented as $e^{-i\frac{\theta}{2}Y}$.

    Notes
    	Upcast is required to use gate-general functions (ex: add to Circuit).
    """

    @overload
    def __init__(self, arg: Gate, /) -> None:
        """Downcast from Gate."""

    @overload
    def __init__(self, arg: Gate, /) -> None: ...

    def gate_type(self) -> scaluq.scaluq_core.GateType:
        """Get gate type as `GateType` enum."""

    def target_qubit_list(self) -> list[int]:
        """Get target qubits as `list[int]`. **Control qubits are not included.**"""

    def control_qubit_list(self) -> list[int]:
        """Get control qubits as `list[int]`."""

    def operand_qubit_list(self) -> list[int]:
        """Get target and control qubits as `list[int]`."""

    def target_qubit_mask(self) -> int:
        """Get target qubits as mask. **Control qubits are not included.**"""

    def control_qubit_mask(self) -> int:
        """Get control qubits as mask."""

    def operand_qubit_mask(self) -> int:
        """Get target and control qubits as mask."""

    def get_inverse(self) -> Gate:
        """Generate inverse gate as `Gate` type. If not exists, return None."""

    @overload
    def update_quantum_state(self, state_vector: StateVector) -> None:
        """
        Apply gate to `state_vector`. `state_vector` in args is directly updated.
        """

    @overload
    def update_quantum_state(self, states: StateVectorBatched) -> None:
        """Apply gate to `states`. `states` in args is directly updated."""

    def get_matrix(self) -> Annotated[ArrayLike, dict(dtype='complex128', shape=(None, None), order='C')]:
        """Get matrix representation of the gate."""

    def to_string(self) -> str:
        """Get string representation of the gate."""

    def __str__(self) -> str:
        """Get string representation of the gate."""

    def to_json(self) -> str:
        """Get JSON representation of the gate."""

    def load_json(self, json_str: str) -> None:
        """Read an object from the JSON representation of the gate."""

    def angle(self) -> float:
        """Get `angle` property."""

class RZGate:
    r"""
    Specific class of Z rotation gate, represented as $e^{-i\frac{\theta}{2}Z}$.

    Notes
    	Upcast is required to use gate-general functions (ex: add to Circuit).
    """

    @overload
    def __init__(self, arg: Gate, /) -> None:
        """Downcast from Gate."""

    @overload
    def __init__(self, arg: Gate, /) -> None: ...

    def gate_type(self) -> scaluq.scaluq_core.GateType:
        """Get gate type as `GateType` enum."""

    def target_qubit_list(self) -> list[int]:
        """Get target qubits as `list[int]`. **Control qubits are not included.**"""

    def control_qubit_list(self) -> list[int]:
        """Get control qubits as `list[int]`."""

    def operand_qubit_list(self) -> list[int]:
        """Get target and control qubits as `list[int]`."""

    def target_qubit_mask(self) -> int:
        """Get target qubits as mask. **Control qubits are not included.**"""

    def control_qubit_mask(self) -> int:
        """Get control qubits as mask."""

    def operand_qubit_mask(self) -> int:
        """Get target and control qubits as mask."""

    def get_inverse(self) -> Gate:
        """Generate inverse gate as `Gate` type. If not exists, return None."""

    @overload
    def update_quantum_state(self, state_vector: StateVector) -> None:
        """
        Apply gate to `state_vector`. `state_vector` in args is directly updated.
        """

    @overload
    def update_quantum_state(self, states: StateVectorBatched) -> None:
        """Apply gate to `states`. `states` in args is directly updated."""

    def get_matrix(self) -> Annotated[ArrayLike, dict(dtype='complex128', shape=(None, None), order='C')]:
        """Get matrix representation of the gate."""

    def to_string(self) -> str:
        """Get string representation of the gate."""

    def __str__(self) -> str:
        """Get string representation of the gate."""

    def to_json(self) -> str:
        """Get JSON representation of the gate."""

    def load_json(self, json_str: str) -> None:
        """Read an object from the JSON representation of the gate."""

    def angle(self) -> float:
        """Get `angle` property."""

class U1Gate:
    r"""
    Specific class of IBMQ's U1 Gate, which is a rotation about Z-axis, represented as $\begin{bmatrix} 1 & 0 \\ 0 & e^{i\lambda} \end{bmatrix}$.

    Notes
    	Upcast is required to use gate-general functions (ex: add to Circuit).
    """

    @overload
    def __init__(self, arg: Gate, /) -> None:
        """Downcast from Gate."""

    @overload
    def __init__(self, arg: Gate, /) -> None: ...

    def gate_type(self) -> scaluq.scaluq_core.GateType:
        """Get gate type as `GateType` enum."""

    def target_qubit_list(self) -> list[int]:
        """Get target qubits as `list[int]`. **Control qubits are not included.**"""

    def control_qubit_list(self) -> list[int]:
        """Get control qubits as `list[int]`."""

    def operand_qubit_list(self) -> list[int]:
        """Get target and control qubits as `list[int]`."""

    def target_qubit_mask(self) -> int:
        """Get target qubits as mask. **Control qubits are not included.**"""

    def control_qubit_mask(self) -> int:
        """Get control qubits as mask."""

    def operand_qubit_mask(self) -> int:
        """Get target and control qubits as mask."""

    def get_inverse(self) -> Gate:
        """Generate inverse gate as `Gate` type. If not exists, return None."""

    @overload
    def update_quantum_state(self, state_vector: StateVector) -> None:
        """
        Apply gate to `state_vector`. `state_vector` in args is directly updated.
        """

    @overload
    def update_quantum_state(self, states: StateVectorBatched) -> None:
        """Apply gate to `states`. `states` in args is directly updated."""

    def get_matrix(self) -> Annotated[ArrayLike, dict(dtype='complex128', shape=(None, None), order='C')]:
        """Get matrix representation of the gate."""

    def to_string(self) -> str:
        """Get string representation of the gate."""

    def __str__(self) -> str:
        """Get string representation of the gate."""

    def to_json(self) -> str:
        """Get JSON representation of the gate."""

    def load_json(self, json_str: str) -> None:
        """Read an object from the JSON representation of the gate."""

class U2Gate:
    r"""
    Specific class of IBMQ's U2 Gate, which is a rotation about X+Z-axis, represented as $\frac{1}{\sqrt{2}} \begin{bmatrix}1 & -e^{-i\lambda}\\ e^{i\phi} & e^{i(\phi+\lambda)} \end{bmatrix}$.

    Notes
    	Upcast is required to use gate-general functions (ex: add to Circuit).
    """

    @overload
    def __init__(self, arg: Gate, /) -> None:
        """Downcast from Gate."""

    @overload
    def __init__(self, arg: Gate, /) -> None: ...

    def gate_type(self) -> scaluq.scaluq_core.GateType:
        """Get gate type as `GateType` enum."""

    def target_qubit_list(self) -> list[int]:
        """Get target qubits as `list[int]`. **Control qubits are not included.**"""

    def control_qubit_list(self) -> list[int]:
        """Get control qubits as `list[int]`."""

    def operand_qubit_list(self) -> list[int]:
        """Get target and control qubits as `list[int]`."""

    def target_qubit_mask(self) -> int:
        """Get target qubits as mask. **Control qubits are not included.**"""

    def control_qubit_mask(self) -> int:
        """Get control qubits as mask."""

    def operand_qubit_mask(self) -> int:
        """Get target and control qubits as mask."""

    def get_inverse(self) -> Gate:
        """Generate inverse gate as `Gate` type. If not exists, return None."""

    @overload
    def update_quantum_state(self, state_vector: StateVector) -> None:
        """
        Apply gate to `state_vector`. `state_vector` in args is directly updated.
        """

    @overload
    def update_quantum_state(self, states: StateVectorBatched) -> None:
        """Apply gate to `states`. `states` in args is directly updated."""

    def get_matrix(self) -> Annotated[ArrayLike, dict(dtype='complex128', shape=(None, None), order='C')]:
        """Get matrix representation of the gate."""

    def to_string(self) -> str:
        """Get string representation of the gate."""

    def __str__(self) -> str:
        """Get string representation of the gate."""

    def to_json(self) -> str:
        """Get JSON representation of the gate."""

    def load_json(self, json_str: str) -> None:
        """Read an object from the JSON representation of the gate."""

    def phi(self) -> float:
        """Get `phi` property."""

class U3Gate:
    r"""
    Specific class of IBMQ's U3 Gate, which is a rotation about 3 axis, represented as $\begin{bmatrix} \cos \frac{\theta}{2} & -e^{i\lambda}\sin\frac{\theta}{2}\\ e^{i\phi}\sin\frac{\theta}{2} & e^{i(\phi+\lambda)}\cos\frac{\theta}{2} \end{bmatrix}$.

    Notes
    	Upcast is required to use gate-general functions (ex: add to Circuit).
    """

    @overload
    def __init__(self, arg: Gate, /) -> None:
        """Downcast from Gate."""

    @overload
    def __init__(self, arg: Gate, /) -> None: ...

    def gate_type(self) -> scaluq.scaluq_core.GateType:
        """Get gate type as `GateType` enum."""

    def target_qubit_list(self) -> list[int]:
        """Get target qubits as `list[int]`. **Control qubits are not included.**"""

    def control_qubit_list(self) -> list[int]:
        """Get control qubits as `list[int]`."""

    def operand_qubit_list(self) -> list[int]:
        """Get target and control qubits as `list[int]`."""

    def target_qubit_mask(self) -> int:
        """Get target qubits as mask. **Control qubits are not included.**"""

    def control_qubit_mask(self) -> int:
        """Get control qubits as mask."""

    def operand_qubit_mask(self) -> int:
        """Get target and control qubits as mask."""

    def get_inverse(self) -> Gate:
        """Generate inverse gate as `Gate` type. If not exists, return None."""

    @overload
    def update_quantum_state(self, state_vector: StateVector) -> None:
        """
        Apply gate to `state_vector`. `state_vector` in args is directly updated.
        """

    @overload
    def update_quantum_state(self, states: StateVectorBatched) -> None:
        """Apply gate to `states`. `states` in args is directly updated."""

    def get_matrix(self) -> Annotated[ArrayLike, dict(dtype='complex128', shape=(None, None), order='C')]:
        """Get matrix representation of the gate."""

    def to_string(self) -> str:
        """Get string representation of the gate."""

    def __str__(self) -> str:
        """Get string representation of the gate."""

    def to_json(self) -> str:
        """Get JSON representation of the gate."""

    def load_json(self, json_str: str) -> None:
        """Read an object from the JSON representation of the gate."""

    def theta(self) -> float:
        """Get `theta` property."""

    def phi(self) -> float:
        """Get `phi` property."""

class SwapGate:
    """
    Specific class of two-qubit swap gate.

    Notes
    	Upcast is required to use gate-general functions (ex: add to Circuit).
    """

    @overload
    def __init__(self, arg: Gate, /) -> None:
        """Downcast from Gate."""

    @overload
    def __init__(self, arg: Gate, /) -> None: ...

    def gate_type(self) -> scaluq.scaluq_core.GateType:
        """Get gate type as `GateType` enum."""

    def target_qubit_list(self) -> list[int]:
        """Get target qubits as `list[int]`. **Control qubits are not included.**"""

    def control_qubit_list(self) -> list[int]:
        """Get control qubits as `list[int]`."""

    def operand_qubit_list(self) -> list[int]:
        """Get target and control qubits as `list[int]`."""

    def target_qubit_mask(self) -> int:
        """Get target qubits as mask. **Control qubits are not included.**"""

    def control_qubit_mask(self) -> int:
        """Get control qubits as mask."""

    def operand_qubit_mask(self) -> int:
        """Get target and control qubits as mask."""

    def get_inverse(self) -> Gate:
        """Generate inverse gate as `Gate` type. If not exists, return None."""

    @overload
    def update_quantum_state(self, state_vector: StateVector) -> None:
        """
        Apply gate to `state_vector`. `state_vector` in args is directly updated.
        """

    @overload
    def update_quantum_state(self, states: StateVectorBatched) -> None:
        """Apply gate to `states`. `states` in args is directly updated."""

    def get_matrix(self) -> Annotated[ArrayLike, dict(dtype='complex128', shape=(None, None), order='C')]:
        """Get matrix representation of the gate."""

    def to_string(self) -> str:
        """Get string representation of the gate."""

    def __str__(self) -> str:
        """Get string representation of the gate."""

    def to_json(self) -> str:
        """Get JSON representation of the gate."""

    def load_json(self, json_str: str) -> None:
        """Read an object from the JSON representation of the gate."""

class SparseMatrixGate:
    """
    Specific class of sparse matrix gate.

    Notes
    	Upcast is required to use gate-general functions (ex: add to Circuit).
    """

    @overload
    def __init__(self, arg: Gate, /) -> None:
        """Downcast from Gate."""

    @overload
    def __init__(self, arg: Gate, /) -> None: ...

    def gate_type(self) -> scaluq.scaluq_core.GateType:
        """Get gate type as `GateType` enum."""

    def target_qubit_list(self) -> list[int]:
        """Get target qubits as `list[int]`. **Control qubits are not included.**"""

    def control_qubit_list(self) -> list[int]:
        """Get control qubits as `list[int]`."""

    def operand_qubit_list(self) -> list[int]:
        """Get target and control qubits as `list[int]`."""

    def target_qubit_mask(self) -> int:
        """Get target qubits as mask. **Control qubits are not included.**"""

    def control_qubit_mask(self) -> int:
        """Get control qubits as mask."""

    def operand_qubit_mask(self) -> int:
        """Get target and control qubits as mask."""

    def get_inverse(self) -> Gate:
        """Generate inverse gate as `Gate` type. If not exists, return None."""

    @overload
    def update_quantum_state(self, state_vector: StateVector) -> None:
        """
        Apply gate to `state_vector`. `state_vector` in args is directly updated.
        """

    @overload
    def update_quantum_state(self, states: StateVectorBatched) -> None:
        """Apply gate to `states`. `states` in args is directly updated."""

    def get_matrix(self) -> Annotated[ArrayLike, dict(dtype='complex128', shape=(None, None), order='C')]:
        """Get matrix representation of the gate."""

    def to_string(self) -> str:
        """Get string representation of the gate."""

    def __str__(self) -> str:
        """Get string representation of the gate."""

    def to_json(self) -> str:
        """Get JSON representation of the gate."""

    def load_json(self, json_str: str) -> None:
        """Read an object from the JSON representation of the gate."""

    def matrix(self) -> Annotated[ArrayLike, dict(dtype='complex128', shape=(None, None), order='C')]: ...

    def sparse_matrix(self) -> scipy.sparse.csr_matrix[complex]: ...

class DenseMatrixGate:
    """
    Specific class of dense matrix gate.

    Notes
    	Upcast is required to use gate-general functions (ex: add to Circuit).
    """

    @overload
    def __init__(self, arg: Gate, /) -> None:
        """Downcast from Gate."""

    @overload
    def __init__(self, arg: Gate, /) -> None: ...

    def gate_type(self) -> scaluq.scaluq_core.GateType:
        """Get gate type as `GateType` enum."""

    def target_qubit_list(self) -> list[int]:
        """Get target qubits as `list[int]`. **Control qubits are not included.**"""

    def control_qubit_list(self) -> list[int]:
        """Get control qubits as `list[int]`."""

    def operand_qubit_list(self) -> list[int]:
        """Get target and control qubits as `list[int]`."""

    def target_qubit_mask(self) -> int:
        """Get target qubits as mask. **Control qubits are not included.**"""

    def control_qubit_mask(self) -> int:
        """Get control qubits as mask."""

    def operand_qubit_mask(self) -> int:
        """Get target and control qubits as mask."""

    def get_inverse(self) -> Gate:
        """Generate inverse gate as `Gate` type. If not exists, return None."""

    @overload
    def update_quantum_state(self, state_vector: StateVector) -> None:
        """
        Apply gate to `state_vector`. `state_vector` in args is directly updated.
        """

    @overload
    def update_quantum_state(self, states: StateVectorBatched) -> None:
        """Apply gate to `states`. `states` in args is directly updated."""

    def get_matrix(self) -> Annotated[ArrayLike, dict(dtype='complex128', shape=(None, None), order='C')]:
        """Get matrix representation of the gate."""

    def to_string(self) -> str:
        """Get string representation of the gate."""

    def __str__(self) -> str:
        """Get string representation of the gate."""

    def to_json(self) -> str:
        """Get JSON representation of the gate."""

    def load_json(self, json_str: str) -> None:
        """Read an object from the JSON representation of the gate."""

    def matrix(self) -> Annotated[ArrayLike, dict(dtype='complex128', shape=(None, None), order='C')]: ...

class PauliGate:
    """
    Specific class of multi-qubit pauli gate, which applies single-qubit Pauli gate to each of qubit.

    Notes
    	Upcast is required to use gate-general functions (ex: add to Circuit).
    """

    @overload
    def __init__(self, arg: Gate, /) -> None:
        """Downcast from Gate."""

    @overload
    def __init__(self, arg: Gate, /) -> None: ...

    def gate_type(self) -> scaluq.scaluq_core.GateType:
        """Get gate type as `GateType` enum."""

    def target_qubit_list(self) -> list[int]:
        """Get target qubits as `list[int]`. **Control qubits are not included.**"""

    def control_qubit_list(self) -> list[int]:
        """Get control qubits as `list[int]`."""

    def operand_qubit_list(self) -> list[int]:
        """Get target and control qubits as `list[int]`."""

    def target_qubit_mask(self) -> int:
        """Get target qubits as mask. **Control qubits are not included.**"""

    def control_qubit_mask(self) -> int:
        """Get control qubits as mask."""

    def operand_qubit_mask(self) -> int:
        """Get target and control qubits as mask."""

    def get_inverse(self) -> Gate:
        """Generate inverse gate as `Gate` type. If not exists, return None."""

    @overload
    def update_quantum_state(self, state_vector: StateVector) -> None:
        """
        Apply gate to `state_vector`. `state_vector` in args is directly updated.
        """

    @overload
    def update_quantum_state(self, states: StateVectorBatched) -> None:
        """Apply gate to `states`. `states` in args is directly updated."""

    def get_matrix(self) -> Annotated[ArrayLike, dict(dtype='complex128', shape=(None, None), order='C')]:
        """Get matrix representation of the gate."""

    def to_string(self) -> str:
        """Get string representation of the gate."""

    def __str__(self) -> str:
        """Get string representation of the gate."""

    def to_json(self) -> str:
        """Get JSON representation of the gate."""

    def load_json(self, json_str: str) -> None:
        """Read an object from the JSON representation of the gate."""

class PauliRotationGate:
    r"""
    Specific class of multi-qubit pauli-rotation gate, represented as $e^{-i\frac{\theta}{2}P}$.

    Notes
    	Upcast is required to use gate-general functions (ex: add to Circuit).
    """

    @overload
    def __init__(self, arg: Gate, /) -> None:
        """Downcast from Gate."""

    @overload
    def __init__(self, arg: Gate, /) -> None: ...

    def gate_type(self) -> scaluq.scaluq_core.GateType:
        """Get gate type as `GateType` enum."""

    def target_qubit_list(self) -> list[int]:
        """Get target qubits as `list[int]`. **Control qubits are not included.**"""

    def control_qubit_list(self) -> list[int]:
        """Get control qubits as `list[int]`."""

    def operand_qubit_list(self) -> list[int]:
        """Get target and control qubits as `list[int]`."""

    def target_qubit_mask(self) -> int:
        """Get target qubits as mask. **Control qubits are not included.**"""

    def control_qubit_mask(self) -> int:
        """Get control qubits as mask."""

    def operand_qubit_mask(self) -> int:
        """Get target and control qubits as mask."""

    def get_inverse(self) -> Gate:
        """Generate inverse gate as `Gate` type. If not exists, return None."""

    @overload
    def update_quantum_state(self, state_vector: StateVector) -> None:
        """
        Apply gate to `state_vector`. `state_vector` in args is directly updated.
        """

    @overload
    def update_quantum_state(self, states: StateVectorBatched) -> None:
        """Apply gate to `states`. `states` in args is directly updated."""

    def get_matrix(self) -> Annotated[ArrayLike, dict(dtype='complex128', shape=(None, None), order='C')]:
        """Get matrix representation of the gate."""

    def to_string(self) -> str:
        """Get string representation of the gate."""

    def __str__(self) -> str:
        """Get string representation of the gate."""

    def to_json(self) -> str:
        """Get JSON representation of the gate."""

    def load_json(self, json_str: str) -> None:
        """Read an object from the JSON representation of the gate."""

class ParamGate:
    """
    General class of parametric quantum gate.

    Notes:
    	Downcast to required to use gate-specific functions.
    """

    @overload
    def __init__(self, arg: ParamGate) -> None:
        """Downcast from ParamGate."""

    @overload
    def __init__(self, arg: ParamGate) -> None:
        """Just copy shallowly."""

    @overload
    def __init__(self, param_gate: ParamRXGate) -> None:
        """Upcast from `ParamRXGate`."""

    @overload
    def __init__(self, param_gate: ParamRYGate) -> None:
        """Upcast from `ParamRYGate`."""

    @overload
    def __init__(self, param_gate: ParamRZGate) -> None:
        """Upcast from `ParamRZGate`."""

    @overload
    def __init__(self, param_gate: ParamPauliRotationGate) -> None:
        """Upcast from `ParamPauliRotationGate`."""

    @overload
    def __init__(self, param_gate: ParamProbabilisticGate) -> None:
        """Upcast from `ParamProbabilisticGate`."""

    def param_gate_type(self) -> scaluq.scaluq_core.ParamGateType:
        """Get parametric gate type as `ParamGateType` enum."""

    def param_coef(self) -> float:
        """Get coefficient of parameter."""

    def target_qubit_list(self) -> list[int]:
        """Get target qubits as `list[int]`. **Control qubits is not included.**"""

    def control_qubit_list(self) -> list[int]:
        """Get control qubits as `list[int]`."""

    def operand_qubit_list(self) -> list[int]:
        """Get target and control qubits as `list[int]`."""

    def target_qubit_mask(self) -> int:
        """Get target qubits as mask. **Control qubits is not included.**"""

    def control_qubit_mask(self) -> int:
        """Get control qubits as mask."""

    def operand_qubit_mask(self) -> int:
        """Get target and control qubits as mask."""

    def get_inverse(self) -> ParamGate:
        """
        Generate inverse parametric-gate as `ParamGate` type. If not exists, return None.
        """

    @overload
    def update_quantum_state(self, state: StateVector, param: float) -> None:
        """
        Apply gate to `state_vector` with holding the parameter. `state_vector` in args is directly updated.
        """

    @overload
    def update_quantum_state(self, states: StateVectorBatched, params: Sequence[float]) -> None:
        """
        Apply gate to `states` with holding the parameter. `states` in args is directly updated.
        """

    def get_matrix(self, param: float) -> Annotated[ArrayLike, dict(dtype='complex128', shape=(None, None), order='C')]:
        """Get matrix representation of the gate with holding the parameter."""

    def to_string(self) -> str:
        """Get string representation of the gate."""

    def __str__(self) -> str:
        """Get string representation of the gate."""

    def to_json(self) -> str:
        """Get JSON representation of the gate."""

    def load_json(self, json_str: str) -> None:
        """Read an object from the JSON representation of the gate."""

class ParamRXGate:
    r"""
    Specific class of parametric X rotation gate, represented as $e^{-i\frac{\mathrm{\theta}}{2}X}$. `theta` is given as `param * param_coef`.

    Notes:
    	Upcast is required to use gate-general functions (ex: add to Circuit).
    """

    @overload
    def __init__(self, arg: ParamRXGate) -> None:
        """Downcast from ParamGate."""

    @overload
    def __init__(self, arg: ParamGate, /) -> None: ...

    def param_gate_type(self) -> scaluq.scaluq_core.ParamGateType:
        """Get parametric gate type as `ParamGateType` enum."""

    def param_coef(self) -> float:
        """Get coefficient of parameter."""

    def target_qubit_list(self) -> list[int]:
        """Get target qubits as `list[int]`. **Control qubits is not included.**"""

    def control_qubit_list(self) -> list[int]:
        """Get control qubits as `list[int]`."""

    def operand_qubit_list(self) -> list[int]:
        """Get target and control qubits as `list[int]`."""

    def target_qubit_mask(self) -> int:
        """Get target qubits as mask. **Control qubits is not included.**"""

    def control_qubit_mask(self) -> int:
        """Get control qubits as mask."""

    def operand_qubit_mask(self) -> int:
        """Get target and control qubits as mask."""

    def get_inverse(self) -> ParamGate:
        """
        Generate inverse parametric-gate as `ParamGate` type. If not exists, return None.
        """

    @overload
    def update_quantum_state(self, state: StateVector, param: float) -> None:
        """
        Apply gate to `state_vector` with holding the parameter. `state_vector` in args is directly updated.
        """

    @overload
    def update_quantum_state(self, states: StateVectorBatched, params: Sequence[float]) -> None:
        """
        Apply gate to `states` with holding the parameter. `states` in args is directly updated.
        """

    def get_matrix(self, param: float) -> Annotated[ArrayLike, dict(dtype='complex128', shape=(None, None), order='C')]:
        """Get matrix representation of the gate with holding the parameter."""

    def to_string(self) -> str:
        """Get string representation of the gate."""

    def __str__(self) -> str:
        """Get string representation of the gate."""

    def to_json(self) -> str:
        """Get JSON representation of the gate."""

    def load_json(self, json_str: str) -> None:
        """Read an object from the JSON representation of the gate."""

class ParamRYGate:
    r"""
    Specific class of parametric Y rotation gate, represented as $e^{-i\frac{\mathrm{\theta}}{2}Y}$. `theta` is given as `param * param_coef`.

    Notes:
    	Upcast is required to use gate-general functions (ex: add to Circuit).
    """

    @overload
    def __init__(self, arg: ParamRYGate) -> None:
        """Downcast from ParamGate."""

    @overload
    def __init__(self, arg: ParamGate, /) -> None: ...

    def param_gate_type(self) -> scaluq.scaluq_core.ParamGateType:
        """Get parametric gate type as `ParamGateType` enum."""

    def param_coef(self) -> float:
        """Get coefficient of parameter."""

    def target_qubit_list(self) -> list[int]:
        """Get target qubits as `list[int]`. **Control qubits is not included.**"""

    def control_qubit_list(self) -> list[int]:
        """Get control qubits as `list[int]`."""

    def operand_qubit_list(self) -> list[int]:
        """Get target and control qubits as `list[int]`."""

    def target_qubit_mask(self) -> int:
        """Get target qubits as mask. **Control qubits is not included.**"""

    def control_qubit_mask(self) -> int:
        """Get control qubits as mask."""

    def operand_qubit_mask(self) -> int:
        """Get target and control qubits as mask."""

    def get_inverse(self) -> ParamGate:
        """
        Generate inverse parametric-gate as `ParamGate` type. If not exists, return None.
        """

    @overload
    def update_quantum_state(self, state: StateVector, param: float) -> None:
        """
        Apply gate to `state_vector` with holding the parameter. `state_vector` in args is directly updated.
        """

    @overload
    def update_quantum_state(self, states: StateVectorBatched, params: Sequence[float]) -> None:
        """
        Apply gate to `states` with holding the parameter. `states` in args is directly updated.
        """

    def get_matrix(self, param: float) -> Annotated[ArrayLike, dict(dtype='complex128', shape=(None, None), order='C')]:
        """Get matrix representation of the gate with holding the parameter."""

    def to_string(self) -> str:
        """Get string representation of the gate."""

    def __str__(self) -> str:
        """Get string representation of the gate."""

    def to_json(self) -> str:
        """Get JSON representation of the gate."""

    def load_json(self, json_str: str) -> None:
        """Read an object from the JSON representation of the gate."""

class ParamRZGate:
    r"""
    Specific class of parametric Z rotation gate, represented as $e^{-i\frac{\mathrm{\theta}}{2}Z}$. `theta` is given as `param * param_coef`.

    Notes:
    	Upcast is required to use gate-general functions (ex: add to Circuit).
    """

    @overload
    def __init__(self, arg: ParamRZGate) -> None:
        """Downcast from ParamGate."""

    @overload
    def __init__(self, arg: ParamGate, /) -> None: ...

    def param_gate_type(self) -> scaluq.scaluq_core.ParamGateType:
        """Get parametric gate type as `ParamGateType` enum."""

    def param_coef(self) -> float:
        """Get coefficient of parameter."""

    def target_qubit_list(self) -> list[int]:
        """Get target qubits as `list[int]`. **Control qubits is not included.**"""

    def control_qubit_list(self) -> list[int]:
        """Get control qubits as `list[int]`."""

    def operand_qubit_list(self) -> list[int]:
        """Get target and control qubits as `list[int]`."""

    def target_qubit_mask(self) -> int:
        """Get target qubits as mask. **Control qubits is not included.**"""

    def control_qubit_mask(self) -> int:
        """Get control qubits as mask."""

    def operand_qubit_mask(self) -> int:
        """Get target and control qubits as mask."""

    def get_inverse(self) -> ParamGate:
        """
        Generate inverse parametric-gate as `ParamGate` type. If not exists, return None.
        """

    @overload
    def update_quantum_state(self, state: StateVector, param: float) -> None:
        """
        Apply gate to `state_vector` with holding the parameter. `state_vector` in args is directly updated.
        """

    @overload
    def update_quantum_state(self, states: StateVectorBatched, params: Sequence[float]) -> None:
        """
        Apply gate to `states` with holding the parameter. `states` in args is directly updated.
        """

    def get_matrix(self, param: float) -> Annotated[ArrayLike, dict(dtype='complex128', shape=(None, None), order='C')]:
        """Get matrix representation of the gate with holding the parameter."""

    def to_string(self) -> str:
        """Get string representation of the gate."""

    def __str__(self) -> str:
        """Get string representation of the gate."""

    def to_json(self) -> str:
        """Get JSON representation of the gate."""

    def load_json(self, json_str: str) -> None:
        """Read an object from the JSON representation of the gate."""

class ParamPauliRotationGate:
    r"""
    Specific class of parametric multi-qubit pauli-rotation gate, represented as $e^{-i\frac{\theta}{2}P}$. `theta` is given as `param * param_coef`.

    Notes:
    	Upcast is required to use gate-general functions (ex: add to Circuit).
    """

    @overload
    def __init__(self, arg: ParamPauliRotationGate) -> None:
        """Downcast from ParamGate."""

    @overload
    def __init__(self, arg: ParamGate, /) -> None: ...

    def param_gate_type(self) -> scaluq.scaluq_core.ParamGateType:
        """Get parametric gate type as `ParamGateType` enum."""

    def param_coef(self) -> float:
        """Get coefficient of parameter."""

    def target_qubit_list(self) -> list[int]:
        """Get target qubits as `list[int]`. **Control qubits is not included.**"""

    def control_qubit_list(self) -> list[int]:
        """Get control qubits as `list[int]`."""

    def operand_qubit_list(self) -> list[int]:
        """Get target and control qubits as `list[int]`."""

    def target_qubit_mask(self) -> int:
        """Get target qubits as mask. **Control qubits is not included.**"""

    def control_qubit_mask(self) -> int:
        """Get control qubits as mask."""

    def operand_qubit_mask(self) -> int:
        """Get target and control qubits as mask."""

    def get_inverse(self) -> ParamGate:
        """
        Generate inverse parametric-gate as `ParamGate` type. If not exists, return None.
        """

    @overload
    def update_quantum_state(self, state: StateVector, param: float) -> None:
        """
        Apply gate to `state_vector` with holding the parameter. `state_vector` in args is directly updated.
        """

    @overload
    def update_quantum_state(self, states: StateVectorBatched, params: Sequence[float]) -> None:
        """
        Apply gate to `states` with holding the parameter. `states` in args is directly updated.
        """

    def get_matrix(self, param: float) -> Annotated[ArrayLike, dict(dtype='complex128', shape=(None, None), order='C')]:
        """Get matrix representation of the gate with holding the parameter."""

    def to_string(self) -> str:
        """Get string representation of the gate."""

    def __str__(self) -> str:
        """Get string representation of the gate."""

    def to_json(self) -> str:
        """Get JSON representation of the gate."""

    def load_json(self, json_str: str) -> None:
        """Read an object from the JSON representation of the gate."""

class ParamProbabilisticGate:
    """
    Specific class of parametric probabilistic gate. The gate to apply is picked from a certain distribution.

    Notes:
    	Upcast is required to use gate-general functions (ex: add to Circuit).
    """

    @overload
    def __init__(self, arg: ParamProbabilisticGate) -> None:
        """Downcast from ParamGate."""

    @overload
    def __init__(self, arg: ParamGate, /) -> None: ...

    def param_gate_type(self) -> scaluq.scaluq_core.ParamGateType:
        """Get parametric gate type as `ParamGateType` enum."""

    def param_coef(self) -> float:
        """Get coefficient of parameter."""

    def target_qubit_list(self) -> list[int]:
        """Get target qubits as `list[int]`. **Control qubits is not included.**"""

    def control_qubit_list(self) -> list[int]:
        """Get control qubits as `list[int]`."""

    def operand_qubit_list(self) -> list[int]:
        """Get target and control qubits as `list[int]`."""

    def target_qubit_mask(self) -> int:
        """Get target qubits as mask. **Control qubits is not included.**"""

    def control_qubit_mask(self) -> int:
        """Get control qubits as mask."""

    def operand_qubit_mask(self) -> int:
        """Get target and control qubits as mask."""

    def get_inverse(self) -> ParamGate:
        """
        Generate inverse parametric-gate as `ParamGate` type. If not exists, return None.
        """

    @overload
    def update_quantum_state(self, state: StateVector, param: float) -> None:
        """
        Apply gate to `state_vector` with holding the parameter. `state_vector` in args is directly updated.
        """

    @overload
    def update_quantum_state(self, states: StateVectorBatched, params: Sequence[float]) -> None:
        """
        Apply gate to `states` with holding the parameter. `states` in args is directly updated.
        """

    def get_matrix(self, param: float) -> Annotated[ArrayLike, dict(dtype='complex128', shape=(None, None), order='C')]:
        """Get matrix representation of the gate with holding the parameter."""

    def to_string(self) -> str:
        """Get string representation of the gate."""

    def __str__(self) -> str:
        """Get string representation of the gate."""

    def to_json(self) -> str:
        """Get JSON representation of the gate."""

    def load_json(self, json_str: str) -> None:
        """Read an object from the JSON representation of the gate."""

    def gate_list(self) -> list[Gate | ParamGate]: ...

    def distribution(self) -> list[float]: ...

def merge_gate(arg0: Gate, arg1: Gate, /) -> tuple[Gate, float]:
    """Merge two gates. return value is (merged gate, global phase)."""

class Circuit:
    """
    Quantum circuit representation.

    Args:
        n_qubits (Number of qubits in the circuit.):
    Examples:
        >>> circuit = Circuit(3)
        >>> print(circuit.to_json())
        {"gate_list":[],"n_qubits":3}
    """

    def __init__(self, n_qubits: int) -> None:
        """Initialize empty circuit of specified qubits."""

    def n_qubits(self) -> int:
        """Get property of `n_qubits`."""

    def gate_list(self) -> list[Gate | tuple[ParamGate, str]]:
        """Get property of `gate_list`."""

    def n_gates(self) -> int:
        """Get property of `n_gates`."""

    def key_set(self) -> set[str]:
        """Get set of keys of parameters."""

    def get_gate_at(self, index: int) -> Gate | tuple[ParamGate, str]:
        """Get reference of i-th gate."""

    def get_param_key_at(self, index: int) -> str | None:
        """Get parameter key of i-th gate. If it is not parametric, return None."""

    def calculate_depth(self) -> int:
        """Get depth of circuit."""

    def add_gate(self, gate: Gate) -> None:
        """Add gate. Given gate is copied."""

    def add_param_gate(self, param_gate: ParamGate, param_key: str) -> None:
        """Add parametric gate with specifying key. Given param_gate is copied."""

    def add_circuit(self, other: Circuit) -> None:
        """Add all gates in specified circuit. Given gates are copied."""

    @overload
    def update_quantum_state(self, state: StateVector, params: Mapping[str, float]) -> None:
        """
        Apply gate to the StateVector. StateVector in args is directly updated. If the circuit contains parametric gate, you have to give real value of parameter as dict[str, float] in 2nd arg.
        """

    @overload
    def update_quantum_state(self, state: StateVector, **kwargs) -> None:
        """
        Apply gate to the StateVector. StateVector in args is directly updated. If the circuit contains parametric gate, you have to give real value of parameter as "name=value" format in kwargs.
        """

    @overload
    def update_quantum_state(self, state: StateVectorBatched, params: Mapping[str, Sequence[float]]) -> None:
        """
        Apply gate to the StateVectorBatched. StateVectorBatched in args is directly updated. If the circuit contains parametric gate, you have to give real value of parameter as dict[str, list[float]] in 2nd arg.
        """

    @overload
    def update_quantum_state(self, state: StateVectorBatched, **kwargs) -> None:
        """
        Apply gate to the StateVectorBatched. StateVectorBatched in args is directly updated. If the circuit contains parametric gate, you have to give real value of parameter as "name=[value1, value2, ...]" format in kwargs.
        """

    def copy(self) -> Circuit:
        """
        Copy circuit. Returns a new circuit instance with all gates copied by reference.
        """

    def get_inverse(self) -> Circuit:
        """Get inverse of circuit. All the gates are newly created."""

    def optimize(self, max_block_size: int = 3) -> None:
        """
        Optimize circuit. Create qubit dependency tree and merge neighboring gates if the new gate has less than or equal to `max_block_size` or the new gate is Pauli.
        """

    def simulate_noise(self, arg0: StateVector, arg1: int, arg2: Mapping[str, float], arg3: int, /) -> list[tuple[StateVector, int]]:
        """
        Simulate noise circuit. Return all the possible states and their counts.
        """

    def to_json(self) -> str:
        """Information as json style."""

    def load_json(self, json_str: str) -> None:
        """Read an object from the JSON representation of the circuit."""

class PauliOperatorData:
    """Internal data structure for PauliOperator."""

    @overload
    def __init__(self, coef: complex = 1.0) -> None:
        """Initialize data with coefficient."""

    @overload
    def __init__(self, pauli_string: str, coef: complex = 1.0) -> None:
        """Initialize data with pauli string."""

    @overload
    def __init__(self, target_qubit_list: Sequence[int], pauli_id_list: Sequence[int], coef: complex = 1.0) -> None:
        """Initialize data with target qubits and pauli ids."""

    @overload
    def __init__(self, pauli_id_par_qubit: Sequence[int], coef: complex = 1.0) -> None:
        """Initialize data with pauli ids per qubit."""

    @overload
    def __init__(self, bit_flip_mask: int, phase_flip_mask: int, coef: complex = 1.0) -> None:
        """Initialize data with bit flip and phase flip masks."""

    @overload
    def __init__(self, data: PauliOperatorData) -> None:
        """Initialize pauli operator from Data object."""

    def add_single_pauli(self, target_qubit: int, pauli_id: int) -> None:
        """Add a single pauli operation to the data."""

    def coef(self) -> complex:
        """Get the coefficient of the Pauli operator."""

    def set_coef(self, c: complex) -> None:
        """Set the coefficient of the Pauli operator."""

    def target_qubit_list(self) -> list[int]:
        """Get the list of target qubits."""

    def pauli_id_list(self) -> list[int]:
        """Get the list of Pauli IDs."""

    def get_XZ_mask_representation(self) -> tuple[int, int]:
        """Get the X and Z mask representation as a tuple of vectors."""

class PauliOperator:
    """
    Pauli operator as coef and tensor product of single pauli for each qubit.

    Given `coef: complex`, Initialize operator which just multiplying coef.

    Given `target_qubit_list: list[int], pauli_id_list: list[int], coef: complex`, Initialize pauli operator. For each `i`, single pauli correspond to `pauli_id_list[i]` is applied to `target_qubit_list[i]`-th qubit.

    Given `pauli_string: str, coef: complex`, Initialize pauli operator. For each `i`, single pauli correspond to `pauli_id_list[i]` is applied to `target_qubit_list[i]`-th qubit.

    Given `pauli_id_par_qubit: list[int], coef: complex`, Initialize pauli operator. For each `i`, single pauli correspond to `paul_id_per_qubit[i]` is applied to `i`-th qubit.

    Given `bit_flip_mask: int, phase_flip_mask: int, coef: complex`, Initialize pauli operator. For each `i`, single pauli applied to `i`-th qubit is got from `i-th` bit of `bit_flip_mask` and `phase_flip_mask` as follows.

    .. csv-table::

        "bit_flip","phase_flip","pauli"
        "0","0","I"
        "0","1","Z"
        "1","0","X"
        "1","1","Y"

    Examples:
        >>> pauli = PauliOperator("X 3 Y 2")
        >>> print(pauli.to_json())
        {"coef":{"imag":0.0,"real":1.0},"pauli_string":"X 3 Y 2"}
    """

    @overload
    def __init__(self, coef: complex = 1.0) -> None:
        """Initialize operator which just multiplying coef."""

    @overload
    def __init__(self, target_qubit_list: Sequence[int], pauli_id_list: Sequence[int], coef: complex = 1.0) -> None:
        """
        Initialize pauli operator. For each `i`, single pauli correspond to `pauli_id_list[i]` is applied to `target_qubit_list[i]`-th qubit.
        """

    @overload
    def __init__(self, pauli_string: str, coef: complex = 1.0) -> None:
        """
        Initialize pauli operator. If `pauli_string` is `"X0Y2"`, Pauli-X is applied to 0-th qubit and Pauli-Y is applied to 2-th qubit. In `pauli_string`, spaces are ignored.
        """

    @overload
    def __init__(self, pauli_id_par_qubit: Sequence[int], coef: complex = 1.0) -> None:
        """
        Initialize pauli operator. For each `i`, single pauli correspond to `paul_id_per_qubit[i]` is applied to `i`-th qubit.
        """

    @overload
    def __init__(self, bit_flip_mask: int, phase_flip_mask: int, coef: complex = 1.0) -> None:
        """
        Initialize pauli operator. For each `i`, single pauli applied to `i`-th qubit is got from `i-th` bit of `bit_flip_mask` and `phase_flip_mask` as follows.

        .. csv-table::

            "bit_flip","phase_flip","pauli"
            "0","0","I"
            "0","1","Z"
            "1","0","X"
            "1","1","Y"
        """

    def coef(self) -> complex:
        """Get property `coef`."""

    def target_qubit_list(self) -> list[int]:
        """Get qubits to be applied pauli."""

    def pauli_id_list(self) -> list[int]:
        """
        Get pauli id to be applied. The order is correspond to the result of `target_qubit_list`
        """

    def get_XZ_mask_representation(self) -> tuple[int, int]:
        """
        Get single-pauli property as binary integer representation. See description of `__init__(bit_flip_mask_py: int, phase_flip_mask_py: int, coef: float=1.)` for details.
        """

    def get_pauli_string(self) -> str:
        """
        Get single-pauli property as string representation. See description of `__init__(pauli_string: str, coef: float=1.)` for details.
        """

    def get_dagger(self) -> PauliOperator:
        """Get adjoint operator."""

    def get_qubit_count(self) -> int:
        r"""
        Get num of qubits to applied with, when count from 0-th qubit. Subset of $[0, \mathrm{qubit_count})$ is the target.
        """

    def apply_to_state(self, state: StateVector) -> None:
        """Apply pauli to state vector."""

    @overload
    def get_expectation_value(self, state: StateVector) -> complex:
        r"""
        Get expectation value of measuring state vector. $\bra{\psi}P\ket{\psi}$.
        """

    @overload
    def get_expectation_value(self, states: StateVectorBatched) -> list[complex]:
        r"""
        Get expectation values of measuring state vectors. $\bra{\psi_i}P\ket{\psi_i}$.
        """

    @overload
    def get_transition_amplitude(self, source: StateVector, target: StateVector) -> complex:
        r"""
        Get transition amplitude of measuring state vector. $\bra{\chi}P\ket{\psi}$.
        """

    @overload
    def get_transition_amplitude(self, states_source: StateVectorBatched, states_target: StateVectorBatched) -> list[complex]:
        r"""
        Get transition amplitudes of measuring state vectors. $\bra{\chi_i}P\ket{\psi_i}$.
        """

    def get_matrix(self) -> Annotated[ArrayLike, dict(dtype='complex128', shape=(None, None), order='C')]:
        """
        Get matrix representation of the PauliOperator. Tensor product is applied from target_qubit_list[-1] to target_qubit_list[0].
        """

    def get_matrix_ignoring_coef(self) -> Annotated[ArrayLike, dict(dtype='complex128', shape=(None, None), order='C')]:
        """
        Get matrix representation of the PauliOperator, but with forcing `coef=1.`
        """

    @overload
    def __mul__(self, arg: PauliOperator, /) -> PauliOperator: ...

    @overload
    def __mul__(self, arg: complex, /) -> PauliOperator: ...

    def to_json(self) -> str:
        """Information as json style."""

    def load_json(self, json_str: str) -> None:
        """Read an object from the JSON representation of the Pauli operator."""

class Operator:
    """
    General quantum operator class.

    Given `qubit_count: int`, Initialize operator with specified number of qubits.

    Examples:
        >>> pauli = PauliOperator("X 3 Y 2")
        >>> operator = Operator(4)
        >>> operator.add_operator(pauli)
        >>> print(operator.to_json())
        {"coef":{"imag":0.0,"real":1.0},"pauli_string":"X 3 Y 2"}
    """

    def __init__(self, qubit_count: int) -> None:
        """Initialize operator with specified number of qubits."""

    def is_hermitian(self) -> bool:
        """Check if the operator is Hermitian."""

    def n_qubits(self) -> int:
        """Get the number of qubits the operator acts on."""

    def terms(self) -> list[PauliOperator]:
        """Get the list of Pauli terms that make up the operator."""

    def to_string(self) -> str:
        """Get string representation of the operator."""

    def add_operator(self, pauli: PauliOperator) -> None:
        """Add a Pauli operator to this operator."""

    def add_random_operator(self, operator_count: int, seed: int | None = None) -> None:
        """
        Add a specified number of random Pauli operators to this operator. An optional seed can be provided for reproducibility.
        """

    def optimize(self) -> None:
        """Optimize the operator by combining like terms."""

    def get_dagger(self) -> Operator:
        """Get the adjoint (Hermitian conjugate) of the operator."""

    def apply_to_state(self, state: StateVector) -> None:
        """Apply the operator to a state vector."""

    @overload
    def get_expectation_value(self, state: StateVector) -> complex:
        """
        Get the expectation value of the operator with respect to a state vector.
        """

    @overload
    def get_expectation_value(self, states: StateVectorBatched) -> list[complex]:
        """
        Get the expectation values of the operator for a batch of state vectors.
        """

    @overload
    def get_transition_amplitude(self, source: StateVector, target: StateVector) -> complex:
        """
        Get the transition amplitude of the operator between two state vectors.
        """

    @overload
    def get_transition_amplitude(self, states_source: StateVectorBatched, states_target: StateVectorBatched) -> list[complex]:
        """
        Get the transition amplitudes of the operator for a batch of state vectors.
        """

    def get_matrix(self) -> Annotated[ArrayLike, dict(dtype='complex128', shape=(None, None), order='C')]:
        """
        Get matrix representation of the Operator. Tensor product is applied from n_qubits-1 to 0.
        """

    @overload
    def __imul__(self, arg: complex, /) -> Operator: ...

    @overload
    def __imul__(self, arg: Operator, /) -> Operator: ...

    @overload
    def __imul__(self, arg: PauliOperator, /) -> Operator: ...

    @overload
    def __mul__(self, arg: complex, /) -> Operator: ...

    @overload
    def __mul__(self, arg: Operator, /) -> Operator: ...

    @overload
    def __mul__(self, arg: PauliOperator, /) -> Operator: ...

    def __pos__(self) -> Operator: ...

    def __neg__(self) -> Operator: ...

    @overload
    def __iadd__(self, arg: Operator, /) -> Operator: ...

    @overload
    def __iadd__(self, arg: PauliOperator, /) -> Operator: ...

    @overload
    def __add__(self, arg: Operator, /) -> Operator: ...

    @overload
    def __add__(self, arg: PauliOperator, /) -> Operator: ...

    @overload
    def __isub__(self, arg: Operator, /) -> Operator: ...

    @overload
    def __isub__(self, arg: PauliOperator, /) -> Operator: ...

    @overload
    def __sub__(self, arg: Operator, /) -> Operator: ...

    @overload
    def __sub__(self, arg: PauliOperator, /) -> Operator: ...

    def to_json(self) -> str:
        """Information as json style."""

    def load_json(self, json_str: str) -> None:
        """Read an object from the JSON representation of the operator."""
