#!/usr/bin/env python3
# breakout-garden-exporter
# Copyright (C) 2025 Andrew Wilkinson
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from typing import Optional

from scd4x import SCD4X

from .metrics import Metrics, GAUGE, COUNTER
from .sensor import Sensor


class SCD4xSensor(Sensor):
    def __init__(self) -> None:
        self.sensor: Optional[SCD4X] = None
        self.initial_readings: int = 0

    def initialise(self, metrics: Metrics) -> bool:
        try:
            self.sensor = SCD4X()
        except OSError:
            return False
        else:
            try:
                self.sensor.self_test()
            except RuntimeError as e:
                print(f"SCD4X self-test failed. {e}")
                return False

            metrics.add_metric("bge_co2",
                               GAUGE,
                               "The co2 (ppm)")
            metrics.add_metric("bge_temperature", GAUGE, "The temperature")
            metrics.add_metric("bge_humidity", GAUGE, "The humidity")
            metrics.add_metric("bge_sensor_update",
                               COUNTER,
                               "The time of the last sensor update",)

            self.sensor.start_periodic_measurement()

            return True

    def measure(self, metrics: Metrics) -> float:
        assert self.sensor is not None, \
            "initialise must be called before measure."

        try:
            data = self.sensor.measure(blocking=False)
        except RuntimeError as e:
            print("Error reading SCD4X sensor:", e)
            return 1.0

        if data is None:
            # data not ready
            return 1.0

        co2, temperature, relative_humidity, timestamp = data

        metrics.set("bge_co2", "sensor=\"scd4x\"", co2)
        metrics.set("bge_temperature", "sensor=\"scd4x\"", temperature)
        metrics.set("bge_humidity", "sensor=\"scd4x\"", relative_humidity)
        metrics.set("bge_sensor_update", "sensor=\"scd4x\"", timestamp)

        return 1.0
