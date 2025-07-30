# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Module for defining client to interact with API."""

from __future__ import annotations

import abc
import dataclasses
from collections.abc import Sequence

import requests
from typing_extensions import override

from garf_core import exceptions


@dataclasses.dataclass
class GarfApiRequest:
  """Base class for specifying request."""


@dataclasses.dataclass
class GarfApiResponse:
  """Base class for specifying response."""

  results: list


class GarfApiError(exceptions.GarfError):
  """API specific exception."""


class BaseClient(abc.ABC):
  """Base API client class."""

  @abc.abstractmethod
  def get_response(
    self, request: GarfApiRequest = GarfApiRequest(), **kwargs: str
  ) -> GarfApiResponse:
    """Method for getting response."""


class RestApiClient(BaseClient):
  """Specifies REST client."""

  OK = 200

  def __init__(self, endpoint: str, **kwargs: str) -> None:
    """Initializes RestApiClient."""
    self.endpoint = endpoint
    self.query_args = kwargs

  @override
  def get_response(
    self, request: GarfApiRequest = GarfApiRequest(), **kwargs: str
  ) -> GarfApiResponse:
    response = requests.get(f'{self.endpoint}/{request.resource_name}')
    if response.status_code == self.OK:
      return GarfApiResponse(response.json())
    raise GarfApiError('Failed to get data from API')


class FakeApiClient(BaseClient):
  """Fake class for specifying API client."""

  def __init__(self, results: Sequence) -> None:
    """Initializes FakeApiClient."""
    self.results = list(results)

  @override
  def get_response(
    self, request: GarfApiRequest = GarfApiRequest()
  ) -> GarfApiResponse:
    del request
    return GarfApiResponse(results=self.results)
