import enum

from . import default as default


def finalize() -> None:
    """
    Terminate the Kokkos execution environment. Release the resources.

    Notes:
        Finalization fails if there exists `StateVector` allocated. You must use `StateVector` only inside inner scopes than the usage of `finalize` or delete all of existing `StateVector`.

        This is automatically called when the program exits. If you call this manually, you cannot use most of scaluq's functions until the program exits.
    """

def is_finalized() -> bool:
    """Return true if :func:`~scaluq.finalize()` is already called."""

class GateType(enum.Enum):
    """Enum of Gate Type."""

    I = 1

    GlobalPhase = 2

    X = 3

    Y = 4

    Z = 5

    H = 6

    S = 7

    Sdag = 8

    T = 9

    Tdag = 10

    SqrtX = 11

    SqrtXdag = 12

    SqrtY = 13

    SqrtYdag = 14

    P0 = 15

    P1 = 16

    RX = 17

    RY = 18

    RZ = 19

    U1 = 20

    U2 = 21

    U3 = 22

    Swap = 23

    Pauli = 24

    PauliRotation = 25

    SparseMatrix = 26

    DenseMatrix = 27

    Probabilistic = 28

class ParamGateType(enum.Enum):
    """Enum of ParamGate Type."""

    ParamRX = 1

    ParamRY = 2

    ParamRZ = 3

    ParamPauliRotation = 4

def get_default_execution_space() -> str:
    """
    Get the default execution space.

    Returns:
        str:
            the default execution space, `cuda` or `host`

    Examples:
        >>> get_default_execution_space()
        'cuda'
    """

def precision_available(arg: str, /) -> bool:
    """
    Return the precision is supported.

    Args:
        precision (str):
            precision name

            This must be one of `f16` `f32` `f64` `bf16`.

    Returns:
        bool:
            the precision is supported

    Examples:
        >>> precision_available('f64')
        True
        >>> precision_available('bf16')
        False
    """
