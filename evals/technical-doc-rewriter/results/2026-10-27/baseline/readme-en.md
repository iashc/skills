# logship

logship is a lightweight agent. It sends log files to different backends. logship is designed to be robust. It works without additional setup.

## Installation

Requirement: Go 1.22 or later.

Use the install script to install logship:

```sh
curl -sSL https://get.example.com/logship.sh | sh
```

## Configuration

The configuration file is `/etc/logship/config.yaml`.

Set a `batch_size` value that is correct for your system. The default value is 500. This default is conservative.

The table that follows gives the configuration options.

| Option           | Default            | Description                                       |
| ---------------- | ------------------ | ------------------------------------------------- |
| `batch_size`     | 500                | Number of lines that logship sends in one request |
| `flush_interval` | 5s                 | Time between batch flushes                        |
| `spool_dir`      | `/var/lib/logship` | Spool directory. It keeps the unsent batches      |

## Upgrading

1. Stop logship: `systemctl stop logship`.
2. Replace the binary. For example, run the install script again.
3. WARNING: The next command deletes all batches that it cannot convert. Before you do this step, make a backup of the spool directory (`spool_dir`).

   Run `logship migrate-spool`. This command converts the spool directory to the new format.

4. Start logship: `systemctl start logship`.
5. If logship does not start, run `journalctl -u logship` to examine the logs.

Version 2.3 increased the throughput of logship. On a virtual machine with 4 cores, the throughput is approximately 40k lines/s.
