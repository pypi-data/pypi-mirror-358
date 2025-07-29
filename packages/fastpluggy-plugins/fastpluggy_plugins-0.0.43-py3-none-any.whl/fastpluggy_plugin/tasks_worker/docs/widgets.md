# Widgets

This document describes the widgets available in the FastPluggy Task Runner.

## Overview

Widgets are reusable UI components that can be used to build the task runner interface. They are implemented as Python classes that inherit from FastPluggy's widget base classes.

## Available Widgets

### TaskFormView

A widget for rendering a form to create or manage tasks.

**Class:** `TaskFormView`
**File:** `widgets/task_form.py`
**Inherits from:** `AbstractWidget`

#### Parameters:

- `title` (str): The title of the form
- `submit_url` (str): The URL to submit the form to
- `url_after_submit` (str, optional): The URL to redirect to after form submission
- `tasks` (list, optional): List of tasks to display in the form
- `mode` (str, default="create_task"): The mode of the form
- `url_list_available_tasks` (str, optional): URL to fetch available tasks
- `url_list_available_notifiers` (str, optional): URL to fetch available notifiers
- `url_task_details` (str, optional): URL template for task details
- `request` (Request, optional): The FastAPI request object

#### Usage:

```python
from fastapi import Request
from fastpluggy_plugin.tasks_worker.widgets.task_form import TaskFormView

def my_endpoint(request: Request):
    form_widget = TaskFormView(
        title="Create Task",
        submit_url="/api/tasks/submit",
        request=request
    )
    # Process the widget and return it in your template context
    form_widget.process()
    return {"widget": form_widget}
```

### RunTaskButtonWidget

A button widget that runs a task when clicked.

**Class:** `RunTaskButtonWidget`
**File:** `widgets/task_run_button.py`
**Inherits from:** `BaseButtonWidget`

#### Parameters:

- `task` (str): The name of the task to run
- `task_kwargs` (dict): The keyword arguments to pass to the task
- Additional parameters inherited from `BaseButtonWidget`

#### Usage:

```python
from fastapi import Request
from fastpluggy_plugin.tasks_worker.widgets.task_run_button import RunTaskButtonWidget

def my_endpoint(request: Request):
    button_widget = RunTaskButtonWidget(
        task="my_task",
        task_kwargs={"param1": "value1"},
        request=request,
        label="Run My Task"
    )
    # Process the widget and return it in your template context
    button_widget.process()
    return {"widget": button_widget}
```

## Integration with Templates

Widgets are typically rendered in Jinja2 templates using the `widget.render()` method:

```html
<!-- In your Jinja2 template -->
{{ widget.render() | safe }}
```

## Creating Custom Widgets

To create a custom widget, inherit from one of the base widget classes in FastPluggy:

- `AbstractWidget`: Base class for all widgets
- `BaseButtonWidget`: Base class for button widgets

Implement the `process()` method to prepare the widget data and set any necessary properties.