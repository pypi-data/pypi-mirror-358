---
id: utils
title: Plugin Utilities
sidebar_position: 3
---

# Plugin Utilities

Utility functions for plugin development and management.

## Configuration

### read_plugin_config()

Read plugin configuration from config.yaml file.

```python
from synapse_sdk.plugins.utils import read_plugin_config

config = read_plugin_config(plugin_path="./my-plugin")
```

## Registration

### register_action()

Decorator for registering plugin actions.

```python
from synapse_sdk.plugins.categories.base import register_action, Action

@register_action("my_action")
class MyAction(Action):
    pass
```

## Validation

Utilities for validating plugin structure and configuration.

## File Operations

Helper functions for plugin file management and archiving.