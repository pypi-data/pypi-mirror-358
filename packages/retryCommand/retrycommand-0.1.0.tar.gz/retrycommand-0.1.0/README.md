# Retry Command

## Introduction

Retry Command is a Python library that allows you to retry executing a command multiple times until it succeeds or reaches the maximum number of retries. It provides options to customize the behavior of retries, such as setting a timeout for each execution and specifying the return codes that indicate success.

## Installation

To use Retry Command, you need to have Python installed on your system. You can install the library using pip:

```bash
pip install retryCommand
```

## Usage

Retry Command can only be used as a standalone script

### Standalone Script

To use Retry Command as a standalone script, you can run the following command:

```bash
do-retry [options] -c <command>
```

Replace `<command>` with the command you want to execute. You can also specify various options to customize the behavior of retries. Use the `-h` or `--help` option to see the available options and their descriptions.

## Options

Retry Command provides several options to customize the behavior of retries:

- `-s, --no-stop-after-success`: Do not stop retrying after the command succeeds.
- `-p, --no-ignore-process-error`: Do not stop retrying after encountering a process error.
- `-m, --max-num-of-retry`: Maximum number of retries. Set to -1 for unlimited retries.
- `-i, --interval`: Interval between retries in seconds.
- `-t, --time-out`: Timeout for each execution in seconds. Set to -1 for no timeout.
- `-d, --cwd`: Current working directory for the command.
- `-n, --success-return-code`: Return codes that indicate success. Multiple values can be specified.
- `-q --quite`: mute more output.
- `--mute`: mute all output.
- `-l, --no-need-to-log`: Does not output any records outside of stdou. It only works when mute is on.
- `-c, --command`: Command to execute.

## Examples

Here are some examples of how to use Retry Command:

- Retry executing a command until it succeeds, ignoring process errors:

```bash
do-retry -c <command>
```

- Retry executing a command with a maximum of 3 retries, an interval of 2 seconds, and a timeout of 5 seconds:

```bash
do-retry -m 3 -i 2 -t 5 -c <command>
```

## License

Retry Command is licensed under the MulanPSL-2.0 License. See the [LICENSE](LICENSE) file for more information.
