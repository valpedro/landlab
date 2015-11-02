"""
This script introspects the contents of the LL components folder.

It has two aims.
Firstly, to create dynamic dictionaries of "problematic components" and
"bad components". The former is any component with a partially declared
by incomplete LL standard interface:
    _name (str)
    _input_var_names (set)
    _output_var_names (set)
    _var_units (dict, name: unit)
    _var_mapping (dict, name: centering)
    _var_doc (dict, name: description)

The latter is any file in 'components' which contains a class, but either
inherits from Component but lacks any interface at all (always wrong), or
lacks an interface and does not inherit from the LL base Component class.
Note the latter will catch any non-component class in the folder which *isn't
meant* to be a LL component! Files which aren't meant to have a LL component
class inside them can be declared as exceptions by adding to the
'file_exceptions' tuple below.

comp_elements is a dict of dict of dicts/sets, where the value at the end
is the dict or set produced by that component property. The first key is the
_name property for that component. i.e., it looks like
    comp_elements[_name][_input_var_names] = set(*field_names*)

Note that if no _name is provided, but other components are, no entry will be
recorded in comp_elements; the component will only appear under
problematic_components.

problematic_components is a dict. The keys are the filenames. The values are
a list of strings describing the format problem(s) with the component
standardization.

bad_components is a dict. The keys are again the filenames. The values are one
of two strings: 'Component lacks std interface', or 'No class in file inherits
from Component'.

This file goes on to build a set of all field names used in named LL
components, called 'all_field_names'. (If a component doesn't have a _name,
its fields won't be included.)
"""

import os.path as path
from os import walk
import fnmatch
import glob
import landlab.components as comp
import dircache
import pkgutil
from copy import copy

abspath = path.abspath(comp.__path__[0])
poss_comp_files = []
for root, dirnames, filenames in walk(abspath):
    for filename in fnmatch.filter(filenames, '*.py'):
        poss_comp_files.append(path.join(root, filename))

props_to_strip_list = [' _name',
                       ' _input_var_names',
                       ' _output_var_names',
                       ' _var_units',
                       ' _var_mapping',
                       ' _var_doc']  # must be in order for first loop

props_to_strip = set(props_to_strip_list)

poss_elements = ['node', 'link', 'cell', 'junction', 'patch', 'corner', 'face']

file_exceptions = ()

comp_elements = {}
problematic_components = {}  # components lacking all the info, but with some
bad_components = {}  # any class in the components folder w/o any interface

last_name = None
total_props = len(props_to_strip)

for LLcomp in poss_comp_files:
    # print LLcomp
    found_a_name = False
    accumulated_props = set()
    for prop in props_to_strip_list:
        lines_captured = []
        start_write = False
        with open(LLcomp, 'r') as inFile:
            for line in inFile:
                if prop in line:
                    accumulated_props.add(prop)
                    start_write = True
                    if prop != ' _name':
                        assert ('{' in line) or ('[' in line)
                    else:
                        found_a_name = True
                if start_write:
                    # first, check there's no comments here
                    nocomment = line.partition('#')[0]
                    nowhite = nocomment.rstrip()
                    nowhite = nowhite.lstrip()
                    no_nl = nowhite.replace('\\', '')
                    lines_captured.append(str(no_nl))
                    if ('}' in line) or (']' in line) or (prop == ' _name'):
                        break
        cat_lines = ''
        for expr in lines_captured:
            cat_lines += expr
        # cat_lines = cat_lines.replace(" ", "")
        if cat_lines and found_a_name:
            # print('EXEC: ', LLcomp)
            exec(cat_lines)  # eval(prop) is now an obj
            if prop is ' _name':
                last_name = eval(prop.lstrip())
                comp_elements[eval(prop.lstrip())] = {}
            else:
                comp_elements[last_name][prop.lstrip()] = copy(
                                                           eval(prop.lstrip()))
    if (len(accumulated_props) != total_props):
        if len(accumulated_props) > 0:
            problematic_components[LLcomp] = props_to_strip - accumulated_props
        else:
            bad_components[LLcomp] = 'No class is present in file.'

for badcomp in bad_components.keys():
    with open(badcomp, 'r') as inFile:
        noclass = True
        for line in inFile:
            if 'class ' in line:
                noclass = False
                if '(Component)' in line:
                    bad_components[badcomp] = 'Component lacks std interface'
                    break
                elif ('(object)' in line):
                    bad_components[badcomp] = 'No class in file inherits ' + \
                                              'from Component'
    excpt = False
    for fname in file_exceptions:
        if not fnmatch.fnmatch(fname, '*.py'):
            fname = fname + '.py'
        excpt = excpt or fnmatch.fnmatch(badcomp, '*'+fname)
    if noclass or excpt:
        # There was no class in the file; can't be a LL component
        bad_components.pop(badcomp)

# build the field name set:
all_field_names = set()
for name in comp_elements.keys():
    this_un = comp_elements[name]
    try:
        all_field_names = all_field_names | this_un['_input_var_names']
    except (TypeError, KeyError):
        pass  # this will get captured in problematic_components
    try:
        all_field_names = all_field_names | this_un['_output_var_names']
    except (TypeError, KeyError):
        pass  # ditto

for name in comp_elements.keys():
    problems = []
    all_fields_here = set()
    this_un = comp_elements[name]
    try:
        all_fields_here = all_fields_here | this_un['_input_var_names']
    except (TypeError, KeyError):
        all_fields_here = set()
    try:
        all_fields_here = all_fields_here | this_un['_output_var_names']
    except (TypeError, KeyError):
        all_fields_here = set()
    if type(name) != str:
        problems.append('The _name '+str(name)+' is not a string.')
    for prop in this_un:
        if prop in ('_input_var_names', '_output_var_names'):
            if type(this_un[prop]) != set:
                problems.append(prop+' is not a set. It should be.')
        if prop in ('_var_units', '_var_mapping', '_var_doc'):
            if type(this_un[prop]) != dict:
                problems.append(prop+' is not a dict. It should be.')
            elif (all_fields_here and not
                    set(this_un[prop].keys()).issubset(all_fields_here)):
                problems.append('Keys in '+prop+' are not the same as those ' +
                                'defined in _input/_output_var_names')
            else:
                if prop is '_var_mapping':
                    for element in this_un[prop].values():
                        if not (element in poss_elements):
                            problems.append(str(element)+" is not a " +
                                            "recognised element type " +
                                            "('node', 'link', etc).")
                else:
                    if any(type(x) is not str for x in this_un[prop].values()):
                        problems.append('One or more values in the dict ' +
                                        prop+' is not a string.')
    try:
        badstdnames = problematic_components[name]  # a set, if exists
    except KeyError:  # no missing fields
        problematic_components[name] = problems
    else:
        problems.append('The following LL standard interface properties are ' +
                        'not defined: '+str(badstdnames))
    finally:
        if problems:
            problematic_components[name] = copy(problems)

# final formatting change to problematic_components:
for (key, vals) in problematic_components.items():
    if len(vals) == 0:
        problematic_components.pop(key)
    elif type(vals) is dict:
        problematic_components[key] = ('The following LL standard interface properties are ' +
                'not defined: ' + str(vals))
