# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Literal, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["ChartParam"]


class ChartParam(TypedDict, total=False):
    aggregate: Optional[Literal["sum", "count", "avg"]]

    chart_type: Annotated[
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
        ],
        PropertyInfo(alias="chartType"),
    ]

    column_gantt_end_date_id: Annotated[Optional[str], PropertyInfo(alias="columnGanttEndDateId")]

    column_gantt_start_date_id: Annotated[Optional[str], PropertyInfo(alias="columnGanttStartDateId")]

    column_label_id: Annotated[str, PropertyInfo(alias="columnLabelId")]

    column_stack_id: Annotated[Optional[str], PropertyInfo(alias="columnStackId")]

    column_value_id: Annotated[Optional[str], PropertyInfo(alias="columnValueId")]

    show_legend: Annotated[bool, PropertyInfo(alias="showLegend")]

    show_title: Annotated[bool, PropertyInfo(alias="showTitle")]

    show_values: Annotated[bool, PropertyInfo(alias="showValues")]

    sort_aggregate: Annotated[Optional[Literal["asc", "desc"]], PropertyInfo(alias="sortAggregate")]
