from .....parser import parser_manager as ParserManager
from ....image_metadata.parser.image.v1_0_0 import Parser as BaseParser
from ...mspec_image import MSpecImage

# No difference with the parent class Image, so we just add the reference to the ParserManager
ParserManager.register(MSpecImage, BaseParser.version, BaseParser())
