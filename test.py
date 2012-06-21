import unittest
# 
# TODO
#
# 1. XSS in href, src [DONE]
# 2. SCRIPT_COMMENT VS HTML_TEXT
# 3. expression in CSS
# 4. CSS_DOUBLE_QUOTE
# 5. CSS_SINGLE_QUOTE
# 6. CSS_TEXT
# 7. CSS_COMMENT
#
html = '''
<html>
    <head>
        <style>
        
        </style>
        <script>
        var foo = '\\'SCRIPT_SINGLE_QUOTE';
        var foo2 = "SCRIPT_DOUBLE_QUOTE";
        SCRIPT_TEXT
        /*

        Some SCRIPT_MULTI_COMMENT  here

        */
        // Some SCRIPT_COMMENT  here
        </script>
    </head>
    <body>
        <h1 foo="ATTR_DOUBLE_QUOTE">HTML_TEXT</h1>
        <TAG>123</TAG>
        <b style="='" foo='fsdfs dfATTR_SINGLE_QUOTE'>dddd</b>
        ATTR_SINGLE_QUOTE
        <i ATTR_NAME="foo">ddd</i>
        <!--
        
        Some HTML_COMMENT here
        
        -->
        <img src="ATTR_DOUBLE_QUOTE" />
        <a href="ATTR_DOUBLE_QUOTE" />link</a>
    </body>
</html>
ATTR_SINGLE_QUOTE'''

class HtmlContext(object):
    name = ''

    def get_name(self):
        return self.name

    def is_match(self, data):
        raise 'is_match() should be implemented'

    def can_break(self, data):
        raise 'can_break() should be implemented'

class Tag(HtmlContext):

    def __init__(self):
        self.name = 'TAG'

    def is_match(self, data):
        if data[-1] == '<':
            return True
        return False

    def can_break(self, data):
        for i in [' ', '>']:
            if i in data:
                return True
        return False

class Text(HtmlContext):

    def __init__(self):
        self.name = 'HTML_TEXT'

    def is_match(self, data):
        if data.rfind('<') <= data.rfind('>'):
            return True
        return False

    def can_break(self, data):
        if "<" in data:
            return True
        return False

class Comment(HtmlContext):

    def __init__(self):
        self.name = 'HTML_COMMENT'

    def is_match(self, data):
        # We are inside <!--...
        if data.rfind('<!--') <= data.rfind('-->'):
            return False
        return True

    def can_break(self, data):
        for i in ['-', '>', '<']:
            if i not in data:
                return False
        return True

class AttrName(HtmlContext):

    def __init__(self):
        self.name = 'ATTR_NAME'

    def is_match(self, data):
        quote_character = None
        open_angle_bracket = data.rfind('<')
        # We are inside <...
        if open_angle_bracket <= data.rfind('>'):
            return False
        # We are not inside <!--...
        if data.rfind('<!--') > data.rfind('-->'):
            return False
        for s in data[open_angle_bracket+1:]:
            if s in ['"', "'"]:
                if quote_character and s == quote_character:
                    quote_character = None
                    continue
                elif not quote_character:
                    quote_character = s
                    continue
        if not quote_character and len(data[open_angle_bracket+1:]):
            return True
        return False

    def can_break(self, data):
        if "=" in data:
            return True
        return False

class ScriptMultiComment(HtmlContext):

    def __init__(self):
        self.name = 'SCRIPT_MULTI_COMMENT'

    def is_match(self, data):
        # We are inside <script...
        if data.rfind('<script') <= data.rfind('</script>'):
            return False
        # We are inside /*...
        if data.rfind('/*') <= data.rfind('*/'):
            return False
        return True

    def can_break(self, data):
        for i in ['/', '*']:
            if i not in data:
                return False
        return True

class ScriptLineComment(HtmlContext):

    def __init__(self):
        self.name = 'SCRIPT_LINE_COMMENT'

    def is_match(self, data):
        last_line = data.split('\n')[-1]
        if last_line.find('//') == 0:
            return True
        return False

    def can_break(self, data):
        for i in ['\n']:
            if i not in data:
                return False
        return True

class ScriptQuote(HtmlContext):

    def __init__(self):
        self.name = None
        self.quote_character = None

    def is_match(self, data):
        data = data.replace('\\"','')
        data = data.replace("\\'",'')
        quote_character = None
        open_angle_bracket = data.rfind('<script')
        # We are inside <...
        if open_angle_bracket <= data.rfind('</script>'):
            return False
        for s in data[open_angle_bracket+1:]:
            if s in ['"', "'"]:
                if quote_character and s == quote_character:
                    quote_character = None
                    continue
                elif not quote_character:
                    quote_character = s
                    continue
        if quote_character == self.quote_character:
            return True
        return False

    def can_break(self, data):
        if self.quote_character in data:
            return True
        return False

class ScriptSingleQuote(ScriptQuote):

    def __init__(self):
        self.name = 'SCRIPT_SINGLE_QUOTE'
        self.quote_character = "'"

class ScriptDoubleQuote(ScriptQuote):

    def __init__(self):
        self.name = 'SCRIPT_DOUBLE_QUOTE'
        self.quote_character = '"'

class AttrQuote(HtmlContext):

    def __init__(self):
        self.name = None
        self.quote_character = None

    def is_match(self, data):
        quote_character = None
        open_angle_bracket = data.rfind('<')
        # We are inside <...
        if open_angle_bracket <= data.rfind('>'):
            return False
        for s in data[open_angle_bracket+1:]:
            if s in ['"', "'"]:
                if quote_character and s == quote_character:
                    quote_character = None
                    continue
                elif not quote_character:
                    quote_character = s
                    continue
        if quote_character == self.quote_character:
            return True
        return False

    def can_break(self, data):
        if self.quote_character in data:
            return True
        # 
        # For cases with src and href + javascript scheme
        #
        data = data.replace(' ', '')
        if data.endswith('href=' + self.quote_character):
            return True
        if data.endswith('src=' + self.quote_character):
            return True
        return False

class AttrSingleQuote(AttrQuote):

    def __init__(self):
        self.name = 'ATTR_SINGLE_QUOTE'
        self.quote_character = "'"

class AttrDoubleQuote(AttrQuote):

    def __init__(self):
        self.name = 'ATTR_DOUBLE_QUOTE'
        self.quote_character = '"'

AVAILABLE_CONTEXTS = []
AVAILABLE_CONTEXTS.append(AttrSingleQuote())
AVAILABLE_CONTEXTS.append(AttrDoubleQuote())
AVAILABLE_CONTEXTS.append(AttrName())
AVAILABLE_CONTEXTS.append(Tag())
AVAILABLE_CONTEXTS.append(Text())
AVAILABLE_CONTEXTS.append(Comment())
AVAILABLE_CONTEXTS.append(ScriptMultiComment())
AVAILABLE_CONTEXTS.append(ScriptLineComment())
AVAILABLE_CONTEXTS.append(ScriptSingleQuote())
AVAILABLE_CONTEXTS.append(ScriptDoubleQuote())

def get_context(data, payload):
    '''
    return list of tuples (<context>, index)
    '''
    chunks = data.split(payload)
    tmp = ''
    result = []
    counter = 0

    if len(chunks) == 1:
        raise Exception('Empty results')

    for chunk in chunks[:-1]:
        tmp += chunk
        for context in AVAILABLE_CONTEXTS:
            if context.is_match(tmp):
                result.append((context, counter))
        counter += 1
    return result

class TestContexts(unittest.TestCase):

    def test_all(self):
        for context in AVAILABLE_CONTEXTS:
            self.assertEqual(
                    get_context(html, context.get_name())[0][0].get_name(), 
                    context.get_name()
                    )

if __name__ == '__main__':
    unittest.main()
