def drop_webhooks(spec: dict) -> dict:
    if "webhooks" in spec:
        del spec["webhooks"]
    return spec

