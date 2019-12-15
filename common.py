import asyncio
import os

from asyncio import StreamReader, StreamWriter


async def send_msg(writer: StreamWriter, msg: str):
    data = msg.encode()
    writer.write(len(data).to_bytes(4, byteorder='big'))
    writer.write(data)
    await writer.drain()


async def read_msg(reader: StreamReader) -> str:
    data = await reader.readexactly(4)
    size = int.from_bytes(data, byteorder='big')
    msg = await reader.readexactly(size)
    return msg.decode()


async def send_file(writer: StreamWriter, filename: str):
    size = os.path.getsize(filename)
    writer.write(size.to_bytes(4, byteorder='big'))
    with open(filename, 'rb') as f:
        writer.write(f.read())
    await writer.drain()


async def read_file(reader: StreamReader) -> bytes:
    data = await reader.readexactly(4)
    size = int.from_bytes(data, byteorder='big')
    return await reader.readexactly(size)


def run_server(client_cb, host, port):
    loop = asyncio.get_event_loop()
    coro = asyncio.start_server(client_cb, host, port)
    server = loop.run_until_complete(coro)

    # Serve requests until Ctrl+C is pressed
    print('Serving on {}'.format(server.sockets[0].getsockname()))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    server.close()
    loop.run_until_complete(server.wait_closed())
    loop.close()
