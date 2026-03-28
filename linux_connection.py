"""
通过 SSH 连接远程 Linux 主机并执行命令的示例。

依赖: pip install -r requirements.txt
"""

from __future__ import annotations

import socket
from typing import Optional

import paramiko


def connect_linux_ssh(
    host: str,
    username: str,
    *,
    port: int = 22,
    password: Optional[str] = None,
    key_filename: Optional[str] = None,
    timeout: float = 10.0,
) -> paramiko.SSHClient:
    """
    建立到 Linux 主机的 SSH 连接，返回已连接的 SSHClient。

    认证方式二选一（或同时提供，按 Paramiko 默认顺序尝试）:
    - password: 密码登录
    - key_filename: 私钥文件路径（如 ~/.ssh/id_rsa）

    使用完毕后请调用 client.close()，或使用下方 run_remote_command 的上下文方式。
    """
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    connect_kwargs: dict = {
        "hostname": host,
        "port": port,
        "username": username,
        "timeout": timeout,
        "banner_timeout": timeout,
        "auth_timeout": timeout,
    }
    if password is not None:
        connect_kwargs["password"] = password
    if key_filename is not None:
        connect_kwargs["key_filename"] = key_filename

    try:
        client.connect(**connect_kwargs)
    except (paramiko.SSHException, socket.error) as e:
        client.close()
        raise ConnectionError(f"无法连接到 {host}:{port}: {e}") from e

    return client


def run_remote_command(
    host: str,
    username: str,
    command: str,
    *,
    port: int = 22,
    password: Optional[str] = None,
    key_filename: Optional[str] = None,
    timeout: float = 10.0,
) -> tuple[int, str, str]:
    """
    连接 Linux、执行一条命令、读取输出并关闭连接。

    返回: (退出码, stdout 文本, stderr 文本)
    """
    client = connect_linux_ssh(
        host,
        username,
        port=port,
        password=password,
        key_filename=key_filename,
        timeout=timeout,
    )
    try:
        stdin, stdout, stderr = client.exec_command(command, timeout=timeout)
        _ = stdin  # 未向远端写 stdin
        exit_status = stdout.channel.recv_exit_status()
        out = stdout.read().decode("utf-8", errors="replace")
        err = stderr.read().decode("utf-8", errors="replace")
        return exit_status, out, err
    finally:
        client.close()


if __name__ == "__main__":
    import argparse
    import getpass
    import sys

    p = argparse.ArgumentParser(description="SSH 连接 Linux 并执行命令")
    p.add_argument("host", help="主机名或 IP")
    p.add_argument("-u", "--user", required=True, help="SSH 用户名")
    p.add_argument("-p", "--port", type=int, default=22, help="SSH 端口")
    p.add_argument("-k", "--key", help="私钥路径")
    p.add_argument("-c", "--command", default="uname -a", help="要执行的命令")
    args = p.parse_args()

    pwd = None if args.key else getpass.getpass("SSH 密码（无密钥时）: ")
    try:
        code, out, err = run_remote_command(
            args.host,
            args.user,
            args.command,
            port=args.port,
            password=pwd or None,
            key_filename=args.key,
        )
    except ConnectionError as e:
        print(e, file=sys.stderr)
        sys.exit(1)

    if out:
        print(out, end="" if out.endswith("\n") else "\n")
    if err:
        print(err, end="" if err.endswith("\n") else "", file=sys.stderr)
    sys.exit(code)
