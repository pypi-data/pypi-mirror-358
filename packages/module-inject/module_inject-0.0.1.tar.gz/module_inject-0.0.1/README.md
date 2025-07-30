# _# module-inject_

**module-inject** is a Python library designed to inject configuration values into modules *before they are imported*, enabling centralized and declarative control over runtime behavior across dynamic or plugin-based systems.

This is particularly useful in applications where modules need to be configured externally, but standard import mechanisms do not allow mutation of module-level state prior to execution.

## Features

- Inject values into modules before import-time execution
- Fine-grained control with per-module and per-package scopes
- Lazy and dynamic module loading after configuration
- Optional type enforcement and stack-based namespace lookup

## Installation

```bash
pip install module-inject
```

## Usage

Consider a plugin system where plugins are python modules under a `plugins/` directory need to be initialized with context-specific parameters.

### Example

#### `main.py`

```python
from pathlib import Path
from module_inject import Module

# Create a controller for the package
package = Module.from_import_path("plugins")

# Set a package-scoped variable
package.set(role="slave")

# Set a variable for the current script
Module.from_path(Path(__file__)).set(role="master")

# Iterate over all module files and inject values before importing
for path in Path("plugins").glob("*.py"):
    module = Module.from_path(path)
    module.set(variable=f"value for {module.import_path}")
    module.load().init()
```

#### `plugins/interesting_plugin.py`

```python
import module_inject as module

def init():
    role = module.get("role", str, package=True)
    print(role)

# Module-level config access
print(module.get("variable"))
print(module.get_namespace())
```

### Output

```
value for plugins.interesting_plugin
{'variable': 'value for plugins.interesting_plugin'}
slave
```

## API

### `Module.from_import_path(path: str) -> Module`

Creates a `Module` controller for the given import path (e.g., `"plugins.interesting_plugin"`). 

### `Module.from_path(path: Path) -> Module`

Creates a `Module` controller from a filesystem path to a `.py` file. 
Searches for the file in `sys.path` under the hood to resolve import path.

### `module.get(key: str, type_: type[T] = None, package: bool = False, recursive: bool = False) -> T`

Retrieves the value associated with `key`.
If `type_` is set - checks if the value in namespace is instance of the provided type.

If `package=True`, it will attempt to retrieve the value from the package scope rather than the module-specific scope.

If `recursive=True`, it will walk over the call stack to find the name.

### `module.get_namespace() -> dict`

Returns a dictionary of all key-value pairs injected into the current module.

### `Module.set(**kwargs) -> None`

Sets key-value pairs to be injected into the associated module upon import.

### `Module.load() -> types.ModuleType`

Loads (imports) the target module with the injected configuration. Must be called to finalize injection.

## Design Philosophy

This library provides a low-level interface to orchestrate dynamic configuration of Python modules, particularly in systems requiring deferred or context-aware initialization. Unlike environment variables or global config objects, this approach allows values to be injected into module namespace dictionaries before execution.

