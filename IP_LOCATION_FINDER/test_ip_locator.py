#!/usr/bin/env python3

# ########################################################################## #
#                                                                            #
#                                                        :::      ::::::::   #
#   test_ip_locator.py                                 :+:      :+:    :+:   #
#                                                    +:+ +:+         +:+     #
#   By: nfitahin <nfitahin@student.42antananarivo  +#+  +:+       +#+        #
#                                                +#+#+#+#+#+   +#+           #
#   Created: 2026/09/21 12:49:29 by nfitahin          #+#    #+#             #
#   Updated: 2026/09/21 12:49:29 by nfitahin         ###   ########.fr       #
#                                                                            #
# ########################################################################## #

import unittest
from unittest.mock import MagicMock, patch

import requests

import ip_locator
from ip_locator import IPLocatorError

SAMPLE = {
    "status": "success",
    "query": "8.8.8.8",
    "country": "United States",
    "regionName": "California",
    "city": "Mountain View",
    "zip": "94043",
    "lat": 37.4056,
    "lon": -122.0775,
    "isp": "Google LLC",
}


def fake_response(status_code=200, payload=None):
    resp = MagicMock()
    resp.status_code = status_code
    resp.json.return_value = payload if payload is not None else SAMPLE
    return resp


class ValidateIPTests(unittest.TestCase):
    def test_valid_public_ipv4(self):
        self.assertEqual(ip_locator.validate_ip("8.8.8.8"), "8.8.8.8")

    def test_valid_public_ipv6(self):
        self.assertEqual(ip_locator.validate_ip("2001:4860:4860::8888"), "2001:4860:4860::8888")

    def test_invalid_ip(self):
        with self.assertRaises(IPLocatorError):
            ip_locator.validate_ip("999.1.1.1")

    def test_private_ip_rejected(self):
        for value in ("192.168.1.1", "10.0.0.5", "127.0.0.1"):
            with self.assertRaises(IPLocatorError):
                ip_locator.validate_ip(value)


class GetLocationTests(unittest.TestCase):
    @patch("ip_locator.requests.get")
    def test_success(self, mock_get):
        mock_get.return_value = fake_response()
        self.assertEqual(ip_locator.get_location("8.8.8.8")["city"], "Mountain View")

    @patch("ip_locator.requests.get")
    def test_api_failure_status(self, mock_get):
        mock_get.return_value = fake_response(payload={"status": "fail", "message": "reserved range"})
        with self.assertRaises(IPLocatorError):
            ip_locator.get_location("8.8.8.8")

    @patch("ip_locator.requests.get")
    def test_rate_limited(self, mock_get):
        mock_get.return_value = fake_response(status_code=429)
        with self.assertRaises(IPLocatorError):
            ip_locator.get_location("8.8.8.8")

    @patch("ip_locator.requests.get", side_effect=requests.exceptions.Timeout)
    def test_timeout(self, _):
        with self.assertRaises(IPLocatorError):
            ip_locator.get_location("8.8.8.8")

    @patch("ip_locator.requests.get", side_effect=requests.exceptions.ConnectionError)
    def test_connection_error(self, _):
        with self.assertRaises(IPLocatorError):
            ip_locator.get_location("8.8.8.8")


class FormatAndCLITests(unittest.TestCase):
    def test_format_contains_fields(self):
        text = ip_locator.format_location(SAMPLE)
        self.assertIn("Mountain View", text)
        self.assertIn("Google LLC", text)

    def test_format_missing_value(self):
        self.assertIn("N/A", ip_locator.format_location({"query": "1.1.1.1"}))

    @patch("ip_locator.requests.get")
    def test_main_success(self, mock_get):
        mock_get.return_value = fake_response()
        self.assertEqual(ip_locator.main(["8.8.8.8"]), ip_locator.EXIT_OK)

    def test_main_invalid_ip_returns_error(self):
        self.assertEqual(ip_locator.main(["not-an-ip"]), ip_locator.EXIT_ERROR)


if __name__ == "__main__":
    unittest.main()
