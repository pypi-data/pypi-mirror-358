|pypi| |actions| |codecov| |downloads|

edc-offstudy
------------

Base classes for off study process


The offstudy model is linked to scheduled models by the visit schedule.

.. code-block:: python

    # visit_schedule.py
    ...
    visit_schedule1 = VisitSchedule(
        name='visit_schedule1',
        offstudy_model='edc_offstudy.subjectoffstudy',
        ...)
    ...


This module includes an offstudy model ``SubjectOffstudy``.

You may also declare your own using the ``OffstudyModelMixin``:

.. code-block:: python

    class SubjectOffstudy(OffstudyModelMixin, BaseUuidModel):

         pass

If you declare your own, be sure to reference it correctly in the visit schedule:

.. code-block:: python

    # visit_schedule.py
    ...
    visit_schedule1 = VisitSchedule(
        name='visit_schedule1',
        offstudy_model='myapp.subjectoffstudy',
        ...)
    ...


When the offstudy model is saved, the data is validated relative to the consent and **visit model**. An offstudy datetime should make sense relative to these model instances for the subject.
Unused appointments in the future relative to the offstudy datetime will be removed.

 Note: There is some redundancy with this model and the offschedule model from ``edc-visit-schedule``. This needs to be resolved.


.. |pypi| image:: https://img.shields.io/pypi/v/edc-offstudy.svg
    :target: https://pypi.python.org/pypi/edc-offstudy

.. |actions| image:: https://github.com/clinicedc/edc-offstudy/actions/workflows/build.yml/badge.svg
  :target: https://github.com/clinicedc/edc-offstudy/actions/workflows/build.yml

.. |codecov| image:: https://codecov.io/gh/clinicedc/edc-offstudy/branch/develop/graph/badge.svg
  :target: https://codecov.io/gh/clinicedc/edc-offstudy

.. |downloads| image:: https://pepy.tech/badge/edc-offstudy
   :target: https://pepy.tech/project/edc-offstudy
