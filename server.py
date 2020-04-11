import asyncio
import gzip
import logging
import os
import shutil
import sys
import tempfile

import click
import tqdm

logger = logging.getLogger(__name__)


class FileServer:
    def __init__(self, dir_, host, port, **kwargs):
        self.files_dir = dir_
        self.server_host = host
        self.server_port = port
        self.server = asyncio.start_server(
            client_connected_cb=self.handle_client,
            host=self.server_host,
            port=self.server_port,
            **kwargs
        )

    async def handle_client(self, reader, writer):
        addr = writer.get_extra_info('peername')
        logger.info("new connection from %s", addr)

        package_len = int.from_bytes(await reader.readexactly(1), sys.byteorder)
        file_size = int.from_bytes(await reader.readexactly(4), sys.byteorder)
        file_name = (await reader.readexactly(package_len - 4)).decode('utf-8')

        progress = tqdm.tqdm(
            range(file_size),
            desc=f"Receiving: {file_name}",
            unit='B',
            unit_scale=True,
            unit_divisor=1024
        )

        file = tempfile.NamedTemporaryFile(delete=False)
        while file_size:
            size = int.from_bytes(await reader.readexactly(4), sys.byteorder)
            data = gzip.decompress(await reader.readexactly(size))
            file.write(data)
            progress.update(len(data))
            file_size -= len(data)
        file.close()
        shutil.move(file.name, os.path.join(self.files_dir, file_name))

        logger.info("closing connection from %s", addr)
        writer.close()


@click.command()
@click.option('--dir', help='working directory', default='out')
@click.option('--host', help='server host', default='127.0.0.1')
@click.option('--port', help='server port', type=int, default=5001)
def server(dir, host, port):
    file_server = FileServer(dir, host, port)
    loop = asyncio.get_event_loop()
    serv = loop.run_until_complete(file_server.server)
    # Serve requests until Ctrl+C is pressed
    print('Serving on {}'.format(serv.sockets[0].getsockname()))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    serv.close()
    loop.run_until_complete(serv.wait_closed())
    loop.close()


if __name__ == '__main__':
    server()
