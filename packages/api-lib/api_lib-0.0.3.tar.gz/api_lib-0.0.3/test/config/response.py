from api_lib.objects.response import (
    APIfield,
    APImetric,
    APIobject,
    JsonResponse,
    MetricResponse,
)


@APIobject
class Repository(JsonResponse):
    name: str = APIfield()
    fullname: str = APIfield("full_name")


@APIobject
class User(JsonResponse):
    login: str = APIfield()
    name: str = APIfield()
    disk_usage: int = APIfield()
    disk_space_limit: int = APIfield("plan/space")


@APIobject
class ResponseClass(JsonResponse):
    field: str = APIfield()
    path_field: str = APIfield(path="path/to/field")
    default_field: str = APIfield(default="default_value")


@APIobject
class ResponseWithList(JsonResponse):
    this_list: list[User] = APIfield()


@APIobject
class UserWithObject(JsonResponse):
    user: User = APIfield()
    repository: Repository = APIfield()


@APIobject
class ResponseWithNestedObjects(JsonResponse):
    that_list: list[UserWithObject] = APIfield()


@APIobject
class MetricResponseClass(MetricResponse):
    metric_one: float = APImetric()
    metric_two: dict = APImetric(["label_name"])
    metric_three: int = APImetric()
    metric_four: dict = APImetric(["label_name", "other_label_name"])
