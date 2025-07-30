def warn_unsupported_keywords(schema: dict, warnings: list = None) -> list:
    unsupported_keys = [
        "unevaluatedProperties", "dependentSchemas", "propertyNames",
        "contains", "patternProperties", "items"  # some forms of "items" $ref may break
    ]
    if warnings is None:
        warnings = []

    if isinstance(schema, dict):
        for key in schema:
            if key in unsupported_keys:
                warnings.append(f"Unsupported keyword in 3.0.x: '{key}'")
        for value in schema.values():
            warn_unsupported_keywords(value, warnings)
    elif isinstance(schema, list):
        for item in schema:
            warn_unsupported_keywords(item, warnings)
    return warnings

