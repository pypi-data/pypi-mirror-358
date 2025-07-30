<p align="center">
    <a href="https://charlabs.dev"><img src="./assets/logo_h_bg.webp" alt="CharLabs" style="width: 100%;" /></a>
</p>

<h1 style="border: none;" align="center">CharLabs PyLib Logging</h1>

<p align="center">
    <a href="#!"><img src="https://img.shields.io/github/commit-activity/m/charlabsdev/pylib_logging?logo=github" alt="Commit Activity" /></a>
</p>

<p align="center">
    <a href="https://github.com/charlabsdev/pylib_logging/releases" alt="Github Release"><img src="https://img.shields.io/github/v/release/charlabsdev/pylib_logging?logo=github" /></a>
    <a href="https://github.com/charlabsdev/pylib_logging/releases" alt="Github Release"><img src="https://img.shields.io/github/release-date/charlabsdev/pylib_logging?logo=github" /></a>
</p>

A comprehensive Python logging library that provides both traditional logging and structured logging (via structlog) with advanced task tracking capabilities.

## Features

- **Dual Logging Backends**: Support for both traditional Python logging and structured logging with `structlog`
- **Task Logger**: Advanced task tracking with progress monitoring, timing, and automatic exception handling
- **Cloud Provider Support**: Special configurations for cloud environments (GCP)
- **Exception Handling**: Automatic setup of exception handlers for uncaught exceptions, thread exceptions, and asyncio exceptions
- **Configuration-driven**: YAML-based configuration for traditional logging
- **Development-friendly**: Rich console output for development environments

## Installation

```bash
pip install charlabs-logging
```

### Optional Dependencies

For different logging backends, install the appropriate dependency groups:

```bash
# For traditional logging with JSON output
pip install charlabs-logging[logging]

# For structured logging with structlog
pip install charlabs-logging[structlog]

# For development with rich console output
pip install charlabs-logging[dev]
```

## Quick Start

### Traditional Logging

```python
from charlabs.logging import LogsSettings, setup_logs, TaskLogger

# Configure logging
settings = LogsSettings(logs_config_path="conf/logging.yaml")
setup_logs(settings)

# Use task logger with automatic progress tracking
items = list(range(1000))
with TaskLogger("data_processing", size=len(items)) as task:
    for item in task.iterate(items):
        # Your processing logic here - progress tracked automatically
        pass
```

### Structured Logging with Structlog

```python
from charlabs.logging.structlog import LogsSettings, setup_logs, TaskLogger
import structlog

# Setup structured logging
settings = LogsSettings(log_level="INFO")
setup_logs(settings, is_dev=True)  # Use is_dev=False for production

# Get a logger
logger = structlog.get_logger("my_app")
logger.info("Application started", version="1.0.0")

# Use task logger with structured logging and automatic progress tracking
items = list(range(1000))
with TaskLogger("data_processing", size=len(items)) as task:
    for item in task.iterate(items):
        # Your processing logic here - progress tracked automatically
        pass
```

## Configuration

### Traditional Logging Configuration

The library uses YAML configuration files that follow the [Python logging configuration dictionary schema](https://docs.python.org/3/library/logging.config.html#logging-config-dictschema).

Example `conf/logging.yaml`:
```yaml
version: 1
disable_existing_loggers: False

formatters:
  json:
    class: jsonlogger.JSONFormatter
    format: "%(asctime)s %(name)s %(message)s %(exc_info)s"

handlers:
  console:
    class: logging.StreamHandler
    level: INFO
    stream: ext://sys.stdout
    formatter: json

root:
  level: INFO
  handlers: [console]
```

Example development configuration `conf/logging.dev.yaml`:
```yaml
version: 1
disable_existing_loggers: False

handlers:
  rich:
    class: rich.logging.RichHandler
    rich_tracebacks: True

loggers:
  app:
    level: DEBUG

root:
  handlers: [rich]
```

### Structured Logging Configuration

```python
from charlabs.logging.structlog import LogsSettings, LogsExecEnvironment

settings = LogsSettings(
    log_level="INFO",
    dev_log_level="DEBUG",
    exec_environment=LogsExecEnvironment.GCP,  # For GCP-specific formatting
    logger_names_extends=["my_custom_logger"]  # Add custom logger names
)
```

## Task Logger

The Task Logger provides comprehensive task tracking with automatic timing, progress reporting, and exception handling.

### Basic Usage

```python
from charlabs.logging import TaskLogger  # or from charlabs.logging.structlog

# ✅ RECOMMENDED: Context manager usage
with TaskLogger("data_processing") as task:
    # Your task logic here
    pass

# ✅ Alternative: Manual control
task = TaskLogger("data_processing")
task.start()
try:
    # Your task logic here
    pass
finally:
    task.end()
```

### Progress Tracking

```python
# ✅ RECOMMENDED: Use task.iterate for automatic progress tracking
items = range(1000)
with TaskLogger("processing_items", size=len(items)) as task:
    for item in task.iterate(items):
        # Process item - progress is tracked automatically
        pass

# ✅ Alternative: Manual progress tracking (less preferred for loops)
with TaskLogger("processing_items", size=1000) as task:
    for i in range(1000):
        # Process item
        task.update(i + 1)  # Manual progress update
```

**Best Practice**: When iterating over collections, prefer using `task.iterate()` instead of manually calling `task.update()`. The `iterate` method automatically handles progress tracking and is more concise and less error-prone.

### Advanced Configuration

```python
from charlabs.logging._base.task_logger import TaskLoggerUpdate, TaskLoggerMsg

# Custom messages
custom_msg = TaskLoggerMsg(
    start="Beginning data processing...",
    end="Data processing completed in {duration}",
    progress="Processing... ({current}s elapsed)"
)

# Advanced configuration
task = TaskLogger(
    name="complex_task",
    size=1000,
    size_unit=(" record", " records"),
    progress_interval=5.0,  # Log progress every 5 seconds
    progress_min_interval=1.0,  # Minimum 1 second between progress logs
    progress_update=TaskLoggerUpdate.ALL,  # Log on both intervals and updates
    msg=custom_msg,
    auto_start=True,  # Start automatically on creation
    on_error=lambda e: print(f"Task failed: {e}")  # Custom error handler
)
```

### Progress Update Modes

- `TaskLoggerUpdate.INTERVAL`: Log progress only at time intervals (default)
- `TaskLoggerUpdate.UPDATE`: Log progress on every `update()` call (including `iterate()`)
- `TaskLoggerUpdate.ALL`: Log progress on both intervals and updates

### Best Practices

#### Use `iterate()` for Collections

When processing collections or iterables, always prefer `task.iterate()` over manual `task.update()` calls:

```python
# ✅ PREFERRED: Automatic progress tracking
data = [1, 2, 3, 4, 5]
with TaskLogger("processing_data", size=len(data)) as task:
    for item in task.iterate(data):
        process(item)

# ❌ AVOID: Manual progress tracking in loops
data = [1, 2, 3, 4, 5]
with TaskLogger("processing_data", size=len(data)) as task:
    for i, item in enumerate(data):
        process(item)
        task.update(i + 1)  # Error-prone and verbose
```

#### Use `update()` for Non-Linear Progress

Reserve `task.update()` for scenarios where progress doesn't follow a simple iteration pattern:

```python
# ✅ APPROPRIATE: Complex progress scenarios
with TaskLogger("batch_processing", size=total_records) as task:
    processed = 0
    while processed < total_records:
        batch = get_next_batch()
        process_batch(batch)
        processed += len(batch)
        task.update(processed)  # Manual update is appropriate here
```

## Exception Handling

The library automatically sets up exception handlers for:

- **Uncaught exceptions**: Main thread exceptions
- **Thread exceptions**: Exceptions in spawned threads
- **Asyncio exceptions**: Unhandled exceptions in async tasks

```python
from charlabs.logging import LogsSettings, setup_logs

settings = LogsSettings(uncaught_log_name="errors")
setup_logs(settings)

# Now all uncaught exceptions will be logged to the "errors" logger
```

## Cloud Provider Support (structlog only)

### Google Cloud Platform (GCP)

When running on GCP, use the GCP execution environment for proper log formatting:

```python
from charlabs.logging.structlog import LogsSettings, LogsExecEnvironment, setup_logs

settings = LogsSettings(exec_environment=LogsExecEnvironment.GCP)
setup_logs(settings, is_dev=False)
```

This automatically maps log levels to GCP's severity levels and includes appropriate metadata.

## Development

### Setup

```bash
# Clone the repository
git clone <repository-url>
cd charlabs_pylib_logging

# Install dependencies
uv sync

# Install pre-commit hooks
make pre-commit-install
```

### Running Tests

```bash
make test
```

### Code Quality

```bash
# Run linting
make lint

# Run type checking
make types

# Run pre-commit checks
make pre-commit

# Fix formatting and linting issues
make format-fix
make lint-fix
```


## API Reference

### LogsSettings Classes

#### `charlabs.logging.LogsSettings`
- `logs_config_path`: Path to YAML logging configuration file
- `uncaught_log_name`: Logger name for uncaught exceptions

#### `charlabs.logging.structlog.LogsSettings`
- `log_level`: Application log level
- `dev_log_level`: Development log level
- `exec_environment`: Cloud execution environment
- `logger_names`: List of logger names to configure
- `logger_names_extends`: Additional logger names
- `uncaught_log_name`: Logger name for uncaught exceptions

### Task Logger Classes

#### `BaseTaskLogger` (Abstract)
Base class for task loggers with common functionality.

#### `charlabs.logging.TaskLogger`
Traditional logging implementation of task logger.

#### `charlabs.logging.structlog.TaskLogger`
Structured logging implementation of task logger.

### Setup Functions

#### `charlabs.logging.setup_logs(logs_settings: LogsSettings)`
Sets up traditional logging from YAML configuration.

#### `charlabs.logging.structlog.setup_logs(logs_settings: LogsSettings, *, is_dev: bool = False)`
Sets up structured logging with structlog.
