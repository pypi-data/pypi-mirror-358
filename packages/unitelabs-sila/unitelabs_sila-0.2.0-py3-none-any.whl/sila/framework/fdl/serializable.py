import collections.abc

import typing_extensions as typing

if typing.TYPE_CHECKING:
    from .deserializer import Deserializer
    from .serializer import Serializer


class Serializable(typing.Protocol):
    """Serialize this class into its xml representation and back."""

    @classmethod
    def serialize(cls, serializer: "Serializer") -> None:
        """
        Serialize the SiLA data type into the xml-based feature language definition.

        Args:
          serializer: The serializer instance used to write xml tokens.
        """
        ...

    @classmethod
    def deserialize(
        cls, deserializer: "Deserializer"
    ) -> collections.abc.Generator[None, typing.Any, type[typing.Self]]:
        """
        Deserialize the xml-based feature language definition into SiLA data types.

        Args:
          deserializer: The deserializer instance used to read xml
            tokens.

        Raises:
          ValueError: If an invalid or unexpected token is detected.
        """
        ...
