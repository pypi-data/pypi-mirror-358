# -*- coding: utf-8 -*-

"""
Personal Python Toolkit
Modularized all-in-one toolkit for Python
----------------------------------------------------------------------------
(C) Tobias "NotTheEvilOne" Wolf - All rights reserved
https://github.com/NotTheEvilOne/ppt_json

This Source Code Form is subject to the terms of the Mozilla Public License,
v. 2.0. If a copy of the MPL was not distributed with this file, You can
obtain one at http://mozilla.org/MPL/2.0/.
"""

import unittest

from ppt_json import JsonResource


class TestJsonResource(unittest.TestCase):
    """
    Unittest for JsonResource

    :since: v1.0.0
    """

    def _get_json_test_data(self):
        """
        Test data with a simple string and a nested list of content.

        :return: (str) Test data
        """

        return """
{
"hello": "world",
"more_complex": [ "this", "that", true, 1 ]
}
        """

    def test_internal(self):
        """
        Tests the internal JSON parser implementation.
        """

        json_resource = JsonResource()
        json_resource.implementation = JsonResource.IMPLEMENTATION_INTERNAL
        json_resource.parse(self._get_json_test_data())

        json_data = json_resource.data

        self.assertTrue(json_data is not None)

        self.assertTrue("hello" in json_data)
        self.assertEqual("world", json_data["hello"])

        self.assertTrue("more_complex" in json_data)
        self.assertEqual(["this", "that", True, 1], json_data["more_complex"])

    def test_native(self):
        """
        Tests the native JSON Python parser.
        """

        json_data = JsonResource.json_to_data(self._get_json_test_data())

        self.assertTrue(json_data is not None)

        self.assertTrue("hello" in json_data)
        self.assertEqual("world", json_data["hello"])

        self.assertTrue("more_complex" in json_data)
        self.assertEqual(["this", "that", True, 1], json_data["more_complex"])

    def test_position_change(self):
        """
        Tests a change to a positional entry.
        """

        json_resource = JsonResource()
        json_resource.parse(self._get_json_test_data())

        self.assertEqual("world", json_resource.get_node("hello"))
        self.assertEqual("that", json_resource.get_node("more_complex#1"))

        self.assertTrue(json_resource.change_node("more_complex#1", "test"))
        self.assertEqual("test", json_resource.get_node("more_complex#1"))

        json_resource.set_cached_node("more_complex#1")

        self.assertTrue(
            json_resource.change_node(
                "more_complex#1", {"some": "unittests", "never": "work"}
            )
        )
        self.assertEqual("work", json_resource.get_node("more_complex#1 never"))

        json_resource.set_cached_node("more_complex#1 never")

        self.assertTrue(
            json_resource.change_node(
                "more_complex#1 never", "work but sometimes they do"
            )
        )
        self.assertEqual(
            "work but sometimes they do", json_resource.get_node("more_complex#1 never")
        )


if __name__ == "__main__":
    unittest.main()
