# Nano SDK for Python

This package provides the Python implementation of the Nano SDK, allowing you to create node servers that communicate with the Nano orchestrator.

## Installation

**This package is not yet published on PyPI. For development, install it in editable mode from your local clone:**

```bash
pip install -e .
```

Or, if you are developing a NanoServer and want to use the SDK from a parent workspace:

```bash
pip install -e ../../nanosdk/python
```

## Usage

### Creating a Server

```python
from nanosdk_py import NanoSDK
import asyncio

# Initialize SDK with a config dictionary
config = {
    'domain': 'local-python.nanograph',     # Domain of your server (required)
    'server_name': 'My Python Server',      # Name of your server (required)
    'server_uid': 'my-python-server',       # Unique server identifier (required)
    'port': 3017,                           # HTTP port (default: 3017)
    'nodes_path': 'nodes',                  # Path to nodes directory (default: 'nodes')
    'auto_watch': True,                     # Automatically watch for node file changes (default: True)
    'watch_debounce_time': 1000             # Debounce time (ms) for file watcher (default: 500)
}
sdk = NanoSDK(config)

# Start the server
async def main():
    await sdk.start()
    print('Python Server started')

# Handle shutdown
async def shutdown_handler():
    print('Python Server is shutting down')
    # Add any cleanup logic here

sdk.on_shutdown(shutdown_handler)

# Graceful shutdown
async def run():
    try:
        await main()
    except KeyboardInterrupt:
        print('Interrupted, stopping server...')
    finally:
        await sdk.stop()

if __name__ == '__main__':
    asyncio.run(run())
```

### Configuration Options

| Key                   | Type      | Default   | Description                                                        |
|-----------------------|-----------|-----------|--------------------------------------------------------------------|
| `domain`              | `str`     | —         | Domain to group servers (required)                                |
| `server_name`         | `str`     | —         | Name of your server (required)                                     |
| `server_uid`          | `str`     | —         | Unique server identifier (required)                                |
| `port`                | `int`     | `3017`    | HTTP port to listen on                                             |
| `nodes_path`          | `str`     | `'nodes'` | Path to the directory containing node files                        |
| `auto_watch`          | `bool`    | `True`    | If true, automatically reload nodes on file changes                |
| `watch_debounce_time` | `int`     | `500`     | Debounce time in milliseconds for file watcher reloads             |

### Creating Nodes

```python
from nanosdk_py import NanoSDK, NodeDefinition, NodeInstance, ExecutionContext

# Define the node
definition = {
    'uid': 'my-unique-python-node-id',
    'name': 'My Python Node',
    'category': 'Processing',
    'version': '1.0.0',
    'description': 'Description of my python node',
    'inputs': [
        {'name': 'input1', 'type': 'string', 'description': 'First input'}
    ],
    'outputs': [
        {'name': 'output1', 'type': 'string', 'description': 'First output'}
    ],
    'parameters': [
        {
            'name': 'param1',
            'type': 'boolean',
            'value': True,
            'default': True,
            'label': 'Parameter 1',
            'description': 'Description of parameter 1'
        }
    ]
}

# Register the node
my_node = NanoSDK.register_node(definition)

# Implement the execution logic
async def execute_node(ctx: ExecutionContext):
    # Get input values
    input1 = ctx.inputs.get('input1', '')
    
    # Send status update
    await ctx.context['send_status']({'type': 'running', 'message': 'Processing...'})
    
    # Check for abort
    if ctx.context['is_aborted']():
        raise Exception('Execution aborted')
    
    # Process the inputs
    output1 = f'Processed by Python: {input1}'
    
    # Return the outputs
    return {'output1': output1}

my_node['execute'] = execute_node

# To export the node if it's in its own file:
# export = my_node 

Nodes are defined in `node.py` files. You can organize your nodes by placing each `node.py`
file (along with any helper modules it might need) into its own subdirectory within the
main `nodes` directory (or the path specified in `nodes_path` in the SDK configuration).
The SDK will scan these directories for `node.py` files to load the definitions.

---

## ExecutionContext Reference

When you implement a node's `execute` function, it receives a single argument: `ctx` (the execution context). This object provides everything your node needs to process inputs, parameters, and interact with the workflow engine.

**The `ExecutionContext` object has the following structure:**

| Field         | Type                | Description                                                                 |
|---------------|---------------------|-----------------------------------------------------------------------------|
| `inputs`      | `dict`              | Input values for this node, keyed by input name.                            |
| `parameters`  | `list`              | List of parameter dicts for this node (see your node definition).           |
| `context`     | `dict`              | Runtime context utilities and metadata (see below).                         |

### `ctx.context` fields

| Key            | Type        | Description                                                                 |
|----------------|-------------|-----------------------------------------------------------------------------|
| `send_status`  | `callable`  | `await ctx.context['send_status']({...})` to send a status/progress update. |
| `is_aborted`   | `callable`  | `ctx.context['is_aborted']()` returns `True` if execution was aborted.      |
| `graph_node`   | `dict`      | The full graph node definition (with position, etc).                        |
| `instance_id`  | `str`       | The workflow instance ID for this execution.                                |

**Example usage in a node:**

```python
async def execute_node(ctx):
    # Access input
    value = ctx.inputs.get('input1')
    # Access parameter
    param = next((p for p in ctx.parameters if p['name'] == 'param1'), None)
    # Send a running status
    await ctx.context['send_status']({'type': 'running', 'message': 'Working...'})
    # Check for abort
    if ctx.context['is_aborted']():
        raise Exception('Aborted!')
    # ...
```

---

## NodeStatus Reference

The `NodeStatus` object is used to communicate the current status, progress, or result of a node execution back to the orchestrator. You send it using `await ctx.context['send_status'](status)` from within your node's `execute` function.

**NodeStatus fields:**

| Field      | Type                | Description                                                          |
|------------|---------------------|----------------------------------------------------------------------|
| `type`     | `str`               | One of: `'idle'`, `'running'`, `'complete'`, `'error'`, `'missing'`  |
| `message`  | `str` (optional)    | Human-readable status or error message                               |
| `progress` | `dict` (optional)   | Progress info, e.g. `{ 'step': 2, 'total': 5 }`                      |
| `outputs`  | `dict` (optional)   | Output values (only for `'complete'` status)                         |

**Example: Sending progress updates from a node**

```python
async def execute_node(ctx):
    total_steps = 5
    for step in range(1, total_steps + 1):
        # Abort fast if needed
        if ctx.context['is_aborted']():
            raise Exception('Aborted!')
        # Simulate work
        await asyncio.sleep(1)
        # Send progress update
        await ctx.context['send_status']({
            'type': 'running',
            'message': f'Processing step {step}/{total_steps}',
            'progress': {'step': step, 'total': total_steps}
        })
    # Just return the outputs; the SDK will send the 'complete' status automatically
    return {'result': 'done'}
```

> **Note:** You do **not** need to manually send a `'complete'` status at the end. The SDK will automatically send a `'complete'` status with the outputs you return from your `execute` function.

---

## Folder Structure

Recommended project structure for a Python NanoServer:

```
my-python-nodeserver/
├── main.py           # Entry point
├── nodes/            # Nodes directory (scans for node.py files in subdirectories)
│   ├── processing/   # Category directory (optional organization)
│   │   ├── simple_text_node/   # Directory for a single node
│   │   │   └── node.py          # Node definition for simple_text_node
│   │   └── complex_math_node/ # Directory for a more complex node
│   │       ├── __init__.py    # Optional, makes 'complex_math_node' a Python package
│   │       ├── node.py        # Main node definition for complex_math_node
│   │       └── math_utils.py  # Helper functions specific to this node
│   └── another_category/      # Another category directory
│       └── another_node/      # Directory for another_node
│           └── node.py        # Node definition for another_node
├── pyproject.toml    # Dependencies and package info
└── README.md
```

## License

MIT
