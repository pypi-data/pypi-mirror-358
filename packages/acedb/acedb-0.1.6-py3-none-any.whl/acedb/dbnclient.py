import os
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta

import pandas as pd
import databento as dbn


class DBNClient:

    def __init__(self):
        if "DATABENTO_API_KEY" not in os.environ:
            raise ValueError("Missing Databento API key")

        self._client = dbn.Historical()
        print("Databento client initialized.")

    def get_data(
        self,
        dataset: str,
        schema: str,
        symbol: str,
        ranges: List[Tuple[datetime, datetime]],
        stype_in: str = "raw_symbol",
        stype_out: str = "instrument_id",
    ) -> Tuple[Dict[str, Any], list]:
        """
        Get data from Databento for a given dataset and schema.
        """

        data = []
        for start, end in ranges:
            data_fragment = self._client.timeseries.get_range(
                dataset=dataset,
                schema=schema,
                symbols=symbol,
                start=start,
                end=end,
                stype_in=stype_in,
                stype_out=stype_out,
            ).to_df()
            data_fragment.reset_index(inplace=True)
            data.append(data_fragment)

        data = pd.concat(data)

        return data

    def _get_col_dict(self, schema: str) -> list:
        """
        Get the column dictionary for a given dataset and schema.
        """

        cols = self._client.metadata.list_fields(schema, "csv")

        for col in cols:
            if col["name"] in ("ts_event", "ts_recv"):
                col["type"] = "timestamp"

        # symbol always appears at the end
        cols.append({"name": "symbol", "type": "string"})

        return cols

    def _resolve_symbology(
        self,
        dataset: str,
        symbols: List[str] | str,
        stype_in: str,
        stype_out: str,
        start_date: datetime,
        end_date: datetime,
    ) -> List[str]:

        symbols = symbols if isinstance(symbols, list) else [symbols]

        if any(item.endswith((".OPT", ".FUT")) for item in symbols):

            symbols = [
                symbol for symbol in symbols if symbol.endswith((".FUT", ".OPT"))
            ]

            max_span = timedelta(days=365 * 3)
            result_symbols = []

            current_start = start_date
            while current_start < end_date:
                current_end = min(current_start + max_span, end_date)

                symbology = self._client.symbology.resolve(
                    dataset=dataset,
                    symbols=symbols,
                    stype_in=stype_in,
                    stype_out=stype_out,
                    start_date=current_start,
                    end_date=current_end,
                )

                result_symbols.extend(list(symbology["result"].keys()))
                result_symbols.extend(symbology["partial"])

                current_start = current_end

            return list(set(result_symbols))  # remove duplicates
        else:
            return symbols

    ### validation functions ###

    def _validate_dataset(self, dataset: str) -> bool:
        """
        Validate if the dataset exists in Databento.
        """
        if dataset not in self._client.metadata.list_datasets():
            print(f"Dataset {dataset} not found in Databento.")
            return False
        return True

    def _validate_schema(self, dataset: str, schema: str) -> bool:
        """
        Validate if the schema exists in Databento.
        """
        if schema not in self._client.metadata.list_schemas(dataset):
            print(f"Schema {schema} not found in Databento.")
            return False
        return True

    def _get_cost(
        self,
        dataset: str,
        schema: str,
        symbol: str,
        ranges: List[Tuple[datetime, datetime]],
        stype_in: str,
    ) -> float:
        """
        Get the cost of a given dataset and schema.
        """
        total_cost = 0.0
        for start, end in ranges:
            cost = self._client.metadata.get_cost(
                dataset=dataset,
                schema=schema,
                symbols=symbol,
                start=start,
                end=end,
                stype_in=stype_in,
            )
            total_cost += cost

        return total_cost

    def _getmax_range(self, dataset) -> dict:
        """
        Get the maximum range for a given dataset in Databento.
        """
        max_range = self._client.metadata.get_dataset_range(dataset)

        return max_range
