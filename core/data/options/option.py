'''
option.py

Copyright 2008 Andres Riancho

This file is part of w3af, w3af.sourceforge.net .

w3af is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation version 2 of the License.

w3af is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with w3af; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

'''

import copy
import cgi
import re

from core.controllers.w3afException import w3afException
from core.data.parsers.urlParser import parse_qs, url_object


class option:
    '''
    This class represents an option.
    
    @author: Andres Riancho ( andres.riancho@gmail.com )
    '''
    BOOL = 'boolean'
    INT = 'integer'
    FLOAT = 'float'
    STRING = 'string'
    URL = 'url'
    IPPORT = 'ipport'
    LIST = 'list'
    REGEX = 'regex'
    
    def __init__(self, name, defaultValue, desc, type, help='', tabid=''):
        '''
        @parameter name: The name of the option
        @parameter defaultValue: The default value of the option
        @parameter desc: The description of the option
        @parameter type: boolean, integer, string, etc..
        @parameter help: The help of the option; a large description of the option
        @parameter tabid: The tab id of the option
        '''
        self._name = name
        self._value = self._defaultValue = defaultValue
        self._desc = desc
        self._type = type
        self._help = help
        self._tabid = tabid
    
    def getName( self ): return self._name
    def getDesc( self ): return self._desc

    def getDefaultValue( self ):
        '''
        @return: The object, as it was set using setDefaultValue / setValue 
                 or the __init__
        '''
        return self._defaultValue
    
    def getValue( self ): return self._value

    # And the string versions of the above methods...
    def _getStr(self, value):
        if isinstance(value,type([])):
            return ','.join( [ str(i) for i in value] )
        else:
            return str(value)

    def getDefaultValueStr( self ): return self._getStr(self._defaultValue)
    def getValueStr( self ): return self._getStr(self._value)
    
    def getType( self ): return self._type
    def getHelp( self ): return self._help
    def getTabId( self ): return self._tabid
    
    def setName( self, v ): self._name = v
    def setDesc( self, v ): self._desc = v
    def setDefaultValue( self, v ): self._defaultValue = v

    def setValue( self, value ):
        '''
        @parameter value: The value parameter is set by the user interface, which
        for example sends 'True' or 'a,b,c'

        Based on the value parameter and the option type, I have to create a nice
        looking object like True or ['a','b','c']. This replaces the *old* parseOptions.
        '''
        try:
            if self._type == 'integer':
                res = int(value)
            elif self._type == 'float':
                res = float(value)
            elif self._type == 'boolean':
                if value.lower() == 'true':
                    res = True
                else:
                    res = False
            elif self._type == 'list':
                res = []
                # Yes, we are regex dummies
                value += ','
                tmp = re.findall('(".*?"|\'.*?\'|.*?),', value, re.U)
                if tmp:
                    tmp = [y.strip() for y in tmp if y != '']
                    
                    # Now I check for single and double quotes
                    for u in tmp:
                        if ( u.startswith('"') and u.endswith('"') ) or \
                           ( u.startswith("'") and u.endswith("'") ):
                            res.append( u[1:-1] )
                        else:
                            res.append( u )

                else:
                    raise ValueError
            elif self._type in ('string', 'ipport'):
                res = str(value)
            elif self._type == 'url':
                try:
                    res = url_object(value)
                except Exception, e:
                    msg = str(e)
                    raise w3afException( msg )
            elif self._type == 'regex':
                # Parse regex stuff...
                try:
                    re.compile(value)
                except:
                    msg = 'The regular expression "%s" is invalid!' % value
                    raise w3afException( msg )
                else:
                    res = value
                # end regex stuff
                
            else:
                raise w3afException('Unknown type: ' + self._type)
        except ValueError:
            msg = 'The value "%s" cannot be casted to "%s".' % (value, self._type)
            raise w3afException( msg )
        else:
            self._value = res

    def setType( self, v ): self._type = v
    def setHelp( self, v ): self._help = v
    def setTabId( self, v ): self._tabid = v
    
    def _sanitize( self, value ):
        '''
        Encode some values that can't be used in XML
        '''
        # FIXME: Not 100% sure about this...
        # I should also kill the \a and other strange escapes...
        # Maybe there is already a function that does this!
        value = cgi.escape(value)
        value = value.replace('"', '&quot;')
        return value
        
    def __repr__(self):
        '''
        A nice way of printing your object =)        
        '''
        fmt = '<option name:%s|type:%s|value:%s>'
        return fmt % (self._name, self._type, self._value)
    
    def __eq__(self, other):
        if not isinstance(other, option):
            return False
        
        name = self._name == other._name
        type = self._type == other._type
        value = self._value == other._value
        return name and type and value 
        
    def copy(self):
        '''
        This method returns a copy of the option Object.
        
        @return: A copy of myself.
        '''
        return copy.deepcopy( self )
        
