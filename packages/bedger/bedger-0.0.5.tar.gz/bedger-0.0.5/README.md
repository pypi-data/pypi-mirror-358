# ConnectionManager Class Documentation

The `ConnectionManager` class manages connections to a UNIX socket for sending and receiving messages.
It provides context management capabilities to ensure connections are properly opened and closed.

## Features
- Context manager support for connection lifecycle management.
- Error handling for socket-related issues.
- Sends event messages with acknowledgment handling.

## Installation
Ensure you have the `bedger` package and its dependencies installed.

```bash
pip install bedger
```

## Usage
The following example demonstrates how to use the `ConnectionManager` to send events:

```python
import time
import bedger.edge.config as config
import bedger.edge.connection as connection
import bedger.edge.entities as entities

if __name__ == "__main__":
    events = [
        {"event_type": "EventA", "severity": entities.Severity.HIGH, "payload": {"key": "value1"}},
        {"event_type": "EventB", "severity": entities.Severity.LOW, "payload": {"key": "value2"}},
        {"event_type": "EventC", "severity": entities.Severity.CRITICAL, "payload": {"key": "value3"}},
    ]

    with connection.ConnectionManager(config.Config()) as conn:
        for event in events:
            time.sleep(1)
            conn.send_event(event["event_type"], event["severity"], event["payload"])
```

## API Reference

### `ConnectionManager`
Manages a connection to a UNIX socket for sending and receiving messages.

#### Constructor
- **`__init__(config: Config = Config())`**
  - Initializes the `ConnectionManager` with a specified configuration.
  - **Parameters:**
    - `config (Config)`: The configuration containing the socket path. Defaults to a new `Config` instance.

#### Context Management
- **`__enter__() -> ConnectionManager`**
  - Establishes the socket connection when entering the context.
  - **Returns:** The instance of the `ConnectionManager`.

- **`__exit__(exc_type, exc_value, traceback) -> None`**
  - Closes the socket connection when exiting the context.

#### Methods
- **`send_event(event_type: str, severity: str | Severity, payload: dict) -> None`**
  - Sends an event message through the socket.
  - **Parameters:**
    - `event_type (str)`: The type of event being sent.
    - `severity (str | Severity)`: The severity level of the event.
    - `payload (dict)`: The event's payload details.
  - **Raises:**
    - `SocketNotConnectedError`: If no active socket connection exists.
    - `SocketBrokenPipeError`: If the socket connection is lost during transmission.
    - `SocketCommunicationError`: If an error occurs during socket communication.

## Error Handling
The `ConnectionManager` raises custom errors from the `bedger.edge.errors` module for:
- Permission issues (`SocketPermissionDeniedError`).
- Missing socket files (`SocketFileNotFoundError`).
- Connection problems (`SocketConnectionError`).
- Communication errors (`SocketCommunicationError`, `SocketBrokenPipeError`).

## Logging
The class uses the `logging` module to log the following:
- Connection attempts and successes.
- Errors during connection, disconnection, and message sending.
- Debug information for message preparation and acknowledgments.

## License
This project is licensed under the MIT License. See the LICENSE file for details.
