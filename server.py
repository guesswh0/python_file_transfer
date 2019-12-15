import argparse
import os
import gzip

import tqdm

from common import run_server, read_file, read_msg

# Working directory
DIR = '.'


async def server(reader, writer):
    addr = writer.get_extra_info('peername')
    print(f"Client connected from {addr}")

    file_name = await read_msg(reader)
    file_size = int(await read_msg(reader))

    progress = tqdm.tqdm(
        range(file_size),
        desc=f"Receiving: {file_name}",
        unit='B',
        unit_scale=True,
        unit_divisor=1024
    )

    with open(os.path.join(DIR, file_name), 'wb') as f:
        while file_size:
            data = gzip.decompress(await read_file(reader))
            f.write(data)
            progress.update(len(data))
            file_size -= len(data)

    print(f"Closing connection with {addr}")
    writer.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--dir', help='Working directory', default='.')
    parser.add_argument('--host', help='Server host', default='127.0.0.1')
    parser.add_argument('--port', help='Server port', type=int, default=5001)
    args = parser.parse_args()
    DIR = args.dir

    run_server(server, args.host, args.port)
