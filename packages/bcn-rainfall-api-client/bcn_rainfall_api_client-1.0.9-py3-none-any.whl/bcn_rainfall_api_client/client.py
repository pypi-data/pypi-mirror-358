"""
API client built to interact with FastAPI application without needing the knowledge of the routes URLs.
"""

from api_session import APISession, JSONDict


class APIClient(APISession):
    def __init__(self, *, base_url: str, **kwargs):
        kwargs.setdefault("read_only", True)
        kwargs.setdefault("timeout", 10)
        kwargs.setdefault("max_retries", 3)

        super().__init__(base_url, **kwargs)

    # -- Rainfall metrics -- #

    def get_rainfall_average(
        self,
        *,
        time_mode: str,
        begin_year: int,
        end_year: int | None = None,
        month: str | None = None,
        season: str | None = None,
    ) -> JSONDict:
        return self.get_json_api(
            "/rainfall/average",
            params={
                "time_mode": time_mode,
                "begin_year": begin_year,
                "end_year": end_year,
                "month": month,
                "season": season,
            },
        )

    def get_rainfall_normal(
        self,
        *,
        time_mode: str,
        begin_year: int,
        month: str | None = None,
        season: str | None = None,
    ) -> JSONDict:
        return self.get_json_api(
            "/rainfall/normal",
            params={
                "time_mode": time_mode,
                "begin_year": begin_year,
                "month": month,
                "season": season,
            },
        )

    def get_rainfall_relative_distance_to_normal(
        self,
        *,
        time_mode: str,
        begin_year: int,
        normal_year: int,
        end_year: int | None = None,
        month: str | None = None,
        season: str | None = None,
    ) -> JSONDict:
        return self.get_json_api(
            "/rainfall/relative_distance_to_normal",
            params={
                "time_mode": time_mode,
                "begin_year": begin_year,
                "normal_year": normal_year,
                "end_year": end_year,
                "month": month,
                "season": season,
            },
        )

    def get_rainfall_standard_deviation(
        self,
        *,
        time_mode: str,
        begin_year: int,
        end_year: int | None = None,
        month: str | None = None,
        season: str | None = None,
        weigh_by_average=False,
    ):
        return self.get_json_api(
            "/rainfall/standard_deviation",
            params={
                "time_mode": time_mode,
                "begin_year": begin_year,
                "end_year": end_year,
                "month": month,
                "season": season,
                "weigh_by_average": weigh_by_average,
            },
        )

    # -- Year metrics -- #

    def get_years_below_normal(
        self,
        *,
        time_mode: str,
        normal_year: int,
        begin_year: int,
        end_year: int | None = None,
        month: str | None = None,
        season: str | None = None,
    ) -> JSONDict:
        return self.get_json_api(
            "/year/below_normal",
            params={
                "time_mode": time_mode,
                "normal_year": normal_year,
                "begin_year": begin_year,
                "end_year": end_year,
                "month": month,
                "season": season,
            },
        )

    def get_years_above_normal(
        self,
        *,
        time_mode: str,
        normal_year: int,
        begin_year: int,
        end_year: int | None = None,
        month: str | None = None,
        season: str | None = None,
    ) -> JSONDict:
        return self.get_json_api(
            "/year/above_normal",
            params={
                "time_mode": time_mode,
                "normal_year": normal_year,
                "begin_year": begin_year,
                "end_year": end_year,
                "month": month,
                "season": season,
            },
        )

    # -- CSV data -- #

    def get_rainfall_by_year_as_csv(
        self,
        time_mode: str,
        begin_year: int,
        end_year: int | None = None,
        month: str | None = None,
        season: str | None = None,
    ):
        return self.get_api(
            "/csv/rainfall_by_year",
            params={
                "time_mode": time_mode,
                "begin_year": begin_year,
                "end_year": end_year,
                "month": month,
                "season": season,
            },
        )

    # -- Plotly graphics data -- #

    def get_rainfall_by_year_as_plotly_json(
        self,
        *,
        time_mode: str,
        begin_year: int,
        end_year: int | None = None,
        month: str | None = None,
        season: str | None = None,
        plot_average=False,
        plot_linear_regression=False,
        kmeans_cluster_count: int | None = None,
    ) -> str:
        return self.get_json_api(
            "/graph/rainfall_by_year",
            params={
                "time_mode": time_mode,
                "begin_year": begin_year,
                "end_year": end_year,
                "month": month,
                "season": season,
                "plot_average": plot_average,
                "plot_linear_regression": plot_linear_regression,
                "kmeans_cluster_count": kmeans_cluster_count,
            },
        )

    def get_rainfall_averages_as_plotly_json(
        self,
        *,
        time_mode: str,
        begin_year: int,
        end_year: int | None = None,
    ) -> str:
        return self.get_json_api(
            "/graph/rainfall_averages",
            params={
                "time_mode": time_mode,
                "begin_year": begin_year,
                "end_year": end_year,
            },
        )

    def get_rainfall_linreg_slopes_as_plotly_json(
        self,
        *,
        time_mode: str,
        begin_year: int,
        end_year: int | None = None,
    ) -> str:
        return self.get_json_api(
            "/graph/rainfall_linreg_slopes",
            params={
                "time_mode": time_mode,
                "begin_year": begin_year,
                "end_year": end_year,
            },
        )

    def get_rainfall_relative_distances_to_normal_as_plotly_json(
        self,
        *,
        time_mode: str,
        normal_year: int,
        begin_year: int,
        end_year: int | None = None,
    ) -> str:
        return self.get_json_api(
            "/graph/relative_distances_to_normal",
            params={
                "time_mode": time_mode,
                "normal_year": normal_year,
                "begin_year": begin_year,
                "end_year": end_year,
            },
        )

    def get_rainfall_standard_deviations_as_plotly_json(
        self,
        *,
        time_mode: str,
        begin_year: int,
        end_year: int | None = None,
        weigh_by_average=False,
    ) -> str:
        return self.get_json_api(
            "/graph/standard_deviations",
            params={
                "time_mode": time_mode,
                "begin_year": begin_year,
                "end_year": end_year,
                "weigh_by_average": weigh_by_average,
            },
        )

    def get_percentage_of_years_above_and_below_normal_as_plotly_json(
        self,
        *,
        time_mode: str,
        normal_year: int,
        begin_year: int,
        end_year: int | None = None,
        month: str | None = None,
        season: str | None = None,
        percentages_of_normal="0,80,120,inf",
    ):
        return self.get_json_api(
            "/graph/percentage_of_years_above_and_below_normal",
            params={
                "time_mode": time_mode,
                "normal_year": normal_year,
                "begin_year": begin_year,
                "end_year": end_year,
                "month": month,
                "season": season,
                "percentages_of_normal": percentages_of_normal,
            },
        )
