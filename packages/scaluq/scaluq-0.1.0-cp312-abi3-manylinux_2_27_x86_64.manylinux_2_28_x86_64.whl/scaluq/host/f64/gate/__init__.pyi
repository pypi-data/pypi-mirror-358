from collections.abc import Sequence
from typing import Annotated, overload

from numpy.typing import ArrayLike
import scipy

import scaluq.scaluq_core.default.f64


def I() -> scaluq.scaluq_core.default.f64.Gate:
    """
    Generate general :class:`~scaluq.f64.Gate` class instance of :class:`~scaluq.f64.IGate`.

    Returns:
        Gate:
            Identity gate instance

    Examples:
        >>> gate = I()
        >>> print(gate)
        Identity Gate
    """

def GlobalPhase(gamma: float, controls: Sequence[int] = [], control_values: Sequence[int] = []) -> scaluq.scaluq_core.default.f64.Gate:
    """
    Generate general :class:`~scaluq.f64.Gate` class instance of :class:`~scaluq.f64.GlobalPhaseGate`.

    Args:
        gamma (float):
            Global phase angle in radians

        controls (list[int], optional):
            Control qubit indices

        control_values (list[int], optional):
            Control qubit values

    Returns:
        Gate:
            Global phase gate instance

    Examples:
        >>> gate = GlobalPhase(math.pi/2)
        >>> print(gate)
        Global Phase Gate

    Notes:
        If you need to use functions specific to the :class:`~scaluq.f64.GlobalPhaseGate` class, please downcast it.
    """

def X(target: int, controls: Sequence[int] = [], control_values: Sequence[int] = []) -> scaluq.scaluq_core.default.f64.Gate:
    """
    Generate general :class:`~scaluq.f64.Gate` class instance of :class:`~scaluq.f64.XGate`. Performs bit flip operation.

    Args:
        target (int):
            Target qubit index

        controls (list[int], optional):
            Control qubit indices

        control_values (list[int], optional):
            Control qubit values

    Returns:
        Gate:
            Pauli-X gate instance

    Examples:
        >>> gate = X(0)  # X gate on qubit 0
        >>> gate = X(1, [0])  # Controlled-X with control on qubit 0

    Notes:
        XGate represents the Pauli-X (NOT) gate class.If you need to use functions specific to the :class:`~scaluq.f64.XGate` class, please downcast it.
    """

def Y(target: int, controls: Sequence[int] = [], control_values: Sequence[int] = []) -> scaluq.scaluq_core.default.f64.Gate:
    """
    Generate general :class:`~scaluq.f64.Gate` class instance of :class:`~scaluq.f64.YGate`. Performs bit flip and phase flip operation.

    Args:
        target (int):
            Target qubit index

        controls (list[int], optional):
            Control qubit indices

        control_values (list[int], optional):
            Control qubit values

    Returns:
        Gate:
            Pauli-Y gate instance

    Examples:
        >>> gate = Y(0)  # Y gate on qubit 0
        >>> gate = Y(1, [0])  # Controlled-Y with control on qubit 0

    Notes:
        YGate represents the Pauli-Y gate class. If you need to use functions specific to the :class:`~scaluq.f64.YGate` class, please downcast it.
    """

def Z(target: int, controls: Sequence[int] = [], control_values: Sequence[int] = []) -> scaluq.scaluq_core.default.f64.Gate:
    """
    Generate general :class:`~scaluq.f64.Gate` class instance of :class:`~scaluq.f64.ZGate`. Performs bit flip and phase flip operation.

    Args:
        target (int):
            Target qubit index

        controls (list[int], optional):
            Control qubit indices

        control_values (list[int], optional):
            Control qubit values

    Returns:
        Gate:
            Pauli-Z gate instance

    Examples:
        >>> gate = Z(0)  # Z gate on qubit 0
        >>> gate = Z(1, [0])  # Controlled-Z with control on qubit 0

    Notes:
        ZGate represents the Pauli-Z gate class. If you need to use functions specific to the :class:`~scaluq.f64.ZGate` class, please downcast it.
    """

def H(target: int, controls: Sequence[int] = [], control_values: Sequence[int] = []) -> scaluq.scaluq_core.default.f64.Gate:
    """
    Generate general :class:`~scaluq.f64.Gate` class instance of :class:`~scaluq.f64.HGate`. Performs superposition operation.

    Args:
        target (int):
            Target qubit index

        controls (list[int], optional):
            Control qubit indices

        control_values (list[int], optional):
            Control qubit values

    Returns:
        Gate:
            Hadamard gate instance

    Examples:
        >>> gate = H(0)  # H gate on qubit 0
        >>> gate = H(1, [0])  # Controlled-H with control on qubit 0

    Notes:
        If you need to use functions specific to the :class:`~scaluq.f64.HGate` class, please downcast it.
    """

def S(target: int, controls: Sequence[int] = [], control_values: Sequence[int] = []) -> scaluq.scaluq_core.default.f64.Gate:
    """
    Generate general :class:`~scaluq.f64.Gate` class instance of :class:`~scaluq.f64.SGate`.

    Args:
        target (int):
            Target qubit index

        controls (list[int], optional):
            Control qubit indices

        control_values (list[int], optional):
            Control qubit values

    Returns:
        Gate:
            S gate instance

    Examples:
        >>> gate = S(0)  # S gate on qubit 0
        >>> gate = S(1, [0])  # Controlled-S with control on qubit 0

    Notes:
        If you need to use functions specific to the :class:`~scaluq.f64.SGate` class, please downcast it.
    """

def Sdag(target: int, controls: Sequence[int] = [], control_values: Sequence[int] = []) -> scaluq.scaluq_core.default.f64.Gate:
    """
    Generate general :class:`~scaluq.f64.Gate` class instance of :class:`~scaluq.f64.SdagGate`.

    Args:
        target (int):
            Target qubit index

        controls (list[int], optional):
            Control qubit indices

        control_values (list[int], optional):
            Control qubit values

    Returns:
        Gate:
            Sdag gate instance

    Examples:
        >>> gate = Sdag(0)  # Sdag gate on qubit 0
        >>> gate = Sdag(1, [0])  # Controlled-Sdag with control on qubit 0

    Notes:
        If you need to use functions specific to the :class:`~scaluq.f64.SdagGate` class, please downcast it.
    """

def T(target: int, controls: Sequence[int] = [], control_values: Sequence[int] = []) -> scaluq.scaluq_core.default.f64.Gate:
    """
    Generate general :class:`~scaluq.f64.Gate` class instance of :class:`~scaluq.f64.TGate`.

    Args:
        target (int):
            Target qubit index

        controls (list[int], optional):
            Control qubit indices

        control_values (list[int], optional):
            Control qubit values

    Returns:
        Gate:
            T gate instance

    Examples:
        >>> gate = T(0)  # T gate on qubit 0
        >>> gate = T(1, [0])  # Controlled-T with control on qubit 0

    Notes:
        If you need to use functions specific to the :class:`~scaluq.f64.TGate` class, please downcast it.
    """

def Tdag(target: int, controls: Sequence[int] = [], control_values: Sequence[int] = []) -> scaluq.scaluq_core.default.f64.Gate:
    """
    Generate general :class:`~scaluq.f64.Gate` class instance of :class:`~scaluq.f64.TdagGate`.

    Args:
        target (int):
            Target qubit index

        controls (list[int], optional):
            Control qubit indices

        control_values (list[int], optional):
            Control qubit values

    Returns:
        Gate:
            Tdag gate instance

    Examples:
        >>> gate = Tdag(0)  # Tdag gate on qubit 0
        >>> gate = Tdag(1, [0])  # Controlled-Tdag with control on qubit 0

    Notes:
        If you need to use functions specific to the :class:`~scaluq.f64.TdagGate` class, please downcast it.
    """

def SqrtX(target: int, controls: Sequence[int] = [], control_values: Sequence[int] = []) -> scaluq.scaluq_core.default.f64.Gate:
    r"""
    Generate general :class:`~scaluq.f64.Gate` class instance of :class:`~scaluq.f64.SqrtXGate`, represented as $\frac{1}{2}\begin{bmatrix} 1+i & 1-i \\ 1-i & 1+i \end{bmatrix}$.

    Args:
        target (int):
            Target qubit index

        controls (list[int], optional):
            Control qubit indices

        control_values (list[int], optional):
            Control qubit values

    Returns:
        Gate:
            SqrtX gate instance

    Examples:
        >>> gate = SqrtX(0)  # SqrtX gate on qubit 0
        >>> gate = SqrtX(1, [0])  # Controlled-SqrtX

    Notes:
        If you need to use functions specific to the :class:`~scaluq.f64.SqrtXGate` class, please downcast it.
    """

def SqrtXdag(target: int, controls: Sequence[int] = [], control_values: Sequence[int] = []) -> scaluq.scaluq_core.default.f64.Gate:
    r"""
    Generate general :class:`~scaluq.f64.Gate` class instance of :class:`~scaluq.f64.SqrtXdagGate`, represented as $\begin{bmatrix} 1-i & 1+i\\ 1+i & 1-i \end{bmatrix}$.

    Args:
        target (int):
            Target qubit index

        controls (list[int], optional):
            Control qubit indices

        control_values (list[int], optional):
            Control qubit values

    Returns:
        Gate:
            SqrtXdag gate instance

    Examples:
        >>> gate = SqrtXdag(0)  # SqrtXdag gate on qubit 0
        >>> gate = SqrtXdag(1, [0])  # Controlled-SqrtXdag

    Notes:
        If you need to use functions specific to the :class:`~scaluq.f64.SqrtXdagGate` class, please downcast it.
    """

def SqrtY(target: int, controls: Sequence[int] = [], control_values: Sequence[int] = []) -> scaluq.scaluq_core.default.f64.Gate:
    r"""
    Generate general :class:`~scaluq.f64.Gate` class instance of :class:`~scaluq.f64.SqrtYGate`, represented as $\begin{bmatrix} 1+i & -1-i \\ 1+i & 1+i \end{bmatrix}$.

    Args:
        target (int):
            Target qubit index

        controls (list[int], optional):
            Control qubit indices

        control_values (list[int], optional):
            Control qubit values

    Returns:
        Gate:
            SqrtY gate instance

    Examples:
        >>> gate = SqrtY(0)  # SqrtY gate on qubit 0
        >>> gate = SqrtY(1, [0])  # Controlled-SqrtY

    Notes:
        If you need to use functions specific to the :class:`~scaluq.f64.SqrtYGate` class, please downcast it.
    """

def SqrtYdag(target: int, controls: Sequence[int] = [], control_values: Sequence[int] = []) -> scaluq.scaluq_core.default.f64.Gate:
    r"""
    Generate general :class:`~scaluq.f64.Gate` class instance of :class:`~scaluq.f64.SqrtYdagGate`, represented as $\begin{bmatrix} 1-i & 1-i \\ -1+i & 1-i \end{bmatrix}$.

    Args:
        target (int):
            Target qubit index

        controls (list[int], optional):
            Control qubit indices

        control_values (list[int], optional):
            Control qubit values

    Returns:
        Gate:
            SqrtYdag gate instance

    Examples:
        >>> gate = SqrtYdag(0)  # SqrtYdag gate on qubit 0
        >>> gate = SqrtYdag(1, [0])  # Controlled-SqrtYdag

    Notes:
        If you need to use functions specific to the :class:`~scaluq.f64.SqrtYdagGate` class, please downcast it.
    """

def P0(target: int, controls: Sequence[int] = [], control_values: Sequence[int] = []) -> scaluq.scaluq_core.default.f64.Gate:
    """
    Generate general :class:`~scaluq.f64.Gate` class instance of :class:`~scaluq.f64.P0Gate`.

    Args:
        target (int):
            Target qubit index

        controls (list[int], optional):
            Control qubit indices

        control_values (list[int], optional):
            Control qubit values

    Returns:
        Gate:
            P0 gate instance

    Examples:
        >>> gate = P0(0)  # P0 gate on qubit 0
        >>> gate = P0(1, [0])  # Controlled-P0

    Notes:
        If you need to use functions specific to the :class:`~scaluq.f64.P0Gate` class, please downcast it.
    """

def P1(target: int, controls: Sequence[int] = [], control_values: Sequence[int] = []) -> scaluq.scaluq_core.default.f64.Gate:
    """
    Generate general :class:`~scaluq.f64.Gate` class instance of :class:`~scaluq.f64.P1Gate`.

    Args:
        target (int):
            Target qubit index

        controls (list[int], optional):
            Control qubit indices

        control_values (list[int], optional):
            Control qubit values

    Returns:
        Gate:
            P1 gate instance

    Examples:
        >>> gate = P1(0)  # P1 gate on qubit 0
        >>> gate = P1(1, [0])  # Controlled-P1

    Notes:
        If you need to use functions specific to the :class:`~scaluq.f64.P1Gate` class, please downcast it.
    """

def RX(target: int, theta: float, controls: Sequence[int] = [], control_values: Sequence[int] = []) -> scaluq.scaluq_core.default.f64.Gate:
    """
    Generate rotation gate around X-axis. Rotation angle is specified in radians.

    Args:
        target (int):
            Target qubit index

        theta (float):
            Rotation angle in radians

        controls (list[int], optional):
            Control qubit indices

        control_values (list[int], optional):
            Control qubit values

    Returns:
        Gate:
            RX gate instance

    Examples:
        >>> gate = RX(0, math.pi/2)  # π/2 rotation around X-axis
        >>> gate = RX(1, math.pi, [0])  # Controlled-RX

    Notes:
        If you need to use functions specific to the :class:`~scaluq.f64.RXGate` class, please downcast it.
    """

def RY(target: int, theta: float, controls: Sequence[int] = [], control_values: Sequence[int] = []) -> scaluq.scaluq_core.default.f64.Gate:
    """
    Generate rotation gate around Y-axis. Rotation angle is specified in radians.

    Args:
        target (int):
            Target qubit index

        theta (float):
            Rotation angle in radians

        controls (list[int], optional):
            Control qubit indices

        control_values (list[int], optional):
            Control qubit values

    Returns:
        Gate:
            RY gate instance

    Examples:
        >>> gate = RY(0, math.pi/2)  # π/2 rotation around Y-axis
        >>> gate = RY(1, math.pi, [0])  # Controlled-RY

    Notes:
        If you need to use functions specific to the :class:`~scaluq.f64.RYGate` class, please downcast it.
    """

def RZ(target: int, theta: float, controls: Sequence[int] = [], control_values: Sequence[int] = []) -> scaluq.scaluq_core.default.f64.Gate:
    """
    Generate rotation gate around Z-axis. Rotation angle is specified in radians.

    Args:
        target (int):
            Target qubit index

        theta (float):
            Rotation angle in radians

        controls (list[int], optional):
            Control qubit indices

        control_values (list[int], optional):
            Control qubit values

    Returns:
        Gate:
            RZ gate instance

    Examples:
        >>> gate = RZ(0, math.pi/2)  # π/2 rotation around Z-axis
        >>> gate = RZ(1, math.pi, [0])  # Controlled-RZ

    Notes:
        If you need to use functions specific to the :class:`~scaluq.f64.RZGate` class, please downcast it.
    """

def U1(target: int, lambda_: float, controls: Sequence[int] = [], control_values: Sequence[int] = []) -> scaluq.scaluq_core.default.f64.Gate:
    """
    Generate general :class:`~scaluq.f64.Gate` class instance of :class:`~scaluq.f64.U1Gate`.

    Args:
        target (int):
            Target qubit index

        lambda_ (float):
            Rotation angle in radians

        controls (list[int], optional):
            Control qubit indices

        control_values (list[int], optional):
            Control qubit values

    Returns:
        Gate:
            U1 gate instance

    Examples:
        >>> gate = U1(0, math.pi/2)  # π/2 rotation around Z-axis
        >>> gate = U1(1, math.pi, [0])  # Controlled-U1

    Notes:
        If you need to use functions specific to the :class:`~scaluq.f64.U1Gate` class, please downcast it.
    """

def U2(target: int, phi: float, lambda_: float, controls: Sequence[int] = [], control_values: Sequence[int] = []) -> scaluq.scaluq_core.default.f64.Gate:
    """
    Generate general :class:`~scaluq.f64.Gate` class instance of :class:`~scaluq.f64.U2Gate`.

    Args:
        target (int):
            Target qubit index

        phi (float):
            Rotation angle in radians

        lambda_ (float):
            Rotation angle in radians

        controls (list[int], optional):
            Control qubit indices

        control_values (list[int], optional):
            Control qubit values

    Returns:
        Gate:
            U2 gate instance

    Examples:
        >>> gate = U2(0, math.pi/2, math.pi)  # π/2 rotation around Z-axis
        >>> gate = U2(1, math.pi, math.pi/2, [0])  # Controlled-U2

    Notes:
        If you need to use functions specific to the :class:`~scaluq.f64.U2Gate` class, please downcast it.
    """

def U3(target: int, theta: float, phi: float, lambda_: float, controls: Sequence[int] = [], control_values: Sequence[int] = []) -> scaluq.scaluq_core.default.f64.Gate:
    """
    Generate general :class:`~scaluq.f64.Gate` class instance of :class:`~scaluq.f64.U3Gate`.

    Args:
        target (int):
            Target qubit index

        theta (float):
            Rotation angle in radians

        phi (float):
            Rotation angle in radians

        lambda_ (float):
            Rotation angle in radians

        controls (list[int], optional):
            Control qubit indices

        control_values (list[int], optional):
            Control qubit values

    Returns:
        Gate:
            U3 gate instance

    Examples:
        >>> gate = U3(0, math.pi/2, math.pi, math.pi)  # π/2 rotation around Z-axis
        >>> gate = U3(1, math.pi, math.pi/2, math.pi, [0])  # Controlled-U3

    Notes:
        If you need to use functions specific to the :class:`~scaluq.f64.U3Gate` class, please downcast it.
    """

def Swap(target1: int, target2: int, controls: Sequence[int] = [], control_values: Sequence[int] = []) -> scaluq.scaluq_core.default.f64.Gate:
    """
    Generate SWAP gate. Swaps the states of two qubits.

    Args:
        target1 (int):
            First target qubit index

        target2 (int):
            Second target qubit index

        controls (list[int], optional):
            Control qubit indices

        control_values (list[int], optional):
            Control qubit values

    Returns:
        Gate:
            SWAP gate instance

    Examples:
        >>> gate = Swap(0, 1)  # Swap qubits 0 and 1
        >>> gate = Swap(1, 2, [0])  # Controlled-SWAP

    Notes:
        If you need to use functions specific to the :class:`~scaluq.f64.SwapGate` class, please downcast it.
    """

def CX(control: int, target: int) -> scaluq.scaluq_core.default.f64.Gate:
    """
    Generate general :class:`~scaluq.f64.Gate` class instance of :class:`~scaluq.f64.XGate` with one control qubit. Performs controlled-X operation.

    Args:
        control (int):
            Control qubit index

        target (int):
            Target qubit index

    Returns:
        Gate:
            CX gate instance

    Examples:
        >>> gate = CX(0, 1)  # CX gate with control on qubit 0
        >>> gate = CX(1, 2)  # CX gate with control on qubit 1

    Notes:
        CX is a specialization of X. If you need to use functions specific to the :class:`~scaluq.f64.XGate` class, please downcast it.
    """

def CNot(control: int, target: int) -> scaluq.scaluq_core.default.f64.Gate:
    """
    Generate general :class:`~scaluq.f64.Gate` class instance of :class:`~scaluq.f64.XGate` with one control qubit. Performs controlled-X operation.

    Args:
        control (int):
            Control qubit index

        target (int):
            Target qubit index

    Returns:
        Gate:
            CNot gate instance

    Examples:
        >>> gate = CNot(0, 1)  # CNot gate with control on qubit 0
        >>> gate = CNot(1, 2)  # CNot gate with control on qubit 1

    Notes:
        CNot is an alias of CX. If you need to use functions specific to the :class:`~scaluq.f64.XGate` class, please downcast it.
    """

def CZ(control: int, target: int) -> scaluq.scaluq_core.default.f64.Gate:
    """
    Generate general :class:`~scaluq.f64.Gate` class instance of :class:`~scaluq.f64.ZGate` with one control qubit. Performs controlled-Z operation.

    Args:
        control (int):
            Control qubit index

        target (int):
            Target qubit index

    Returns:
        Gate:
            CZ gate instance

    Examples:
        >>> gate = CZ(0, 1)  # CZ gate with control on qubit 0
        >>> gate = CZ(1, 2)  # CZ gate with control on qubit 1

    Notes:
        CZ is a specialization of Z. If you need to use functions specific to the :class:`~scaluq.f64.ZGate` class, please downcast it.
    """

def CCX(control1: int, control2: int, target: int) -> scaluq.scaluq_core.default.f64.Gate:
    """
    Generate general :class:`~scaluq.f64.Gate` class instance of :class:`~scaluq.f64.XGate` with two control qubits. Performs controlled-controlled-X operation.

    Args:
        control1 (int):
            First control qubit index

        control2 (int):
            Second control qubit index

        target (int):
            Target qubit index

    Returns:
        Gate:
            CCX gate instance

    Examples:
        >>> gate = CCX(0, 1, 2)  # CCX gate with controls on qubits 0 and 1
        >>> gate = CCX(1, 2, 3)  # CCX gate with controls on qubits 1 and 2

    Notes:
        If you need to use functions specific to the :class:`~scaluq.f64.XGate` class, please downcast it.
    """

def CCNot(control1: int, control2: int, target: int) -> scaluq.scaluq_core.default.f64.Gate:
    """
    Generate general :class:`~scaluq.f64.Gate` class instance of :class:`~scaluq.f64.XGate` with two control qubits. Performs controlled-controlled-X operation.

    Args:
        control1 (int):
            First control qubit index

        control2 (int):
            Second control qubit index

        target (int):
            Target qubit index

    Returns:
        Gate:
            CCNot gate instance

    Examples:
        >>> gate = CCNot(0, 1, 2)  # CCNot gate with controls on qubits 0 and 1
        >>> gate = CCNot(1, 2, 3)  # CCNot gate with controls on qubits 1 and 2

    Notes:
        CCNot is an alias of CCX. If you need to use functions specific to the :class:`~scaluq.f64.XGate` class, please downcast it.
    """

def Toffoli(control1: int, control2: int, target: int) -> scaluq.scaluq_core.default.f64.Gate:
    """
    Generate general :class:`~scaluq.f64.Gate` class instance of :class:`~scaluq.f64.XGate` with two control qubits. Performs controlled-controlled-X operation.

    Args:
        control1 (int):
            First control qubit index

        control2 (int):
            Second control qubit index

        target (int):
            Target qubit index

    Returns:
        Gate:
            Toffoli gate instance

    Examples:
        >>> gate = Toffoli(0, 1, 2)  # Toffoli gate with controls on qubits 0 and 1
        >>> gate = Toffoli(1, 2, 3)  # Toffoli gate with controls on qubits 1 and 2

    Notes:
        Toffoli is an alias of CCX. If you need to use functions specific to the :class:`~scaluq.f64.XGate` class, please downcast it.
    """

def DenseMatrix(targets: Sequence[int], matrix: Annotated[ArrayLike, dict(dtype='complex128', shape=(None, None), order='C')], controls: Sequence[int] = [], control_values: Sequence[int] = [], is_unitary: bool = False) -> scaluq.scaluq_core.default.f64.Gate:
    """
    Generate general :class:`~scaluq.f64.Gate` class instance of :class:`~scaluq.f64.DenseMatrixGate`. Performs dense matrix operation.

    Args:
        targets (list[int]):
            Target qubit indices

        matrix (numpy.ndarray):
            Matrix to be applied

        controls (list[int], optional):
            Control qubit indices

        control_values (list[int], optional):
            Control qubit values

        is_unitary (bool, optional):
            Whether the matrix is unitary. When the flag indicating that the gate is unitary is set to True, a more efficient implementation is used.

    Returns:
        Gate:
            DenseMatrix gate instance

    Examples:
        >>> matrix = np.array([[1, 0], [0, 1]])
        >>> gate = DenseMatrix([0], matrix)
        >>> gate = DenseMatrix([0], matrix, [1])  # Controlled-DenseMatrix

    Notes:
        If you need to use functions specific to the :class:`~scaluq.f64.DenseMatrixGate` class, please downcast it.
    """

def SparseMatrix(targets: Sequence[int], matrix: scipy.sparse.csr_matrix[complex], controls: Sequence[int] = [], control_values: Sequence[int] = []) -> scaluq.scaluq_core.default.f64.Gate:
    """
    Generate general :class:`~scaluq.f64.Gate` class instance of :class:`~scaluq.f64.SparseMatrixGate`. Performs sparse matrix operation.

    Args:
        targets (list[int]):
            Target qubit indices

        matrix (scipy.sparse.csr_matrix):
            Matrix to be applied

        controls (list[int], optional):
            Control qubit indices

        control_values (list[int], optional):
            Control qubit values

    Returns:
        Gate:
            SparseMatrix gate instance

    Examples:
        >>> matrix = scipy.sparse.csr_matrix([[1, 0], [0, 1]])
        >>> gate = SparseMatrix([0], matrix)
        >>> gate = SparseMatrix([0], matrix, [1])  # Controlled-SparseMatrix

    Notes:
        If you need to use functions specific to the :class:`~scaluq.f64.SparseMatrixGate` class, please downcast it.
    """

def Pauli(pauli: scaluq.scaluq_core.default.f64.PauliOperator, controls: Sequence[int] = [], control_values: Sequence[int] = []) -> scaluq.scaluq_core.default.f64.Gate:
    """
    Generate general :class:`~scaluq.f64.Gate` class instance of :class:`~scaluq.f64.PauliGate`. Performs Pauli operation.

    Args:
        pauli (PauliOperator):
            Pauli operator

        controls (list[int], optional):
            Control qubit indices

        control_values (list[int], optional):
            Control qubit values

    Returns:
        Gate:
            Pauli gate instance

    Examples:
        >>> pauli = PauliOperator('X 0')
        >>> gate = Pauli(pauli)
        >>> gate = Pauli(pauli, [1])  # Controlled-Pauli

    Notes:
        If you need to use functions specific to the :class:`~scaluq.f64.PauliGate` class, please downcast it.
    """

def PauliRotation(pauli: scaluq.scaluq_core.default.f64.PauliOperator, theta: float, controls: Sequence[int] = [], control_values: Sequence[int] = []) -> scaluq.scaluq_core.default.f64.Gate:
    """
    Generate general :class:`~scaluq.f64.Gate` class instance of :class:`~scaluq.f64.PauliRotationGate`. Performs Pauli rotation operation.

    Args:
        pauli (PauliOperator):
            Pauli operator

        theta (float):
            Rotation angle in radians

        controls (list[int], optional):
            Control qubit indices

        control_values (list[int], optional):
            Control qubit values

    Returns:
        Gate:
            PauliRotation gate instance

    Examples:
        >>> pauli = PauliOperator('X', 0)
        >>> gate = PauliRotation(pauli, math.pi/2)
        >>> gate = PauliRotation(pauli, math.pi/2, [1])  # Controlled-Pauli

    Notes:
        If you need to use functions specific to the :class:`~scaluq.f64.PauliRotationGate` class, please downcast it.
    """

def Probabilistic(distribution: Sequence[float], gate_list: Sequence[scaluq.scaluq_core.default.f64.Gate]) -> scaluq.scaluq_core.default.f64.Gate:
    """
    Generate general :class:`~scaluq.f64.Gate` class instance of :class:`~scaluq.f64.ProbabilisticGate`. Performs probabilistic operation.

    Args:
        distribution (list[float]):
            Probabilistic distribution

        gate_list (list[Gate]):
            List of gates

    Returns:
        Gate:
            Probabilistic gate instance

    Examples:
        >>> distribution = [0.3, 0.7]
        >>> gate_list = [X(0), Y(0)]
        >>> # X is applied with probability 0.3, Y is applied with probability 0.7
        >>> gate = Probabilistic(distribution, gate_list)

    Notes:
        If you need to use functions specific to the :class:`~scaluq.f64.ProbabilisticGate` class, please downcast it.
    """

def BitFlipNoise(target: int, error_rate: float) -> scaluq.scaluq_core.default.f64.Gate:
    """
    Generates a general Gate class instance of BitFlipNoise. `error_rate` is the probability of a bit-flip noise, corresponding to the X gate.
    """

def DephasingNoise(target: int, error_rate: float) -> scaluq.scaluq_core.default.f64.Gate:
    """
    Generates a general Gate class instance of DephasingNoise. `error_rate` is the probability of a dephasing noise, corresponding to the Z gate.
    """

def BitFlipAndDephasingNoise(target: int, error_rate: float) -> scaluq.scaluq_core.default.f64.Gate:
    """
    Generates a general Gate class instance of BitFlipAndDephasingNoise. `error_rate` is the probability of both bit-flip noise and dephasing noise, corresponding to the X gate and Z gate.
    """

def DepolarizingNoise(target: int, error_rate: float) -> scaluq.scaluq_core.default.f64.Gate:
    """
    Generates a general Gate class instance of DepolarizingNoise. `error_rate` is the total probability of depolarizing noise, where an X, Y, or Z gate is applied with a probability of `error_rate / 3` each.
    """

def ParamRX(target: int, coef: float = 1.0, controls: Sequence[int] = [], control_values: Sequence[int] = []) -> scaluq.scaluq_core.default.f64.ParamGate:
    """
    Generate general :class:`~scaluq.f64.ParamGate` class instance of :class:`~scaluq.f64.ParamRXGate`.

    Args:
        target (int):
            Target qubit index

        coef (float, optional):
            Parameter coefficient

        controls (list[int], optional):
            Control qubit indices

        control_values (list[int], optional):
            Control qubit values

    Returns:
        ParamGate:
            ParamRX gate instance

    Examples:
        >>> gate = ParamRX(0)  # ParamRX gate on qubit 0
        >>> gate = ParamRX(1, [0])  # Controlled-ParamRX

    Notes:
        If you need to use functions specific to the :class:`~scaluq.f64.ParamRXGate` class, please downcast it.
    """

def ParamRY(target: int, coef: float = 1.0, controls: Sequence[int] = [], control_values: Sequence[int] = []) -> scaluq.scaluq_core.default.f64.ParamGate:
    """
    Generate general :class:`~scaluq.f64.ParamGate` class instance of :class:`~scaluq.f64.ParamRYGate`.

    Args:
        target (int):
            Target qubit index

        coef (float, optional):
            Parameter coefficient

        controls (list[int], optional):
            Control qubit indices

        control_values (list[int], optional):
            Control qubit values

    Returns:
        ParamGate:
            ParamRY gate instance

    Examples:
        >>> gate = ParamRY(0)  # ParamRY gate on qubit 0
        >>> gate = ParamRY(1, [0])  # Controlled-ParamRY

    Notes:
        If you need to use functions specific to the :class:`~scaluq.f64.ParamRYGate` class, please downcast it.
    """

def ParamRZ(target: int, coef: float = 1.0, controls: Sequence[int] = [], control_values: Sequence[int] = []) -> scaluq.scaluq_core.default.f64.ParamGate:
    """
    Generate general :class:`~scaluq.f64.ParamGate` class instance of :class:`~scaluq.f64.ParamRZGate`.

    Args:
        target (int):
            Target qubit index

        coef (float, optional):
            Parameter coefficient

        controls (list[int], optional):
            Control qubit indices

        control_values (list[int], optional):
            Control qubit values

    Returns:
        ParamGate:
            ParamRZ gate instance

    Examples:
        >>> gate = ParamRZ(0)  # ParamRZ gate on qubit 0
        >>> gate = ParamRZ(1, [0])  # Controlled-ParamRZ

    Notes:
        If you need to use functions specific to the :class:`~scaluq.f64.ParamRZGate` class, please downcast it.
    """

def ParamPauliRotation(pauli: scaluq.scaluq_core.default.f64.PauliOperator, coef: float = 1.0, controls: Sequence[int] = [], control_values: Sequence[int] = []) -> scaluq.scaluq_core.default.f64.ParamGate:
    """
    Generate general :class:`~scaluq.f64.ParamGate` class instance of :class:`~scaluq.f64.ParamPauliRotationGate`.

    Args:
        pauli (PauliOperator):
            Pauli operator

        coef (float, optional):
            Parameter coefficient

        controls (list[int], optional):
            Control qubit indices

        control_values (list[int], optional):
            Control qubit values

    Returns:
        ParamGate:
            ParamPauliRotation gate instance

    Examples:
        >>> gate = ParamPauliRotation(PauliOperator(), 0.5)  # Pauli rotation gate with PauliOperator and coefficient 0.5
        >>> gate = ParamPauliRotation(PauliOperator(), 0.5, [0])  # Controlled-ParamPauliRotation

    Notes:
        If you need to use functions specific to the :class:`~scaluq.f64.ParamPauliRotationGate` class, please downcast it.
    """

@overload
def ParamProbabilistic(distribution: Sequence[float], gate_list: Sequence[scaluq.scaluq_core.default.f64.Gate | scaluq.scaluq_core.default.f64.ParamGate]) -> scaluq.scaluq_core.default.f64.ParamGate:
    """
    Generate general :class:`~scaluq.f64.ParamGate` class instance of :class:`~scaluq.f64.ParamProbabilisticGate`.

    Args:
        distribution (list[float]):
            List of probability

        gate_list (list[Union[Gate, ParamGate]]):
            List of gates

    Returns:
        ParamGate:
            ParamProbabilistic gate instance

    Examples:
        >>> gate = ParamProbabilistic([0.1, 0.9], [X(0), ParamRX(0, 0.5)])  # probabilistic gate with X and ParamRX
    """

@overload
def ParamProbabilistic(prob_gate_list: Sequence[tuple[float, scaluq.scaluq_core.default.f64.Gate | scaluq.scaluq_core.default.f64.ParamGate]]) -> scaluq.scaluq_core.default.f64.ParamGate:
    """
    Generate general :class:`~scaluq.f64.ParamGate` class instance of :class:`~scaluq.f64.ParamProbabilisticGate`.

    Args:
        prob_gate_list (list[tuple[float, Union[Gate, ParamGate]]]):
            List of tuple of probability and gate

    Returns:
        ParamGate:
            ParamProbabilistic gate instance

    Examples:
        >>> gate = ParamProbabilistic([(0.1, X(0)), (0.9, I(0))])  # probabilistic gate with X and I
    """
