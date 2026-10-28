# logship

logship is a lightweight agent that ships log files to various backends. It's designed to be robust and simply works out of the box.

## Installation

Installation can be performed with the install script. You must have Go 1.22 or newer.

```sh
curl -sSL https://get.example.com/logship.sh | sh
```

## Configuration

The config file is located at `/etc/logship/config.yaml`. Make sure to set an appropriate `batch_size`; the default of 500 is fairly conservative. Relevant options are described below.

| Option           | Default            | Description                      |
| ---------------- | ------------------ | -------------------------------- |
| `batch_size`     | 500                | Number of lines sent per request |
| `flush_interval` | 5s                 | How often batches are flushed    |
| `spool_dir`      | `/var/lib/logship` | Where unsent batches are kept    |

## Upgrading

1. Stop the agent with `systemctl stop logship`.
2. Replace the binary, e.g. by re-running the install script.
3. Run `logship migrate-spool` to convert the spool to the new format.
   Note: this deletes any batches that can't be converted, so back up `spool_dir` before doing it.
4. Start the agent again with `systemctl start logship` and check the logs with `journalctl -u logship` if it fails to start.

Throughput was improved significantly in v2.3 (about 40k lines/s on a 4-core VM).
