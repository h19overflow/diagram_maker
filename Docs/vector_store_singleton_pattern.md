# VectorStore Singleton Pattern

## Overview

The `VectorStore` uses a **singleton pattern with lazy initialization** to provide the benefits of a global variable while maintaining flexibility and testability.

## Why This Approach?

### ✅ **Benefits (Same as Global Variable)**
- **Single Instance**: Only one VectorStore exists, ensuring consistency
- **Fast Access**: No initialization overhead after first access
- **Shared State**: All parts of the application use the same vector store
- **Memory Efficient**: Only one instance in memory

### ✅ **Additional Benefits (Better than Pure Global)**
- **Lazy Initialization**: Only creates when first accessed (not at import time)
- **Testable**: Can reset the instance for testing with `reset_vector_store()`
- **Flexible**: Can still pass custom instances when needed
- **Explicit Control**: `get_vector_store()` makes the singleton pattern explicit

## Usage Patterns

### Pattern 1: Direct Import (Recommended for Most Cases)
```python
from src.core.pipeline.vector_store import vector_store

# Use directly - already initialized
results = await vector_store.search("query", k=10)
```

### Pattern 2: Getter Function (When You Need Control)
```python
from src.core.pipeline.vector_store import get_vector_store

# Get the singleton instance
store = get_vector_store()
results = await store.search("query", k=10)
```

### Pattern 3: Custom Instance (For Testing or Special Cases)
```python
from src.core.pipeline.vector_store import VectorStore

# Create a custom instance (bypasses singleton)
custom_store = VectorStore(persist_directory="/custom/path")
```

### Pattern 4: Testing
```python
from src.core.pipeline.vector_store import get_vector_store, reset_vector_store

# Reset before test
reset_vector_store()

# Test with fresh instance
store = get_vector_store()
# ... run tests ...

# Clean up
reset_vector_store()
```

## Trade-offs vs Pure Global Variable

| Aspect | Global Variable | Singleton Pattern |
|--------|----------------|-------------------|
| **Initialization** | At import time | Lazy (on first access) |
| **Testability** | Hard to test | Easy to reset/mock |
| **Flexibility** | Fixed at import | Can customize first init |
| **Explicitness** | Hidden | Explicit via `get_vector_store()` |
| **Performance** | Same | Same (after first access) |

## Thread Safety

**Current Implementation**: Not thread-safe for concurrent initialization.

If you need thread-safe initialization in a multi-threaded environment, you can add a lock:

```python
import threading

_lock = threading.Lock()

def get_vector_store(persist_directory: Optional[str] = None) -> VectorStore:
    global _vector_store_instance
    
    if _vector_store_instance is None:
        with _lock:
            # Double-check pattern
            if _vector_store_instance is None:
                _vector_store_instance = VectorStore(persist_directory=persist_directory)
    
    return _vector_store_instance
```

## When to Use Each Pattern

- **Use `vector_store` directly**: Most common case, simple and fast
- **Use `get_vector_store()`**: When you need to ensure initialization or pass custom path
- **Use `VectorStore()` directly**: Testing, multiple instances, or special configurations
- **Use `reset_vector_store()`**: Testing or when you need to reinitialize

## Current Implementation

The module exports:
- `vector_store`: Pre-initialized global instance (created on import)
- `get_vector_store()`: Getter function for explicit singleton access
- `reset_vector_store()`: Reset function for testing
- `VectorStore`: Class for custom instances

This gives you the best of both worlds: convenience of a global variable with the flexibility of a singleton pattern.

