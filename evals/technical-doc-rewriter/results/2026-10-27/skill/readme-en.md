# logship

logship is a lightweight agent that ships log files to backends. logship is designed to be robust. It works with the default configuration.

## Installation

You must have Go 1.22 or newer. Install logship with the install script:

```sh
curl -sSL https://get.example.com/logship.sh | sh
```

## Configuration

The config file is `/etc/logship/config.yaml`. You must set `batch_size`. The default value of 500 is conservative. The table below describes the options.

| Option           | Default            | Description                      |
| ---------------- | ------------------ | -------------------------------- |
| `batch_size`     | 500                | Number of lines sent per request |
| `flush_interval` | 5s                 | How often batches are flushed    |
| `spool_dir`      | `/var/lib/logship` | Where unsent batches are kept    |

## Upgrading

1. Stop the agent with `systemctl stop logship`.
2. Replace the binary. For example, run the install script again.

**Warning:** Back up `spool_dir` before you run `logship migrate-spool`. The command deletes each batch that it cannot convert.

3. Back up `spool_dir`.
4. Run `logship migrate-spool` to convert the spool to the new format.
5. Start the agent with `systemctl start logship`.
6. If the agent fails to start, check the logs with `journalctl -u logship`.

In v2.3, throughput improved (about 40k lines/s on a 4-core VM).
