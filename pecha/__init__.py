from pyPdf import pdf
from pyPdf.generic import ByteStringObject, TextStringObject
from pyPdf.pdf import ContentStream, PageObject


# Let's do some monkey-patching...
def getContent(self):
    return self["/Contents"].getObject()
PageObject.getContent = getContent

def getContentStream(self):
    content = self.getContent()
    if not isinstance(content, ContentStream):
        content = ContentStream(content, self.pdf)
    return content
PageObject.getContentStream = getContentStream

def isTextType(data):
    if isinstance(data, unicode):
        return True
    return False

def getAllText(self):
    text = u""
    content = self.getContentStream()
    import pdb;pdb.set_trace()
    legalOperators = ["Tm", "TJ", "Tf", "Tj", "Td", "TD", "T*", "'", '"']
    for operands, operator in content.operations:
        if operator == "Tj":
            _text = operands[0]
            if isTextType(_text):
                text += _text
        elif operator == "T*":
            text += "\n"
        elif operator == "'":
            text += "\n"
            _text = operands[0]
            if isTextType(_text):
                text += operands[0]
        elif operator == '"':
            _text = operands[2]
            if isTextType(_text):
                text += "\n"
                text += _text
        elif operator == "TJ":
            for i in operands[0]:
                if isTextType(i):
                    text += i
    return text
PageObject.getAllText = getAllText

pdf.PageObject = PageObject
