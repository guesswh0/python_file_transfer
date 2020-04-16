# asyncio_file_transfer

Used to asynchronously send chunks of archived file from client to server

## Usage:

### Start server 
    python server.py [options] ... [--dir | --host | --port]

### Archive file
    python archiver.py [options] ... [-d, --dest | -s, --chunk-size] file
    
### Send files from path to server
    python client.py [options] ... [--host | --port] path
