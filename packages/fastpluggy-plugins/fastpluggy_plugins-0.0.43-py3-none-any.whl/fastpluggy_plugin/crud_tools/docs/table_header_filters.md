# Table Header Filters Roadmap

This document outlines the plan for implementing filters in table headers based on field types in the crud_tools plugin.

## Overview

The goal is to add filtering capabilities to table headers in the crud_tools plugin, with the filter type depending on the field type. For example, text fields would have text search filters, boolean fields would have checkbox filters, and select fields would have dropdown filters.

## Implementation Roadmap

### Phase 1: Core Filter Infrastructure

- [ ] Create a base `HeaderFilter` class that all filter types will inherit from
- [ ] Implement the filter rendering mechanism in the table header
- [ ] Extend the `TableModelView` to support header filters
- [ ] Update the `get_list_filters` method in `CrudAdmin` to use field types for filter generation

### Phase 2: Field Type-Specific Filters

- [ ] Implement `TextHeaderFilter` for `TextFieldType` and `TextareaFieldType`
  - [ ] Add text search input with options for exact match, contains, starts with, ends with
- [ ] Implement `NumberHeaderFilter` for `IntegerFieldType`
  - [ ] Add numeric range filter with options for equal, greater than, less than, between
- [ ] Implement `BooleanHeaderFilter` for `BooleanFieldType`
  - [ ] Add checkbox filter with true/false/any options
- [ ] Implement `SelectHeaderFilter` for `SelectFieldType` and `EnumFieldType`
  - [ ] Add dropdown filter with options from the field's choices
- [ ] Implement `DateHeaderFilter` for `DateTimeFieldType`
  - [ ] Add date range picker with options for before, after, between
- [ ] Implement `AssociationHeaderFilter` for `AssociationFieldType`
  - [ ] Add dropdown filter with options from the related model

### Phase 3: Filter UI and UX Improvements

- [ ] Add clear filter button for each header filter
- [ ] Add "Clear All Filters" button
- [ ] Implement filter persistence across page reloads
- [ ] Add visual indication of active filters
- [ ] Implement responsive design for filters on mobile devices

### Phase 4: Advanced Features

- [ ] Add support for multiple filters on the same column
- [ ] Implement filter presets that can be saved and reused
- [ ] Add export functionality for filtered data
- [ ] Implement server-side filtering for large datasets
- [ ] Add filter analytics to track most used filters

## Technical Considerations

### Filter Storage and Retrieval

Filters will be stored in the request query parameters to allow for bookmarking and sharing filtered views. The format will be:

```
?filter[field_name][operator]=value
```

For example:
```
?filter[name][contains]=john&filter[age][gt]=30
```

### Filter Application

Filters will be applied at the database query level when possible to optimize performance. The `get_list_filters` method in `CrudAdmin` will be extended to convert the filter parameters into SQLAlchemy filter expressions.

### Filter UI Components

Each filter type will have its own UI component that will be rendered in the table header. These components will be implemented using HTML, CSS, and JavaScript, with a focus on accessibility and usability.

## Conclusion

This roadmap provides a structured approach to implementing table header filters based on field types in the crud_tools plugin. By following this plan, we can ensure that the implementation is comprehensive, maintainable, and user-friendly.

# Remarks and improvement:
js_files make this for [dynamic-select.js](../src/static/js/dynamic-select.js)
