# Copyright (C) 2015 Lukas Rist
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

import random

from . import functions


FUNCTIONS = functions.FUNCTIONS
WHITELIST = functions.WHITELIST

print("<?php\n//Generated by Glastopf sandbox.generate.py\n")
print("if(!extension_loaded('bfr')) {\n\tdl('bfr.so');\n}\n")
print("error_reporting(0);\n")

print("$functions = get_defined_functions();")
print("$functions = $functions['internal'];")

print("$whitelist = array(")
for i, function in enumerate(WHITELIST):
    print(('\t\t%s => "%s",' % (i, function)))
print(");")

print("$functions = array_diff($functions, $whitelist);\n")

print("foreach ($functions as $function){")
print("\t$rand_int = rand(100,999);")
print("\trename_function($function, $function.'_'.$rand_int);")
print("}\n")

seed_int = 0
for function, return_val in list(FUNCTIONS.items()):
    parts = function.split(";")
    function_name = parts[0]
    function_args = ", ".join(parts[1:-1])
    rand_int = random.randint(100, 999)
    print(
        (
            "override_function('%s', '%s', 'return %s_rep(%s);');"
            % (function_name, function_args, function_name, function_args)
        )
    )
    print(("function %s_rep(%s) {" % (function_name, function_args)))
    if return_val == "None":
        return_val = "\treturn;"
    print(return_val)
    # print("\terror_log(\"ret:%s(\" . join(', ', $args) . \")= \" . $result);" % function_name)
    print("}")
    print(("rename_function('__overridden__', '%s');\n" % seed_int))
    seed_int += 1

print("\ninclude $argv[1];\n?>")
