from .....parser import parser_manager as ParserManager
from .....parser.plot.v0_0_0 import Parser as BaseParser
from ...plot import Plot

# No difference with the parent class Plot, so we just add the reference to the ParserManager
ParserManager.register(Plot, BaseParser.version, BaseParser())
