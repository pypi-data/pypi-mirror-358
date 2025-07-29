import json
from fakts_next.contrib.rath.auth import FaktsAuthLink
from unlok_next.unlok import Unlok
from unlok_next.rath import UnlokLinkComposition, UnlokRath
from rath.links.split import SplitLink
from fakts_next.contrib.rath.aiohttp import FaktsAIOHttpLink
from fakts_next.contrib.rath.graphql_ws import FaktsGraphQLWSLink
from graphql import OperationType
from fakts_next import Fakts

from arkitekt_next.service_registry import (
    BaseArkitektService,
    Params,
    get_default_service_registry,
)
from fakts_next.models import Requirement
import os


def build_relative_path(*path: str) -> str:
    return os.path.join(os.path.dirname(__file__), *path)


class UnlokService(BaseArkitektService):
    def get_service_name(self):
        return "unlok"

    def build_service(self, fakts: Fakts, params: Params):
        return Unlok(
            rath=UnlokRath(
                link=UnlokLinkComposition(
                    auth=FaktsAuthLink(fakts=fakts),
                    split=SplitLink(
                        left=FaktsAIOHttpLink(
                            fakts_group="unlok", fakts=fakts, endpoint_url="FAKE_URL"
                        ),
                        right=FaktsGraphQLWSLink(
                            fakts_group="unlok", fakts=fakts, ws_endpoint_url="FAKE_URL"
                        ),
                        split=lambda o: o.node.operation != OperationType.SUBSCRIPTION,
                    ),
                )
            )
        )

    def get_requirements(self):
        return [
            Requirement(
                key="unlok",
                service="live.arkitekt.lok",
                description="An instance of ArkitektNext Lok to authenticate the user",
            ),
        ]

    def get_graphql_schema(self):
        schema_graphql_path = build_relative_path("api", "schema.graphql")
        with open(schema_graphql_path) as f:
            return f.read()

    def get_turms_project(self):
        turms_prject = build_relative_path("api", "project.json")
        with open(turms_prject) as f:
            return json.loads(f.read())


get_default_service_registry().register(UnlokService())
