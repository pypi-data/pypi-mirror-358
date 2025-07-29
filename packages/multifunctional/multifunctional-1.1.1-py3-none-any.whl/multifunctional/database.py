from typing import Optional

from bw2data.backends import SQLiteBackend
from bw2data.backends.schema import ActivityDataset

from .node_dispatch import multifunctional_node_dispatcher
from .utils import add_exchange_input_if_missing, label_multifunctional_nodes


def multifunctional_dispatcher_method(
    db: "MultifunctionalDatabase", document: Optional[ActivityDataset] = None
):
    return multifunctional_node_dispatcher(document)


SIMAPRO_ATTRIBUTES = (
    "simapro_project",
    "simapro_libraries",
    "simapro_filepath",
    "simapro_version",
    "simapro_csv_version",
)


class MultifunctionalDatabase(SQLiteBackend):
    """A database which includes multifunctional processes (i.e. processes which have more than one
    functional input and/or output edge). Such multifunctional processes normally break square
    matrix construction, so need to be resolved in some way.

    We support three options:

    * Mark the process as `"skip_allocation"=True`. You have manually constructed the database so
        that is produces a valid technosphere matrix, by e.g. having two multifunctional processes
        with the same two functional edge products.
    * Using substitution, so that a functional edge corresponds to the same functional edge in
        another process, e.g. combined heat and power produces two functional products, but the
        heat product is also produced by another process, so the amount of that other process would
        be decreased.
    * Using allocation, and splitting a multifunctional process in multiple read-only single output
        unit processes. The strategy used for allocation can be changed dynamically to investigate
        the impact of different allocation approaches.

    This class uses custom `Node` classes for multifunctional processes and read-only single-output
    unit processes.

    Stores default allocation strategies per database in the `Database` metadata dictionary:

    * `default_allocation`: str. Reference to function in `multifunctional.allocation_strategies`.

    Each database has one default allocation, but individual processes can also have specific
    default allocation strategies in `MultifunctionalProcess['default_allocation']`.

    Allocation strategies need to reference a process `property`. See the README.

    """

    backend = "multifunctional"
    node_class = multifunctional_dispatcher_method

    def write(self, data: dict, **kwargs) -> None:
        data = label_multifunctional_nodes(add_exchange_input_if_missing(data))
        super().write(data, **kwargs)

    def process(self, csv: bool = False, allocate: bool = True) -> None:
        if allocate:
            is_simapro = any(
                key in self.metadata for key in SIMAPRO_ATTRIBUTES
            ) or self.metadata.get("products_as_process")

            for node in filter(lambda x: x.multifunctional, self):
                node.allocate(products_as_process=is_simapro)
        super().process(csv=csv)
