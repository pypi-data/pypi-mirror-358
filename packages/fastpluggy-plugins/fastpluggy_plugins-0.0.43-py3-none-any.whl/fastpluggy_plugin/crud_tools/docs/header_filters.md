# Table Header Filters

This document explains how to use the table header filters feature in the crud_tools plugin.

## Overview

The table header filters feature allows users to filter table data by entering filter criteria in the table headers. The filter type depends on the field type. For example, text fields have text search filters, boolean fields have checkbox filters, and select fields have dropdown filters.

## Usage

### Enabling Header Filters

Header filters are enabled by default in the FilteredTableModelView class. You can disable them by setting the `enable_header_filters` parameter to `False`:

```python
show_item = FilteredTableModelView(
    model=admin.model,
    exclude_fields=admin.get_excluded_fields(context=CrudAction.LIST),
    field_callbacks=admin.get_fields_callbacks(context=CrudAction.LIST),
    filters=admin.get_list_filters(context=CrudAction.LIST),
    default_sort=admin.get_default_sort(),
    fields=field_list.keys(),
    links=inline_actions,
    enable_header_filters=False  # Disable header filters
)
```

### Filter Types

The filter type depends on the field type:

- **Text Fields**: Text search input with options for exact match, contains, starts with, and ends with.
- **Number Fields**: Numeric input with options for equal, greater than, less than, and between.
- **Boolean Fields**: Dropdown with options for Any, Yes, and No.
- **Select Fields**: Dropdown with options from the field's choices.
- **Date Fields**: Date range picker with options for before, after, and between.

### Custom Filters

You can provide custom filters by overriding the `get_list_filters` method in your CrudAdmin class:

```python
def get_list_filters(self, context: CrudAction) -> dict:
    """
    To filter the query on table view / sqlalchemy select.
    """
    # Get default filters based on field types
    filters = super().get_list_filters(context)
    
    # Customize filters
    if 'name' in filters:
        # Use a different filter type for the name field
        filters['name'] = TextHeaderFilter(
            field_name='name',
            model=self.model,
            filter_type='startswith'
        )
    
    return filters
```

## Implementation Details

### FilteredTableModelView

The FilteredTableModelView class extends TableModelView and adds support for header filters. It automatically creates filters based on field types and renders them in the table headers.

### FilteredTableWidget

The FilteredTableWidget class extends TableWidget and adds support for header filters. It's used by FilteredTableModelView to render the table with header filters.

### Header Filters JavaScript

The header_filters.js file contains the JavaScript code for rendering and handling header filters. It adds filter inputs to table headers based on field types and applies filters to the table.

### Header Filters CSS

The header_filters.css file contains the CSS styles for header filters. It makes the filters look good and provides visual feedback when filters are active.

## Conclusion

The table header filters feature provides a powerful way to filter table data based on field types. It's easy to use and customize, and it provides a great user experience.