"""retryCommand.cli - A command-line utility to retry commands with various options."""

import subprocess
import argparse
import os
import time
import tempfile
from pathlib import Path

import rich


def ordinalInt(value: int):
    """Convert an integer to its ordinal representation."""
    number = str(value)
    suffix = "th"
    if number.endswith("1"):
        suffix = "st"
    elif number.endswith("2"):
        suffix = "nd"
    elif number.endswith("3"):
        suffix = "rd"
    return number + suffix


class OutputControler:
    """The class to control the output of the program."""

    def __init__(self, mute, quite, noNeedToLog) -> None:
        self.mute = mute
        self.quite = quite
        self.noNeedToLog = noNeedToLog
        if not self.noNeedToLog and self.mute:
            self.tempdir = (
                Path(tempfile.gettempdir())
                / f"retryCommand-{time.time()}-{os.getpid()}"
            )
            self.tempdir.mkdir(parents=True, exist_ok=True)

            self.outputs = self.tempdir / "outputs"
            self.outputs.mkdir(parents=True, exist_ok=True)

            rich.print(f"[yellow]Output are saved in {self.outputs}[/yellow]")

    def output(self, *arg, **kw):
        """Output the message to the console or to a file."""
        if self.quite or self.mute:
            return
        rich.print(*arg, **kw)

    def getStdout(self, _id: int):
        """Get the stdout file for the command."""
        if self.mute and self.noNeedToLog:
            return subprocess.DEVNULL
        if self.mute:
            filePath = self.outputs / f"stdout-{_id}.txt"
            return filePath.open("w", encoding="utf-8")
        return None


def retryCommand():
    """The main function to retry a command."""
    argparser = argparse.ArgumentParser()
    argparser.add_argument(
        "-s",
        "--no-stop-after-success",
        action="store_true",
        default=False,
        required=False,
        help="no stop after success",
    )
    argparser.add_argument(
        "-p",
        "--no-ignore-process-error",
        action="store_true",
        default=False,
        required=False,
        help="no stop after success",
    )
    argparser.add_argument(
        "-m",
        "--max-num-of-retry",
        required=False,
        default=-1,
        type=int,
        help="max number of retry",
    )
    argparser.add_argument(
        "-i",
        "--interval",
        required=False,
        default=1,
        type=int,
        help="interval to retry",
    )
    argparser.add_argument(
        "-t",
        "--time-out",
        required=False,
        default=-1,
        type=int,
        help="time out to kill process",
    )
    argparser.add_argument(
        "-d",
        "--cwd",
        required=False,
        default=os.getcwd(),
        help="current working directory",
    )
    argparser.add_argument(
        "-n",
        "--success-return-code",
        required=False,
        nargs="+",
        type=int,
        action="extend",
        default=[0],
        help="current working directory",
    )
    argparser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        default=False,
        required=False,
        help="mute more output",
    )
    argparser.add_argument(
        "--mute",
        required=False,
        default=False,
        action="store_true",
        help="Disable unnecessary auxiliary outputs",
    )
    argparser.add_argument(
        "-l",
        "--no-need-to-log",
        required=False,
        default=False,
        action="store_true",
        help="Does not output any records outside of stdou. It only works when mute is on.",
    )
    argparser.add_argument(
        "-o",
        "--overwrite-stdin",
        nargs="*",
        action="extend",
        default=[],
        help="overwrite stdin",
    )
    argparser.add_argument(
        "-c",
        "--command",
        nargs=argparse.REMAINDER,
        required=True,
        help="command to execute",
    )
    args = argparser.parse_args().__dict__

    if args["time_out"] == -1:
        args["time_out"] = None

    i = 0

    ioControl = OutputControler(
        mute=args["mute"], quite=args["quiet"], noNeedToLog=args["no_need_to_log"]
    )
    output = ioControl.output

    while args["max_num_of_retry"] == -1 or i < args["max_num_retries"]:
        i += 1
        output(f"[bold blue]the {ordinalInt(i)} attempt:[/bold blue]")
        try:
            stdout = ioControl.getStdout(i)
            with subprocess.Popen(
                args["command"], cwd=args["cwd"], stdout=stdout, stderr=stdout
            ) as popen:
                popen.wait(args["time_out"])
        except subprocess.TimeoutExpired:
            output("[bold yellow]time out[/bold yellow]")
        except Exception as e:  # pylint: disable=broad-exception-caught
            output("[bold red]failed to execute command[/bold red]")
            output(f"[red]{e.__class__.__name__}:{e}[/red]")
            if args["no_ignore_process_error"]:
                output("[bold blue]stop after error[/bold blue]")
                break
        else:
            output(f"[bold green]return code: {popen.returncode}[/bold green]")
            if popen.returncode in args["success_return_code"]:
                if not args["no_stop_after_success"]:
                    output("[bold blue]stop after success[/bold blue]")
                    break
        time.sleep(args["interval"])
        output("[blue]---------[/blue]")
    output("[bold blue]done[/bold blue]")


if __name__ == "__main__":
    retryCommand()
