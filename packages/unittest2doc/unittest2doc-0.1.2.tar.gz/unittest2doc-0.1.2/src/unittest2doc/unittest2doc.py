import unittest
import inspect
import textwrap
import traceback
import sys
import functools
from pathlib import Path
from io import StringIO
import logging
import json
from typing import Optional, Callable, Iterator, Union, Any, Optional, Mapping, MutableMapping, Sequence, Iterable

from rich.pretty import pprint,pretty_repr
from .templates import *

# Add at the beginning of the file
logger = logging.getLogger(__name__)

class Tee(object):
    ''' Tee sys.stdout to self.file, and then you can read it out to somewhere else

        will also redirect logging things 

        from https://stackoverflow.com/questions/616645/how-to-duplicate-sys-stdout-to-a-log-file

        **Usage**: ::

            tee = Tee()
            try:
                # do something
            except:
                tee.stop()
                del tee
            else:
                tee.file.seek(0)
                _output_str = tee.file.read()
                tee.stop()
                del tee
                # output _output_str
    '''
    def __init__(self, name:Optional[str]=None, mode='a', tee:bool=True, unbuffered:bool=False, prefix="  "):
      '''
        Args:
            name: If not None, will tee to file.  Else will tee to StringIO.
            mode: The file mode if `name` is set, default is `a`
            prefix: extra prefix string to add for each record lines
            tee: default is True, still write to sys.stdout.
                 if set to false, will eat all outputs

      '''
      if name is not None:
          self.file = open(name, mode) #: store Tee content
      else:
          self.file = StringIO()
      self.stdout = sys.stdout
      self.stderr = sys.stderr
      sys.stdout = self
      sys.stderr = self
      self.tee = tee
      self.unbuffered = unbuffered
      self.prefix = prefix
      self._stopped = False
      self._update_logging_stream_handlers(on=True)
    def isatty(self):
        return False
    def stop(self):
        """ stop tee sys.stdout and do cleanups
        """
        if not self._stopped:
            import sys
            sys.stdout = self.stdout
            sys.stderr = self.stderr
            self.file.seek(0)
            self._result = self.file.read()
            # this may cause some error for multi thread tests, so we do not close it
            # self.file.close()
            self._stopped = True
            self._update_logging_stream_handlers(on=False)
    def _update_logging_stream_handlers(self, on=True):
        """ change all streamHandler of all loggers to self or sys.stderr
        """
        loggers = logging.root.manager.loggerDict
        for name,logger in loggers.items():
            if isinstance(logger, logging.Logger):
                for handler in logger.handlers:
                    if type(handler) is logging.StreamHandler:
                        if on:
                            handler.stream = self
                        else:
                            handler.stream = sys.stderr
    def __del__(self):
        if not self._stopped:
            import sys
            sys.stdout = self.stdout
            sys.stderr = self.stderr
            self.file.close()
    def write(self, data, from_logger=False):
        if self.tee:
            self.stdout.write(data)
        end_with_newline = data.endswith('\n')
        if end_with_newline:
            data = data[:-1]
        data = data.split('\n')
        data = list(map(lambda _:self.prefix+_ if _ else _, data))
        data = '\n'.join(data)
        if end_with_newline:
            data = data+'\n'
        if 'FROM_LOGGER' in globals(): # ?
            return
        try:
            self.file.write(data)
        except Exception as e:
            print(f"error in Tee.write for {self.file}, try to write {data}")
            raise
        if self.unbuffered:
            self.file.flush()
    def flush(self):
        self.file.flush()

def all_type_json_serializer(obj:Any) -> str:
    """try to use repr() to serialize objects that are not JSON serializable"""
    try:
        return json.JSONEncoder().default(obj)
    except TypeError:
        return repr(obj)

class FLog:
    """ Record the function and its output, used to generate document for unittest functions

        *Usage*: ::

            # in Unittest2Doc.setUp
            s.flog = FLog(do_print=True, input_prefix='# call=> ', input_suffix=' ==>')
            s.func=s.flog.func

            # in test functions
            s.r = s.func(somefunc)
            s.r = s.func(somefunc, args=[], kwargs={})
            s.r = s.frun(somefunc, arg1, args2, args3, kwarg0=..., kwargs1=..., kwargs2=...)

    """
    def __init__(self,
            fargs:Optional[dict[Callable]]=None,
            fkwargs:Optional[dict]=None,
            do_print:Optional[bool]=True,
            do_print_input:Optional[bool]=None,
            do_print_output:Optional[bool]=None,
            input_prefix:Optional[str]='',
            input_suffix:Optional[str]='',
            output_suffix:Optional[str]='',
            input_max_width:int=80,
        ):
        self.fargs = fargs
        self.fkwargs = fkwargs
        self.do_print = do_print
        self.do_print_input  = do_print_input
        self.do_print_output = do_print_output
        self.input_prefix = input_prefix
        self.input_suffix = input_suffix
        self.output_suffix = output_suffix
        self.input_max_width = input_max_width
    def frun(self, func, *args, **kwargs):
        self.func(func,args=args,kwargs=kwargs)
    def func(self, func:Callable, *,
              args:Optional[Union[list,tuple]]=None,
              kwargs:Optional[dict]=None,
              fargs:Optional[dict[Callable]]=None,
              fkwargs:Optional[dict]=None,
              do_print:Optional[bool]=None,
              do_print_input:Optional[bool]=None,
              do_print_output:Optional[bool]=None,
              input_prefix:Optional[str]=None,
              input_suffix:Optional[str]=None,
              output_suffix:Optional[str]=None,
              input_max_width:Optional[int]=None,
          ) -> dict:
          """ run function with give args and kwargs, return formated result

              Args:
                  args: see below
                  kwargs:  together with ``args``, we call the function like ``func(*args, **kwargs)``
                  fargs: function to reformat args befreo we print it in the `input` retion section, see below
                  fkwargs: together with ``fargs``, we preprocess (reformat) the input 
                           and then print them in the function input part, see the ``Returns`` for details
                  print: if true, will also print the ``input`` and ``output`` results
                  input_prefix: add prefix for the `input` result
                  input_suffix: add suffix for the `input` result

              Returns:
                  dict with the keys ``output``, ``input``.

                  The ``output`` is the return value from the func call
                  The ``intput`` is like ::

                      func(args[0], args[1], ..., args[-1], key0=value0, key1=value1, ...)

                  where the ``key<n>`` and ``value<n>`` are from ``kwargs``

                  if fargs and fkwargs are not None, we preprocess the input data before we print them, like::

                      func(
                          fargs[0](args[0]), fargs[1](args[1]), ..., fargs[-1](args[-1]),
                          key0=fkwargs[key0](value0), key1=fkwargs[key1](value1), ...)

          """
          if args is None:
              args = []
          if kwargs is None:
              kwargs = {}
          if "get parameters from self config":
              if fargs is None:
                  fargs = self.fargs
              if fkwargs is None:
                  fkwargs = self.fkwargs
              if do_print_input is None:
                  if do_print is None:
                      if self.do_print_input is None:
                          do_print_input = self.do_print
                      else:
                          do_print_input = self.do_print_input
                  else:
                      do_print_input = do_print
              if do_print_output is None:
                  if do_print is None:
                      if self.do_print_output is None:
                          do_print_output = self.do_print
                      else:
                          do_print_output = self.do_print_output
                  else:
                      do_print_output = do_print
            
              if input_prefix is None:
                  input_prefix = self.input_prefix
              if input_suffix is None:
                  input_suffix = self.input_suffix
              if output_suffix is None:
                  output_suffix = self.output_suffix
              if input_max_width is None:
                  input_max_width = self.input_max_width

          output = func(*args, **kwargs)
          fname = func.__code__.co_name

          args_list = []
          for i, each in enumerate(args):
              if fargs is not None and i < len(fargs):
                  each = fargs[i](each)
              args_list.append(repr(each))
          kwargs_list = []
          for key, each in kwargs.items():
              if fkwargs is not None and key in fkwargs:
                  each = fkwargs[key](each)
              kwargs_list.append(f"{key}={repr(each)}")
          if len(args_list):
              args_str = ', '.join(args_list) + ', '
          else:
              args_str = ''
          if len(kwargs_list):
              kwargs_str = ', '.join(kwargs_list)
          else:
              kwargs_str = ''
          input = f"{input_prefix}{fname}({args_str}{kwargs_str}){input_suffix}"
          if len(input) > input_max_width: # input line too long, we make multiline print
              args_list = []
              for i, each in enumerate(args):
                  if fargs is not None and i < len(fargs):
                      each = fargs[i](each)
                  if len(str(each))>input_max_width:
                      args_list.append(f"{repr(each)}")
                  else:
                      args_list.append(f"{json.dumps(each, indent=2, default=all_type_json_serializer)}")
              kwargs_list = []
              for key, each in kwargs.items():
                  if fkwargs is not None and key in fkwargs:
                      each = fkwargs[key](each)
                  if len(f"{key}={repr(each)}")>input_max_width:
                      kwargs_list.append(f"{key}={json.dumps(each, indent=2, default=all_type_json_serializer)}")
                  else:
                      kwargs_list.append(f"{key}={repr(each)}")
              if len(args_list):
                  args_str = ',\n'.join(args_list)
                  args_str   = "\n".join(map(lambda _:'  '+_, args_str.split('\n')))
              else:
                  args_str = ''
              if len(kwargs_list):
                  if len(args_str):
                      args_str += ",\n"
                  kwargs_str = ',\n'.join(kwargs_list)
                  kwargs_str = "\n".join(map(lambda _:'  '+_, kwargs_str.split('\n')))
              else:
                  kwargs_str = ''
              input_str = f"{args_str}{kwargs_str}"
              if len(input_str):
                  input_str = '\n' + input_str + '\n'
              input = f"{input_prefix}{fname}({input_str}){input_suffix}"

          if do_print_input:
              print(input)
          if do_print_output:
              print(output, end=f"{output_suffix}\n")
          return {'input': input, 'output': output}

def _linenumber_of_member(m):
    """ Get the line number of a class member for sorting purposes
    
        This function extracts the line number of a class member to enable
        sorting members in their original declaration order in the source code.
    
        Args:
            m: A (name, method) tuple from class inspection

        Returns:
            int: The line number where the member was defined, or -1 if not determinable
    """
    try:
        raw_lineno = getattr(m[1], '__raw_lineno', None)
        if raw_lineno is not None:
            return raw_lineno

        raw_lineno = getattr(m[1], '_co_number', None)
        if raw_lineno is None:
            return m[1].__code__.co_firstlineno
        else:
            return raw_lineno
    except AttributeError:
        return -1
def _mask_data(data, starts:int|None=None, ends:int|None=None):
    """ Mask sensitive data with option to show partial content
    
        Creates a masked representation of data that hides most content
        but optionally shows the beginning and/or end portions.
    
        Args:
            data: The data to mask
            starts: If provided, show this many characters from the beginning
            ends: If provided, show this many characters from the end

        Returns:
            str: A masked representation of the data
    """
    result = f'**MASKED**:({len(str(data))})'
    if starts is not None or ends is not None:
        v = str(data)
        if starts is not None:
            s = v[:starts]
        else:
            s = ''
        if ends is not None:
            e = v[ends:]
        else:
            e = ''
        v = '...'
        result += f'|{s}{v}{e}'
    return result

UNDEFINED = Exception('undefined')
def nested_get(d:dict, path:list[str]):
    """ Get a nested dictionary value using a key path
    
        Traverses a nested dictionary structure using a list of keys.
    
        Args:
            d: The dictionary to traverse
            path: A list of keys representing the path to the desired value

        Returns:
            The value at the specified path, or UNDEFINED if the path is invalid
    """
    for key in path:
        if isinstance(d, dict) and key in d:
            d = d[key]
        else:
            return UNDEFINED
    return d

def nested_set(D, path:list[str], value, create_missing:bool=False):
    """ set value for a dict with given key path like dict.A.B.C.

        From https://stackoverflow.com/questions/13687924/setting-a-value-in-a-nested-python-dictionary-given-a-list-of-indices-and-value

        Args:
          dict: the dict to update
          path:
            the dick key path like dict.<path> to modify
          value:
            set dict.<path> to this value
          create_missing:
            if dict.<path> not exist

        **Example**: ::

            # Trying to set a value of a nonexistent key DOES NOT create a new value
            >>> print(nested_set({"A": {"B": 1}}, ["A", "8"], 2, False))
            {'A': {'B': 1}}

            # Trying to set a value of an existent key DOES create a new value
            >>> print(nested_set({"A": {"B": 1}}, ["A", "8"], 2, True))
            {'A': {'B': 1, '8': 2}}

            # Set the value of an existing key
            >>> print(nested_set({"A": {"B": 1}}, ["A", "B"], 2))
            {'A': {'B': 2}}
    """
    d = D
    for key in path[:-1]:
        if key in d:
            d = d[key]
        elif create_missing:
            d = d.setdefault(key, {})
        else:
            return D
    if path[-1] in d or create_missing:
        d[path[-1]] = value
    return D

def docpprint(data:any, **kwargs):
    """ Pretty print data for documentation purposes
    
        A wrapper around rich.pretty.pprint with default settings optimized
        for documentation output.
    
        Args:
            data: The data to pretty print
            **kwargs: Additional arguments passed to rich.pretty.pprint
    """
    pprint(data, indent_guides=False, expand_all=True, **kwargs)
  # pprint.pprint(data, indent=2, width=160, compact=True, sort_dicts=False, **kwargs)

def docpformat(data:any, indent=4, **kwargs):
    return pretty_repr(data, indent_size=indent, expand_all=True, **kwargs)

def get_caller_func_name() -> str:
    frame = inspect.currentframe()
    caller_frame = frame.f_back
    caller_name = caller_frame.f_code.co_name
    return caller_name

# decorator functions
def skip(func):
    """ use @unittest2doc.skip to skip some unittest
    """
    def wrapper(*args, **kwargs):
        _skipped = True
        func(*args, **kwargs)
    # return wrapper
    return unittest.skip("skipped with unittest2doc.skip")(wrapper)

def stop(func):
    """ use @unittest2doc.stop to stop unittest before this function

        Note: it work only when you use Unittest2Doc.generate_docs(),
              it does not work when you use unittest.main()
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        _stopped = True
        func(*args, **kwargs)
    wrapper.__raw_lineno = func.__code__.co_firstlineno
    wrapper.__unittest2doc_stop__ = True
    return wrapper

def only(func):
    """ use @unittest2doc.only to only run some unittest

        Note: it work only when you use Unittest2Doc.generate_docs(),
              it does not work when you use unittest.main()
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        _only = True
        func(*args, **kwargs)
    wrapper.__raw_lineno = func.__code__.co_firstlineno
    wrapper.__unittest2doc_only__ = True
    return wrapper

def stop_after(func):
    """ use @unittest2doc.stop_after to stop unittest after this function

        Note: it work only when you use Unittest2Doc.generate_docs(),
              it does not work when you use unittest.main()
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        _stop_after = True
        func(*args, **kwargs)
    wrapper.__raw_lineno = func.__code__.co_firstlineno
    wrapper.__unittest2doc_stop_after__ = True
    return wrapper

def expected_failure(func):
    """ use @unittest2doc.expected_failure to mark a test as expected to fail """
    wrapper = unittest.expectedFailure(func)
    wrapper.__raw_lineno = func.__code__.co_firstlineno
    wrapper.__unittest2doc_expected_failure__ = True
    return wrapper

# utils functions for user
def v(toshow:list[str], l:dict, g:dict, mask:list=None, doprint:bool=True) -> dict:
    """ pretty print varialbes in toshow list

        Args:
            toshow: the variables to be shown
            l: should input ``locals()``
            g: should input ``globals()``
            mask: the variables that contain secret values, should be masked
            doprint: if True, do pprint

        **Usages**: ::

            # in Unittest2Doc test functions
            s.v(['var0', 'var1'], locals(), globals(), mask=[])

            # mask some secrets
            s.v(['a', 'b', 'c', 'd'], locals(), globals(), mask=[
                'c.secret',
                'c.subsecret.bad',
                'c.subsecret.sub.bad',
            ])

    """
    if mask is None:
        mask = []
    result = {}
    for each in toshow:
        result[each] = eval(each, g, l)

    dmask = isinstance(mask, dict)
    for each in mask:
        if each in result:
            if dmask:
                masked_str = _mask_data(result[each], **mask[each])
            else:
                masked_str = _mask_data(result[each])
            result[each] = masked_str
        elif '.' in each: # search parent
            parent = each.split('.')
            sub = []
            for i in range(len(parent)-1):
                sub.insert(0, parent.pop())
                key_parent = '.'.join(parent)
                if key_parent in result and isinstance(result[key_parent], dict):
                    value = nested_get(result[key_parent], sub)
                    if value is not UNDEFINED: # now the sub value is good to use
                        if dmask:
                            masked_str = _mask_data(value, **mask[each])
                        else:
                            masked_str = _mask_data(value)
                        nested_set(result[key_parent], sub, masked_str)
                        break
    if doprint:
        docpprint(result)
    return result

def add_foldable_output(self, *, name, output, highlight='', open=False):
    """ add extra foldabel text at end of the doc page

        params: name, output, highlight, open
        
        **usage**: ::

            # in unittest.TestCase test functions
            unittest2doc.add_foldable_output(
                self,
                name="some code",
                highlight='python',
                output=textwrap.dedent('''
                    # some code ...
                    def func(*args, **kwargs):
                    pass
                '''
                ),
                open=True,
            )

    """
    open_flag='  :open:\n' if open else ''
    output = output.split('\n')
    output = list(map(lambda _:'    '+_, output))
    output_str = '\n'.join(output)
    output_str = f"  .. code-block:: {highlight}\n\n" + output_str
    P_EXTRA = textwrap.dedent('''
      .. collapse:: {name}
      {open_flag}
      {output_str}

    ''')[1:].format(name=name, open_flag=open_flag, output_str=output_str)

    l = get_config(self, 'extra_doc_suffix')
    if isinstance(l, list):
        l.append(P_EXTRA)

def update_config(self, **kwargs):
    """ update config for unittest2doc

        call this function in unittest.TestCase test functions

        keys can be:

        * title_marker
        * open_input
        * open_output
        * output_highlight
        * save_stdout
        * output_processors
    """
    if not hasattr(self, '_unittest2doc'):
        self._unittest2doc = {}
    self._unittest2doc.update(kwargs)
def get_config(self, key):
    if not hasattr(self, '_unittest2doc'):
        self._unittest2doc = {}
    return self._unittest2doc.get(key, None)

# helper functions
def process_docstring(docstring):
    """ clean white spaces """
    docstringlines = docstring.split('\n')
    if len(docstringlines) <= 1:
        docstring = docstring.strip()
    else:
        first,*latter = docstringlines
        first = first.strip()
        latter = textwrap.dedent('\n'.join(latter))
        docstring = '\n'.join([first, latter])
    return docstring

class Unittest2Doc:
    """ wrapper unittests and make documentation pages for sphinx

        **Docstring formats in the unittest functions**:

        * the docstring of the custom Unittest2Doc class will be added to beginning of the doc page

        * the first line of the docstring can be used as config section, e.g.
          
          * ``{"open_input":false}`` to close the input by default

          * ``{"title_marker": "^"}`` to leveldown this test (change default title marker to ``^``)

          * ``{"title_marker": "-"}`` to levelup this test (change default title marker to ``-``)

          * ``{"output_highlight": "python"}``, ``{"output_highlight": "json"}``

        * functions used

          * we only run functions that name startswith ``test``

          * we only use their docstring for functions that name startswith ``rst``

          * setUp is always called at beginning of the test and tearDown is always called at end

        **Usage**: ::

          t = ThisTest(
            name='unittest2doc.unittest2doc.Unittest2Doc.basic',   # required
            ref=':class:`unittest2doc.unittest2doc.Unittest2Doc`', # optional
            doc_root=Path(__file__).absolute().parent.parent / 'sphinx-docs/source/unittests', # required
          )
        
        see :doc:`/unittests/unittest2doc/unittest2doc/Unittest2Doc/index` for more detailed examples

    """

    def __init__(self, *,
            testcase:unittest.TestCase,
            name:str,
            ref:str='',
            update_index=True,
            no_test_prefix=True,
            open_input=True,
            open_output=True,
            output_highlight='',
            doc_root=None,
            output_processors=None,
            **kwargs
        ):
        """
            Args:
                name: name of the package, e.g., name='lib.utils'
                ref: if set, will add `references: {ref}` at beginning. ref should be a rst link in sphinx
                doc_root:
                    root folder of the unittests docs folder.
                    Usually it should be `<package-folder>/docs/source/unittests`
                update_index: update all parent index files
                output_highlight: the highlight language for the output section
                open_input: open input section
                open_output: open output section
                no_test_prefix: remove the ``test_`` function name prefix in the doc page
        """
        self.testcase = testcase
        self.title_marker = '-'
        self.open_input  = open_input
        self.open_output = open_output
        self.no_test_prefix = no_test_prefix
        self.output_highlight = output_highlight
        self.output_processors = output_processors or []

        assert isinstance(self.testcase, unittest.TestCase), "testcase should be an instance of unittest.TestCase"
        assert isinstance(name, str), "name should be a string"

        doc_path = name.replace('.', '/')

        self.doc_root = Path(doc_root)
        self.doc_root.mkdir(parents=True, exist_ok=True)
        doc_path = self.doc_root / doc_path
        self.doc_dir = doc_path.parent
        self.doc_dir.mkdir(parents=True, exist_ok=True)

        # generate index.rst index files in parent folders
        _path_list = name.split('.')[:-1]
        _path_list.insert(0, self.doc_root.name)
        _path = ''
        for i,basename in enumerate(_path_list):
            title = '.'.join(_path_list[1:i+1])
            if not len(_path):
                _path = f"{basename}"
            else:
                _path = f"{_path}/{basename}"
            index_file = Path(self.doc_root.parent, _path, 'index.rst')
            if not index_file.exists() or update_index:
                pfolder = index_file.parent

                contents = [P_MAIN_title.format(title=title if i>0 else 'UNITTESTs')]
                if len(list(pfolder.glob('*.rst'))) > 1 or i == len(_path_list) - 1:
                    contents.append(P_MAIN_local)
                if len(list(pfolder.glob("*/*"))) > 0 or i != len(_path_list) - 1:
                    contents.append(P_MAIN_sub)
                with open(index_file, 'w') as f:
                    f.write("\n".join(contents))
                #if i == 0:
                #  with open(index_file, 'w') as f:
                #    f.write(P_MAIN.format(title='UNITTESTs', subs='*/index'))
                #else:
                #  _title = '.'.join(_path.split('/')[1:])
                #  if i == len(_path_list) - 1:
                #    with open(index_file, 'w') as f:
                #      f.write(P_MAIN.format(title=_title, subs='*'))
                #  else: # normal
                #    with open(index_file, 'w') as f:
                #      f.write(P_MAIN.format(title=_title, subs='*/index'))

        self.doc_name = doc_path.name

        self._name = name
        if len(ref):
            self._ref_str = f'references: {ref}\n'
        else:
            self._ref_str = ''
        self._tresults = []

    def generate_docs(self):
        """ do unittest and generate docs
        """
        testcase = self.testcase
        if "select test functions":
            tests_raw = inspect.getmembers(testcase)
            tests_raw_names = list(map(lambda _:_[0], tests_raw))
            tests = list(
                filter( # we only run functions that name startswith ``test`` and ``rst``
                      lambda _:_[0].startswith('test') or 
                      _[0].startswith('rst')
                  , tests_raw))
            lines = [(_[0], _linenumber_of_member(_)) for _ in tests]
            tests.sort(key=_linenumber_of_member)
            tests = list(map(lambda _:_[0], tests))

            # process `only` tests
            excepted_failures = []
            _tests_only = []
            have_only = False
            for i, testname in enumerate(tests):
                if testname in ['tearDown', 'setUp']:
                    _tests_only.append(testname)
                else:
                    func = getattr(testcase, testname)
                    if getattr(func, '__unittest2doc_only__', False):
                        _tests_only.append(testname)
                        have_only = True
                    if getattr(func, '__unittest_expecting_failure__', False):
                        excepted_failures.append(testname)
                    if getattr(func, '__unittest2doc_stop__', False):
                        tests = tests[:i]
                        break
                    if getattr(func, '__unittest2doc_stop_after__', False):
                        tests = tests[:i+1]
                        break
            if have_only:
                tests = _tests_only

            if 'setUp' in tests_raw_names:
                __ = getattr(testcase, 'setUp')
                if __.__doc__ is not None:
                    if not __.__doc__.startswith('Hook method for setting up the test fixture before exercising it.'):
                        tests.insert(0, 'setUp')
                else:
                    tests.insert(0, 'setUp')
            if 'tearDown' in tests_raw_names:
                __ = getattr(testcase, 'tearDown')
                if __.__doc__ is not None:
                    if not __.__doc__.startswith('Hook method for deconstructing the test fixture after testing it.'):
                        tests.append('tearDown')
                else:
                    tests.append('tearDown')
      
        _result_doc = [
            P_HEADER.format(
                name=self._name,
                ref_str=self._ref_str,
                target_str=f".. _unittests/{self._name}:"
            )
        ]

        if 'process class docstring':
            docstring = testcase.__doc__
            if docstring is not None:
                docstring = process_docstring(docstring)
                if len(docstring):
                    _result_doc.append(docstring+'\n')

        tests = list(
          filter(
            lambda _:not getattr(getattr(testcase, _), '__unittest_skip__', False), 
          tests))

        update_config(testcase,
            title_marker=self.title_marker,
            open_input=self.open_input,
            open_output=self.open_output,
            output_highlight=self.output_highlight,
            save_stdout=True,
            extra_doc_prefix=[],
            extra_doc_suffix=[],
            output_processors=[],
        )

        print(f'do tests for {tests}')
        for testname in tests:
            func = getattr(testcase, testname)
            _source = textwrap.dedent(inspect.getsource(func))
            _input_str = '\n'.join(['    '+_ for _ in _source.split('\n')])
            #if '_skipped' in func.__code__.co_varnames:
            #    continue
            print(f'=====> {testname}')
            if testname.startswith('test_'):
                test_target_name = testname[5:]
            else:
                test_target_name = testname
            # if first line is a json, we use it as config
            docstring = func.__doc__

            # you can change these configs in test functions
            title_marker = get_config(testcase, 'title_marker')
            open_input   = get_config(testcase, 'open_input')
            open_output  = get_config(testcase, 'open_output')
            output_highlight = get_config(testcase, 'output_highlight')
            save_stdout = get_config(testcase, 'save_stdout')
            output_processors = get_config(testcase, 'output_processors')
            output_processors = list(filter(lambda _:_, output_processors))

            dconfig = {}
            if docstring is not None:
                try:
                    first = docstring.split('\n')[0].strip()
                    dconfig = json.loads(first)
                except Exception as e:
                    pass
                else: # have dconfig, make online changes
                    docstring = '\n'.join(docstring.split('\n')[1:])
                    if 'title_marker' in dconfig:
                        title_marker = dconfig['title_marker'] # change title marker only for this test
                    if 'open_input' in dconfig:
                        open_input  = dconfig['open_input']
                    if 'open_output' in dconfig:
                        open_output = dconfig['open_output']
                    if 'output_highlight' in dconfig:
                        output_highlight = dconfig['output_highlight']
                    if 'save_stdout' in dconfig: # you can temporarily disable save_stdout for some test functions
                        save_stdout = dconfig['save_stdout']
                    if 'output_processors' in dconfig:
                      output_processors = [self.output_processors[k] for k in dconfig['output_processors']]
                      output_processors = list(filter(lambda _:_, output_processors))

            if self.no_test_prefix and testname.startswith('test_'):
                testtitle = testname[5:]
            else:
                testtitle = testname
            if not testname.startswith('rst_'):
                _result_doc.append(
                    P_SUBTITLE.format(
                        title=testtitle,
                        title_marker=title_marker*len(testtitle),
                        target_str=f".. _unittests/{self._name}.{test_target_name}:",
                    )
                )

            # go on with doc string
            if docstring is not None:
                docstring = process_docstring(docstring)
                if len(docstring):
                    _result_doc.append(docstring+'\n')
            if testname.startswith('rst') or not save_stdout: # only use docstring for rst_* functions
                save_stdout = False
            else:
                save_stdout = True

            # add INPUT
            if save_stdout:
                #_input_str = "  .. code-block:: python\n     :linenos:\n\n" + _input_str
                _input_str = f"  .. code-block:: python\n\n" + _input_str
                _result_doc.append( P_INPUT.format(
                    input_str=_input_str,
                    open_flag='  :open:\n' if open_input else '',
                ) )
            # prepare Tee and run function
            if save_stdout:
                tee = Tee(tee=self.doc_root is not None)
            try:
                func()
            except Exception as e:
                # meet error
                exp = traceback.format_exc()
                ss = exp.split('\n')
                ss = filter(lambda _:_.strip(), ss)
                output = list(map(lambda _:'    '+_, ss))
                _output_str = '\n'.join(output)
                if output_processors:
                  for processor in output_processors:
                    _output_str = processor(_output_str)
                _output_str = f"  .. code-block:: {output_highlight}\n\n" + _output_str
                # record error into docstring and exit
                #   you can compile this result and inspect it in Sphinx pages
                _result_doc.append( P_ERROR.format(
                    error_str=_output_str,
                    open_flag='  :open:\n' if open_output else '',
                ) )
                with open(Path(self.doc_dir, self.doc_name+'.rst'), 'w') as f:
                    f.write('\n'.join(_result_doc))
                if save_stdout:
                    tee.stop()
                    del tee
                if testname not in excepted_failures:
                    raise
            else:
                # no errors
                if save_stdout:
                    tee.file.seek(0)
                    _output_str = tee.file.read()
                    tee.stop()
                    del tee
                    if len(_output_str) != 0 and not dconfig.get("no_output", False):
                        output = _output_str.split('\n')
                        output = list(map(lambda _:'  '+_, output))
                        _output_str = '\n'.join(output)
                        if output_processors:
                            for processor in output_processors:
                                _output_str = processor(_output_str)
                        _output_str = f"  .. code-block:: {output_highlight}\n\n" + _output_str
                        _result_doc.append( P_RESULT.format(
                            output_str=_output_str,
                            open_flag='  :open:\n' if open_output else '',
                        ) )
            _result_doc[:0] = get_config(testcase, 'extra_doc_prefix')
            _result_doc.extend(get_config(testcase, 'extra_doc_suffix'))
            update_config(testcase,
                extra_doc_prefix=[],
                extra_doc_suffix=[],
            )
        with open(Path(self.doc_dir, self.doc_name+'.rst'), 'w') as f:
            f.write('\n'.join(_result_doc))

__all__ = [
  'Unittest2Doc',
  'FLog',
  'docpprint',
  'docpformat',
  'unittest',
  'skip',
  'stop',
  'only',
  'stop_after',
  'expected_failure',
  'add_foldable_output',
  'v',
  'update_config',
  'all_type_json_serializer',
  'get_caller_func_name',
]
