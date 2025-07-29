# Admin Inspection

This document explains the Admin Inspection feature in the crud_tools plugin, which allows you to inspect how field types, filters, and other configurations are detected and configured for each CRUD action.

## Overview

The Admin Inspection feature provides a detailed view of how the CRUD admin system works with your models. It shows:

- How field types are detected and configured
- How filters are created based on field types
- What fields are excluded for each action
- What callbacks are used for field rendering
- What JavaScript dependencies are required

This information is valuable for understanding how the CRUD admin system works and for debugging issues with your models.

## Accessing the Admin Inspection

You can access the Admin Inspection for a model by clicking the "Inspect" link in the Models list view, or by navigating directly to:

```
/models/inspect/{model_name}
```

Where `{model_name}` is the name of your model class.

## Information Displayed

### Model Information

Basic information about the model, including:

- Model Name: The name of the model class
- Admin Class: The name of the admin class used for this model
- Primary Key: The primary key field for the model
- Table Name: The database table name for the model

### Field Types

For each CRUD action (CREATE, EDIT, LIST, VIEW), the Admin Inspection shows:

- Field Name: The name of the field
- Field Type: The type of field used (e.g., TextFieldType, IntegerFieldType)
- Detection Logic: How the field type was detected (e.g., based on field type, primary key status)
- Required: Whether the field is required
- Default: The default value for the field
- Help Text: The help text for the field
- Primary Key: Whether the field is a primary key
- Readonly: Whether the field is readonly

### Filters

For the LIST action, the Admin Inspection shows:

- Field Name: The name of the field
- Filter Type: The type of filter used (e.g., TextHeaderFilter, NumberHeaderFilter)
- Filter Mode: The mode of the filter (e.g., partial, exact)
- Field Type: The underlying field type

### Excluded Fields

For each CRUD action, the Admin Inspection shows which fields are excluded from the form or view.

### Field Callbacks

The Admin Inspection shows what callbacks are used for rendering fields, if any.

### JavaScript Dependencies

The Admin Inspection shows what JavaScript dependencies are required for the fields, if any.

## Use Cases

### Debugging Field Type Detection

If a field is not displaying correctly, you can use the Admin Inspection to see how the field type was detected and what field type is being used.

### Understanding Filter Configuration

If filters are not working as expected, you can use the Admin Inspection to see what filter types are being used and how they are configured.

### Customizing Admin Classes

When creating custom admin classes, you can use the Admin Inspection to understand how the default admin class works and what you need to override.

## Conclusion

The Admin Inspection feature is a powerful tool for understanding and debugging the CRUD admin system. It provides detailed information about how field types, filters, and other configurations are detected and configured for each CRUD action.