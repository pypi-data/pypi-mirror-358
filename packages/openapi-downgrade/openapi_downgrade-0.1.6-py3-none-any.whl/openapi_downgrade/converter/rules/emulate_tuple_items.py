def emulate_tuple_items(schema: dict, warnings: list = None) -> dict:
    if warnings is None:
        warnings = []

    if isinstance(schema, dict):
        if schema.get("type") == "array" and isinstance(schema.get("items"), list):
            items_list = schema["items"]
            warnings.append("Tuple-style 'items' detected; emulating using 'x-tuple-items'.")

            schema["items"] = {}
            schema.setdefault("minItems", len(items_list))
            schema.setdefault("maxItems", len(items_list))

            # Add custom vendor extension to preserve logic
            schema["x-tuple-items"] = []
            for idx, item_schema in enumerate(items_list):
                schema["x-tuple-items"].append({"index": idx, **item_schema})
        for value in schema.values():
            emulate_tuple_items(value, warnings)
    elif isinstance(schema, list):
        for item in schema:
            emulate_tuple_items(item, warnings)

    return schema
