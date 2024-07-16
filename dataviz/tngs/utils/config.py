from typing import Dict

import pandas as pd
from pydantic import BaseModel
from st_aggrid import AgGrid, GridOptionsBuilder, List
from utils.constants import RETAIN_FILTER_STATE_OPTIONS


class GridOptionsBuilderConfig(BaseModel):
    configure_pagination: List[Dict] = []
    configure_selection: List[Dict] = []
    configure_default_column: List[Dict] = []
    configure_side_bar: List[Dict] = []
    configure_first_column_as_index: List[Dict] = []
    configure_columns: List[Dict] = []
    configure_grid_options: List[Dict] = []

    def build(self, grid_options_builder: GridOptionsBuilder):
        for _ in self.configure_pagination:
            grid_options_builder.configure_pagination(**_)

        for _ in self.configure_selection:
            grid_options_builder.configure_selection(**_)

        for _ in self.configure_default_column:
            grid_options_builder.configure_default_column(**_)

        for _ in self.configure_side_bar:
            grid_options_builder.configure_side_bar(**_)

        for _ in self.configure_first_column_as_index:
            grid_options_builder.configure_first_column_as_index(**_)

        for _ in self.configure_columns:
            grid_options_builder.configure_columns(**_)

        for _ in self.configure_grid_options:
            grid_options_builder.configure_grid_options(**_)


class AgGridConfig(BaseModel):
    grid_options_builder_config: GridOptionsBuilderConfig
    kwargs: Dict = {}

    def get_aggrid(self, grid_options_builder: GridOptionsBuilder, df: pd.DataFrame):
        self.grid_options_builder_config.build(grid_options_builder)
        go = grid_options_builder.build()
        return AgGrid(df, gridOptions=go, **self.kwargs)


def test():
    df = pd.DataFrame.from_records([{"col1": 1, "col2": "2"}])
    gb = GridOptionsBuilder.from_dataframe(df)
    ag_grid_config = AgGridConfig(
        grid_options_builder_config=GridOptionsBuilderConfig(
            configure_grid_options=[RETAIN_FILTER_STATE_OPTIONS]
        )
    )
    aggrid = ag_grid_config.get_aggrid(gb, df)
    print(aggrid.data)


if __name__ == "__main__":
    test()
