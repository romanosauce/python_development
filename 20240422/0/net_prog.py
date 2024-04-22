from prog import sqroots
import asyncio
import socket


async def echo(reader, writer):
    data = await reader.readline()
    try:
        msg = sqroots(data.decode())
    except Exception:
        msg = ""
    msg += '\n'
    writer.write(msg.encode())
    writer.close()
    await writer.wait_closed()


async def main():
    server = await asyncio.start_server(echo, '0.0.0.0', 1337)
    async with server:
        await server.serve_forever()


def sqrootnet(coeffs: str, s: socket.socket) -> str:
    s.sendall((coeffs + "\n").encode())
    return s.recv(128).decode().strip()


def client(port):
    coeffs = input(">")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(("localhost", port))
        res = sqrootnet(coeffs, s)
    print(res)


if __name__ == "__main__":
    asyncio.run(main())
