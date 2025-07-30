from typing import Optional, Callable, Iterator, Union, Any, Mapping, MutableMapping, Sequence, Iterable
import json
import copy

def data2json(d:Any, prefix:str='\t') -> str:
    ''' custom dump for json: add ``prefix`` for each line

        Args:
            d: dict to dump
            prefix: prefix to be added into each line
        Returns:
            the json str of input
    '''
    j = json.dumps(d, indent=2, default=str)
    result = [ '\t'+_ for _ in j.split('\n')]
    return '\n'.join(result)

def pformat_json(data,
        comments:str|dict|None=None,
        indent:int=2,
        level:int=0,
        comment_prefix:str="# ",
        compact:int|None=None,
        debug:bool=False
    ):
    """ Pretty format JSON data with support for a comment system
    
        This function formats nested Python data structures (dicts, lists, etc.) into a readable 
        string representation with support for various types of comments.
    
        Args:
            data: Data to format (dict, list, or simple value)
            comments: Comment configuration, can be a dict or string
                - Dict type supports advanced commenting features (see below)
                - String type serves as a title comment for the top-level object
            indent: Number of spaces for indentation
            level: Current recursion level (used for indentation)
            comment_prefix: Comment prefix character(s), defaults to "# "
    
        Dict comment special keys:
            __dtitle__: String, shown as dict title after opening brace
            __lcompact__: Integer, maximum line length for compact mode
            __lsub__: Any value, comments to apply to all child elements
    
        List comment special keys:
            __ltitle__: String, shown as list title after opening bracket
            __lprefix__: List, prefix comment lines to add at the beginning
            __lsuffix__: List, suffix comment lines to add at the end
            __lcompact__: Integer, maximum line length for compact mode
            __llist__: Any value, comments to apply to all list-type child elements
            __ldict__: Any value, comments to apply to all dict-type child elements
            __lsub__: Any value, comments to apply to all child elements
            Integer keys: Comments to apply to specific index elements
    
        Returns:
            Formatted data string
    """
    subkwargs = {'indent':indent, 'comment_prefix':comment_prefix, 'compact':compact, 'debug':debug} # fixed parameters for sub-calls
    if isinstance(data, dict):
        valuestrs = {}

        # calculate all value strings for print, in nested way
        for key,value in data.items():
            if comments is not None:
                if isinstance(comments, dict):
                    lsub = comments.get('__lsub__', dict())
                    subcomments = comments.get(key, dict())

                    if isinstance(subcomments, str) and len(lsub):
                        if isinstance(value, dict):
                            subcomments = {"__dtitle__": subcomments}
                        elif isinstance(value, list):
                            subcomments = {"__ltitle__": subcomments}

                    if isinstance(subcomments, dict):
                        _ = copy.deepcopy(lsub) 
                        _.update(subcomments)
                        if len(lsub):
                            if '__lsub__' in subcomments:
                                __ = copy.deepcopy(subcomments['__lsub__'])
                                __.update(lsub)
                                _['__lsub__'] = __
                            else:
                                _['__lsub__'] = lsub
                        subcomments = _
                    # else subcomments should be a string or None
                elif isinstance(comments, str):
                    subcomments = None
                else:
                    subcomments = None
            else:
                subcomments = None
            if debug:
                print(f"level: {level}, key: {key}, value: {value}, subcomments: {subcomments}")
            valuestrs[key] = pformat_json(value, comments=subcomments, level=level+1, **subkwargs)

        # prepare comment title for dict
        if comments is not None:
            if isinstance(comments, dict) and '__dtitle__' in comments:
                dict_title = comments['__dtitle__']
            elif isinstance(comments, str):
                dict_title = comments
            else:
                dict_title = ''
            if '\n' in dict_title:
                dict_title_list = dict_title.split('\n')
                for i,each in enumerate(dict_title_list):
                    if i==0:
                        dict_title_list[i] = f' {comment_prefix}{each}'
                    else:
                        dict_title_list[i] = ' '*indent*level + f'  {comment_prefix}{each}'
                dict_title = '\n'.join(dict_title_list)
            elif len(dict_title):
                dict_title = f" {comment_prefix}{dict_title}"
        else:
            dict_title = ''

        # get compact option
        if comments is not None and isinstance(comments, dict):
            lcompact = comments.get('__lcompact__', compact)
        else:
            lcompact = compact
        assert lcompact is None or isinstance(lcompact, int)

        # prepare result list
        result_list = ['{' + dict_title] # first line of dict
        line_groups = []
        current_group = [] # tuple of (key, valuestr, comment, type)
        for (key,value),(rkey,rvalue) in zip(valuestrs.items(), data.items()):
            if '\n' in value: # process line_groups
                if len(current_group):
                    line_groups.append(current_group)
                current_group = []

            # normal one line object
            if comments is not None and isinstance(comments, dict):
                thiscomment = comments.get(key, '')
                if callable(thiscomment):
                    thecomment = thiscomment(key, data[key])
                    current_group.append([repr(key), value, f'{comment_prefix}{thecomment}'])
                elif len(thiscomment) and not isinstance(data[key], (dict, list, tuple)):
                    current_group.append([repr(key), value, f'{comment_prefix}{thiscomment}'])
                else:
                    current_group.append([repr(key), value, ''])
            #elif comments is not None and isinstance(comments, str):
            #    pass # str comments is used for dict title, nothing to do for sub keys
            else:
                current_group.append([repr(key), value, ''])
            if isinstance(rvalue, (dict, list, tuple)):
                current_group[-1].append('map')
            else:
                current_group[-1].append('')
        line_groups.append(current_group)

        # now we have several groups, do print for each group
        #  line_groups is a list of tuple (key, valuestr, comment, type)
        for current_group in line_groups:
            # calculate max length of key + valuestr
            alllens = [len(_[0]) + len(_[1]) for _ in current_group]
            maxlen = max(alllens) if len(alllens) else 0

            thisoneline = ''
            thisonelinecount = 0
            thisonelinecomment = ''
            for k,v,c,t in current_group:
                if lcompact is None or t == 'map': # no lcompact option
                    before_comment = ' '*indent*(level+1) + f'{k}: {v},'
                    if len(c): # add comment
                        extra_str = " " * (maxlen - len(k) - len(v)+1)
                        for i,eachc in enumerate(c.split('\n')):
                            if i == 0:
                                result_list.append(
                                    before_comment + f'{extra_str}{eachc}'
                                )
                            else:
                                result_list.append(
                                    ' ' * len(before_comment) + f'{extra_str}{comment_prefix}{eachc}'
                                )
                    else: # no comment
                        result_list.append(before_comment)
                else: # line is compact, we put all comments at end
                    if indent*(level+1)>lcompact:
                        raise Exception(f'level too deep ({level+1}) and __lcompact__({lcompact}) is too small')
                    if thisonelinecount == 0:
                        this_line=' '*indent*(level+1) + f'{k}: {v},'
                    else:
                        this_line=f'{k}: {v},'

                    if len(this_line) + len(thisoneline)>lcompact: # print this oneline and put the current line as next oneline
                        # print before lines
                        if len(thisonelinecomment):
                            result_list.append(f'{thisoneline} {thisonelinecomment}')
                        else:
                            result_list.append(f'{thisoneline}')
                        # add current line as the first of this oneline
                        thisoneline = ' '*indent*(level+1) + f'{k}: {v},'
                        thisonelinecount = 1
                        if len(c):
                            if '\n' in c:
                                c = ' '.join(c.split('\n'))
                                # raise Exception('can not have multi-line comment in a compact format')
                            thisonelinecomment = f'{comment_prefix}{k}:{c[len(comment_prefix):]}'
                        else:
                            thisonelinecomment = ''
                    else: # concat lines
                        thisonelinecount += 1
                        if len(thisoneline):
                            thisoneline = thisoneline +' '+ this_line
                        else:
                            thisoneline = this_line
                        if len(c):
                            if '\n' in c:
                                c = ' '.join(c.split('\n'))
                                # raise Exception('can not have multi-line comment in a compact format')
                            if len(thisonelinecomment):
                                thisonelinecomment = thisonelinecomment + f' {comment_prefix}{k}:{c[len(comment_prefix):]}'
                            else:
                                thisonelinecomment = f'{comment_prefix}{k}:{c[len(comment_prefix):]}'
            if lcompact is not None and t != 'map': # do print last line:
                if len(thisonelinecomment):
                    result_list.append(f'{thisoneline} {thisonelinecomment}')
                else:
                    result_list.append(f'{thisoneline}')

        result_list.append(' '*indent*level + '}')
        return '\n'.join(result_list)
    elif isinstance(data, (list, tuple)):
        # keys of comments:
        #   * __ltitle__:  str,  will appear after the [
        #   * __lprefix__: list, will be added in the first few lines
        #   * __lsuffix__: list, will be added in the last few lines
        #   * __lcompact__:  int, will make several list item in one line
        #                       so that it is not longer than this value
        #   * __llist__:   any,  subcomments for all list element
        #   * __ldict__:   any,  subcomments for all dict element
        #   * __lsub__:    any,  subcomments for all element
        #   * <int>: int index will transfer subcomments for the selected element
        valuestrs = []
        for i, value in enumerate(data):
            if comments is not None and isinstance(comments, dict):
                if i in comments:
                    subcomments = comments[i]
                elif i-len(data) in comments:
                    subcomments = comments[i-len(data)]
                elif isinstance(value, list) and '__llist__' in comments:
                    subcomments = comments["__llist__"]
                elif isinstance(value, dict) and '__ldict__' in comments:
                    subcomments = comments["__ldict__"]
                else:
                    subcomments = None
                if isinstance(subcomments, dict):
                    if '__lsub__' in comments:
                        _ = copy.deepcopy(comments['__lsub__'])
                        _.update(subcomments)
                        subcomments = _
                        if "__lsub__" in subcomments:
                            __ = copy.deepcopy(subcomments['__lsub__'])
                            __.update(subcomments)
                            _['__lsub__'] = __
                            subcomments = _
            else:
                subcomments = None
            this_value_strs = pformat_json(value, comments=subcomments, level=level+1, **subkwargs)
            valuestrs.append(this_value_strs)

        # get list_title
        if comments is not None:
            if isinstance(comments, dict) and '__ltitle__' in comments:
                list_title = comments['__ltitle__']
            elif isinstance(comments, str):
                list_title = comments
            else:
                list_title = ''
            if len(list_title):
                list_title_list = list_title.split('\n')
                for i,each in enumerate(list_title_list):
                    if i==0:
                        list_title_list[i] = f' {comment_prefix}{each}'
                    else:
                        list_title_list[i] = ' '*indent*level + f'  {comment_prefix}{each}'
                list_title = '\n'.join(list_title_list)
        else:
            list_title = ''

        # get compact option
        if comments is not None and isinstance(comments, dict):
            lcompact = comments.get('__lcompact__', compact)
        else:
            lcompact = compact
        assert lcompact is None or isinstance(lcompact, int)

        # prepare result list
        result_list = ['[' + list_title]
        line_groups = []
        current_group = []
        if comments is not None and isinstance(comments, dict) and '__lprefix__' in comments:
            for each in comments['__lprefix__']:
                result_list.append(' '*indent*(level+1) + f"{comment_prefix}{each}")

        for (key,value),rvalue in zip(enumerate(valuestrs), data):
            if '\n' in value: # process line_groups
                if len(current_group):
                    line_groups.append(current_group)
                current_group = []
            # normal one line object
            if comments is not None and isinstance(comments, dict):
                thiscomment = comments.get(key, '')
                if callable(thiscomment):
                    thecomment = thiscomment(key, data[key])
                    current_group.append([repr(key), value, f'{comment_prefix}{thecomment}'])
                elif len(thiscomment) and not isinstance(data[key], (dict, list, tuple)):
                    current_group.append([repr(key), value, f'{comment_prefix}{thiscomment}'])
                else:
                    current_group.append([repr(key), value, ''])
            else:
                current_group.append([repr(key), value, ''])
            if isinstance(rvalue, (dict, list, tuple)):
                current_group[-1].append('map')
            else:
                current_group[-1].append('')
        line_groups.append(current_group)

        # now we have several groups, do print for each group
        for current_group in line_groups:
            # calculate max length of valuestr
            alllens = [len(_[1]) for _ in current_group]
            maxlen = max(alllens) if len(alllens) else 0

            thisoneline = ''
            thisonelinecount = 0
            thisonelinecomment = ''
            for ic, (k,v,c,t) in enumerate(current_group):
                if lcompact is None or t == 'map': # no lcompact option
                    before_comment = ' '*indent*(level+1) + f'{v},'
                    if len(c):
                        extra_str = " " * (maxlen - len(v)+1)
                        for i,eachc in enumerate(c.split('\n')):
                            if i == 0:
                                thisline = before_comment + f'{extra_str}{eachc}'
                                result_list.append(thisline)
                            else:
                                thisline = ' ' * len(before_comment) + f'{extra_str}{comment_prefix}{eachc}'
                                result_list.append(thisline)
                    else:
                        thisline = before_comment
                        result_list.append(thisline)
                else: # line is compact, we put all comments at end
                    if indent*(level+1)>lcompact:
                        raise Exception(f'level too deep ({level+1}) and __lcompact__({lcompact}) is too small')
                    if thisonelinecount == 0:
                        this_line=' '*indent*(level+1) + f'{v},'
                    else:
                        this_line=f'{v},'

                    if len(this_line) + len(thisoneline)>lcompact: # print this oneline and put the current line as next oneline
                        # print before lines
                        if len(thisonelinecomment):
                            result_list.append(f'{thisoneline} {thisonelinecomment}')
                        else:
                            result_list.append(f'{thisoneline}')
                        # add current line as the first of this oneline
                        thisoneline = ' '*indent*(level+1) + f'{v},'
                        thisonelinecount = 1
                        if len(c):
                            if '\n' in c:
                                c = ' '.join(c.split('\n'))
                                # raise Exception('can not have multi-line comment in a compact format')
                            thisonelinecomment = f'{comment_prefix}{k}:{c[len(comment_prefix):]}'
                        else:
                            thisonelinecomment = ''
                    else: # concat lines
                        thisonelinecount += 1
                        if len(thisoneline):
                            thisoneline = thisoneline +' '+ this_line
                        else:
                            thisoneline = this_line
                        if len(c):
                            if '\n' in c:
                                c = ' '.join(c.split('\n'))
                                # raise Exception('can not have multi-line comment in a compact format')
                            if len(thisonelinecomment):
                                thisonelinecomment = thisonelinecomment + f' {comment_prefix}{k}:{c[len(comment_prefix):]}'
                            else:
                                thisonelinecomment = f'{comment_prefix}{k}:{c[len(comment_prefix):]}'
            if lcompact is not None and t != 'map': # do print last line:
                if len(thisonelinecomment):
                    result_list.append(f'{thisoneline} {thisonelinecomment}')
                else:
                    result_list.append(f'{thisoneline}')

        if comments is not None and isinstance(comments, dict) and '__lsuffix__' in comments:
            for each in comments['__lsuffix__']:
                result_list.append(' '*indent*(level+1) + f"{comment_prefix}{each}")
        result_list.append(' '*indent*level + ']')
        return '\n'.join(result_list)
    else:
        return repr(data)