import argparse
import asyncio
import os
from pathlib import PurePosixPath

import tqdm

from common import send_file, send_msg


async def client(path, host, port):
    reader, writer = await asyncio.open_connection(host, port)
    files = os.listdir(path)
    files.sort()

    # send file name
    file_name = PurePosixPath(files[-1]).stem
    await send_msg(writer, file_name)

    # send file size
    with open(os.path.join(path, files[-1]), 'r') as marker:
        size = marker.read()
        await  send_msg(writer, size)

    # progress bar
    progress = tqdm.tqdm(desc=f"Sending: {file_name}", total=len(files) - 1)

    # send path files
    for file in files[:-1]:
        await send_file(writer, os.path.join(path, file))
        progress.update()

    print("Close the socket")
    writer.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('path', help="Files directory path")
    parser.add_argument('--host', help="Server host", default='127.0.0.1')
    parser.add_argument('--port', help="Server port", type=int, default=5001)
    args = parser.parse_args()

    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(client(args.path, args.host, args.port))
    except KeyboardInterrupt:
        loop.close()
