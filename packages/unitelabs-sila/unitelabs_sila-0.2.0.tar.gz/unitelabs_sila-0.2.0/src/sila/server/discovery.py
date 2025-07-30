import contextlib
import ipaddress
import logging
import socket
import weakref

import typing_extensions as typing
import zeroconf.asyncio

if typing.TYPE_CHECKING:
    from .server import Server


class Discovery:
    """
    Promotes the provided server on the network.

    In order to provide a true zero-configuration experience, this
    implements multicast DNS (mDNS) and DNS-based Service Discovery
    (DNS-SD). It broadcasts the socket address on which the grpc
    server is available, some metadata about the server and
    optionally the server certificate.

    Args:
      server: The server to promote on the network.
    """

    def __init__(self, server: "Server"):
        self._server: "Server" = weakref.proxy(server)

        self.mdns = zeroconf.asyncio.AsyncZeroconf(interfaces=zeroconf.InterfaceChoice.Default)

    @property
    def logger(self) -> logging.Logger:
        """A python logger instance."""

        return logging.getLogger(__name__)

    async def start(self) -> None:
        """Start broadcasting the service on mDNS."""

        await self._server.wait_for_ready()
        service = Discovery.create_service(self._server)

        await self.mdns.zeroconf.async_wait_for_start()
        await self.mdns.async_register_service(service)
        self.logger.info("Registered service for discovery.")

    async def stop(self) -> None:
        """Stop broadcasting the service on mDNS."""

        await self.mdns.async_unregister_all_services()
        await self.mdns.async_close()
        self.logger.info("Removed service from discovery.")

    @classmethod
    def find_ip_address(cls, address: str) -> str:
        """
        Return a valid ip address for a given hostname or address.

        Args:
            address: A hostname or address, e.g. `localhost` or `0.0.0.0`.

        Returns:
            A valid ip address that represents the given address.
        """
        if address == "0.0.0.0":
            ip_address = "127.0.0.1"
            with contextlib.suppress(OSError):
                ip_address = socket.gethostbyname(socket.gethostname())

            if ip_address == "127.0.0.1":
                connection = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                connection.settimeout(0)
                with contextlib.suppress(OSError):
                    connection.connect(("8.8.8.8", 80))
                ip_address = next(iter(connection.getsockname()), ip_address)

            return ip_address

        try:
            return ipaddress.ip_address(address).exploded
        except ValueError:
            try:
                return socket.gethostbyname(address)
            except OSError:
                return "127.0.0.1"

    @classmethod
    def create_service(cls, server: "Server") -> zeroconf.asyncio.AsyncServiceInfo:
        """Create zeroconf service info from the given server."""

        properties = {
            "version": server.version.encode("utf-8")[:247],
            "server_name": server.name.encode("utf-8")[:243],
            "description": server.description.encode("utf-8")[:243],
        }

        if server._config.get("tls", True):
            certificate = server._config.get("certificate_chain", None)
            if certificate:
                properties.update({f"ca{i}": line for i, line in enumerate(certificate.splitlines(keepends=False))})

        hostname, _, port = server._address.rpartition(":")

        return zeroconf.asyncio.AsyncServiceInfo(
            type_="_sila._tcp.local.",
            name=f"{server.uuid}._sila._tcp.local.",
            parsed_addresses=[Discovery.find_ip_address(hostname)],
            port=int(port),
            properties=properties,
        )
