from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import Any, Dict, Optional, Set

from pydantic import BaseModel, ConfigDict


class BaseOphelosModel(BaseModel):

    model_config = ConfigDict(
        extra="allow",
        use_enum_values=True,
    )

    @classmethod
    def _get_api_body_fields(cls) -> Optional[Set[str]]:
        return getattr(cls, "__api_body_fields__", None)

    @classmethod
    def _get_api_exclude_fields(cls) -> Set[str]:
        return getattr(cls, "__api_exclude_fields__", {"id", "object", "created_at", "updated_at"})

    def to_api_body(self, exclude_none: bool = True) -> Dict[str, Any]:
        api_body_fields = self._get_api_body_fields()
        if api_body_fields is not None:
            allowed_fields = api_body_fields
        else:
            all_field_names = set(self.__class__.model_fields.keys())
            allowed_fields = all_field_names - self._get_api_exclude_fields()

        api_data = {}

        for field_name in allowed_fields:
            value = getattr(self, field_name, None)

            if exclude_none and value is None:
                continue

            processed_value = self._process_nested_value(value, field_name)
            api_data[field_name] = processed_value

        return api_data

    def _process_nested_value(self, value: Any, field_name: str = "") -> Any:
        if isinstance(value, BaseOphelosModel):
            should_convert_to_id = (
                field_name in {"customer", "organisation"}
                and hasattr(value, "id")
                and getattr(value, "id", None)
                and not getattr(value, "id", "").startswith("temp")
            )

            if should_convert_to_id:
                return getattr(value, "id")

            return value.to_api_body()

        elif isinstance(value, (datetime, date)):
            return value.isoformat()

        elif isinstance(value, list):
            return [self._process_nested_value(item, field_name) for item in value]

        elif isinstance(value, dict):
            return {k: self._process_nested_value(v, k) for k, v in value.items()}

        else:
            return value


class Currency(str, Enum):
    GBP = "GBP"
    EUR = "EUR"
    USD = "USD"
