import asyncio
import os
import sys

import click
import tqdm


async def dispatcher(path, host, port, **kwargs):
    files = sorted(os.listdir(path))
    # check if path contains marker file
    if not files[-1].endswith('.done'):
        raise RuntimeError(f"'{path}' path does't contain marker file")

    reader, writer = await asyncio.open_connection(host, port, **kwargs)
    marker_file = files.pop()
    file_name = marker_file[:-5]
    with open(os.path.join(path, marker_file), 'r') as marker:
        file_size = int(marker.read())

    # write package as [total_len|file_size|file_name]
    writer.write((4 + len(file_name)).to_bytes(1, sys.byteorder))
    writer.write(file_size.to_bytes(4, sys.byteorder))
    writer.write(file_name.encode('utf-8'))
    await writer.drain()

    # progress bar
    progress = tqdm.tqdm(desc=f"Sending: {file_name}", total=len(files))

    # send path files
    for name in files:
        file = os.path.join(path, name)
        size = os.path.getsize(file)
        writer.write(size.to_bytes(4, sys.byteorder))
        with open(file, 'rb') as f:
            writer.write(f.read())
        await writer.drain()
        progress.update()

    progress.close()
    writer.close()


@click.command()
@click.argument('path')
@click.option('--host', help='server host', default='127.0.0.1')
@click.option('--port', help='server port', type=int, default=5001)
def client(path, host, port):
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(dispatcher(path, host, port))
    except KeyboardInterrupt:
        loop.close()


if __name__ == '__main__':
    client()
