# OSDU Python SDK


## Contents

- [OSDU Python SDK](#osdu-python-sdk)
  - [Contents](#contents)
- [Introduction](#introduction)
- [Getting Started](#getting-started)
  - [Installation from source](#installation-from-source)
  - [Installation from Package Registry](#installation-from-package-registry)
  - [Impersonation](#impersonation)
  - [Testing](#testing)
    - [Running E2E Tests](#running-e2e-tests)
    - [Running CSP tests](#running-csp-tests)
  - [Release Notes](#release-notes)
    - [0.28](#028)
    - [0.17](#017)
  - [Licence](#licence)


# Introduction
The Python SDK is a package to interface with OSDU microservices.

Interactions with OSDU services are cloud platform-agnostic by design. However, there are specific implementation requirements by cloud
platforms, and the OSDU R3 Prototype provides a dedicated Python SDK to make sure that interactions are independent from the
cloud platforms.

The Python SDK must be installed on the machine that uses OSDU services.

In OSDU R3 Prototype, the SDK encapsulates calls to the ODES Storage and Search services.


Also, in `osdu_api.providers` folder the SDK provides common interfaces for writing cloud-specific implementations for authorization and accessing
cloud storages. In this `osdu_api.providers` folder CSP code is stored.

# Getting Started

## Installation from source


1. Pull the latest Python SDK's changes from https://community.opengroup.org/osdu/platform/system/sdks/common-python-sdk

2. Use Python 3.13. Also, it is highly recommended using an isolated virtual environment for development purposes
  (Creation of virtual environments: https://docs.python.org/3.11/library/venv.html)

3.  Make sure you have setuptools and wheel installed
```sh
pip install --upgrade setuptools wheel
```

4.  Change directory to the root of PythonSDK project

```sh
cd path/to/python-sdk
```

5. Make sure osdu-api isn't already installed
```sh
pip uninstall osdu-api
````

6. Install Python SDK

```sh
pip install '.[common]'
```

Example import after installing:
`from osdu_api.clients.storage.record_client import RecordClient`


## Installation from Package Registry

```sh
pip install 'osdu-api' --extra-index-url=https://community.opengroup.org/api/v4/projects/148/packages/pypi/simple
```

## Impersonation

If client objects are initialized with `client_id` argument then either `x-on-behalf-of` or `on-behalf-of` headers are set. The former header is used by default. The latter is used when the `ENTITLEMENTS_IMPERSONATION` environment variable is "True" or "true"


## Testing
### Running E2E Tests
Specify of end-services URLs into `tests/osdu_api.yaml` and run

```sh
pip install '.[dev, common]'
pytest
```

### Running CSP tests

```shell
export CLOUD_PROVIDER=<cloud_provider>
pip install '.[dev, common]'
pytest
```

For Google Cloud, you can select the type of token to use: ID token or Access token.

You can configure this via the `GC_ID_TOKEN` environment variable. Here's how to set it:

- for enabling ID token: 'y', 'yes', 'on', 'true' (case-insensitive)
- for using Access token: any other value, or don't set the variable at all

## Release Notes

### 0.29

Updated project structure and added support for Python 3.13. Dual publishing to PyPi and OpenGroup package registry.

### 0.28

From this release verification of SSL certificates is enabled by default. If your environment is using self-signed certificates or a private CA this can be disabled by setting the environment variable
`OSDU_API_DISABLE_SSL_VERIFICAITON` to **iknowthemaninthemiddle**.

### 0.17

Starting from this release each particular client class has 2 more optional parameters: `provider` and the corresponding client service URL. This was done in order to make using `osdu_api.ini` file optional. If you are not using **named arguments** in initializing your clients it can break your code since the order of parameters was changed.


## Licence
Copyright © Amazon Web Services
Copyright © Google LLC
Copyright © EPAM Systems

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

[http://www.apache.org/licenses/LICENSE-2.0](http://www.apache.org/licenses/LICENSE-2.0)

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
A package to interface with OSDU microservices

