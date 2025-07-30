"""モデル生成用テンプレート"""

# 基本モデルテンプレート
MODEL_TEMPLATE = '''"""{{ model.name }} モデル定義"""

from __future__ import annotations
from typing import Any
from pydantic import BaseModel


class {{ model.name }}(BaseModel):
    """{{ model.description }}"""
{%- for field in model.fields %}
    {{ field.name }}: {{ field.type }}{% if field.description %}  # {{ field.description }}{% endif %}
{%- endfor %}

'''
