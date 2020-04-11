import gzip
import os

import click


@click.command()
@click.argument('file')
@click.option('-d', '--dest', help="destination folder", default='data')
@click.option('-s', '--chunk-size', type=int, help="arhive chunk sizes",
              default=1024 * 1024)
def archiver(file, dest, chunk_size):
    # mkdir if dest not exists
    if not os.path.isdir(dest):
        os.mkdir(dest)
    file_size = os.path.getsize(file)
    file_name = os.path.basename(file)
    output = os.path.join(dest, file_name)
    with open(file, 'rb') as in_file:
        counter = 0
        size = 0
        while size < file_size:
            with gzip.open(output + '-%07d.gz' % counter, 'wb') as out_file:
                out_file.write(in_file.read(chunk_size))
            counter += 1
            size += chunk_size
        with open(output + '.done', 'w') as done:
            done.write(str(file_size))


if __name__ == '__main__':
    archiver()
