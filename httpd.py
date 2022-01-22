import argparse
import logging
import mimetypes
import multiprocessing
import os
import socket
import threading
from datetime import datetime
from typing import Optional, Tuple
from urllib.parse import unquote, urlparse

OK = 200
FORBIDDEN = 403
NOT_FOUND = 404
NOT_ALLOWED = 405

CODES_MAPPING = {
    OK: "OK",
    NOT_FOUND: "Not Found",
    FORBIDDEN: "Forbidden",
    NOT_ALLOWED: "Method Not Allowed",
}


class RequestHandler:
    _http_protocol = "HTTP/1.0"
    _server_name = "CustomWebServer"
    _buffer_size = 1024
    _base_delimiter = "\r\n"
    _head_delimiter = "\r\n\r\n"
    _encoding = "utf8"
    _index_file = "index.html"
    _methods = ("GET", "HEAD")

    def __init__(self, client_socket: socket.socket, address: str, document_root: str):
        self._socket = client_socket
        self._address = address
        self._document_root = document_root
        self._headers = {
            "Content-Type": "text/html",
            "Content-Length": "0",
            "Connection": "close",
            "Server": self._server_name,
            "Date": datetime.utcnow().isoformat(),
        }
        self.handle()

    def handle(self) -> None:
        try:
            request = self._read_request()
            response_code, method, path = self._parse_request(request)
            logging.info(f"Path: {path}")
            self._send_response(response_code, method, path)
        except socket.error as e:
            logging.info(f"Unable to handle request: {e}")
        finally:
            self._socket.close()

    def _read_request(self) -> str:
        buffer = ""
        while True:
            val = self._socket.recv(self._buffer_size)
            if not val:
                break
            buffer += val.decode(self._encoding)
            if val.endswith(self._head_delimiter.encode(self._encoding)):
                break
        return buffer

    def _parse_request(
        self, raw_request: str
    ) -> Tuple[int, Optional[str], Optional[str]]:
        try:
            request = raw_request.split("\r\n")
            method, url, protocol = request[0].split()
        except ValueError:
            return NOT_ALLOWED, None, None

        if method not in self._methods:
            return NOT_ALLOWED, None, None

        router = unquote(urlparse(url).path)
        if router.endswith("/"):
            router = os.path.join(router, self._index_file)
        path = self._document_root + os.path.realpath(router)
        logging.info(f"Path: {path}")
        if not os.path.isfile(path):
            return NOT_FOUND, method.upper(), path

        content_type, _ = mimetypes.guess_type(path)
        self._set_headers(("Content-Type", content_type))
        try:
            size = os.path.getsize(path)
            logging.info(size)
            self._set_headers(("Content-Length", str(size)))
        except os.error:
            return NOT_ALLOWED, None, None

        return OK, method.upper(), path

    def _set_headers(self, values: Tuple[str, str]) -> None:
        k, v = values
        self._headers[k] = v

    def _send_response(self, response_code: int, method: str, path: str) -> None:
        primary_line = (
            f"{self._http_protocol} {response_code} {CODES_MAPPING[response_code]}"
        )
        headers_line = self._base_delimiter.join(
            f"{k}: {v}" for k, v in self._headers.items()
        )
        body = ""
        if response_code == OK:
            body = self._get_response_body(path) if method == "GET" else ""
        resp = f"{primary_line}{self._base_delimiter}{headers_line}{self._head_delimiter}{body}"
        try:
            self._socket.sendall(resp.encode(self._encoding))
        except socket.error as e:
            logging.info(f"Unable to send response from socket: {e}")

    def _get_response_body(self, path: str = None) -> str:
        body = ""
        if not path:
            return body
        size = int(self._headers["Content-Length"])
        with open(path, "r") as f:
            body = f.read(size)
        return body


class WebServer:
    def __init__(self, host: str, port: int) -> None:
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._bind_server(host, port, reuse_address=True, reuse_port=True)
        self._activate_server(request_queue_size=5)

    def _bind_server(
        self, host: str, port: int, reuse_address: bool, reuse_port: bool
    ) -> None:
        """Called by init to bind the socket"""
        if reuse_address:
            self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        if reuse_port:
            self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        self._socket.bind((host, port))
        self.server_address = self._socket.getsockname()

    def _activate_server(self, request_queue_size: int) -> None:
        """Called by init to activate the server"""
        self._socket.listen(request_queue_size)

    def close(self) -> None:
        """Clean up the server"""
        self._socket.close()

    def serve_forever(
        self, request_handler: RequestHandler, document_root: str
    ) -> None:
        while True:
            try:
                client_socket, address = self._socket.accept()
                thread = threading.Thread(
                    target=request_handler,
                    args=(client_socket, address, document_root),
                    daemon=True,
                )
                thread.start()
            except socket.error as e:
                logging.info(f"Unable to accept socket connection: {e}")
                self.close()


def main(host: str, port: int, workers: int, document_root: str) -> None:
    processes = []
    try:
        for _ in range(workers):
            server = WebServer(host, port)
            process = multiprocessing.Process(
                target=server.serve_forever, args=(RequestHandler, document_root)
            )
            processes.append(process)
            process.start()
            logging.info(f"Started server on {host}:{port}")
        for process in processes:
            process.join()
    except KeyboardInterrupt:
        for process in processes:
            if process:
                process.terminate()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="HTTP server")
    parser.add_argument("-s", "--host", type=str, default="localhost")
    parser.add_argument("-p", "--port", type=int, default=8080)
    parser.add_argument("-w", "--workers", type=int, default=5)
    parser.add_argument("-r", "--document-root", default=".", help="document root")
    parser.add_argument("-l", "--log", action="store", default=None)
    args = parser.parse_args()
    logging.basicConfig(
        filename=args.log,
        level=logging.INFO,
        format="[%(asctime)s] %(levelname).1s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    main(args.host, args.port, args.workers, args.document_root)
