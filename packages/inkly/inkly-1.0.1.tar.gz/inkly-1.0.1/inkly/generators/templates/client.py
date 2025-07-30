"""クライアント生成用テンプレート"""

# 同期クライアントテンプレート
CLIENT_SYNC_TEMPLATE = '''"""生成されたAPIクライアント(同期版)"""

from __future__ import annotations
from typing import Any

import httpx
from pydantic import BaseModel

{%- if not flat_structure %}
from .models import *
{%- endif %}

{%- if flat_structure and models %}
# モデル定義
{%- for model in models %}
class {{ model.name }}(BaseModel):
    """{{ model.description }}"""
{%- for field in model.fields %}
    {{ field.name }}: {{ field.type }}{% if field.description %}  # {{ field.description }}{% endif %}
{%- endfor %}
{%- endfor %}
{%- endif %}

class APIClient:
    """生成されたAPIクライアント(同期版)"""

    def __init__(self, base_url: str, headers: dict[str, str] | None = None) -> None:
        self.base_url = base_url.rstrip('/')
        self.headers = headers or {}
        self.client = httpx.Client()

    def __del__(self) -> None:
        if hasattr(self, 'client'):
            self.client.close()

{%- for endpoint in endpoints %}
    def {{ endpoint.operation_id }}(
        self,
{%- for param in endpoint.parameters %}
        {{ param.name }}: {{ param.type }},
{%- endfor %}
{%- if endpoint.request_body %}
        data: {{ endpoint.request_body.type }},
{%- endif %}
    ) -> {{ endpoint.responses | get_return_type }}:
        """{{ endpoint.summary }}"""
        url = f"{self.base_url}{{ endpoint.path }}"

{%- if endpoint.parameters %}
        # パスパラメータの置換
{%- for param in endpoint.parameters %}
{%- if param.in == 'path' %}
        url = url.replace("{{ '{' + param.name + '}' }}", str({{ param.name }}))
{%- endif %}
{%- endfor %}

        # クエリパラメータの設定
        params = {}
{%- for param in endpoint.parameters %}
{%- if param.in == 'query' %}
        if {{ param.name }} is not None:
            params["{{ param.name }}"] = {{ param.name }}
{%- endif %}
{%- endfor %}
{%- endif %}

        response = self.client.{{ endpoint.method | lower }}(
            url,
{%- if endpoint.parameters %}
            params=params,
{%- endif %}
{%- if endpoint.request_body %}
            json=data.model_dump() if hasattr(data, 'model_dump') else data,
{%- endif %}
            headers=self.headers,
        )
        response.raise_for_status()

{%- if endpoint.responses | get_return_type != "None" %}
        return response.json()
{%- else %}
        return None
{%- endif %}

{%- endfor %}
'''

# 非同期クライアントテンプレート
CLIENT_ASYNC_TEMPLATE = '''"""生成されたAPIクライアント(非同期版)"""

from __future__ import annotations
from typing import Any

import httpx
from pydantic import BaseModel

{%- if not flat_structure %}
from .models import *
{%- endif %}

{%- if flat_structure and models %}
# モデル定義
{%- for model in models %}
class {{ model.name }}(BaseModel):
    """{{ model.description }}"""
{%- for field in model.fields %}
    {{ field.name }}: {{ field.type }}{% if field.description %}  # {{ field.description }}{% endif %}
{%- endfor %}
{%- endfor %}
{%- endif %}

class APIClient:
    """生成されたAPIクライアント(非同期版)"""

    def __init__(self, base_url: str, headers: dict[str, str] | None = None) -> None:
        self.base_url = base_url.rstrip('/')
        self.headers = headers or {}
        self.client = httpx.AsyncClient()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()

{%- for endpoint in endpoints %}
    async def {{ endpoint.operation_id }}(
        self,
{%- for param in endpoint.parameters %}
        {{ param.name }}: {{ param.type }},
{%- endfor %}
{%- if endpoint.request_body %}
        data: {{ endpoint.request_body.type }},
{%- endif %}
    ) -> {{ endpoint.responses | get_return_type }}:
        """{{ endpoint.summary }}"""
        url = f"{self.base_url}{{ endpoint.path }}"

{%- if endpoint.parameters %}
        # パスパラメータの置換
{%- for param in endpoint.parameters %}
{%- if param.in == 'path' %}
        url = url.replace("{{ '{' + param.name + '}' }}", str({{ param.name }}))
{%- endif %}
{%- endfor %}

        # クエリパラメータの設定
        params = {}
{%- for param in endpoint.parameters %}
{%- if param.in == 'query' %}
        if {{ param.name }} is not None:
            params["{{ param.name }}"] = {{ param.name }}
{%- endif %}
{%- endfor %}
{%- endif %}

        response = await self.client.{{ endpoint.method | lower }}(
            url,
{%- if endpoint.parameters %}
            params=params,
{%- endif %}
{%- if endpoint.request_body %}
            json=data.model_dump() if hasattr(data, 'model_dump') else data,
{%- endif %}
            headers=self.headers,
        )
        response.raise_for_status()

{%- if endpoint.responses | get_return_type != "None" %}
        return response.json()
{%- else %}
        return None
{%- endif %}

{%- endfor %}
'''

# 同期版エンドポイント別テンプレート
ENDPOINT_SYNC_TEMPLATE = '''"""{{ tag }} エンドポイント(同期版)"""

from __future__ import annotations
from typing import Any

import httpx


class {{ tag | title }}Endpoints:
    """{{ tag }} エンドポイント"""

    def __init__(self, client: httpx.Client, base_url: str, headers: dict[str, str]) -> None:
        self.client = client
        self.base_url = base_url
        self.headers = headers

{%- for endpoint in endpoints %}
    def {{ endpoint.operation_id }}(
        self,
{%- for param in endpoint.parameters %}
        {{ param.name }}: {{ param.type }},
{%- endfor %}
{%- if endpoint.request_body %}
        data: {{ endpoint.request_body.type }},
{%- endif %}
    ) -> {{ endpoint.responses | get_return_type }}:
        """{{ endpoint.summary }}"""
        url = f"{self.base_url}{{ endpoint.path }}"

{%- if endpoint.parameters %}
        # パスパラメータの置換
{%- for param in endpoint.parameters %}
{%- if param.in == 'path' %}
        url = url.replace("{{ '{' + param.name + '}' }}", str({{ param.name }}))
{%- endif %}
{%- endfor %}

        # クエリパラメータの設定
        params = {}
{%- for param in endpoint.parameters %}
{%- if param.in == 'query' %}
        if {{ param.name }} is not None:
            params["{{ param.name }}"] = {{ param.name }}
{%- endif %}
{%- endfor %}
{%- endif %}

        response = self.client.{{ endpoint.method | lower }}(
            url,
{%- if endpoint.parameters %}
            params=params,
{%- endif %}
{%- if endpoint.request_body %}
            json=data.model_dump() if hasattr(data, 'model_dump') else data,
{%- endif %}
            headers=self.headers,
        )
        response.raise_for_status()

{%- if endpoint.responses | get_return_type != "None" %}
        return response.json()
{%- else %}
        return None
{%- endif %}

{%- endfor %}
'''

# 非同期版エンドポイント別テンプレート
ENDPOINT_ASYNC_TEMPLATE = '''"""{{ tag }} エンドポイント(非同期版)"""

from __future__ import annotations
from typing import Any

import httpx


class {{ tag | title }}Endpoints:
    """{{ tag }} エンドポイント"""

    def __init__(self, client: httpx.AsyncClient, base_url: str, headers: dict[str, str]) -> None:
        self.client = client
        self.base_url = base_url
        self.headers = headers

{%- for endpoint in endpoints %}
    async def {{ endpoint.operation_id }}(
        self,
{%- for param in endpoint.parameters %}
        {{ param.name }}: {{ param.type }},
{%- endfor %}
{%- if endpoint.request_body %}
        data: {{ endpoint.request_body.type }},
{%- endif %}
    ) -> {{ endpoint.responses | get_return_type }}:
        """{{ endpoint.summary }}"""
        url = f"{self.base_url}{{ endpoint.path }}"

{%- if endpoint.parameters %}
        # パスパラメータの置換
{%- for param in endpoint.parameters %}
{%- if param.in == 'path' %}
        url = url.replace("{{ '{' + param.name + '}' }}", str({{ param.name }}))
{%- endif %}
{%- endfor %}

        # クエリパラメータの設定
        params = {}
{%- for param in endpoint.parameters %}
{%- if param.in == 'query' %}
        if {{ param.name }} is not None:
            params["{{ param.name }}"] = {{ param.name }}
{%- endif %}
{%- endfor %}
{%- endif %}

        response = await self.client.{{ endpoint.method | lower }}(
            url,
{%- if endpoint.parameters %}
            params=params,
{%- endif %}
{%- if endpoint.request_body %}
            json=data.model_dump() if hasattr(data, 'model_dump') else data,
{%- endif %}
            headers=self.headers,
        )
        response.raise_for_status()

{%- if endpoint.responses | get_return_type != "None" %}
        return response.json()
{%- else %}
        return None
{%- endif %}

{%- endfor %}
'''
