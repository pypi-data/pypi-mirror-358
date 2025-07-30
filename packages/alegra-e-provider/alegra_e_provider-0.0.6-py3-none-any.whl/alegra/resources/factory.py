from typing import Callable, Dict

from pydantic import BaseModel

from .base import ApiResource


class ResourceFactory:
    def __init__(
        self,
        client,
        endpoint: str,
        request_method: Callable,
        actions_config: Dict[str, Dict[str, str]],
    ):
        self.resource = ApiResource(client, endpoint, request_method, actions_config)

    def get(self, resource_id):
        return self.resource.get(resource_id)

    def create(self, data):
        return self.resource.create(data)

    def update(self, resource_id, data):
        return self.resource.update(resource_id, data)

    def delete(self, resource_id):
        return self.resource.delete(resource_id)

    def list(self, params=None):
        return self.resource.list(params)

    def perform_subaction(
        self, resource_id: str, subaction: str, data: BaseModel = None
    ):
        return self.resource.perform_subaction(resource_id, subaction, data)
