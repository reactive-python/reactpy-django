from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable, Mapping, TypeVar

from django.db.models.base import Model


try:
    from django_filters import FilterSet
except ImportError:
    FilterSet = TypeVar("FilterSet")


__all__ = ["FilterSet", "TableConfig", "bs_table_column_attrs", "bs_table_row_attrs"]


@dataclass
class TableConfig:
    # Will check if value exists in either the model or TableConfig class
    # Automatically tries to get all model and TableConfig fields if `None`
    fields: Iterable[str] | None = None

    model: Model | None = None

    # Allows for renaming columns in the form {old_name: new_name}
    column_names: Mapping[str, str] | None = None

    # By default, all fields are sortable
    sortable_fields: Iterable[str] | None = None

    # https://django-tables2.readthedocs.io/en/latest/pages/column-attributes.html#id1
    # Probably want a callable API similar to  this `func(value:Any, node_type:str)``
    column_attrs: dict[Callable] | None = None

    # https://django-tables2.readthedocs.io/en/latest/pages/column-attributes.html#row-attributes
    # Probably want a callable API similar to  this `func(record:Model, node_type:str)``
    row_attrs: dict[Callable] | None = None

    # https://sparkbyexamples.com/pandas/pandas-sort-dataframe-by-multiple-columns/
    order_by: Iterable[str] | None = None

    # https://django-tables2.readthedocs.io/en/latest/pages/filtering.html
    filterset: FilterSet | None = None

    # Zero means no pagination.
    # https://docs.djangoproject.com/en/4.1/ref/paginator/#django.core.paginator.Paginator
    pagination: int = 0

    # Allows for a custom render function to change render layout
    renderer: Callable | None = None


bs_table_column_attrs = {}
bs_table_row_attrs = {}
