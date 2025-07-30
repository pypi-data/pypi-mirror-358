import enum
from typing import Annotated

from numpy.typing import ArrayLike


class fixed_dimensional_encoding_config:
    """
    Configuration for fixed-dimensional encoding of multi-dimensional vectors
    """

    def __init__(self) -> None: ...

    def set_num_repetitions(self, r: int) -> fixed_dimensional_encoding_config: ...

    def set_num_simhash_projections(self, k: int) -> fixed_dimensional_encoding_config: ...

    def set_seed(self, s: int) -> fixed_dimensional_encoding_config: ...

    def set_encoding_type(self, type: encoding_type) -> fixed_dimensional_encoding_config: ...

    def set_projection_dimension(self, dp: int) -> fixed_dimensional_encoding_config: ...

    def set_projection_type(self, pt: projection_type) -> fixed_dimensional_encoding_config: ...

    def enable_fill_empty(self, v: bool = True) -> fixed_dimensional_encoding_config: ...

    def set_final_projection_dimension(self, d: int) -> fixed_dimensional_encoding_config: ...

    @property
    def num_repetitions(self) -> int: ...

    @property
    def num_simhash_projections(self) -> int: ...

    @property
    def seed(self) -> int: ...

    @property
    def projection_dimension(self) -> int: ...

    @property
    def fill_empty_partitions(self) -> bool: ...

    @property
    def final_projection_dimension(self) -> int: ...

    @property
    def encoding_type(self) -> encoding_type: ...

    @property
    def projection_type(self) -> projection_type: ...

class encoding_type(enum.Enum):
    """
    Encoding types for fixed-dimensional encoding of multi-dimensional vectors
    """

    DEFAULT_SUM = 0

    AVERAGE = 1

DEFAULT_SUM: encoding_type = encoding_type.DEFAULT_SUM

AVERAGE: encoding_type = encoding_type.AVERAGE

class projection_type(enum.Enum):
    """
    Projection types for fixed-dimensional encoding of multi-dimensional vectors
    """

    DEFAULT_IDENTITY = 0

    AMS_SKETCH = 1

DEFAULT_IDENTITY: projection_type = projection_type.DEFAULT_IDENTITY

AMS_SKETCH: projection_type = projection_type.AMS_SKETCH

def generate_fixed_dimensional_encoding(input_embedding_matrix: Annotated[ArrayLike, dict(dtype='float32', shape=(None, None), writable=False)], config: fixed_dimensional_encoding_config) -> Annotated[ArrayLike, dict(dtype='float32', shape=(None), order='C')]:
    """
    Generates a fixed-dimensional encoding for the input embedding matrix using the provided configuration.
    """
