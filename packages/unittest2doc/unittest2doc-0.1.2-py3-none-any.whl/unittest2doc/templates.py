import textwrap

''' example of sphinx doc
    lib.some_model
    --------------

    INPUT:: 

        def a():
            pass

    OUTPUT:: 

        a = 1

    test crossref for :class:`lib.with_logging.with_logging.CountStatistic`

    test crossref for :func:`lib.with_logging.with_logging.CountStatistic.__init__`

    test crossref for :attr:`lib.with_logging.with_logging.CountStatistic.now`

    test crossref for :const:`lib.with_logging.with_logging.CountStatistic.now`

    test crossref for :doc:`/unittests/main`

    sub section
    ^^^^^^^^^^^^^^^^^^

    subsub section
    """"""""""""""""
'''

P_HEADER = textwrap.dedent('''
  {target_str}

  {name}
  ========================================================================================

  {ref_str}
''')[1:]
P_SUBTITLE = textwrap.dedent('''
  {target_str}

  {title}
  {title_marker}
''')[1:]
P_INPUT = textwrap.dedent('''
  .. collapse:: INPUT
  {open_flag}
  {input_str}

''')[1:]
P_ERROR = textwrap.dedent('''
  .. collapse:: ERROR
  {open_flag}
  {error_str}

''')[1:]
P_RESULT = textwrap.dedent('''
  .. collapse:: OUTPUT
  {open_flag}
  {output_str}

''')[1:]

P_MAIN_title = textwrap.dedent('''
  {title}
  =======================================================

''')[1:]

P_MAIN_sub = textwrap.dedent('''

  .. toctree::
    :maxdepth: 3
    :glob:

    */index

''')[1:]

P_MAIN_local = textwrap.dedent('''

  .. toctree::
    :maxdepth: 3
    :glob:

    *

''')[1:]