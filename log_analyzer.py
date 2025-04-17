import json
from pathlib import Path
from typing import Any

import pandas as pd
from loguru import logger


class LogAnalyzer:
    def __init__(self, logs_dir: str = "logs"):
        self.logs_dir = Path(logs_dir)
        self.log_data: list[dict[str, Any]] = []
        self.df: pd.DataFrame | None = None

    def load_logs(self) -> pd.DataFrame:
        """Load and parse all log files in the logs directory."""
        logger.info(f"Loading logs from {self.logs_dir}")

        for log_file in self.logs_dir.glob("*.log"):
            try:
                with open(log_file) as f:
                    for line in f:
                        try:
                            log_entry = json.loads(line)
                            if "record" in log_entry:
                                self.log_data.append(log_entry["record"])
                        except json.JSONDecodeError:
                            logger.warning(f"Failed to parse log line in {log_file}")
                            continue
            except Exception as e:
                logger.error(f"Error reading log file {log_file}: {e}")

        if not self.log_data:
            logger.warning("No log data found")
            return pd.DataFrame()

        self.df = pd.DataFrame(self.log_data)
        return self.df

    def get_level_distribution(self) -> pd.DataFrame:
        """Get distribution of log levels."""
        if self.df is None:
            return pd.DataFrame()

        # Extract log levels and count their occurrences
        level_counts = self.df["level"].apply(lambda x: x["name"]).value_counts()

        # Create a DataFrame with unique column names
        return pd.DataFrame({"level": level_counts.index, "frequency": level_counts.values})

    def get_response_times(self) -> pd.DataFrame:
        """Get API response times."""
        if self.df is None:
            return pd.DataFrame()

        mask = self.df["message"].str.contains("received data from API", na=False)
        return self.df[mask].loc[:, ["elapsed", "extra", "time", "message"]]

    def get_process_durations(self) -> pd.DataFrame:
        """Get process durations."""
        if self.df is None:
            return pd.DataFrame()

        return (
            self.df[["elapsed", "module", "function", "message"]]
            .assign(duration=lambda x: x["elapsed"].apply(lambda y: y["seconds"]))
            .sort_values("duration", ascending=False)
        )

    def get_module_activity(self) -> pd.DataFrame:
        """Get module activity over time."""
        if self.df is None:
            return pd.DataFrame()

        return (
            self.df[["time", "module", "message"]]
            .assign(timestamp=lambda x: pd.to_datetime(x["time"].apply(lambda y: y["repr"])))
            .sort_values(["timestamp"], ascending=False)
            .reset_index(drop=True)
        )

    def get_success_error_rate(self) -> dict[str, int]:
        """Get success vs error rate."""
        if self.df is None:
            return {"success": 0, "error": 0}

        success = len(self.df[self.df["level"].apply(lambda x: x["name"] in ["SUCCESS", "INFO"])])
        error = len(self.df[self.df["level"].apply(lambda x: x["name"] in ["ERROR", "WARNING"])])
        return {"success": success, "error": error}

    def get_data_processing_stats(self) -> pd.DataFrame:
        """Get statistics about data processing."""
        if self.df is None:
            return pd.DataFrame()

        mask = self.df["message"].str.contains("Created DataFrame from API data", na=False)
        stats_series = self.df[mask].apply(lambda x: x["extra"]["extra"], axis=1)
        return pd.DataFrame(stats_series.tolist())
