#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import asyncio
import socket
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Optional, Sequence

import thrift.py3.server
from folly.iobuf import IOBuf
from stack_args.clients import StackService
from stack_args.services import StackServiceInterface
from stack_args.types import simple
from testing.clients import TestingService
from testing.services import TestingServiceInterface
from testing.types import Color, easy
from thrift.py3 import (
    Protocol,
    RequestContext,
    RpcOptions,
    ThriftServer,
    TransportError,
    get_client,
    get_context,
)
from thrift.py3.client import ClientType


class Handler(TestingServiceInterface):
    @TestingServiceInterface.pass_context_invert
    async def invert(self, ctx: RequestContext, value: bool) -> bool:
        if "from client" in ctx.read_headers:
            ctx.set_header("from server", "with love")
        return not value

    async def getName(self) -> str:
        if sys.version_info[:2] >= (3, 7):
            ctx = get_context()
            ctx.set_header("contextvar", "true")
        return "Testing"

    async def shutdown(self) -> None:
        pass

    async def complex_action(
        self, first: str, second: str, third: int, fourth: str
    ) -> int:
        return third

    async def takes_a_list(self, ints: Sequence[int]) -> None:
        pass

    async def take_it_easy(self, how: int, what: easy) -> None:
        pass

    async def pick_a_color(self, color: Color) -> None:
        pass

    async def int_sizes(self, one: int, two: int, three: int, four: int) -> None:
        pass


class TestServer:
    server: ThriftServer
    serve_task: asyncio.Task

    def __init__(
        self,
        ip: Optional[str] = None,
        path: Optional["thrift.py3.server.Path"] = None,
        handler: thrift.py3.server.ServiceInterface = Handler(),  # noqa: B008
    ) -> None:
        self.server = ThriftServer(handler, ip=ip, path=path)

    async def __aenter__(self) -> thrift.py3.server.SocketAddress:
        self.serve_task = asyncio.get_event_loop().create_task(self.server.serve())
        return await self.server.get_address()

    async def __aexit__(self, *exc_info) -> None:
        self.server.stop()
        await self.serve_task


class ClientServerTests(unittest.TestCase):
    """
    These are tests where a client and server talk to each other
    """

    @unittest.skipIf(sys.version_info[:2] < (3, 7), "Requires py3.7")
    def test_get_context(self) -> None:
        loop = asyncio.get_event_loop()

        async def inner_test() -> None:
            async with TestServer(ip="::1") as sa:
                assert sa.ip and sa.port
                async with get_client(
                    TestingService, host=sa.ip, port=sa.port
                ) as client:
                    options = RpcOptions()
                    self.assertEqual(
                        "Testing", await client.getName(rpc_options=options)
                    )
                    self.assertEqual("true", options.read_headers["contextvar"])

        loop.run_until_complete(inner_test())

        async def outside_context_test() -> None:
            handler = Handler()  # so we can call it outside the thrift server
            with self.assertRaises(LookupError):
                await handler.getName()

        loop.run_until_complete(outside_context_test())

    def test_rpc_headers(self) -> None:
        loop = asyncio.get_event_loop()

        async def inner_test() -> None:
            async with TestServer(ip="::1") as sa:
                assert sa.ip and sa.port
                async with get_client(
                    TestingService, host=sa.ip, port=sa.port
                ) as client:
                    options = RpcOptions()
                    options.set_header("from client", "with love")
                    self.assertFalse(await client.invert(True, rpc_options=options))
                    self.assertIn("from server", options.read_headers)

        loop.run_until_complete(inner_test())

    def test_client_resolve(self) -> None:
        loop = asyncio.get_event_loop()
        hostname = socket.gethostname()

        async def inner_test() -> None:
            async with TestServer() as sa:
                assert sa.port
                async with get_client(
                    TestingService, host=hostname, port=sa.port
                ) as client:
                    self.assertTrue(await client.invert(False))
                    self.assertFalse(await client.invert(True))

        loop.run_until_complete(inner_test())

    def test_unframed_binary(self) -> None:
        loop = asyncio.get_event_loop()

        async def inner_test() -> None:
            async with TestServer(ip="::1") as sa:
                assert sa.ip and sa.port
                async with get_client(
                    TestingService,
                    host=sa.ip,
                    port=sa.port,
                    client_type=ClientType.THRIFT_UNFRAMED_DEPRECATED,
                    protocol=Protocol.BINARY,
                ) as client:
                    self.assertTrue(await client.invert(False))
                    self.assertFalse(await client.invert(True))

        loop.run_until_complete(inner_test())

    def test_framed_deprecated(self) -> None:
        loop = asyncio.get_event_loop()

        async def inner_test() -> None:
            async with TestServer(ip="::1") as sa:
                assert sa.ip and sa.port
                async with get_client(
                    TestingService,
                    host=sa.ip,
                    port=sa.port,
                    client_type=ClientType.THRIFT_FRAMED_DEPRECATED,
                ) as client:
                    self.assertTrue(await client.invert(False))
                    self.assertFalse(await client.invert(True))

        loop.run_until_complete(inner_test())

    def test_framed_compact(self) -> None:
        loop = asyncio.get_event_loop()

        async def inner_test() -> None:
            async with TestServer(ip="::1") as sa:
                assert sa.ip and sa.port
                async with get_client(
                    TestingService,
                    host=sa.ip,
                    port=sa.port,
                    client_type=ClientType.THRIFT_FRAMED_COMPACT,
                ) as client:
                    self.assertTrue(await client.invert(False))
                    self.assertFalse(await client.invert(True))

        loop.run_until_complete(inner_test())

    def test_http_endpoint(self) -> None:
        loop = asyncio.get_event_loop()

        async def inner_test() -> None:
            async with TestServer(ip="::1") as sa:
                assert sa.ip and sa.port
                async with get_client(
                    TestingService,
                    host=sa.ip,
                    port=sa.port,
                    path="/some/endpoint",
                    client_type=ClientType.THRIFT_HTTP_CLIENT_TYPE,
                ) as client:
                    try:
                        self.assertTrue(await client.invert(False))
                    except TransportError as err:
                        # The test server gets an invalid request because its a HTTP request
                        self.assertEqual(err.type.value, 4)  # END OF FILE

        loop.run_until_complete(inner_test())

    def test_server_localhost(self) -> None:
        loop = asyncio.get_event_loop()

        async def inner_test() -> None:
            async with TestServer(ip="::1") as sa:
                assert sa.ip and sa.port
                async with get_client(
                    TestingService, host=sa.ip, port=sa.port
                ) as client:
                    self.assertTrue(await client.invert(False))
                    self.assertFalse(await client.invert(True))

        loop.run_until_complete(inner_test())

    def test_unix_socket(self) -> None:
        loop = asyncio.get_event_loop()

        async def inner_test(dir: Path) -> None:
            async with TestServer(path=dir / "tserver.sock") as sa:
                assert sa.path
                async with get_client(TestingService, path=sa.path) as client:
                    self.assertTrue(await client.invert(False))
                    self.assertFalse(await client.invert(True))

        with tempfile.TemporaryDirectory() as tdir:
            loop.run_until_complete(inner_test(Path(tdir)))

    def test_no_client_aexit(self) -> None:
        loop = asyncio.get_event_loop()

        async def inner_test() -> None:
            async with TestServer() as sa:
                assert sa.port and sa.ip
                client = get_client(TestingService, host=sa.ip, port=sa.port)
                await client.__aenter__()
                self.assertTrue(await client.invert(False))
                self.assertFalse(await client.invert(True))

        # If we do not abort here then good

        loop.run_until_complete(inner_test())

    def test_client_aexit_cancel(self) -> None:
        """
        This actually handles the case if __aexit__ is not awaited
        """
        loop = asyncio.get_event_loop()

        async def inner_test() -> None:
            async with TestServer() as sa:
                assert sa.port and sa.ip
                client = get_client(TestingService, host=sa.ip, port=sa.port)
                await client.__aenter__()
                self.assertTrue(await client.invert(False))
                self.assertFalse(await client.invert(True))
                fut = client.__aexit__(None, None, None)
                fut.cancel()  # type: ignore
                del client  # If we do not abort here then good

        loop.run_until_complete(inner_test())

    def test_no_client_no_aenter(self) -> None:
        """
        This covers if aenter was canceled since those two are the same really
        """
        loop = asyncio.get_event_loop()

        async def inner_test() -> None:
            async with TestServer() as sa:
                assert sa.port and sa.ip
                get_client(TestingService, host=sa.ip, port=sa.port)

        # If we do not abort here then good

        loop.run_until_complete(inner_test())


class StackHandler(StackServiceInterface):
    async def add_to(self, lst: Sequence[int], value: int) -> Sequence[int]:
        return [x + value for x in lst]

    async def get_simple(self) -> simple:
        return simple(val=66)

    async def take_simple(self, smpl: simple) -> None:
        if smpl.val != 10:
            raise Exception("WRONG")

    async def get_iobuf(self) -> IOBuf:
        return IOBuf(b"abc")

    async def take_iobuf(self, iobuf: IOBuf) -> None:
        if bytes(iobuf) != b"cba":
            raise Exception("WRONG")

    # currently unsupported by cpp backend:
    # async def get_iobuf_ptr(self) -> IOBuf:
    #     return IOBuf(b'xyz')

    async def take_iobuf_ptr(self, iobuf_ptr: IOBuf) -> None:
        if bytes(iobuf_ptr) != b"zyx":
            raise Exception("WRONG")


class ClientStackServerTests(unittest.TestCase):
    """
    These are tests where a client and server(stack_arguments) talk to each other
    """

    def test_server_localhost(self) -> None:
        loop = asyncio.get_event_loop()

        async def inner_test() -> None:
            async with TestServer(handler=StackHandler(), ip="::1") as sa:
                assert sa.ip and sa.port
                async with get_client(StackService, host=sa.ip, port=sa.port) as client:
                    self.assertEqual(
                        (3, 4, 5, 6), await client.add_to(lst=(1, 2, 3, 4), value=2)
                    )
                    self.assertEqual(66, (await client.get_simple()).val)
                    await client.take_simple(simple(val=10))
                    self.assertEqual(b"abc", bytes(await client.get_iobuf()))
                    await client.take_iobuf(IOBuf(b"cba"))
                    # currently unsupported by cpp backend:
                    # self.assertEqual(b'xyz', (await client.get_iobuf_ptr()))
                    await client.take_iobuf_ptr(IOBuf(b"zyx"))

        loop.run_until_complete(inner_test())
