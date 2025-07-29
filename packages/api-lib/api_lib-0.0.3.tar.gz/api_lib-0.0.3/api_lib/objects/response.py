from dataclasses import dataclass, field, fields
from decimal import Decimal
from typing import Any, Iterable, Optional, get_args, get_origin

APIobject = dataclass(init=False)


def APIfield(path: Optional[str] = None, default: Optional[object] = None):
    metadata: dict[str, Any] = dict()
    if path:
        metadata["path"] = path
    if default:
        metadata["default"] = default

    return field(metadata=metadata)


def APImetric(labels: Optional[list[str]] = None):
    metadata: dict[str, Any] = dict()
    if labels:
        metadata["labels"] = labels

    return field(metadata=metadata)


class Response:
    def post_init(self):
        pass

    @property
    def is_null(self):
        return all(getattr(self, key) is None for key in [f.name for f in fields(self)])

    @property
    def as_dict(self) -> dict:
        return {key: getattr(self, key) for key in [f.name for f in fields(self)]}

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return str(self)


class JsonResponse(Response):
    def __init__(self, data: dict):
        for f in fields(self):
            origin: Optional[Any] = get_origin(f.type)
            args = get_args(f.type)
            arg = args[0] if args else f.type

            v = data
            for subkey in f.metadata.get("path", f.name).split("/"):
                v = v.get(subkey, None)
                if v is None:
                    break
            if v is None:
                if default := f.metadata.get("default", None):
                    if not isinstance(default, arg):
                        raise TypeError(
                            f"Default value for {f.name} must be of type {arg.__name__}, "  # ty: ignore[possibly-unbound-attribute]
                            f"got {type(default).__name__}"
                        )
                    setattr(self, f.name, default)
                else:
                    setattr(self, f.name, None)
            else:
                if origin and issubclass(origin, Iterable) and arg:
                    setattr(self, f.name, [arg(obj) for obj in v])
                else:
                    setattr(self, f.name, arg(v))  # ty: ignore[call-non-callable]
        self.post_init()


class MetricResponse(Response):
    def __init__(self, data: str):
        for f in fields(self):
            args = get_args(f.type)
            arg = args[0] if args else f.type

            values = {}
            labels = f.metadata.get("labels", [])

            for line in data.split("\n"):
                if not line.strip().startswith(f.name):
                    continue

                value = line.split(" ")[-1]

                if len(labels) == 0:
                    setattr(self, f.name, arg(value) + getattr(self, f.name, 0))  # ty: ignore[call-non-callable]
                else:
                    labels_values = {
                        pair.split("=")[0].strip('"').strip(): pair.split("=")[1].strip('"').strip()
                        for pair in line.split("{")[1].split("}")[0].split(",")
                    }
                    dict_path = [labels_values[label] for label in labels if label in labels_values]
                    current = values

                    for part in dict_path[:-1]:
                        if part not in current:
                            current[part] = {}
                        current = current[part]
                    if dict_path[-1] not in current:
                        current[dict_path[-1]] = Decimal("0")
                    current[dict_path[-1]] += Decimal(value)

            if len(labels) > 0:
                setattr(self, f.name, arg(values))  # ty: ignore[call-non-callable]
