import collections.abc
import dataclasses
import enum

import typing_extensions as typing

from ..data_types.integer import Integer
from ..data_types.real import Real
from ..fdl import Characters, Deserializer, EndElement, Serializer, StartElement
from .constraint import Constraint

if typing.TYPE_CHECKING:
    from ..data_types import BasicType, List

T = typing.TypeVar("T", int, float)


class SIUnit(str, enum.Enum):
    """
    Enumeration of SI units used in measurement.

    This enumeration defines the standard SI units that can be used
    for measurements, including both base and derived units.
    """

    DIMENSIONLESS = "Dimensionless"
    """Represents a dimensionless quantity."""

    METER = "Meter"
    """Represents the meter (m) unit of length."""

    KILOGRAM = "Kilogram"
    """Represents the kilogram (kg) unit of mass."""

    SECOND = "Second"
    """Represents the second (s) unit of time."""

    AMPERE = "Ampere"
    """Represents the ampere (A) unit of electric current."""

    KELVIN = "Kelvin"
    """Represents the kelvin (K) unit of temperature."""

    MOLE = "Mole"
    """Represents the mole (mol) unit of amount of substance."""

    CANDELA = "Candela"
    """Represents the candela (cd) unit of luminous intensity."""


class UnitComponent(typing.NamedTuple):
    """
    Represents a component of a unit in terms of its base unit and
    exponent.

    This named tuple defines a base unit and its exponent, allowing
    for the representation of complex units through their components.

    Args:
      unit: The base unit represented as a string (e.g., 'Meter').
      exponent: The exponent to which the base unit is raised,
    """

    unit: typing.Literal[
        "Dimensionless",
        "Meter",
        "Kilogram",
        "Second",
        "Ampere",
        "Kelvin",
        "Mole",
        "Candela",
    ]
    """
    The base unit represented as a string (e.g., 'Meter').
    """

    exponent: int = 1
    """
    The exponent to which the base unit is raised.
    """


@dataclasses.dataclass
class Unit(Constraint[T]):
    """
    A constraint that defines a unit of measurement with its label
    and components.

    This class allows for the definition of units of measurement
    including their label, components, scaling factor, and offset. It
    ensures that the label does not exceed a specified length.

    Args:
      label: A string representing the label of the unit.
      components: A sequence of `UnitComponent` defining the
        composition of the unit.
      factor: A scaling factor for the unit.
      offset: An offset value for the unit.

    Raises:
      ValueError: If the length of the label exceeds 255 characters.
    """

    Component: typing.ClassVar[type[UnitComponent]] = UnitComponent
    """
    Represents a component of a unit in terms of its base unit and
    exponent.
    """

    SI: typing.ClassVar[type[SIUnit]] = SIUnit
    """
    Enumeration of SI units used in measurement.
    """

    label: str
    """
    A string representing the label of the unit.
    """

    components: collections.abc.Sequence[UnitComponent]
    """
    A sequence of `UnitComponent` defining the composition of the
    unit.
    """

    factor: float = 1
    """
    A scaling factor for the unit (default is 1).
    """

    offset: float = 0
    """
    An offset value for the unit (default is 0).
    """

    def __post_init__(self):
        if len(self.label) > 255:
            raise ValueError("The length of the label must not exceed 255 characters.")

        self.components = [
            UnitComponent(
                component.unit.value if isinstance(component.unit, SIUnit) else component.unit, component.exponent
            )
            for component in self.components
        ]

    async def validate(self, value: T) -> bool:
        if not isinstance(value, (int, float)):
            raise TypeError(f"Expected value of type 'int' or 'float', received '{type(value).__name__}'.")

        return True

    def serialize(self, serializer: Serializer) -> None:
        serializer.start_element("Unit")
        serializer.write_str("Label", self.label)
        serializer.write_float("Factor", self.factor)
        serializer.write_float("Offset", self.offset)
        for component in self.components:
            serializer.start_element("UnitComponent")
            serializer.write_str("SIUnit", component.unit)
            serializer.write_int("Exponent", component.exponent)
            serializer.end_element("UnitComponent")

        serializer.end_element("Unit")

    @classmethod
    def deserialize(
        cls, deserializer: Deserializer, data_type: typing.Union[type["BasicType"], type["List"]]
    ) -> collections.abc.Generator[None, typing.Any, typing.Self]:
        if not issubclass(data_type, (Integer, Real)):
            raise ValueError(
                f"Expected constraint's data type to be 'Integer' or 'Real', received '{data_type.__name__}'."
            )

        yield from deserializer.read_start_element(name="Unit")

        # Label
        yield from deserializer.read_start_element(name="Label")
        label = yield from deserializer.read_str()
        yield from deserializer.read_end_element(name="Label")

        # Factor
        yield from deserializer.read_start_element(name="Factor")
        factor = yield from deserializer.read_float()
        yield from deserializer.read_end_element(name="Factor")

        # Offset
        yield from deserializer.read_start_element(name="Offset")
        offset = yield from deserializer.read_float()
        yield from deserializer.read_end_element(name="Offset")

        components: list[UnitComponent] = []
        while True:
            token = yield

            if isinstance(token, StartElement):
                if token.name == "UnitComponent":
                    # SIUnit
                    yield from deserializer.read_start_element("SIUnit")
                    unit = yield from deserializer.read_str()
                    try:
                        unit = Unit.SI(unit).value
                    except ValueError:
                        raise ValueError(f"Expected a valid 'SIUnit' value, received '{unit}'.") from None
                    yield from deserializer.read_end_element("SIUnit")

                    # Exponent
                    yield from deserializer.read_start_element("Exponent")
                    exponent = yield from deserializer.read_int()
                    yield from deserializer.read_end_element("Exponent")

                    components.append(UnitComponent(unit, exponent))
                else:
                    raise ValueError(
                        f"Expected start element with name 'UnitComponent', received start element with name '{token.name}'."
                    )

            elif isinstance(token, EndElement):
                if token.name == "UnitComponent":
                    continue
                else:
                    break  # pragma: no cover

            elif isinstance(token, Characters):
                raise ValueError(
                    f"Expected start element with name 'UnitComponent', received characters '{token.value}'."
                )

        if not components:
            raise ValueError("Expected at least one 'UnitComponent' element inside the 'Unit' element.")

        return cls(label, components, factor, offset)
