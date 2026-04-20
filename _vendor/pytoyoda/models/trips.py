"""Model for Trip Summaries."""

# ruff: noqa: FA100

from datetime import datetime, timedelta
from typing import Optional, TypeVar, Union

from pydantic import BaseModel, computed_field

from pytoyoda.const import (
    KILOMETERS_UNIT,
    MILES_UNIT,
    ML_TO_GAL_FACTOR,
    ML_TO_L_FACTOR,
)
from pytoyoda.models.endpoints.trips import _TripModel
from pytoyoda.utils.conversions import convert_distance, convert_to_mpg
from pytoyoda.utils.models import CustomAPIBaseModel

T = TypeVar(
    "T",
    bound=Union[_TripModel, bool],
)


class TripPositions(BaseModel):
    """Latitude and longitude."""

    lat: Optional[float]
    lon: Optional[float]


class TripLocations(BaseModel):
    """Trip locations."""

    start: Optional[TripPositions]
    end: Optional[TripPositions]


class Trip(CustomAPIBaseModel[type[T]]):
    """Base class of Daily, Weekly, Monthly, Yearly summary."""

    def __init__(
        self,
        trip: _TripModel,
        metric: bool,  # noqa : FBT001
        **kwargs: dict,
    ) -> None:
        """Initialise Class.

        Args:
            trip (_TripModel, required): Contains all information regarding the trip
            metric (bool, required): Report in Metric or Imperial
            **kwargs: Additional keyword arguments passed to the parent class

        """
        data = {
            "trip": trip,
            "metric": metric,
        }
        super().__init__(data=data, **kwargs)  # type: ignore[reportArgumentType, arg-type]
        self._trip = trip
        self._distance_unit: str = KILOMETERS_UNIT if metric else MILES_UNIT

    @computed_field  # type: ignore[prop-decorator]
    @property
    def locations(self) -> Optional[TripLocations]:
        """Trip locations.

        Returns:
            TripLocations: Latitude and longitude for trip start and end points

        """
        if self._trip.summary:
            return TripLocations(
                start=TripPositions(
                    lat=self._trip.summary.start_lat, lon=self._trip.summary.start_lon
                ),
                end=TripPositions(
                    lat=self._trip.summary.end_lat, lon=self._trip.summary.end_lon
                ),
            )
        return None

    @computed_field  # type: ignore[prop-decorator]
    @property
    def start_time(self) -> Optional[datetime]:
        """Start time.

        Returns:
            datetime: Start time of trip

        """
        return self._trip.summary.start_ts if self._trip.summary else None

    @computed_field  # type: ignore[prop-decorator]
    @property
    def end_time(self) -> Optional[datetime]:
        """End time.

        Returns:
            datetime: End time of trip

        """
        return self._trip.summary.end_ts if self._trip.summary else None

    @computed_field  # type: ignore[prop-decorator]
    @property
    def duration(self) -> Optional[timedelta]:
        """The total time driving.

        Returns:
            timedelta: The amount of time driving

        """
        if self._trip.summary and self._trip.summary.duration:
            return timedelta(seconds=self._trip.summary.duration)
        # Hybrid vehicles return summary=null; sum all HDC drive-mode times instead
        if self._trip.hdc:
            total_s = sum(filter(None, [self._trip.hdc.ev_time, self._trip.hdc.eco_time, self._trip.hdc.power_time, self._trip.hdc.charge_time]))
            if total_s:
                return timedelta(seconds=total_s)
        return None

    @computed_field  # type: ignore[prop-decorator]
    @property
    def distance(self) -> Optional[float]:
        """The total distance covered.

        Returns:
            float: Distance covered in the selected metric

        """
        if self._trip.summary and self._trip.summary.length:
            return convert_distance(
                self._distance_unit, KILOMETERS_UNIT, self._trip.summary.length / 1000.0
            )
        # Hybrid vehicles return summary=null; sum all HDC drive-mode distances instead
        if self._trip.hdc:
            total_m = sum(filter(None, [self._trip.hdc.ev_distance, self._trip.hdc.eco_dist, self._trip.hdc.power_dist, self._trip.hdc.charge_dist]))
            if total_m:
                return convert_distance(self._distance_unit, KILOMETERS_UNIT, total_m / 1000.0)
        return None

    @computed_field  # type: ignore[prop-decorator]
    @property
    def ev_duration(self) -> Optional[timedelta]:
        """The total time driving using EV.

        Returns:
            timedelta: The amount of time driving using EV or None if not supported

        """
        return (
            timedelta(seconds=self._trip.hdc.ev_time)
            if self._trip.hdc and self._trip.hdc.ev_time
            else None
        )

    @computed_field  # type: ignore[prop-decorator]
    @property
    def ev_distance(self) -> Optional[float]:
        """The total time distance driven using EV.

        Returns:
            timedelta: The distance driven using EV in selected metric
                or None if not supported.

        """
        return (
            convert_distance(
                self._distance_unit,
                KILOMETERS_UNIT,
                self._trip.hdc.ev_distance / 1000.0,
            )
            if self._trip.hdc and self._trip.hdc.ev_distance
            else None
        )

    @computed_field  # type: ignore[prop-decorator]
    @property
    def fuel_consumed(self) -> Optional[float]:
        """The total amount of fuel consumed.

        Returns:
            Optional[float]: Fuel consumed in liters (metric) or gallons, None if unavailable

        """
        if self._trip.summary and self._trip.summary.fuel_consumption:
            return (
                round(self._trip.summary.fuel_consumption / ML_TO_L_FACTOR, 3)
                if self._distance_unit == KILOMETERS_UNIT
                else round(self._trip.summary.fuel_consumption / ML_TO_GAL_FACTOR, 3)
            )
        return None

    @computed_field  # type: ignore[prop-decorator]
    @property
    def average_fuel_consumed(self) -> Optional[float]:
        """The average amount of fuel consumed.

        Returns:
            Optional[float]: Average fuel in l/100km (metric) or mpg, None if unavailable

        """
        if (
            self._trip.summary
            and self._trip.summary.fuel_consumption
            and self._trip.summary.length
        ):
            avg_fuel_consumed = (
                self._trip.summary.fuel_consumption / self._trip.summary.length
            ) * 100
            return (
                round(avg_fuel_consumed, 3)
                if self._distance_unit == KILOMETERS_UNIT
                else convert_to_mpg(avg_fuel_consumed)
            )
        return None

    @property
    def score(self) -> Optional[float]:
        """The (hybrid) score for the trip."""
        if self._trip.scores and self._trip.scores.global_:
            return self._trip.scores.global_
        return None

    @property
    def score_acceleration(self) -> Optional[float]:
        """The (hybrid) acceleration score for the trip."""
        if self._trip.scores and self._trip.scores.acceleration:
            return self._trip.scores.acceleration
        return None

    @property
    def score_braking(self) -> Optional[float]:
        """The (hybrid) braking score for the trip."""
        if self._trip.scores and self._trip.scores.braking:
            return self._trip.scores.braking
        return None

    @property
    def score_advice(self) -> Optional[float]:
        """The (hybrid) advice score for the trip."""
        if self._trip.scores and self._trip.scores.advice:
            return self._trip.scores.advice
        return None

    @property
    def score_constant_speed(self) -> Optional[float]:
        """The (hybrid) constant speed score for the trip."""
        if self._trip.scores and self._trip.scores.constant_speed:
            return self._trip.scores.constant_speed
        return None

    @computed_field  # type: ignore[prop-decorator]
    @property
    def route(self) -> Optional[list[TripPositions]]:
        """The route taken.

        Returns:
            Optional[list[Tuple[float, float]]]: List of Lat, Lon of the route taken.
                None if no route provided.

        """
        if self._trip.route:
            return [TripPositions(lat=rm.lat, lon=rm.lon) for rm in self._trip.route]

        return None
