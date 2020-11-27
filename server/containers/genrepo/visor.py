#!/usr/bin/env python3
from __future__ import annotations
from typing import *

import asyncio
import ctypes
import ctypes.util
import datetime
import os
import signal
import subprocess
import sys


FILTER_OUT = ["Did not receive identification string from"]
PROCESSES = []


def out(txt: str, *args: Any, **kwargs: Any) -> None:
    """A print wrapper with filtering and a timestamp in the front."""
    for filtered in FILTER_OUT:
        if filtered in txt:
            return

    now = datetime.datetime.utcnow()
    millis = f"{now.microsecond:0>6}"[:3]
    ts = now.strftime(f"%H:%M:%S.{millis}")
    print(ts, txt, *args, **kwargs)


def ensure_dead_with_parent() -> None:
    """A last resort measure to make sure this process dies with its parent."""
    if not sys.platform.startswith("linux"):
        return

    PR_SET_PDEATHSIG = 1  # include/uapi/linux/prctl.h
    libc = ctypes.CDLL(ctypes.util.find_library("c"))  # type: ignore
    libc.prctl(PR_SET_PDEATHSIG, signal.SIGKILL)


async def keep_printing(prefix: str, stream: asyncio.StreamReader) -> None:
    """Print from the stream with a prefix."""
    while True:
        line_b = await stream.readline()
        if not line_b:
            break
        out(f"{prefix}: {line_b.decode('utf8')}", end="")


async def run(cmd: List[str], user: str = "") -> int:
    """Run a command and stream its stdout and stderr."""
    cmd_name, args = cmd[0], cmd[1:]
    out("Starting", cmd)
    run_cmd = cmd_name
    if user:
        run_cmd = "gosu"
        args.insert(0, cmd_name)
        args.insert(0, user)
    proc = await asyncio.create_subprocess_exec(
        run_cmd,
        *args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        preexec_fn=ensure_dead_with_parent,
    )
    assert proc.stdout
    assert proc.stderr
    PROCESSES.append(proc)
    out("Running", cmd_name, "at", proc.pid)
    await asyncio.wait(
        [
            keep_printing(cmd_name + " OUT", proc.stdout),
            keep_printing(cmd_name + " ERR", proc.stderr),
        ]
    )
    return await proc.wait()


def stop_processes() -> None:
    out("Received SIGINT or SIGTERM, shutting down...")
    for proc in PROCESSES:
        try:
            proc.terminate()
        except BaseException:
            continue


async def async_main() -> int:
    loop = asyncio.get_event_loop()
    loop.add_signal_handler(signal.SIGINT, stop_processes)
    loop.add_signal_handler(signal.SIGTERM, stop_processes)

    commands = [run(sys.argv[1:])]

    if not os.environ.get("SKIP_INOTICOMING"):
        spool_dir = "/var/spool/repo"
        inoticoming_cmd_line = [
            "inoticoming",
            "--initialsearch",
            "--foreground",
            f"{spool_dir}/incoming/triggers/",
            "/usr/local/bin/process_incoming.py",
            r"triggers/{}",
            ";",
        ]
        commands.append(run(inoticoming_cmd_line, user="repomgr:repomgr"))

    return_code = 0
    for coro in asyncio.as_completed(commands):
        earliest_return_code = await coro
        if earliest_return_code and return_code == 0:
            stop_processes()
            return_code = earliest_return_code
            loop.call_later(5, sys.exit, return_code)  # time out

    out("Done.")
    return return_code


if __name__ == "__main__":
    sys.exit(asyncio.run(async_main()))
