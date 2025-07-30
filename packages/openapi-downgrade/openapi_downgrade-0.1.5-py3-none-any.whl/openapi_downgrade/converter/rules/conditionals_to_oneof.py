def conditionals_to_oneof(schema: dict) -> dict:
    def transform(schema):
        if not isinstance(schema, dict):
            return schema

        if "if" in schema and ("then" in schema or "else" in schema):
            if_cond = schema.get("if", {})
            then_cond = schema.get("then", {})
            else_cond = schema.get("else", {})

            # Basic check: if condition is based on a constant property
            props = if_cond.get("properties", {})
            if len(props) == 1:
                prop, condition = next(iter(props.items()))
                if "const" in condition:
                    const_value = condition["const"]

                    # Construct then schema
                    then_schema = {
                        "required": then_cond.get("required", []) + [prop],
                        "properties": {
                            **then_cond.get("properties", {}),
                            prop: {"enum": [const_value]},
                        }
                    }

                    # Construct else schema
                    else_schema = {
                        "required": else_cond.get("required", []) + [prop],
                        "properties": {
                            **else_cond.get("properties", {}),
                            prop: {"not": {"const": const_value}},
                        }
                    }

                    schema.pop("if", None)
                    schema.pop("then", None)
                    schema.pop("else", None)
                    schema["oneOf"] = [then_schema, else_schema]
                else:
                    schema["x-original-conditionals"] = {
                        "if": schema.pop("if"),
                        "then": schema.pop("then", None),
                        "else": schema.pop("else", None)
                    }
            else:
                schema["x-original-conditionals"] = {
                    "if": schema.pop("if"),
                    "then": schema.pop("then", None),
                    "else": schema.pop("else", None)
                }

        # Recurse
        for key, value in list(schema.items()):
            if isinstance(value, dict):
                schema[key] = transform(value)
            elif isinstance(value, list):
                schema[key] = [transform(v) if isinstance(v, dict) else v for v in value]

        return schema

    return transform(schema)
