import collections.abc
import dataclasses

import typing_extensions as typing

from .property import Property


@dataclasses.dataclass
class ObservableProperty(Property):
    """A property describes certain aspects of a SiLA server that do not require an action on the SiLA server."""

    observable: bool = dataclasses.field(init=False, repr=False, default=True)

    def subscribe(self, metadata: typing.Optional[dict] = None) -> collections.abc.AsyncIterator[bytes]:
        """
        Subscribe to value changes of the property.

        Args:
          metadata: Additional metadata sent from client to server.

        Yields:
          The current value of the property.

        Raises:
          NoMetadataAllowed: If providing metadata is not allowed.
          InvalidMetadata: If metadata is missing or invalid.
          DefinedExecutionError: If property access results in a defined
            execution error
          UnefinedExecutionError: If property access results in an
            undefined execution error.
        """

        raise NotImplementedError
