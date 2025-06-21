from typing import Any, Dict
from json import dumps
from datetime import timedelta
from concurrent.futures import ThreadPoolExecutor


class Master_Catacombs:
    def __init__(self, master_catacombs: Dict[str, Any]) -> None:
        self._data = master_catacombs

    def __str__(self) -> str:
        return dumps(self._data, indent=3)

    def _format_time(self, timestamps: Dict[int | str, int]) -> Dict[int | str, str]:
        formatted_timestamps = {}
        for floor, time in timestamps.items():
            formatted_timestamps[floor] = self._format_timedelta(
                timedelta(milliseconds=time)
            )

        return formatted_timestamps

    def _format_timedelta(self, td: timedelta):
        total_seconds = td.total_seconds()
        minutes = int(total_seconds // 60)
        seconds = int(total_seconds % 60)
        milliseconds = int(td.microseconds / 1000)
        return f"{minutes:02}:{seconds:02}.{milliseconds:03}"

    def _strip_excess(self, d: Dict[int | str, Any]) -> Dict[int | str, Any]:
        return {k: v for k, v in d.items() if k not in ["total", "best"]}

    def format_data(self) -> Dict[str, Any]:
        with ThreadPoolExecutor() as executor:
            futures = {
                "completions": executor.submit(self._strip_excess, self.completions),
                "fastest_time": executor.submit(self._strip_excess, self.fastest_time),
                "fastest_time_s": executor.submit(
                    self._strip_excess, self.fastest_time_s
                ),
                "fastest_time_s_plus": executor.submit(
                    self._strip_excess, self.fastest_time_s_plus
                ),
                "best_score": executor.submit(self._strip_excess, self.best_score),
            }

            completions = futures["completions"].result()
            fastest_time = futures["fastest_time"].result()
            fastest_time_s = futures["fastest_time_s"].result()
            fastest_time_s_plus = futures["fastest_time_s_plus"].result()
            best_score = futures["best_score"].result()

        all_keys = (
            set(completions)
            | set(fastest_time)
            | set(fastest_time_s)
            | set(fastest_time_s_plus)
            | set(best_score)
        )

        formatted_data = {}
        for key in all_keys:
            formatted_data[int(key)] = {
                "completions": completions.get(key),
                "fastest_time": fastest_time.get(key),
                "fastest_time_s": fastest_time_s.get(key),
                "fastest_time_s_plus": fastest_time_s_plus.get(key),
                "best_score": best_score.get(key),
            }

        return formatted_data

    @property
    def completions(self) -> Dict[int | str, int]:
        return self._data.get("tier_completions", {})

    @property
    def fastest_time(self) -> Dict[int | str, str]:
        return self._format_time(self._data.get("fastest_time", {}))

    @property
    def fastest_time_s(self) -> Dict[int | str, str]:
        return self._format_time(self._data.get("fastest_time_s", {}))

    @property
    def fastest_time_s_plus(self) -> Dict[int | str, str]:
        return self._format_time(self._data.get("fastest_time_s_plus", {}))

    @property
    def best_score(self) -> Dict[int | str, int]:
        return self._data.get("best_score", {})
