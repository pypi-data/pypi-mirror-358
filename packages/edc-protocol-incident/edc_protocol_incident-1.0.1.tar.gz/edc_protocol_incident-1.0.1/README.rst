|pypi| |actions| |codecov| |downloads|

edc-protocol-incident
---------------------

Class to handle clinical trial protocol incidents (deviations and violations).

There are two types of this PRN form:


Protocol deviation / violation (default)
========================================
The default version requires additional details if the incident is a `violation`.


Protocol incident
=================
To use this version set:

.. code-block:: python

    settings.EDC_PROTOCOL_VIOLATION_TYPE = "incident"

Requires additional details for both types: `violation` and `deviation`.


.. |pypi| image:: https://img.shields.io/pypi/v/edc-protocol-incident.svg
    :target: https://pypi.python.org/pypi/edc-protocol-incident

.. |actions| image:: https://github.com/clinicedc/edc-protocol-incident/actions/workflows/build.yml/badge.svg
  :target: https://github.com/clinicedc/edc-protocol-incident/actions/workflows/build.yml

.. |codecov| image:: https://codecov.io/gh/clinicedc/edc-protocol-incident/branch/develop/graph/badge.svg
  :target: https://codecov.io/gh/clinicedc/edc-protocol-incident

.. |downloads| image:: https://pepy.tech/badge/edc-protocol-incident
   :target: https://pepy.tech/project/edc-protocol-incident
