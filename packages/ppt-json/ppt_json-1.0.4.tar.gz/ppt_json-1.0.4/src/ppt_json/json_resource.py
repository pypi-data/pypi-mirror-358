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

# pylint: disable=invalid-name,undefined-variable

from copy import copy
from weakref import proxy, ProxyTypes
import json
import re

try:
    from collections.abc import (
        Iterable,
        Mapping,
        MutableMapping,
        MutableSequence,
        Sequence,
    )
except ImportError:
    from collections import Iterable, Mapping, MutableMapping, MutableSequence, Sequence


class JsonResource(object):
    """
    This class provides a bridge between Python and JSON to read JSON on the
    fly.

    :author:     Tobias "NotTheEvilOne" Wolf et al.
    :copyright:  Tobias "NotTheEvilOne" Wolf - All rights reserved
    :package:    ppt
    :since:      v1.0.0
    :license:    http://mozilla.org/MPL/2.0/
                 Mozilla Public License, v. 2.0
    """

    IMPLEMENTATION_INTERNAL = 1
    """
Use internal parser for JSON operations
    """
    IMPLEMENTATION_NATIVE = 2
    """
Use native Python functions for JSON operations
    """

    RE_ESCAPED = re.compile("(\\\\+)$")
    """
RegExp to find escape characters
    """
    RE_NODE_POSITION = re.compile("^(.+)#(\\d+)$")
    """
RegExp to find node names with a specified position in a list
    """

    __slots__ = (
        "__weakref__",
        "_data",
        "data_cache_node",
        "data_cache_ptr",
        "_implementation",
        "_log_handler",
        "struct_type",
    )
    """
python.org: __slots__ reserves space for the declared variables and prevents
the automatic creation of __dict__ and __weakref__ for each instance.
    """

    def __init__(self, struct_type=dict, log_handler=None):
        """
        Constructor __init__(JsonResource)

        :param struct_type: Dict implementation for new struct elements
        :param log_handler: Log handler to use

        :since: v1.0.0
        """

        self._data = None
        """
JSON data
        """
        self.data_cache_node = ""
        """
Path of the cached node pointer
        """
        self.data_cache_ptr = ""
        """
Reference of the cached node pointer (string if unset)
        """
        self._implementation = 0
        """
Implementation identifier
        """
        self._log_handler = None
        """
The log handler is called whenever debug messages should be logged or errors
happened.
        """
        self.struct_type = struct_type
        """
Dict implementation used to create new struct elements
        """

        if log_handler is not None:
            self.log_handler = log_handler

        self.implementation = None

    @property
    def data(self):
        """
        Return the Python representation data of this "JsonResource" instance.

        :return: (mixed) Python representation data; None if not parsed
        :since:  v1.0.0
        """

        return self._data.copy() if hasattr(self._data, "copy") else copy(self._data)

    @data.setter
    def data(self, data_dict):
        """
        Sets the Python representation data of this "JsonResource" instance.

        :param data_dict: Python representation data

        :since: v1.0.0
        """

        self.set_json(data_dict, True)

    @property
    def implementation(self):
        """
        Returns the parser implementation in use.

        :return: (int) Implementation identifier
        :since:  v1.0.0
        """

        return self._implementation

    @implementation.setter
    def implementation(self, implementation):
        """
        Set the parser implementation to use.

        :param implementation: Implementation identifier

        :since: v1.0.0
        """

        if self._log_handler is not None:
            self._log_handler.debug(
                "#echo(__FILEPATH__)# -json.implementation()- (#echo(__LINE__)#)"
            )

        if self.struct_type != dict:
            self._implementation = JsonResource.IMPLEMENTATION_INTERNAL
        elif implementation is None:
            self._implementation = JsonResource.IMPLEMENTATION_NATIVE
        else:
            self._implementation = implementation

    @property
    def json(self):
        """
        Returns the JSON string for the Python representation data of this instance.

        :return: (str) Result string
        :since:  v1.0.0
        """

        return self.export_data()

    @property
    def log_handler(self):
        """
        Returns the log handler.

        :return: (object) Log handler in use
        :since:  v1.0.0
        """

        return self._log_handler

    @log_handler.setter
    def log_handler(self, log_handler):
        """
        Sets the log handler.

        :param log_handler: Log handler to use

        :since: v1.0.0
        """

        self._log_handler = (
            log_handler if isinstance(log_handler, ProxyTypes) else proxy(log_handler)
        )

    def add_node(self, node_path, data):
        """
        Adds a node with content. Recursion is not supported because both arrays
        or objects are possible for numeric path definitions.

        :param node_path: Path to the new node - delimiter is space
        :param data: Data for the new node

        :return: (bool) False on error
        :since:  v1.0.0
        """

        if self._log_handler is not None:
            self._log_handler.debug(
                "#echo(__FILEPATH__)# -json.add_node({0})- (#echo(__LINE__)#)",
                node_path,
            )

        if self._data is None:
            self._data = self.struct_type()

        return self.change_node(node_path, data, True)

    def change_node(self, node_path, data, add_recursively=False):
        """
        Change the content of a specified node.

        :param node_path: Path to the new node - delimiter is space
        :param data: Data for the new node
        :param add_recursively: True to create undefined nodes

        :return: (bool) False on error
        :since:  v1.0.0
        """

        if self._log_handler is not None:
            self._log_handler.debug(
                "#echo(__FILEPATH__)# -json.change_node({0})- (#echo(__LINE__)#)",
                node_path,
            )

        _return = False

        if isinstance(node_path, str):
            """
Get the parent node of the target.
            """

            node_path_list = node_path.split(" ")

            node_path_count = len(node_path_list)
            node_name = node_path if (node_path_count < 2) else None

            if node_path_count > 1 or JsonResource.RE_NODE_POSITION.match(node_path):
                if node_path_count > 1:
                    node_name = node_path_list.pop()
                    node_path = " ".join(node_path_list)

                    node_ptr = self._get_node_ptr(node_path)
                else:
                    node_path = ""

                    node_ptr = self._get_node_ptr(
                        JsonResource.RE_NODE_POSITION.match(node_name).group(1)
                    )
            else:
                node_path = ""
                node_ptr = self._data

            """
Change the node
            """

            re_result = JsonResource.RE_NODE_POSITION.match(node_name)

            if re_result is None:
                node_position = -1
            else:
                node_name = re_result.group(1)
                node_position = int(re_result.group(2))

            if isinstance(node_ptr, MutableMapping) and (
                node_name in node_ptr or add_recursively
            ):
                node_ptr[node_name] = data
                _return = True

                if self.data_cache_node != "":
                    node_path_changed = (
                        "{0} {1}".format(node_path, node_name)
                        if len(node_path) > 0
                        else node_name
                    )

                    if self.data_cache_node == node_path_changed:
                        self.data_cache_ptr = node_ptr[node_name]
            elif isinstance(node_ptr, MutableSequence) and 0 <= node_position < len(
                node_ptr
            ):
                node_ptr[node_position] = data
                _return = True

                if self.data_cache_node != "":
                    node_path_changed = (
                        "{0} {1}".format(node_path, node_name)
                        if len(node_path) > 0
                        else node_name
                    )

                    node_path_changed += "#{0:d}".format(node_position)

                    if self.data_cache_node == node_path_changed:
                        self.data_cache_ptr = node_ptr[node_position]

        return _return

    def count_node(self, node_path):
        """
        Count the occurrence of a specified node.

        :param node_path: Path to the node - delimiter is space

        :return: (int) Counted number off matching nodes
        :since:  v1.0.0
        """

        if self._log_handler is not None:
            self._log_handler.debug(
                "#echo(__FILEPATH__)# -json.count_node({0})- (#echo(__LINE__)#)",
                node_path,
            )

        _return = 0

        if isinstance(node_path, str):
            """
Get the parent node of the target.
            """

            node_ptr = self._get_node_ptr(node_path) if " " in node_path else self._data

            if node_ptr is not None:
                _return = (
                    len(node_ptr) if isinstance(node_ptr, (Mapping, Sequence)) else 1
                )

        return _return

    def data_to_json(self, data):
        """
        Builds recursively a valid JSON ouput reflecting the given data.

        :param data: Python data

        :return: (str) JSON output string
        :since:  v1.0.0
        """

        if self._log_handler is not None:
            self._log_handler.debug(
                "#echo(__FILEPATH__)# -json.data_to_json()- (#echo(__LINE__)#)"
            )

        _return = ""

        if self.implementation == JsonResource.IMPLEMENTATION_NATIVE:
            _return = json.dumps(
                data, default=self._get_native_serializable_data, skipkeys=True
            )
        else:
            if isinstance(data, bool):
                _return = "true" if (data) else "false"
            elif isinstance(data, Mapping):
                _return = ""

                if len(data) > 0:
                    for key in data:
                        if _return != "":
                            _return += ","

                        _return += "{0}:{1}".format(
                            self.data_to_json(str(key)), self.data_to_json(data[key])
                        )

                _return = "{{{0}}}".format(_return)
            elif isinstance(data, Iterable):
                _return = ""

                for value in data:
                    if _return != "":
                        _return += ","
                    _return += self.data_to_json(value)

                _return = "[{0}]".format(_return)
            elif isinstance(data, (float, int)):
                _return = str(data)
            elif isinstance(data, str):
                data = data.replace("\\", "\\\\")
                data = data.replace('"', '\\"')
                data = data.replace("\x08", "\\b")
                data = data.replace("\f", "\\f")
                data = data.replace("\n", "\\n")
                data = data.replace("\r", "\\r")
                data = data.replace("\t", "\\t")
                _return = '"{0}"'.format(data)
            else:
                _return = "null"

        return _return

    def export_data(self, flush=False):
        """
        Convert the Python representation data into a JSON string.

        :param flush: True to delete the instance content

        :return: (str) Result string
        :since:  v1.0.0
        """

        if self._log_handler is not None:
            self._log_handler.debug(
                "#echo(__FILEPATH__)# -json.export_data()- (#echo(__LINE__)#)"
            )

        if self._data is None:
            _return = ""
        else:
            _return = self.data_to_json(self._data)

            if flush:
                self._data = None

        return _return

    def _get_native_serializable_data(self, o):
        """
        python.org: default(obj) is a function that should return a serializable
        version of obj or raise TypeError.

        :param o: Object to encode

        :return: (mixed) Serializable object
        :since:  v1.0.0
        """

        if isinstance(o, Mapping):
            _return = dict(o)
        elif isinstance(o, Iterable):
            _return = list(o)
        else:
            _return = None

        return _return

    def get_node(self, node_path):
        """
        Read a specified node including all children if applicable.

        :param node_path: Path to the node - delimiter is space

        :return: (mixed) JSON data; None on error
        :since:  v1.0.0
        """

        if self._log_handler is not None:
            self._log_handler.debug(
                "#echo(__FILEPATH__)# -json.get_node({0})- (#echo(__LINE__)#)",
                node_path,
            )

        _return = None

        if isinstance(node_path, str):
            node_ptr = self._get_node_ptr(node_path)

            if node_ptr is not None:
                _return = node_ptr.copy() if (isinstance(node_ptr, dict)) else node_ptr

        return _return

    def _get_node_ptr(self, node_path):
        """
        Returns the pointer to a specific node.

        :param node_path: Path to the node - delimiter is space

        :return: (dict) JSON tree element; None on error
        :since:  v1.0.0
        """

        if self._log_handler is not None:
            self._log_handler.debug(
                "#echo(__FILEPATH__)# -json._get_node_ptr({0})- (#echo(__LINE__)#)",
                node_path,
            )

        _return = None

        if isinstance(node_path, str):
            if (
                self.data_cache_node != ""
                and node_path[: len(self.data_cache_node)].lower()
                == self.data_cache_node.lower()
            ):
                node_path = node_path[len(self.data_cache_node) :].strip()
                node_ptr = self.data_cache_ptr
            else:
                node_ptr = self._data

            is_valid = True
            node_path_list = node_path.split(" ") if (len(node_path) > 0) else []

            while is_valid and len(node_path_list) > 0:
                is_valid = False
                node_name = node_path_list.pop(0)

                re_result = JsonResource.RE_NODE_POSITION.match(node_name)

                if re_result is None:
                    node_position = -1
                else:
                    node_name = re_result.group(1)
                    node_position = int(re_result.group(2))

                if isinstance(node_ptr, Mapping):
                    if node_name in node_ptr:
                        is_valid = True
                        node_ptr = node_ptr[node_name]

                if (
                    node_position >= 0
                    and isinstance(node_ptr, Sequence)
                    and node_position < len(node_ptr)
                ):
                    is_valid = True
                    node_ptr = node_ptr[node_position]

            if is_valid:
                _return = node_ptr

        return _return

    def _json_to_data_walker(self, data, end_tag=""):
        """
        Converts JSON data recursively into the corresponding PHP data ...

        :param data: Input JSON data
        :param end_tag: Ending delimiter

        :return: (mixed) JSON data; None on error
        :since:  v1.0.0
        """

        if self._log_handler is not None:
            self._log_handler.debug(
                "#echo(__FILEPATH__)# -json._json_to_data_walker()- (#echo(__LINE__)#)"
            )

        _return = None

        data = data.strip()

        if end_tag == "]":
            _return = []

            while len(data) > 0:
                if data[0] == "{":
                    data_part = JsonResource._find_string(data, "}", "{")
                elif data[0] == "[":
                    data_part = JsonResource._find_string(data, "]", "[")
                else:
                    data_part = JsonResource._find_string(data, ",")

                if data_part is None:
                    data_part = JsonResource._find_string(data, "]")

                if data_part is not None:
                    data = data[len(data_part) + 1 :].strip()

                    if len(data_part) > 0:
                        if data_part[0] == "{":
                            _return.append(
                                self._json_to_data_walker(data_part[1:], "}")
                            )
                        elif data_part[0] == "[":
                            _return.append(
                                self._json_to_data_walker(data_part[1:], "]")
                            )
                        else:
                            _return.append(self._json_to_data_walker(data_part))
                else:
                    if len(data) > 0 and data != "]":
                        _return = None
                    break
        elif end_tag == "}":
            _return = self.struct_type()

            while len(data) > 0:
                if data == "}":
                    break
                else:
                    if data[0] == ",":
                        data = data[1:].strip()

                    if data[0] == '"':
                        key_string_tag = '"'
                    elif data[0] == "'":
                        key_string_tag = "'"
                    else:
                        key_string_tag = None

                    key = None

                    if key_string_tag is not None:
                        key = JsonResource._find_string(data[1:], key_string_tag)

                        if key is not None:
                            data = data[len(key) + 2 :].strip()

                    if (
                        key is not None
                        and len(key) > 0
                        and len(data) > 1
                        and data[0] == ":"
                    ):
                        data = data[1:].strip()

                        if data[0] == "{":
                            data_part = JsonResource._find_string(data, "}", "{")
                        elif data[0] == "[":
                            data_part = JsonResource._find_string(data, "]", "[")
                        else:
                            data_part = JsonResource._find_string(data, ",")

                        if data_part is None:
                            data_part = JsonResource._find_string(data, "}")

                        if data_part is not None:
                            data = data[len(data_part) :].strip()

                            if len(data_part) > 0:
                                if data_part[0] == "{":
                                    _return[key] = self._json_to_data_walker(
                                        data_part[1:], "}"
                                    )
                                elif data_part[0] == "[":
                                    _return[key] = self._json_to_data_walker(
                                        data_part[1:], "]"
                                    )
                                else:
                                    _return[key] = self._json_to_data_walker(data_part)
                        elif len(data) > 0 and data != "}":
                            data = None
                        else:
                            data = ""
                    else:
                        _return = None
                        break
        elif data == "true":
            _return = True
        elif data == "false":
            _return = False
        elif len(data) > 0 and data != "null":
            if data[0] == '"':
                value_string_tag = '"'
            elif data[0] == "'":
                value_string_tag = "'"
            else:
                value_string_tag = None

            if value_string_tag is None:
                try:
                    _return = int(data)
                except ValueError:
                    pass

                if _return is None:
                    try:
                        _return = float(data)
                    except ValueError:
                        pass
            else:
                _return = JsonResource._find_string(data[1:], value_string_tag)

                if _return is not None:
                    _return = _return.replace('"', '"')
                    _return = _return.replace("\\\\", "\\")
                    _return = _return.replace("\\b", "\x08")
                    _return = _return.replace("\\f", "\f")
                    _return = _return.replace("\\n", "\n")
                    _return = _return.replace("\\r", "\r")
                    _return = _return.replace("\\t", "\t")

        return _return

    def parse(self, data):
        """
        Parses the given JSON data.

        :param data: Input JSON data

        :since: v1.0.0
        """

        if self._log_handler is not None:
            self._log_handler.debug(
                "#echo(__FILEPATH__)# -json.parse()- (#echo(__LINE__)#)"
            )

        data = data.strip()

        if self.implementation == JsonResource.IMPLEMENTATION_NATIVE:
            native_error_class = getattr(json, "JSONDecodeError", ValueError)

            try:
                self._data = json.loads(data)
            except native_error_class:
                self._data = None
        elif data[0] == "{":
            self._data = self._json_to_data_walker(data[1:], "}")
        elif data[0] == "[":
            self._data = self._json_to_data_walker(data[1:], "]")
        else:
            self._data = None

    def remove_node(self, node_path):
        """
        Remove a node and all children if applicable.

        :param node_path: Path to the node - delimiter is space

        :return: (bool) False on error
        :since:  v1.0.0
        """

        if self._log_handler is not None:
            self._log_handler.debug(
                "#echo(__FILEPATH__)# -json.remove_node({0})- (#echo(__LINE__)#)",
                node_path,
            )

        _return = False

        if isinstance(node_path, str):
            """
Get the parent node of the target.
            """

            node_path_list = node_path.split(" ")

            node_path_count = len(node_path_list)
            node_name = node_path if (node_path_count < 2) else None

            if node_path_count > 1 or JsonResource.RE_NODE_POSITION.match(node_path):
                if node_path_count > 1:
                    node_name = node_path_list.pop()
                    node_ptr = self._get_node_ptr(" ".join(node_path_list))
                else:
                    node_ptr = self._get_node_ptr(
                        JsonResource.RE_NODE_POSITION.match(node_name).group(1)
                    )

                if (
                    self.data_cache_node != ""
                    and node_path[: len(self.data_cache_node)] == self.data_cache_node
                ):
                    self.data_cache_node = ""
                    self.data_cache_ptr = self._data
            else:
                node_ptr = self._data

                self.data_cache_node = ""
                self.data_cache_ptr = self._data

            """
Delete the node
            """

            re_result = JsonResource.RE_NODE_POSITION.match(node_name)

            if re_result is None:
                node_position = -1
            else:
                node_name = re_result.group(1)
                node_position = int(re_result.group(2))

            if isinstance(node_ptr, MutableMapping) and node_name in node_ptr:
                del node_ptr[node_name]
                _return = True
            elif (
                isinstance(node_ptr, MutableSequence)
                and node_position >= 0
                and node_position < len(node_ptr)
            ):
                del node_ptr[node_position]
                _return = True

        return _return

    def set_json(self, data_dict, overwrite=False):
        """
        "Imports" Python representation data for this "JsonResource" instance.

        :param data_dict: Python representation data
        :param overwrite: True to overwrite the current (non-empty) cache

        :return: (bool) True on success
        :since:  v1.0.0
        """

        if self._log_handler is not None:
            self._log_handler.debug(
                "#echo(__FILEPATH__)# -json.set_json()- (#echo(__LINE__)#)"
            )

        _return = False

        if (self._data is None or overwrite) and (
            isinstance(data_dict, (Mapping, Sequence))
        ):
            self._data = data_dict
            _return = True

        return _return

    def set_cached_node(self, node_path):
        """
        Set the cache pointer to a specific node.

        :param node_path: Path to the node - delimiter is space

        :return: (bool) True on success
        :since:  v1.0.0
        """

        if self._log_handler is not None:
            self._log_handler.debug(
                "#echo(__FILEPATH__)# -json.set_cached_node({0})- (#echo(__LINE__)#)",
                node_path,
            )

        _return = False

        if isinstance(node_path, str):
            if node_path == self.data_cache_node:
                _return = True
            else:
                node_ptr = self._get_node_ptr(node_path)

                if node_ptr is not None:
                    self.data_cache_node = node_path
                    self.data_cache_ptr = node_ptr
                    _return = True

        return _return

    @staticmethod
    def _find_string(data, end_tag, zone_tag=None):
        """
        Searches the given data for a matching end tag. Sub zone end tags are
        ignored.

        :param data: Input data
        :param end_tag: Ending delimiter
        :param zone_tag: Zone start tag for sub zones

        :return: (str) Matched data; None if not found
        :since:  v1.0.0
        """

        _return = None

        zone_count = 0

        if zone_tag is None:
            cache = ""
        else:
            cache = data[0]
            data = data[1:]

        data_list = data.split(end_tag)

        if zone_tag is not None:
            re_zone_tag = re.compile("([\\\\]*){0}".format(re.escape(zone_tag)))

        while _return is None and len(data_list) > 0:
            data = data_list.pop(0)

            if zone_tag is not None:
                for result in re_zone_tag.finditer(data):
                    if len(result.group(1)) % 2 == 0:
                        zone_count += 1

            re_result = JsonResource.RE_ESCAPED.search(data)

            if re_result is not None and (len(re_result.group(1)) % 2) == 1:
                cache += data
            elif len(data_list) > 0:
                if zone_count:
                    cache += data
                    zone_count -= 1
                else:
                    _return = cache + data
            else:
                cache += data

            if len(data_list) > 0:
                if _return is not None and zone_tag is not None:
                    _return += end_tag
                else:
                    cache += end_tag

        return _return

    @staticmethod
    def json_to_data(data):
        """
        Converts JSON data into a Python representation.

        :param data: Input JSON data

        :return: (mixed) JSON data; None on error
        :since:  v1.0.0
        """

        # pylint: disable=broad-except

        json_resource = JsonResource()
        json_resource.parse(data)

        return json_resource.data
