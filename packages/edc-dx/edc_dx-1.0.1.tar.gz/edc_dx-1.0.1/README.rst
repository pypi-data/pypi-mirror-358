|pypi| |actions| |codecov| |downloads|

edc dx
------

Classes to manage review of HIV, DM and HTN diagnoses

Add settings attribute with the conditions to be managed by the `Diagnosis` class.

For example:

.. code-block:: python

    # settings.py
    ...
    EDC_DX_LABELS = dict(
        hiv="HIV",
        dm="Diabetes",
        htn="Hypertension",
        chol="High Cholesterol"
    )
    ...


.. |pypi| image:: https://img.shields.io/pypi/v/edc-dx.svg
    :target: https://pypi.python.org/pypi/edc-dx

.. |actions| image:: https://github.com/clinicedc/edc-dx/actions/workflows/build.yml/badge.svg
  :target: https://github.com/clinicedc/edc-dx/actions/workflows/build.yml

.. |codecov| image:: https://codecov.io/gh/clinicedc/edc-dx/branch/develop/graph/badge.svg
  :target: https://codecov.io/gh/clinicedc/edc-dx

.. |downloads| image:: https://pepy.tech/badge/edc-dx
   :target: https://pepy.tech/project/edc-dx
