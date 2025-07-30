# README

This repository contains a wrapper around Panorama/PaloAlto API.

## Documentation
Documentation can be found [here](https://divad1196.github.io/pa-api-sdk/pa_api/xmlapi.html)
It is automatically generated using [pdoc](https://pdoc.dev/docs/pdoc.html#deploying-to-github-pages)

## Why the need for this library ?

For simple resource retrieval, the existing API is enough, but the libraries available are not practical for it.
Especially, we don't have much information on the data' schema.

The [official python SDK of PaloAltoNetworks](https://github.com/PaloAltoNetworks/pan-os-python) itself relies on a [third party wrapper](https://github.com/kevinsteves/pan-python) for their API.


This library provides clients (JSON/XML APIs) with a more popular approach when wrapping the API, making it easier to use for developers. It also provides types' wrappers using [pydantic](https://docs.pydantic.dev/latest/) library to simplify their usage or utility functions to re-structure the data we receive. This provides the usual benefits of types like:
* IDE completion: IDE will be able to provide you with completion as you type your code
* Consistancy: a value that might be missing will always be defined either as `None` or as an empty list
* Correctness: using `mypy`, you will be able to catch errors before they go to production.

NOTE: The json API is very limited and is, in fact, a mere translation of the xml using the same process as `xmltodict` library.
Also, it is quite slow. For big read operations, it is better to retrieve big portions of the configuration at once and work completely locally.


## Current State of the library

This library was developed over months by adding features when they were needed.
It was tested against 9.x to 11.x paloalto and panorama devices.

There are a few caveats though:
* Not everything is done now
* The main focus is put on the XML API (there is no real reason to use the json API with this library)
* The distinction between paloalto and panorama is not clearly defined everywhere.
  NOTE: we are trying to make the distinction transparent.
* It currently focus on data retrieval more than insertion/update/deletion.
* Methods should be re-arranged and re-grouped to simplify the usage of the library.
* This does not support async/await currently.

Contributions are welcome:
* Completing / Correcting types is more than welcome
* Bug fixes are also very welcome
* We would also like people opinions on how we can improve the library:
  * How should we organize the client classes and methods
  * How the creation/update/deletion should be taken care
  Don't hesitate to open an issue/discussion on this topic.

## TODO

* Improve the documentation
  * Re-organize the methods

* Mix Rest API and XML API ? (at least for create/update/delete ?)
  https://docs.paloaltonetworks.com/pan-os/9-1/pan-os-panorama-api/get-started-with-the-pan-os-rest-api/create-security-policy-rule-rest-api


## Links
