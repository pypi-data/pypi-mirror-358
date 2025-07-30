from collections.abc import Mapping
from typing import Any

import pytest
from routelit import RouteLitRequest
from routelit.domain import PropertyDict

from routelit_silicon.builder import RLBuilder


class MockRLRequest(RouteLitRequest):
    def __init__(
        self,
        headers: Mapping[str, str] = {},
        path_params: Mapping[str, Any] = {},
        referrer: str | None = None,
        is_json: bool = True,
        json: dict[str, Any] | None = None,
        query_params: Mapping[str, str] = {},
        query_param_list: Mapping[str, list[str]] = {},
        session_id: str = "123",
        pathname: str = "/test",
        host: str = "localhost",
        method: str = "GET",
    ):
        self.headers = headers
        self.path_params = path_params
        self.referrer = referrer
        self._is_json = is_json
        self.json = json
        self.query_params = query_params
        self.query_param_list = query_param_list
        self.session_id = session_id
        self.pathname = pathname
        self.host = host
        self._method = method

    def get_headers(self) -> dict[str, str]:
        return self.headers

    def get_path_params(self) -> Mapping[str, Any] | None:
        return self.path_params

    def get_referrer(self) -> str | None:
        return self.referrer

    def is_json(self) -> bool:
        return self.is_json

    def get_json(self) -> dict[str, Any] | None:
        return self.json

    def get_query_param(self, key: str) -> str | None:
        return self.query_params.get(key)

    def get_query_param_list(self, key: str) -> list[str]:
        return self.query_param_list.get(key, [])

    def get_session_id(self) -> str:
        return self.session_id

    def get_pathname(self) -> str:
        return self.pathname

    def get_host(self) -> str:
        return self.host

    @property
    def method(self) -> str:
        return self._method


class TestRLBuilder:
    @pytest.fixture
    def mock_request(self):
        return MockRLRequest(method="POST")

    @pytest.fixture
    def builder(self, mock_request):
        return RLBuilder(request=mock_request, session_state=PropertyDict({}), fragments={})

    def test_init_with_sidebar(self, builder: RLBuilder):
        builder.set_config(use_sidebar=True)

        elements = builder.get_elements()
        assert len(elements) == 1
        assert elements[0].name == "root"
        assert elements[0].key == "root"

        assert len(elements[0].children) == 2
        assert elements[0].children[0].name == "sidebar"
        assert elements[0].children[1].name == "main"

    def test_init_without_sidebar(self, builder: RLBuilder):
        builder.set_config(use_sidebar=False)

        elements = builder.get_elements()
        assert len(elements) == 0

    def test_init_with_sidebar_and_elements(self, builder: RLBuilder):
        builder.set_config(use_sidebar=True)

        with builder.sidebar:
            builder.text("Hello, world in sidebar!")
        builder.sidebar.text("Hello, world in sidebar 2!")
        builder.text("Hello, world in main!")

        elements = builder.get_elements()
        assert len(elements) == 1
        sidebar_children = elements[0].children[0].children
        assert len(sidebar_children) == 2
        assert sidebar_children[0].name == "markdown"
        assert sidebar_children[0].props["body"] == "Hello, world in sidebar!"
        assert sidebar_children[1].name == "markdown"
        assert sidebar_children[1].props["body"] == "Hello, world in sidebar 2!"

        main_children = elements[0].children[1].children
        assert len(main_children) == 1
        assert main_children[0].name == "markdown"
        assert main_children[0].props["body"] == "Hello, world in main!"
