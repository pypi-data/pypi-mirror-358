# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["Chart"]


class Chart(BaseModel):
    aggregate: Optional[Literal["sum", "count", "avg"]] = None

    chart_type: Optional[
        Literal[
            "bar",
            "horizontal-bar",
            "stacked-bar",
            "stacked-horizontal-bar",
            "clustered-bar",
            "clustered-horizontal-bar",
            "grouped-bar",
            "area",
            "line",
            "multiaxis-line",
            "pie",
            "doughnut",
            "polar-area",
            "radar",
            "scatter",
            "bubble",
            "gantt",
        ]
    ] = FieldInfo(alias="chartType", default=None)

    column_gantt_end_date_id: Optional[str] = FieldInfo(alias="columnGanttEndDateId", default=None)

    column_gantt_start_date_id: Optional[str] = FieldInfo(alias="columnGanttStartDateId", default=None)

    column_label_id: Optional[str] = FieldInfo(alias="columnLabelId", default=None)

    column_stack_id: Optional[str] = FieldInfo(alias="columnStackId", default=None)

    column_value_id: Optional[str] = FieldInfo(alias="columnValueId", default=None)

    show_legend: Optional[bool] = FieldInfo(alias="showLegend", default=None)

    show_title: Optional[bool] = FieldInfo(alias="showTitle", default=None)

    show_values: Optional[bool] = FieldInfo(alias="showValues", default=None)

    sort_aggregate: Optional[Literal["asc", "desc"]] = FieldInfo(alias="sortAggregate", default=None)
