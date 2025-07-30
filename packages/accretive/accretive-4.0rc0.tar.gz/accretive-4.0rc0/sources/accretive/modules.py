# vim: set filetype=python fileencoding=utf-8:
# -*- coding: utf-8 -*-

#============================================================================#
#                                                                            #
#  Licensed under the Apache License, Version 2.0 (the "License");           #
#  you may not use this file except in compliance with the License.          #
#  You may obtain a copy of the License at                                   #
#                                                                            #
#      http://www.apache.org/licenses/LICENSE-2.0                            #
#                                                                            #
#  Unless required by applicable law or agreed to in writing, software       #
#  distributed under the License is distributed on an "AS IS" BASIS,         #
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  #
#  See the License for the specific language governing permissions and       #
#  limitations under the License.                                            #
#                                                                            #
#============================================================================#


''' Accretive modules.

    Provides a module type that enforces attribute immutability after
    assignment. This helps ensure that module-level constants remain constant
    and that module interfaces remain stable during runtime.

    The module implementation is derived from :py:class:`types.ModuleType` and
    adds accretive behavior. This makes it particularly useful for:

    * Ensuring constants remain constant
    * Preventing accidental modification of module interfaces

    Also provides a convenience function:

    * ``reclassify_modules``: Converts existing modules to accretive modules.
'''


from . import __
from . import iclasses as _iclasses


ModuleNamespaceDictionary: __.typx.TypeAlias = (
    __.cabc.Mapping[ str, __.typx.Any ] )

ReclassifyModulesModuleArgument: __.typx.TypeAlias = __.typx.Annotated[
    str | __.types.ModuleType | ModuleNamespaceDictionary,
    __.ddoc.Doc( ''' Module, module name, or module namespace. ''' ),
]
ReclassifyModulesRecursiveArgument: __.typx.TypeAlias = __.typx.Annotated[
    bool, __.ddoc.Doc( ''' Recursively reclassify package modules? ''' )
]


class Module(
    __.types.ModuleType,
    metaclass = _iclasses.Class,
    instances_assigner_core = _iclasses.assign_attribute_if_absent_mutable,
):
    ''' Accretive module. '''

    _dynadoc_fragments_ = ( 'module', 'module conceal', 'module accrete' )


def reclassify_modules(
    module: ReclassifyModulesModuleArgument, /, *,
    recursive: ReclassifyModulesRecursiveArgument = False,
) -> None:
    ''' Reclassifies modules to be accretive.

        Can operate on individual modules or entire package hierarchies.

        Only converts modules within the same package to prevent unintended
        modifications to external modules.

        When used with a dictionary, converts any module objects found as
        values if they belong to the same package.

        Has no effect on already-accretive modules.
    '''
    __.ccstd.reclassify_modules(
        module,
        attributes_namer = __.calculate_attrname,
        replacement_class = Module )
