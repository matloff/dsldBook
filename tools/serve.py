#!/usr/bin/env python3
"""Serve the built book locally, allowing bursts of asset/font requests."""

import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


class BookServer(ThreadingHTTPServer):
    # Python's default queue of five can reset parallel browser requests.
    request_queue_size = 128


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=8765)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1] / 'docs'
    if not (root / 'index.html').exists():
        parser.error('No rendered book found. Run make html first.')
    handler = partial(SimpleHTTPRequestHandler, directory=str(root))
    with BookServer(('127.0.0.1', args.port), handler) as server:
        print(f'Book preview: http://127.0.0.1:{args.port}', flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == '__main__':
    main()
