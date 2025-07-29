|pypi| |actions| |codecov| |downloads|

edc-pdutils
+++++++++++

Use pandas with the Edc


Using the management command to export to CSV and STATA
+++++++++++++++++++++++++++++++++++++++++++++++++++++++

The ``export_models`` management command requires you to log in with an account that has export permissions.

The basic command requires an app_label (``-a``) and a path to the export folder (``-p``)

By default, the export format is CSV but delimited using the pipe delimiter, ``|``.

Export one or more modules
==========================

.. code-block:: python

    python manage.py export_models -a ambition_subject -p /ambition/export


The ``-a`` excepts more than one app_label

.. code-block:: python

    python manage.py export_models -a ambition_subject,ambition_prn,ambition_ae -p /ambition/export


Export data in CSV format or STATA format
==========================================
To export as CSV where the delimiter is ``|``

.. code-block:: python

    python manage.py export_models -a ambition_subject -p /ambition/export


To export as STATA ``dta`` use option ``-f stata``

.. code-block:: python

    python manage.py export_models -a ambition_subject -p /ambition/export -f stata


Export encrypted data
=====================
To export encrypted fields include option ``--decrypt``:

.. code-block:: python

    python manage.py export_models -a ambition_subject -p /ambition/export  --decrypt


**Note:** If using the ``--decrypt`` option, the user account will need ``PII_EXPORT`` permissions

Export with a simple file name
==============================

To export using a simpler filename that drops the tablename app_label prefix and does not include a datestamp suffix.

Add option ``--use_simple_filename``.

.. code-block:: python

    python manage.py export_models -a ambition_subject -p /ambition/export  --use_simple_filename

Export for a country only
=========================

Add option ``--country``.

.. code-block:: python

    python manage.py export_models -a ambition_subject -p /ambition/export  --country="uganda"



_________________________________

Export manually
+++++++++++++++

To export Crf data, for example:

.. code-block:: python

    from edc_pdutils.df_exporters import CsvCrfTablesExporter
    from edc_pdutils.df_handlers import CrfDfHandler

    app_label = 'ambition_subject'
    csv_path = '/Users/erikvw/Documents/ambition/export/'
    date_format = '%Y-%m-%d'
    sep = '|'
    exclude_history_tables = True

    class MyDfHandler(CrfDfHandler):
        visit_tbl = f'{app_label}_subjectvisit'
        exclude_columns = ['form_as_json', 'survival_status','last_alive_date',
                           'screening_age_in_years', 'registration_datetime',
                           'subject_type']

    class MyCsvCrfTablesExporter(CsvCrfTablesExporter):
        visit_column = 'subject_visit_id'
        datetime_fields = ['randomization_datetime']
        df_handler_cls = MyDfHandler
        app_label = app_label
        export_folder = csv_path

    sys.stdout.write('\n')
    exporter = MyCsvCrfTablesExporter(
        export_folder=csv_path,
        exclude_history_tables=exclude_history_tables
    )
    exporter.to_csv(date_format=date_format, delimiter=sep)

To export INLINE data for any CRF configured with an inline, for example:

.. code-block:: python

    class MyDfHandler(CrfDfHandler):
        visit_tbl = 'ambition_subject_subjectvisit'
        exclude_columns = ['form_as_json', 'survival_status','last_alive_date',
                           'screening_age_in_years', 'registration_datetime',
                           'subject_type']


    class MyCsvCrfInlineTablesExporter(CsvCrfInlineTablesExporter):
        visit_columns = ['subject_visit_id']
        df_handler_cls = MyDfHandler
        app_label = 'ambition_subject'
        export_folder = csv_path
        exclude_inline_tables = [
            'ambition_subject_radiology_abnormal_results_reason',
            'ambition_subject_radiology_cxr_type']
    sys.stdout.write('\n')
    exporter = MyCsvCrfInlineTablesExporter()
    exporter.to_csv(date_format=date_format, delimiter=sep)


Settings
========

``EXPORT_FILENAME_TIMESTAMP_FORMAT``: True/False (Default: False)

By default a timestamp of the current date is added as a suffix to CSV export filenames.

By default a timestamp of format ``%Y%m%d%H%M%S`` is added.

``EXPORT_FILENAME_TIMESTAMP_FORMAT`` may be set to an empty string or a valid format for ``strftime``.

If ``EXPORT_FILENAME_TIMESTAMP_FORMAT`` is set to an empty string, "", a suffix is not added.

For example:

.. code-block:: bash

    # default
    registered_subject_20190203112555.csv

    # EXPORT_FILENAME_TIMESTAMP_FORMAT = "%Y%m%d"
    registered_subject_20190203.csv

    # EXPORT_FILENAME_TIMESTAMP_FORMAT = ""
    registered_subject.csv

.. |pypi| image:: https://img.shields.io/pypi/v/edc-pdutils.svg
    :target: https://pypi.python.org/pypi/edc-pdutils

.. |actions| image:: https://github.com/clinicedc/edc-pdutils/actions/workflows/build.yml/badge.svg
  :target: https://github.com/clinicedc/edc-pdutils/actions/workflows/build.yml

.. |codecov| image:: https://codecov.io/gh/clinicedc/edc-pdutils/branch/develop/graph/badge.svg
  :target: https://codecov.io/gh/clinicedc/edc-pdutils

.. |downloads| image:: https://pepy.tech/badge/edc-pdutils
   :target: https://pepy.tech/project/edc-pdutils
