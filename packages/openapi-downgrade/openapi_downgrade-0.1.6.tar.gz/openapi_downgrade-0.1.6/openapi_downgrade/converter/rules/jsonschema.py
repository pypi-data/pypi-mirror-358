def downgrade_json_schema(schema: dict) -> dict:
    unsupported = ["if", "then", "else", "const", "not", "dependentSchemas", "unevaluatedProperties"]
    if isinstance(schema, dict):
        for u in unsupported:
            if u in schema:
                schema[f"x-dropped-{u}"] = schema.pop(u)
        for key, value in schema.items():
            downgrade_json_schema(value)
    elif isinstance(schema, list):
        for item in schema:
            downgrade_json_schema(item)
    return schema