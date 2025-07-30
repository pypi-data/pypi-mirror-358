"""
F1 Safety Car Prediction ETL Pipeline - Complete Aggregated Code
================================================================

This file contains all the code from the f1_etl package aggregated into a single
file for easy testing in Jupyter notebooks. It includes the per-session temporal
integrity improvements to prevent cross-session contamination.

Usage in Jupyter:
    exec(open('f1_etl_complete.py').read())

    # Then use normally:
    session = SessionConfig(2024, "Monaco Grand Prix", "R")
    config = DataConfig(sessions=[session])
    dataset = create_safety_car_dataset(config)
"""

import numpy as np
import pandas as pd
import fastf1
import pickle
import logging
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional, Union, Dict, Any, Tuple
from collections import defaultdict
from sklearn.preprocessing import LabelEncoder


# =============================================================================
# LOGGING MODULE
# =============================================================================


def setup_logger(
    name: str = "f1_etl", level: int = logging.INFO, enable_debug: bool = False
) -> logging.Logger:
    """Setup logger for the ETL pipeline"""
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG if enable_debug else level)

    # Clear existing handlers
    logger.handlers.clear()

    # Create console handler
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG if enable_debug else level)

    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    return logger


# Default logger
logger = setup_logger()


# =============================================================================
# CONFIG MODULE
# =============================================================================


@dataclass
class SessionConfig:
    """Configuration for a single F1 session"""

    year: int
    race: str
    session_type: str


@dataclass
class DataConfig:
    """Configuration for data processing"""

    sessions: List[SessionConfig]
    drivers: Optional[List[str]] = None
    telemetry_frequency: Union[str, int] = "original"
    include_weather: bool = True
    cache_dir: Optional[str] = None


# =============================================================================
# ENCODERS MODULE
# =============================================================================


class TrackStatusLabelEncoder:
    """Encodes track status labels for safety car prediction"""

    def __init__(self):
        self.label_encoder = LabelEncoder()
        self.is_fitted = False
        self.track_status_mapping = {
            "1": "green",
            "2": "yellow",
            "4": "safety_car",
            "5": "red",
            "6": "vsc",
            "7": "vsc_ending",
        }

    def fit(self, track_status_data: pd.Series) -> "TrackStatusLabelEncoder":
        mapped_labels = track_status_data.map(self.track_status_mapping).fillna(
            "unknown"
        )
        self.label_encoder.fit(mapped_labels)
        self.is_fitted = True
        return self

    def transform(self, track_status_data: pd.Series) -> np.ndarray:
        if not self.is_fitted:
            raise ValueError("LabelEncoder must be fitted before transform")
        mapped_labels = track_status_data.map(self.track_status_mapping).fillna(
            "unknown"
        )
        return self.label_encoder.transform(mapped_labels)

    def fit_transform(self, track_status_data: pd.Series) -> np.ndarray:
        return self.fit(track_status_data).transform(track_status_data)

    def inverse_transform(self, encoded_labels: np.ndarray) -> np.ndarray:
        return self.label_encoder.inverse_transform(encoded_labels)

    def get_classes(self) -> np.ndarray:
        return self.label_encoder.classes_


class DriverLabelEncoder:
    """Encodes driver identifiers for consistency"""

    def __init__(self):
        self.label_encoder = LabelEncoder()
        self.is_fitted = False
        self.driver_to_number = {}  # Maps abbreviations to driver numbers
        self.number_to_driver = {}  # Maps driver numbers to abbreviations

    def fit_session(self, session) -> "DriverLabelEncoder":
        """Fit the encoder using session driver data"""
        driver_numbers = session.drivers

        for driver_number in driver_numbers:
            driver_info = session.get_driver(driver_number)
            abbreviation = driver_info["Abbreviation"]

            self.driver_to_number[abbreviation] = driver_number
            self.number_to_driver[driver_number] = abbreviation

        # Fit encoder on abbreviations for consistent encoding
        abbreviations = list(self.driver_to_number.keys())
        self.label_encoder.fit(abbreviations)
        self.is_fitted = True
        return self

    def transform_driver_to_number(self, drivers):
        """Transform driver abbreviations to driver numbers"""
        if not self.is_fitted:
            raise ValueError("Encoder not fitted")
        return [self.driver_to_number[driver] for driver in drivers]

    def transform_number_to_driver(self, numbers):
        """Transform driver numbers to abbreviations"""
        if not self.is_fitted:
            raise ValueError("Encoder not fitted")
        return [self.number_to_driver[number] for number in numbers]


# =============================================================================
# EXTRACTION MODULE
# =============================================================================


class RawDataExtractor:
    """Handles extraction of raw fastf1 data"""

    def __init__(self, cache_dir: Optional[str] = None):
        self.cache_dir = Path(cache_dir) if cache_dir else None
        if self.cache_dir:
            self.cache_dir.mkdir(exist_ok=True)

    def extract_session(self, config: SessionConfig) -> Dict[str, Any]:
        """Extract all data for a single session"""
        print(f"Loading session: {config.year} {config.race} {config.session_type}")

        cache_key = f"{config.year}_{config.race}_{config.session_type}".replace(
            " ", "_"
        )
        cache_file = self.cache_dir / f"{cache_key}.pkl" if self.cache_dir else None

        if cache_file and cache_file.exists():
            print(f"Loading from cache: {cache_file}")
            with open(cache_file, "rb") as f:
                return pickle.load(f)

        session = fastf1.get_session(config.year, config.race, config.session_type)
        session.load()

        driver_mapping = {}
        for driver_number in session.drivers:
            driver_info = session.get_driver(driver_number)
            driver_mapping[driver_number] = driver_info["Abbreviation"]

        session_data = {
            "session_info": {
                "year": config.year,
                "race": config.race,
                "session_type": config.session_type,
                "event_name": session.event.EventName,
                "event_date": session.event.EventDate,
                "session_start": session.session_start_time,
                "t0_date": session.t0_date,
            },
            "laps": session.laps,
            "weather": session.weather_data,
            "track_status": session.track_status,
            "car_data": {},
            "pos_data": {},
            "drivers": list(session.drivers),
            "driver_mapping": driver_mapping,
        }

        for driver_number in session_data["drivers"]:
            try:
                session_data["car_data"][driver_number] = session.car_data[
                    driver_number
                ]
                session_data["pos_data"][driver_number] = session.pos_data[
                    driver_number
                ]
            except Exception as e:
                abbreviation = driver_mapping.get(driver_number, driver_number)
                print(
                    f"Warning: Could not extract telemetry for driver ({abbreviation}, {driver_number}): {e}"
                )

        if cache_file:
            with open(cache_file, "wb") as f:
                pickle.dump(session_data, f)

        return session_data


# =============================================================================
# AGGREGATION MODULE
# =============================================================================


class DataAggregator:
    """Aggregates raw data across multiple sessions"""

    def __init__(self):
        self.aggregated_data = defaultdict(list)

    def aggregate_telemetry_data(
        self, sessions_data: List[Dict[str, Any]], drivers: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """Aggregate telemetry data across sessions with track status alignment"""
        all_telemetry = []

        for session_data in sessions_data:
            session_telemetry = self._merge_session_telemetry(session_data, drivers)

            session_telemetry["SessionYear"] = session_data["session_info"]["year"]
            session_telemetry["SessionRace"] = session_data["session_info"]["race"]
            session_telemetry["SessionType"] = session_data["session_info"][
                "session_type"
            ]
            session_telemetry["SessionId"] = (
                f"{session_data['session_info']['year']}_{session_data['session_info']['race']}_{session_data['session_info']['session_type']}"
            )

            track_status = session_data.get("track_status", pd.DataFrame())
            t0_date = session_data["session_info"]["t0_date"]
            session_telemetry = self._align_track_status(
                session_telemetry, track_status, t0_date
            )

            all_telemetry.append(session_telemetry)

        return pd.concat(all_telemetry, ignore_index=True)

    def process_single_session(
        self, session_data: Dict[str, Any], drivers: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """Process a single session's telemetry data with track status alignment

        This method encapsulates all the session-specific processing logic to ensure
        consistent handling of temporal context and track status alignment.
        """
        logger.debug(f"Processing session: {session_data['session_info']}")

        # Extract and merge telemetry data for this session
        session_telemetry = self._merge_session_telemetry(session_data, drivers)

        if session_telemetry.empty:
            logger.warning("No telemetry data available for session")
            return session_telemetry

        # Add session metadata to preserve racing context
        session_telemetry["SessionYear"] = session_data["session_info"]["year"]
        session_telemetry["SessionRace"] = session_data["session_info"]["race"]
        session_telemetry["SessionType"] = session_data["session_info"]["session_type"]
        session_telemetry["SessionId"] = (
            f"{session_data['session_info']['year']}_{session_data['session_info']['race']}_{session_data['session_info']['session_type']}"
        )

        # Align track status within this session's temporal context
        track_status = session_data.get("track_status", pd.DataFrame())
        t0_date = session_data["session_info"]["t0_date"]
        session_telemetry = self._align_track_status(
            session_telemetry, track_status, t0_date
        )

        logger.debug(f"Processed {len(session_telemetry)} telemetry rows for session")
        return session_telemetry

    def _align_track_status(
        self, telemetry: pd.DataFrame, track_status: pd.DataFrame, t0_date
    ) -> pd.DataFrame:
        """Align track status with telemetry timestamps using forward fill"""
        if track_status is None or track_status.empty or telemetry.empty:
            if not telemetry.empty:
                telemetry["TrackStatus"] = "1"
                telemetry["TrackStatusMessage"] = "AllClear"
            return telemetry

        if "Date" not in telemetry.columns:
            logger.warning(
                "No Date column in telemetry data, skipping track status alignment"
            )
            telemetry["TrackStatus"] = "1"
            telemetry["TrackStatusMessage"] = "AllClear"
            return telemetry

        if "Time" not in track_status.columns or "Status" not in track_status.columns:
            logger.warning("Track status data missing required columns, using default")
            telemetry["TrackStatus"] = "1"
            telemetry["TrackStatusMessage"] = "AllClear"
            return telemetry

        try:
            track_status_with_date = track_status.copy()
            track_status_with_date["Date"] = t0_date + track_status_with_date["Time"]

            status_cols = ["Date", "Status"]
            if "Message" in track_status_with_date.columns:
                status_cols.append("Message")

            telemetry_with_status = pd.merge_asof(
                telemetry.sort_values("Date"),
                track_status_with_date[status_cols].sort_values("Date"),
                on="Date",
                direction="backward",
            ).fillna({"Status": "1", "Status_y": "1"})  # Handle both possible names

            # Check which Status column exists and rename appropriately
            status_col = (
                "Status_y" if "Status_y" in telemetry_with_status.columns else "Status"
            )
            message_col = (
                "Message_y"
                if "Message_y" in telemetry_with_status.columns
                else "Message"
            )

            if message_col not in telemetry_with_status.columns:
                telemetry_with_status[message_col] = "AllClear"
            else:
                telemetry_with_status[message_col] = telemetry_with_status[
                    message_col
                ].fillna("AllClear")

            # Rename using the correct column names
            rename_dict = {status_col: "TrackStatus"}
            if message_col in telemetry_with_status.columns:
                rename_dict[message_col] = "TrackStatusMessage"

            telemetry_with_status = telemetry_with_status.rename(columns=rename_dict)

            return telemetry_with_status

        except Exception as e:
            logger.warning(f"Failed to align track status: {e}")
            telemetry["TrackStatus"] = "1"
            telemetry["TrackStatusMessage"] = "AllClear"
            return telemetry

    def _merge_session_telemetry(
        self, session_data: Dict[str, Any], drivers: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """Merge car and position data for a single session"""
        session_drivers = drivers if drivers else session_data["drivers"]
        session_telemetry = []

        for driver_number in session_drivers:
            if driver_number not in session_data["car_data"]:
                continue

            try:
                car_data = session_data["car_data"][driver_number]
                pos_data = session_data["pos_data"][driver_number]

                merged = car_data.merge_channels(pos_data, frequency="original")
                merged = merged.add_distance().add_differential_distance()
                merged["Driver"] = driver_number

                session_telemetry.append(merged)

            except Exception as e:
                logger.warning(
                    f"Could not merge telemetry for driver {driver_number}: {e}"
                )

        if session_telemetry:
            result = pd.concat(session_telemetry, ignore_index=True)
            if "Date" not in result.columns and "Time" in result.columns:
                result = result.rename(columns={"Time": "Date"})
            elif (
                "Date" not in result.columns
                and hasattr(result, "index")
                and hasattr(result.index, "name")
            ):
                result = result.reset_index()
                if "index" in result.columns:
                    result = result.rename(columns={"index": "Date"})
            return result
        else:
            return pd.DataFrame()


# =============================================================================
# TIME SERIES MODULE
# =============================================================================


class TimeSeriesGenerator:
    """Generates sliding window time series sequences from telemetry data"""

    def __init__(
        self,
        window_size: int,
        step_size: int = 1,
        features: Optional[List[str]] = None,
        prediction_horizon: int = 1,
        handle_non_numeric: str = "encode",  # 'encode' or 'drop'
        target_column: str = "TrackStatus",
    ):  # Configurable target column
        self.window_size = window_size
        self.step_size = step_size
        self.prediction_horizon = prediction_horizon
        self.handle_non_numeric = handle_non_numeric
        self.target_column = target_column
        self.features = features or [
            "Speed",
            "RPM",
            "nGear",
            "Throttle",
            "Brake",
            "X",
            "Y",
            "Distance",
            "DifferentialDistance",
        ]

    def _process_features(
        self, group_data: pd.DataFrame
    ) -> Tuple[np.ndarray, List[str]]:
        """
        Process features to handle non-numeric data types
        Returns numpy array with proper dtype and list of processed feature names
        """
        available_features = [f for f in self.features if f in group_data.columns]
        if not available_features:
            raise ValueError(
                f"No requested features found in data. Available: {list(group_data.columns)}"
            )

        feature_data = group_data[available_features].copy()
        processed_features = []

        for feature in available_features:
            col = feature_data[feature]

            if pd.api.types.is_numeric_dtype(col):
                # Already numeric, keep as-is
                processed_features.append(feature)
            elif pd.api.types.is_bool_dtype(col) or col.dtype == "bool":
                # Boolean - encode as 0/1
                if self.handle_non_numeric == "encode":
                    feature_data[feature] = col.astype(int)
                    processed_features.append(feature)
                    logger.debug(f"Encoded boolean feature '{feature}' as 0/1")
                elif self.handle_non_numeric == "drop":
                    logger.debug(f"Dropping boolean feature '{feature}'")
                    feature_data = feature_data.drop(columns=[feature])
            elif col.dtype == "object":
                # Check if it's actually numeric stored as object
                try:
                    converted = pd.to_numeric(col, errors="coerce")
                    if not converted.isna().all():
                        feature_data[feature] = converted
                        processed_features.append(feature)
                        logger.debug(f"Converted object feature '{feature}' to numeric")
                    else:
                        # Non-numeric object
                        if self.handle_non_numeric == "encode":
                            # Simple label encoding for categorical
                            unique_vals = col.unique()
                            mapping = {val: i for i, val in enumerate(unique_vals)}
                            feature_data[feature] = col.map(mapping)
                            processed_features.append(feature)
                            logger.debug(
                                f"Label encoded categorical feature '{feature}': {mapping}"
                            )
                        elif self.handle_non_numeric == "drop":
                            logger.debug(f"Dropping non-numeric feature '{feature}'")
                            feature_data = feature_data.drop(columns=[feature])
                except Exception as e:
                    logger.warning(f"Could not process feature '{feature}': {e}")
                    if self.handle_non_numeric == "drop":
                        feature_data = feature_data.drop(columns=[feature])
            else:
                # Other data types
                if self.handle_non_numeric == "drop":
                    logger.debug(
                        f"Dropping unsupported feature '{feature}' (dtype: {col.dtype})"
                    )
                    feature_data = feature_data.drop(columns=[feature])
                else:
                    logger.warning(
                        f"Attempting to convert '{feature}' (dtype: {col.dtype}) to numeric"
                    )
                    try:
                        feature_data[feature] = pd.to_numeric(col, errors="coerce")
                        processed_features.append(feature)
                    except:
                        feature_data = feature_data.drop(columns=[feature])

        if feature_data.empty:
            raise ValueError("No valid features remaining after processing")

        # Convert to numeric numpy array
        try:
            feature_array = feature_data[processed_features].astype(np.float64).values
        except Exception as e:
            logger.error(f"Error converting to float64: {e}")
            logger.error(f"Data types: {feature_data[processed_features].dtypes}")
            raise

        return feature_array, processed_features

    def generate_sequences(
        self, telemetry_data: pd.DataFrame, group_by: List[str] = None
    ) -> Tuple[np.ndarray, np.ndarray, List[dict]]:
        """Generate sliding window sequences with built-in preprocessing

        Now expects telemetry_data from a single session to ensure temporal coherence.
        This prevents the creation of sequences that span across different racing contexts.
        """
        if group_by is None:
            # Changed from ['SessionId', 'Driver'] to just ['Driver'] since we now
            # process sessions independently and all data should be from one session
            group_by = ["Driver"]

        # Validate temporal integrity - all data should be from the same session
        if "SessionId" in telemetry_data.columns:
            unique_sessions = telemetry_data["SessionId"].nunique()
            if unique_sessions > 1:
                session_ids = telemetry_data["SessionId"].unique()
                raise ValueError(
                    f"Multiple sessions detected in single call: {session_ids}. "
                    f"This violates the per-session processing assumption and could "
                    f"lead to temporal contamination. Each call should contain data "
                    f"from exactly one racing session."
                )
            elif unique_sessions == 1:
                session_id = telemetry_data["SessionId"].iloc[0]
                logger.debug(f"Processing single session: {session_id}")

        # Continue with existing sequence generation logic
        # The rest of the function remains unchanged since the core windowing
        # algorithm is sound - we've just ensured it operates on clean data
        sequences = []
        labels = []
        metadata = []

        logger.info(
            f"Processing {len(telemetry_data)} telemetry rows from single session"
        )
        logger.info(f"Grouping by: {group_by}")
        logger.debug(f"Available columns: {list(telemetry_data.columns)}")

        group_count = 0
        for group_keys, group_data in telemetry_data.groupby(group_by):
            group_count += 1
            logger.debug(f"Processing group {group_count}: {group_keys}")
            logger.debug(f"  Group size: {len(group_data)} rows")
            logger.debug(
                f"  Required minimum rows: {self.window_size + self.prediction_horizon}"
            )

            try:
                group_sequences, group_labels, group_metadata = (
                    self._generate_group_sequences(group_data, group_keys, group_by)
                )
                logger.debug(f"  Generated {len(group_sequences)} sequences")
                sequences.extend(group_sequences)
                labels.extend(group_labels)
                metadata.extend(group_metadata)

            except Exception as e:
                logger.warning(f"Error processing group {group_keys}: {e}")
                logger.debug("Full traceback:", exc_info=True)
                continue

        logger.info(f"Total sequences generated: {len(sequences)}")
        if not sequences:
            logger.error("No sequences generated - debugging info:")
            logger.error(f"  Total groups processed: {group_count}")
            logger.error(f"  Window size: {self.window_size}")
            logger.error(f"  Prediction horizon: {self.prediction_horizon}")
            logger.error(f"  Required features: {self.features}")
            logger.error(f"  Target column: {self.target_column}")

            # Check if target column exists
            if self.target_column not in telemetry_data.columns:
                logger.error(
                    f"  ERROR: {self.target_column} column missing! Available: {list(telemetry_data.columns)}"
                )
            else:
                logger.error(
                    f"  {self.target_column} values: {telemetry_data[self.target_column].unique()}"
                )

            raise ValueError("No sequences generated - see debug output above")

        return np.array(sequences), np.array(labels), metadata

    def _generate_group_sequences(
        self, group_data: pd.DataFrame, group_keys: Tuple, group_by: List[str]
    ) -> Tuple[List, List, List]:
        """Generate sequences for a single group"""
        # Sort by time
        if "Date" not in group_data.columns:
            raise ValueError(
                f"Date column missing from group data. Available: {list(group_data.columns)}"
            )

        group_data_sorted = group_data.sort_values("Date").reset_index(drop=True)
        logger.debug(f"    Sorted group data: {len(group_data_sorted)} rows")

        # Process features to handle non-numeric data
        try:
            feature_array, processed_features = self._process_features(
                group_data_sorted
            )
            logger.debug(f"    Processed features: {processed_features}")
            logger.debug(f"    Feature array shape: {feature_array.shape}")
        except Exception as e:
            logger.debug(f"    Feature processing failed: {e}")
            raise

        sequences = []
        labels = []
        metadata = []

        max_start_idx = (
            len(feature_array) - self.window_size - self.prediction_horizon + 1
        )
        logger.debug(
            f"    Max start index: {max_start_idx} (need >= 0 to generate sequences)"
        )

        if max_start_idx <= 0:
            logger.debug(
                f"    Insufficient data: need {self.window_size + self.prediction_horizon} rows, have {len(feature_array)}"
            )
            return sequences, labels, metadata

        # Check for target column
        if self.target_column not in group_data_sorted.columns:
            logger.debug(
                f"    {self.target_column} column missing! Available: {list(group_data_sorted.columns)}"
            )
            return sequences, labels, metadata

        sequences_generated = 0
        for i in range(0, max_start_idx, self.step_size):
            sequence = feature_array[i : i + self.window_size]

            label_idx = i + self.window_size + self.prediction_horizon - 1
            if label_idx < len(group_data_sorted):
                label = group_data_sorted.iloc[label_idx][self.target_column]
            else:
                logger.debug(
                    f"    Label index {label_idx} out of bounds (max: {len(group_data_sorted) - 1})"
                )
                continue

            seq_metadata = {
                "start_time": group_data_sorted.iloc[i]["Date"],
                "end_time": group_data_sorted.iloc[i + self.window_size - 1]["Date"],
                "prediction_time": group_data_sorted.iloc[label_idx]["Date"],
                "sequence_length": self.window_size,
                "prediction_horizon": self.prediction_horizon,
                "features_used": processed_features,
                "target_column": self.target_column,
            }

            for j, key in enumerate(group_by):
                seq_metadata[key] = (
                    group_keys[j] if isinstance(group_keys, tuple) else group_keys
                )

            # Ensure SessionId is always included in metadata for temporal validation
            if "SessionId" in group_data_sorted.columns:
                seq_metadata["SessionId"] = group_data_sorted.iloc[0]["SessionId"]

            sequences.append(sequence)
            labels.append(label)
            metadata.append(seq_metadata)
            sequences_generated += 1

        logger.debug(f"    Successfully generated {sequences_generated} sequences")
        return sequences, labels, metadata


# =============================================================================
# FEATURE ENGINEERING MODULE
# =============================================================================


class FeatureEngineer:
    """Applies feature engineering to time series data"""

    def __init__(self):
        self.normalization_params = {}
        self.is_fitted = False

    def handle_missing_values(
        self, X: np.ndarray, strategy: str = "forward_fill"
    ) -> np.ndarray:
        """Handle missing values in numeric time series data"""
        if not np.isnan(X).any():
            logger.info("No missing values detected, skipping imputation")
            return X

        logger.info(f"Handling missing values with strategy: {strategy}")
        X_filled = X.copy()

        if strategy == "forward_fill":
            for i in range(X.shape[0]):
                for j in range(X.shape[2]):
                    series = X_filled[i, :, j]
                    mask = np.isnan(series)
                    if mask.any():
                        last_valid = None
                        for k in range(len(series)):
                            if not np.isnan(series[k]):
                                last_valid = series[k]
                            elif last_valid is not None:
                                series[k] = last_valid

                        if np.isnan(series[0]):
                            valid_indices = np.where(~np.isnan(series))[0]
                            if len(valid_indices) > 0:
                                fill_value = series[valid_indices[0]]
                                for k in range(valid_indices[0]):
                                    series[k] = fill_value
                        X_filled[i, :, j] = series
        elif strategy == "mean_fill":
            for j in range(X.shape[2]):
                feature_data = X[:, :, j]
                feature_mean = np.nanmean(feature_data)
                X_filled[:, :, j] = np.where(
                    np.isnan(feature_data), feature_mean, feature_data
                )
        elif strategy == "zero_fill":
            X_filled = np.where(np.isnan(X_filled), 0, X_filled)

        return X_filled

    def normalize_sequences(
        self, X: np.ndarray, method: str = "standard", fit: bool = True
    ) -> np.ndarray:
        """Normalize time series sequences"""
        if method == "standard":
            if fit or not self.is_fitted:
                means = np.mean(X, axis=(0, 1), keepdims=True)
                stds = np.std(X, axis=(0, 1), keepdims=True)
                stds = np.where(stds == 0, 1, stds)
                self.normalization_params = {"means": means, "stds": stds}
                self.is_fitted = True

            params = self.normalization_params
            return (X - params["means"]) / params["stds"]

        elif method == "minmax":
            if fit or not self.is_fitted:
                mins = np.min(X, axis=(0, 1), keepdims=True)
                maxs = np.max(X, axis=(0, 1), keepdims=True)
                ranges = maxs - mins
                ranges = np.where(ranges == 0, 1, ranges)
                self.normalization_params = {"mins": mins, "ranges": ranges}
                self.is_fitted = True

            params = self.normalization_params
            return (X - params["mins"]) / params["ranges"]

        elif method == "per_sequence":
            normalized = np.zeros_like(X)
            for i in range(X.shape[0]):
                seq = X[i]
                seq_mean = np.mean(seq, axis=0, keepdims=True)
                seq_std = np.std(seq, axis=0, keepdims=True)
                seq_std = np.where(seq_std == 0, 1, seq_std)
                normalized[i] = (seq - seq_mean) / seq_std
            return normalized

        else:
            raise ValueError(f"Unknown normalization method: {method}")


# =============================================================================
# PIPELINE MODULE
# =============================================================================


def validate_temporal_integrity(metadata):
    """Validate that all sequences maintain proper temporal boundaries

    This function helps verify that the per-session approach is working correctly
    by ensuring no sequence spans across different racing contexts.
    """
    logger.info("Validating temporal integrity of generated sequences...")

    session_sequence_counts = {}
    temporal_violations = []

    for i, meta in enumerate(metadata):
        session_id = meta["SessionId"]
        start_time = meta["start_time"]
        end_time = meta["end_time"]
        prediction_time = meta["prediction_time"]

        # Count sequences per session
        session_sequence_counts[session_id] = (
            session_sequence_counts.get(session_id, 0) + 1
        )

        # Verify that all times are reasonable (this catches obvious temporal issues)
        if prediction_time < end_time:
            temporal_violations.append(
                f"Sequence {i}: prediction time {prediction_time} before sequence end {end_time}"
            )

        # Log detailed info for debugging
        logger.debug(
            f"Sequence {i}: {session_id} from {start_time} to {prediction_time}"
        )

    if temporal_violations:
        logger.error(f"Found {len(temporal_violations)} temporal violations:")
        for violation in temporal_violations:
            logger.error(f"  {violation}")
        raise ValueError("Temporal integrity validation failed")

    logger.info("Temporal integrity validation passed")
    logger.info(f"Sequences per session: {session_sequence_counts}")
    return session_sequence_counts


def create_safety_car_dataset(
    config: DataConfig,
    window_size: int = 100,
    prediction_horizon: int = 10,
    handle_non_numeric: str = "encode",
    normalization_method: str = "standard",
    target_column: str = "TrackStatus",
    enable_debug: bool = False,
) -> Dict[str, Any]:
    """Complete ETL pipeline for safety car prediction dataset"""

    # Setup logging
    global logger
    logger = setup_logger(enable_debug=enable_debug)

    # Step 1: Extract raw data
    extractor = RawDataExtractor(config.cache_dir)
    sessions_data = [
        extractor.extract_session(session_config) for session_config in config.sessions
    ]

    # Step 2: Initialize data aggregator for per-session processing
    aggregator = DataAggregator()

    # Step 3: Initialize time series generator
    ts_generator = TimeSeriesGenerator(
        window_size=window_size,
        step_size=window_size // 2,
        prediction_horizon=prediction_horizon,
        handle_non_numeric=handle_non_numeric,
        target_column=target_column,
    )

    # Step 4: Process each session independently to maintain temporal integrity
    all_sequences = []
    all_labels = []
    all_metadata = []

    # Initialize label encoder once to ensure consistency across all sessions
    label_encoder = None
    if target_column == "TrackStatus":
        label_encoder = TrackStatusLabelEncoder()

        # Pre-fit the encoder on track status values from all sessions
        # This ensures consistent encoding across different racing contexts
        all_track_statuses = []
        for session_data in sessions_data:
            temp_telemetry = aggregator._merge_session_telemetry(
                session_data, config.drivers
            )
            if not temp_telemetry.empty:
                track_status = session_data.get("track_status", pd.DataFrame())
                t0_date = session_data["session_info"]["t0_date"]
                temp_telemetry = aggregator._align_track_status(
                    temp_telemetry, track_status, t0_date
                )
                if "TrackStatus" in temp_telemetry.columns:
                    all_track_statuses.extend(temp_telemetry["TrackStatus"].unique())

        if all_track_statuses:
            # Fit encoder on all possible track status values for consistency
            sample_series = pd.Series(list(set(all_track_statuses)))
            label_encoder.fit(sample_series)

    # Process each session independently to maintain temporal integrity
    for session_data in sessions_data:
        session_id = f"{session_data['session_info']['year']}_{session_data['session_info']['race']}_{session_data['session_info']['session_type']}"
        logger.info(f"Processing session: {session_id}")

        # Extract and prepare telemetry for this specific session
        session_telemetry = aggregator._merge_session_telemetry(
            session_data, config.drivers
        )

        # Add session metadata to telemetry data
        session_telemetry["SessionYear"] = session_data["session_info"]["year"]
        session_telemetry["SessionRace"] = session_data["session_info"]["race"]
        session_telemetry["SessionType"] = session_data["session_info"]["session_type"]
        session_telemetry["SessionId"] = session_id

        # Align track status for this session's temporal context
        track_status = session_data.get("track_status", pd.DataFrame())
        t0_date = session_data["session_info"]["t0_date"]
        session_telemetry = aggregator._align_track_status(
            session_telemetry, track_status, t0_date
        )

        # Skip sessions with insufficient data
        if session_telemetry.empty:
            logger.warning(f"No telemetry data for session {session_id}")
            continue

        # Apply consistent track status encoding for this session
        if (
            target_column == "TrackStatus"
            and "TrackStatus" in session_telemetry.columns
            and label_encoder
        ):
            encoded_labels = label_encoder.transform(session_telemetry["TrackStatus"])
            session_telemetry["TrackStatusEncoded"] = encoded_labels
        elif target_column not in session_telemetry.columns:
            logger.warning(
                f"Target column '{target_column}' not found in session {session_id}"
            )
            continue

        # Generate sequences only within this session's temporal boundaries
        # This is the critical step that prevents cross-session contamination
        X_session, y_session, metadata_session = ts_generator.generate_sequences(
            session_telemetry
        )

        # Collect results from this session
        if len(X_session) > 0:
            all_sequences.append(X_session)
            all_labels.extend(y_session)
            all_metadata.extend(metadata_session)
            logger.info(
                f"Generated {len(X_session)} sequences for session {session_id}"
            )
        else:
            logger.warning(f"No sequences generated for session {session_id}")

    # Combine sequences from all sessions into final dataset
    if all_sequences:
        X = np.concatenate(all_sequences, axis=0)
        y = np.array(all_labels)
        metadata = all_metadata
        logger.info(
            f"Combined {len(X)} total sequences from {len(all_sequences)} sessions"
        )
    else:
        raise ValueError("No sequences generated from any session")

    if len(X) == 0:
        raise ValueError("No sequences generated")

    logger.info(f"Generated {len(X)} sequences with shape {X.shape}")

    # Step 5: Validate temporal integrity
    validate_temporal_integrity(metadata)

    # Step 6: Apply feature engineering (missing values + normalization)
    engineer = FeatureEngineer()

    # Handle missing values (only if they exist)
    X_clean = engineer.handle_missing_values(X, strategy="forward_fill")

    # Normalize sequences
    X_normalized = engineer.normalize_sequences(X_clean, method=normalization_method)

    # Encode prediction labels if using track status
    if label_encoder:
        y_encoded = label_encoder.transform(pd.Series(y))
    else:
        # For non-track status targets, create a simple label encoder
        simple_encoder = LabelEncoder()
        y_encoded = simple_encoder.fit_transform(y)
        label_encoder = simple_encoder

    # Calculate class distribution
    unique, counts = np.unique(y_encoded, return_counts=True)
    if hasattr(label_encoder, "inverse_transform"):
        try:
            class_labels = label_encoder.inverse_transform(unique)
        except:
            class_labels = unique
    else:
        class_labels = unique

    class_distribution = dict(zip(class_labels, counts))

    return {
        "X": X_normalized,
        "y": y_encoded,
        "y_raw": y,
        "metadata": metadata,
        "label_encoder": label_encoder,
        "feature_engineer": engineer,
        "raw_telemetry": None,  # Per-session data not aggregated
        "class_distribution": class_distribution,
        "config": {
            "window_size": window_size,
            "prediction_horizon": prediction_horizon,
            "handle_non_numeric": handle_non_numeric,
            "normalization_method": normalization_method,
            "target_column": target_column,
            "n_sequences": len(X_normalized),
            "n_features": X_normalized.shape[2],
            "feature_names": metadata[0]["features_used"] if metadata else [],
        },
    }


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================


def create_season_configs(
    year: int, session_types: Optional[List[str]] = None
) -> List[SessionConfig]:
    """Create session configs for a full season"""
    if session_types is None:
        session_types = ["R"]
    # This is a basic implementation - you might want to expand this
    # to automatically fetch race names from the F1 calendar
    raise NotImplementedError(
        f"Season config creation for {year} with types {session_types} not implemented in this aggregated version"
    )


# =============================================================================
# USAGE EXAMPLE
# =============================================================================

if __name__ == "__main__":
    print("F1 ETL Pipeline loaded successfully!")
    print("\nExample usage:")
    print("session = SessionConfig(2024, 'Monaco Grand Prix', 'R')")
    print("config = DataConfig(sessions=[session])")
    print("dataset = create_safety_car_dataset(config)")
