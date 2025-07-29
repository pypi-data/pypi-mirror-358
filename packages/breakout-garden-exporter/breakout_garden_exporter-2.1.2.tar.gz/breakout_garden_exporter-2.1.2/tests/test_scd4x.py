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

from typing import cast, Optional
import unittest
from unittest.mock import patch, Mock

from breakoutgardenexporter import SCD4xSensor, Metrics


class TestSCD4x(unittest.TestCase):
    @patch("breakoutgardenexporter.scd4x.SCD4X")
    def test_create_sensor(self, mock_scd4x):
        instance = Mock()
        mock_scd4x.return_value = instance
        instance.self_test.side_effect = [None]
        instance.measure.return_value = (400, 25.0, 50.0, 1234567890)

        metrics = Metrics()
        sensor = SCD4xSensor()

        self.assertTrue(sensor.initialise(metrics))

        self.assertEqual(sensor.measure(metrics), 1.0)
        self.assertIn(
            "bge_co2{sensor=\"scd4x\"} 400.000000", str(metrics))
        self.assertIn(
            "bge_sensor_update{sensor=\"scd4x\"} 1234567890.000000",
            str(metrics))

    @patch("breakoutgardenexporter.scd4x.SCD4X")
    def test_missing_sensor(self, mock_scd4x):
        mock_scd4x.side_effect = OSError

        metrics = Metrics()
        sensor = SCD4xSensor()

        self.assertFalse(sensor.initialise(metrics))

    @patch("breakoutgardenexporter.scd4x.SCD4X")
    def test_self_test_fail(self, mock_scd4x):
        instance = Mock()
        mock_scd4x.return_value = instance
        instance.self_test.side_effect = RuntimeError("Self-test failed")

        metrics = Metrics()
        sensor = SCD4xSensor()

        self.assertFalse(sensor.initialise(metrics))

    @patch("breakoutgardenexporter.scd4x.SCD4X")
    def test_error_measuring(self, mock_scd4x):
        instance = Mock()
        mock_scd4x.return_value = instance
        instance.self_test.side_effect = [True]
        instance.measure.side_effect = RuntimeError("Measurement error")

        metrics = Metrics()
        sensor = SCD4xSensor()

        self.assertTrue(sensor.initialise(metrics))

        self.assertEqual(sensor.measure(metrics), 1.0)
