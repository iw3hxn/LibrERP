# flake8: noqa
# -*- coding: utf-8 -*-
# ./dati_fattura_v_2_0.py
# PyXB bindings for NM:c8403c44c9a54a32bd3b5aec75a6504db99822c4
# Generated 2017-10-03 10:08:19.850035 by PyXB version 1.2.4 using Python 2.7.5.final.0
# by Antonio Maria Vigliotti <antoniomaria.vigliotti@gmail.com>
# Namespace http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v2.0
from __future__ import unicode_literals
import logging
import io
import sys
_logger = logging.getLogger(__name__)
try:
    import pyxb
    import pyxb.binding
    import pyxb.binding.saxer
    import pyxb.utils.utility
    import pyxb.utils.domutils
    import pyxb.utils.six as _six
except ImportError as err:
    _logger.debug(err)

# Unique identifier for bindings created at the same time
_GenerationUID = pyxb.utils.utility.UniqueIdentifier(
    'urn:uuid:faf43498-a811-11e7-95f5-005056ba06a2')

# Version of PyXB used to generate the bindings
_PyXBVersion = '1.2.4'
# Generated bindings are not compatible across PyXB versions
if pyxb.__version__ != _PyXBVersion:
    raise pyxb.PyXBVersionError(_PyXBVersion)

# Import bindings for namespaces imported into schema
from . import _ds as _ImportedBinding__ds
try:
    import pyxb.binding.datatypes
except ImportError as err:
    _logger.debug(err)

# NOTE: All namespace declarations are reserved within the binding
Namespace = pyxb.namespace.NamespaceForURI(
    'http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v2.0', create_if_missing=True)
Namespace.configureCategories(['typeBinding', 'elementBinding'])
_Namespace_ds = _ImportedBinding__ds.Namespace
_Namespace_ds.configureCategories(['typeBinding', 'elementBinding'])


def CreateFromDocument(xml_text, default_namespace=None, location_base=None):
    """Parse the given XML and use the document element to create a
    Python instance.

    @param xml_text An XML document.  This should be data (Python 2
    str or Python 3 bytes), or a text (Python 2 unicode or Python 3
    str) in the L{pyxb._InputEncoding} encoding.

    @keyword default_namespace The L{pyxb.Namespace} instance to use as the
    default namespace where there is no default namespace in scope.
    If unspecified or C{None}, the namespace of the module containing
    this function will be used.

    @keyword location_base: An object to be recorded as the base of all
    L{pyxb.utils.utility.Location} instances associated with events and
    objects handled by the parser.  You might pass the URI from which
    the document was obtained.
    """

    if pyxb.XMLStyle_saxer != pyxb._XMLStyle:
        dom = pyxb.utils.domutils.StringToDOM(xml_text)
        return CreateFromDOM(dom.documentElement, default_namespace=default_namespace)
    if default_namespace is None:
        default_namespace = Namespace.fallbackNamespace()
    saxer = pyxb.binding.saxer.make_parser(
        fallback_namespace=default_namespace, location_base=location_base)
    handler = saxer.getContentHandler()
    xmld = xml_text
    if isinstance(xmld, _six.text_type):
        xmld = xmld.encode(pyxb._InputEncoding)
    saxer.parse(io.BytesIO(xmld))
    instance = handler.rootObject()
    return instance


def CreateFromDOM(node, default_namespace=None):
    """Create a Python instance from the given DOM node.
    The node tag must correspond to an element declaration in this module.

    @deprecated: Forcing use of DOM interface is unnecessary; use L{CreateFromDocument}."""
    if default_namespace is None:
        default_namespace = Namespace.fallbackNamespace()
    return pyxb.binding.basis.element.AnyCreateFromDOM(node, default_namespace)


# Atomic simple type:
# {http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v2.0}CodiceFiscaleType
class CodiceFiscaleType (pyxb.binding.datatypes.string):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'CodiceFiscaleType')
    _XSDLocation = pyxb.utils.utility.Location(
        '../data/datifatture/DatiFatturav2.0.xsd', 291, 2)
    _Documentation = None


CodiceFiscaleType._CF_pattern = pyxb.binding.facets.CF_pattern()
CodiceFiscaleType._CF_pattern.addPattern(pattern='[A-Z0-9]{8,16}')
CodiceFiscaleType._InitializeFacetMap(CodiceFiscaleType._CF_pattern)
Namespace.addCategoryObject(
    'typeBinding', 'CodiceFiscaleType', CodiceFiscaleType)

# Atomic simple type:
# {http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v2.0}NazioneType


class NazioneType (pyxb.binding.datatypes.string):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'NazioneType')
    _XSDLocation = pyxb.utils.utility.Location(
        '../data/datifatture/DatiFatturav2.0.xsd', 297, 2)
    _Documentation = None


NazioneType._CF_pattern = pyxb.binding.facets.CF_pattern()
NazioneType._CF_pattern.addPattern(pattern='[A-Z]{2}')
NazioneType._InitializeFacetMap(NazioneType._CF_pattern)
Namespace.addCategoryObject('typeBinding', 'NazioneType', NazioneType)

# Atomic simple type:
# {http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v2.0}NazioneITType


class NazioneITType (pyxb.binding.datatypes.string, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'NazioneITType')
    _XSDLocation = pyxb.utils.utility.Location(
        '../data/datifatture/DatiFatturav2.0.xsd', 303, 2)
    _Documentation = None


NazioneITType._CF_enumeration = pyxb.binding.facets.CF_enumeration(
    value_datatype=NazioneITType, enum_prefix=None)
NazioneITType.IT = NazioneITType._CF_enumeration.addEnumeration(
    unicode_value='IT', tag='IT')
NazioneITType._CF_length = pyxb.binding.facets.CF_length(
    value=pyxb.binding.datatypes.nonNegativeInteger(2))
NazioneITType._InitializeFacetMap(NazioneITType._CF_enumeration,
                                  NazioneITType._CF_length)
Namespace.addCategoryObject('typeBinding', 'NazioneITType', NazioneITType)

# Atomic simple type:
# {http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v2.0}CodiceType


class CodiceType (pyxb.binding.datatypes.string):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'CodiceType')
    _XSDLocation = pyxb.utils.utility.Location(
        '../data/datifatture/DatiFatturav2.0.xsd', 312, 2)
    _Documentation = None


CodiceType._CF_maxLength = pyxb.binding.facets.CF_maxLength(
    value=pyxb.binding.datatypes.nonNegativeInteger(28))
CodiceType._CF_minLength = pyxb.binding.facets.CF_minLength(
    value=pyxb.binding.datatypes.nonNegativeInteger(1))
CodiceType._InitializeFacetMap(CodiceType._CF_maxLength,
                               CodiceType._CF_minLength)
Namespace.addCategoryObject('typeBinding', 'CodiceType', CodiceType)

# Atomic simple type:
# {http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v2.0}CodiceIvaType


class CodiceIvaType (pyxb.binding.datatypes.string):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'CodiceIvaType')
    _XSDLocation = pyxb.utils.utility.Location(
        '../data/datifatture/DatiFatturav2.0.xsd', 319, 2)
    _Documentation = None


CodiceIvaType._CF_maxLength = pyxb.binding.facets.CF_maxLength(
    value=pyxb.binding.datatypes.nonNegativeInteger(11))
CodiceIvaType._CF_minLength = pyxb.binding.facets.CF_minLength(
    value=pyxb.binding.datatypes.nonNegativeInteger(1))
CodiceIvaType._InitializeFacetMap(CodiceIvaType._CF_maxLength,
                                  CodiceIvaType._CF_minLength)
Namespace.addCategoryObject('typeBinding', 'CodiceIvaType', CodiceIvaType)

# Atomic simple type:
# {http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v2.0}NumeroCivicoType


class NumeroCivicoType (pyxb.binding.datatypes.normalizedString):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'NumeroCivicoType')
    _XSDLocation = pyxb.utils.utility.Location(
        '../data/datifatture/DatiFatturav2.0.xsd', 326, 2)
    _Documentation = None


NumeroCivicoType._CF_pattern = pyxb.binding.facets.CF_pattern()
NumeroCivicoType._CF_pattern.addPattern(pattern='(\\p{IsBasicLatin}{1,8})')
NumeroCivicoType._InitializeFacetMap(NumeroCivicoType._CF_pattern)
Namespace.addCategoryObject(
    'typeBinding', 'NumeroCivicoType', NumeroCivicoType)

# Atomic simple type:
# {http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v2.0}CAPType


class CAPType (pyxb.binding.datatypes.string):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'CAPType')
    _XSDLocation = pyxb.utils.utility.Location(
        '../data/datifatture/DatiFatturav2.0.xsd', 332, 2)
    _Documentation = None


CAPType._CF_pattern = pyxb.binding.facets.CF_pattern()
CAPType._CF_pattern.addPattern(pattern='[0-9][0-9][0-9][0-9][0-9]')
CAPType._InitializeFacetMap(CAPType._CF_pattern)
Namespace.addCategoryObject('typeBinding', 'CAPType', CAPType)

# Atomic simple type:
# {http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v2.0}ProvinciaType


class ProvinciaType (pyxb.binding.datatypes.string):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'ProvinciaType')
    _XSDLocation = pyxb.utils.utility.Location(
        '../data/datifatture/DatiFatturav2.0.xsd', 338, 2)
    _Documentation = None


ProvinciaType._CF_pattern = pyxb.binding.facets.CF_pattern()
ProvinciaType._CF_pattern.addPattern(pattern='[A-Z]{2}')
ProvinciaType._InitializeFacetMap(ProvinciaType._CF_pattern)
Namespace.addCategoryObject('typeBinding', 'ProvinciaType', ProvinciaType)

# Atomic simple type:
# {http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v2.0}TipoDocumentoType


class TipoDocumentoType (pyxb.binding.datatypes.string, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'TipoDocumentoType')
    _XSDLocation = pyxb.utils.utility.Location(
        '../data/datifatture/DatiFatturav2.0.xsd', 344, 2)
    _Documentation = None


TipoDocumentoType._CF_enumeration = pyxb.binding.facets.CF_enumeration(
    value_datatype=TipoDocumentoType, enum_prefix=None)
TipoDocumentoType.TD01 = TipoDocumentoType._CF_enumeration.addEnumeration(
    unicode_value='TD01', tag='TD01')
TipoDocumentoType.TD04 = TipoDocumentoType._CF_enumeration.addEnumeration(
    unicode_value='TD04', tag='TD04')
TipoDocumentoType.TD05 = TipoDocumentoType._CF_enumeration.addEnumeration(
    unicode_value='TD05', tag='TD05')
TipoDocumentoType.TD07 = TipoDocumentoType._CF_enumeration.addEnumeration(
    unicode_value='TD07', tag='TD07')
TipoDocumentoType.TD08 = TipoDocumentoType._CF_enumeration.addEnumeration(
    unicode_value='TD08', tag='TD08')
TipoDocumentoType.TD10 = TipoDocumentoType._CF_enumeration.addEnumeration(
    unicode_value='TD10', tag='TD10')
TipoDocumentoType.TD11 = TipoDocumentoType._CF_enumeration.addEnumeration(
    unicode_value='TD11', tag='TD11')
TipoDocumentoType._CF_length = pyxb.binding.facets.CF_length(
    value=pyxb.binding.datatypes.nonNegativeInteger(4))
TipoDocumentoType._InitializeFacetMap(TipoDocumentoType._CF_enumeration,
                                      TipoDocumentoType._CF_length)
Namespace.addCategoryObject(
    'typeBinding', 'TipoDocumentoType', TipoDocumentoType)

# Atomic simple type:
# {http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v2.0}DataFatturaType


class DataFatturaType (pyxb.binding.datatypes.date):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'DataFatturaType')
    _XSDLocation = pyxb.utils.utility.Location(
        '../data/datifatture/DatiFatturav2.0.xsd', 371, 2)
    _Documentation = None


DataFatturaType._CF_minInclusive = pyxb.binding.facets.CF_minInclusive(
    value_datatype=DataFatturaType, value=pyxb.binding.datatypes.date('1970-01-01'))
DataFatturaType._InitializeFacetMap(DataFatturaType._CF_minInclusive)
Namespace.addCategoryObject('typeBinding', 'DataFatturaType', DataFatturaType)

# Atomic simple type:
# {http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v2.0}PosizioneType


class PosizioneType (pyxb.binding.datatypes.integer):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'PosizioneType')
    _XSDLocation = pyxb.utils.utility.Location(
        '../data/datifatture/DatiFatturav2.0.xsd', 377, 2)
    _Documentation = None


PosizioneType._CF_maxInclusive = pyxb.binding.facets.CF_maxInclusive(
    value_datatype=PosizioneType, value=pyxb.binding.datatypes.integer(9999999))
PosizioneType._CF_minInclusive = pyxb.binding.facets.CF_minInclusive(
    value_datatype=PosizioneType, value=pyxb.binding.datatypes.integer(1))
PosizioneType._InitializeFacetMap(PosizioneType._CF_maxInclusive,
                                  PosizioneType._CF_minInclusive)
Namespace.addCategoryObject('typeBinding', 'PosizioneType', PosizioneType)

# Atomic simple type:
# {http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v2.0}CaricaType


class CaricaType (pyxb.binding.datatypes.integer):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'CaricaType')
    _XSDLocation = pyxb.utils.utility.Location(
        '../data/datifatture/DatiFatturav2.0.xsd', 384, 2)
    _Documentation = None


CaricaType._CF_maxInclusive = pyxb.binding.facets.CF_maxInclusive(
    value_datatype=CaricaType, value=pyxb.binding.datatypes.integer(15))
CaricaType._CF_minInclusive = pyxb.binding.facets.CF_minInclusive(
    value_datatype=CaricaType, value=pyxb.binding.datatypes.integer(1))
CaricaType._InitializeFacetMap(CaricaType._CF_maxInclusive,
                               CaricaType._CF_minInclusive)
Namespace.addCategoryObject('typeBinding', 'CaricaType', CaricaType)

# Atomic simple type:
# {http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v2.0}String10Type


class String10Type (pyxb.binding.datatypes.normalizedString):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'String10Type')
    _XSDLocation = pyxb.utils.utility.Location(
        '../data/datifatture/DatiFatturav2.0.xsd', 392, 2)
    _Documentation = None


String10Type._CF_pattern = pyxb.binding.facets.CF_pattern()
String10Type._CF_pattern.addPattern(pattern='(\\p{IsBasicLatin}{1,10})')
String10Type._InitializeFacetMap(String10Type._CF_pattern)
Namespace.addCategoryObject('typeBinding', 'String10Type', String10Type)

# Atomic simple type:
# {http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v2.0}String18Type


class String18Type (pyxb.binding.datatypes.normalizedString):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'String18Type')
    _XSDLocation = pyxb.utils.utility.Location(
        '../data/datifatture/DatiFatturav2.0.xsd', 398, 2)
    _Documentation = None


String18Type._CF_pattern = pyxb.binding.facets.CF_pattern()
String18Type._CF_pattern.addPattern(pattern='(\\p{IsBasicLatin}{1,18})')
String18Type._InitializeFacetMap(String18Type._CF_pattern)
Namespace.addCategoryObject('typeBinding', 'String18Type', String18Type)

# Atomic simple type:
# {http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v2.0}String20Type


class String20Type (pyxb.binding.datatypes.normalizedString):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'String20Type')
    _XSDLocation = pyxb.utils.utility.Location(
        '../data/datifatture/DatiFatturav2.0.xsd', 404, 2)
    _Documentation = None


String20Type._CF_pattern = pyxb.binding.facets.CF_pattern()
String20Type._CF_pattern.addPattern(pattern='(\\p{IsBasicLatin}{1,20})')
String20Type._InitializeFacetMap(String20Type._CF_pattern)
Namespace.addCategoryObject('typeBinding', 'String20Type', String20Type)

# Atomic simple type:
# {http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v2.0}String60LatinType


class String60LatinType (pyxb.binding.datatypes.normalizedString):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'String60LatinType')
    _XSDLocation = pyxb.utils.utility.Location(
        '../data/datifatture/DatiFatturav2.0.xsd', 410, 2)
    _Documentation = None


String60LatinType._CF_pattern = pyxb.binding.facets.CF_pattern()
String60LatinType._CF_pattern.addPattern(
    pattern='[\\p{IsBasicLatin}\\p{IsLatin-1Supplement}]{1,60}')
String60LatinType._InitializeFacetMap(String60LatinType._CF_pattern)
Namespace.addCategoryObject(
    'typeBinding', 'String60LatinType', String60LatinType)

# Atomic simple type:
# {http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v2.0}String80LatinType


class String80LatinType (pyxb.binding.datatypes.normalizedString):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'String80LatinType')
    _XSDLocation = pyxb.utils.utility.Location(
        '../data/datifatture/DatiFatturav2.0.xsd', 416, 2)
    _Documentation = None


String80LatinType._CF_pattern = pyxb.binding.facets.CF_pattern()
String80LatinType._CF_pattern.addPattern(
    pattern='[\\p{IsBasicLatin}\\p{IsLatin-1Supplement}]{1,80}')
String80LatinType._InitializeFacetMap(String80LatinType._CF_pattern)
Namespace.addCategoryObject(
    'typeBinding', 'String80LatinType', String80LatinType)

# Atomic simple type:
# {http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v2.0}VersioneType


class VersioneType (pyxb.binding.datatypes.string, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'VersioneType')
    _XSDLocation = pyxb.utils.utility.Location(
        '../data/datifatture/DatiFatturav2.0.xsd', 422, 2)
    _Documentation = None


VersioneType._CF_enumeration = pyxb.binding.facets.CF_enumeration(
    value_datatype=VersioneType, enum_prefix=None)
VersioneType.DAT20 = VersioneType._CF_enumeration.addEnumeration(
    unicode_value='DAT20', tag='DAT20')
VersioneType._CF_length = pyxb.binding.facets.CF_length(
    value=pyxb.binding.datatypes.nonNegativeInteger(5))
VersioneType._InitializeFacetMap(VersioneType._CF_enumeration,
                                 VersioneType._CF_length)
Namespace.addCategoryObject('typeBinding', 'VersioneType', VersioneType)

# Atomic simple type:
# {http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v2.0}NaturaType


class NaturaType (pyxb.binding.datatypes.string, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'NaturaType')
    _XSDLocation = pyxb.utils.utility.Location(
        '../data/datifatture/DatiFatturav2.0.xsd', 431, 2)
    _Documentation = None


NaturaType._CF_enumeration = pyxb.binding.facets.CF_enumeration(
    value_datatype=NaturaType, enum_prefix=None)
NaturaType.N1 = NaturaType._CF_enumeration.addEnumeration(
    unicode_value='N1', tag='N1')
NaturaType.N2 = NaturaType._CF_enumeration.addEnumeration(
    unicode_value='N2', tag='N2')
NaturaType.N3 = NaturaType._CF_enumeration.addEnumeration(
    unicode_value='N3', tag='N3')
NaturaType.N4 = NaturaType._CF_enumeration.addEnumeration(
    unicode_value='N4', tag='N4')
NaturaType.N5 = NaturaType._CF_enumeration.addEnumeration(
    unicode_value='N5', tag='N5')
NaturaType.N6 = NaturaType._CF_enumeration.addEnumeration(
    unicode_value='N6', tag='N6')
NaturaType.N7 = NaturaType._CF_enumeration.addEnumeration(
    unicode_value='N7', tag='N7')
NaturaType._InitializeFacetMap(NaturaType._CF_enumeration)
Namespace.addCategoryObject('typeBinding', 'NaturaType', NaturaType)

# Atomic simple type:
# {http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v2.0}DeducibileType


class DeducibileType (pyxb.binding.datatypes.string, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'DeducibileType')
    _XSDLocation = pyxb.utils.utility.Location(
        '../data/datifatture/DatiFatturav2.0.xsd', 462, 2)
    _Documentation = None


DeducibileType._CF_enumeration = pyxb.binding.facets.CF_enumeration(
    value_datatype=DeducibileType, enum_prefix=None)
DeducibileType.SI = DeducibileType._CF_enumeration.addEnumeration(
    unicode_value='SI', tag='SI')
DeducibileType._CF_length = pyxb.binding.facets.CF_length(
    value=pyxb.binding.datatypes.nonNegativeInteger(2))
DeducibileType._InitializeFacetMap(DeducibileType._CF_enumeration,
                                   DeducibileType._CF_length)
Namespace.addCategoryObject('typeBinding', 'DeducibileType', DeducibileType)

# Atomic simple type:
# {http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v2.0}EsigibilitaIVAType


class EsigibilitaIVAType (pyxb.binding.datatypes.string, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(
        Namespace, 'EsigibilitaIVAType')
    _XSDLocation = pyxb.utils.utility.Location(
        '../data/datifatture/DatiFatturav2.0.xsd', 472, 2)
    _Documentation = None


EsigibilitaIVAType._CF_enumeration = pyxb.binding.facets.CF_enumeration(
    value_datatype=EsigibilitaIVAType, enum_prefix=None)
EsigibilitaIVAType.D = EsigibilitaIVAType._CF_enumeration.addEnumeration(
    unicode_value='D', tag='D')
EsigibilitaIVAType.I = EsigibilitaIVAType._CF_enumeration.addEnumeration(
    unicode_value='I', tag='I')
EsigibilitaIVAType.S = EsigibilitaIVAType._CF_enumeration.addEnumeration(
    unicode_value='S', tag='S')
EsigibilitaIVAType._CF_maxLength = pyxb.binding.facets.CF_maxLength(
    value=pyxb.binding.datatypes.nonNegativeInteger(1))
EsigibilitaIVAType._CF_minLength = pyxb.binding.facets.CF_minLength(
    value=pyxb.binding.datatypes.nonNegativeInteger(1))
EsigibilitaIVAType._InitializeFacetMap(EsigibilitaIVAType._CF_enumeration,
                                       EsigibilitaIVAType._CF_maxLength,
                                       EsigibilitaIVAType._CF_minLength)
Namespace.addCategoryObject(
    'typeBinding', 'EsigibilitaIVAType', EsigibilitaIVAType)

# Atomic simple type:
# {http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v2.0}RateType


class RateType (pyxb.binding.datatypes.string):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'RateType')
    _XSDLocation = pyxb.utils.utility.Location(
        '../data/datifatture/DatiFatturav2.0.xsd', 494, 3)
    _Documentation = None


# RateType._CF_maxInclusive = pyxb.binding.facets.CF_maxInclusive(value_datatype=RateType, value=pyxb.binding.datatypes.decimal('100.0'))
RateType._CF_pattern = pyxb.binding.facets.CF_pattern()
RateType._CF_pattern.addPattern(pattern='[0-9]{1,3}\\.[0-9]{2}')
RateType._InitializeFacetMap(RateType._CF_pattern)
Namespace.addCategoryObject('typeBinding', 'RateType', RateType)

# Atomic simple type:
# {http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v2.0}Amount2DecimalType


class Amount2DecimalType (pyxb.binding.datatypes.string):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(
        Namespace, 'Amount2DecimalType')
    _XSDLocation = pyxb.utils.utility.Location(
        '../data/datifatture/DatiFatturav2.0.xsd', 502, 2)
    _Documentation = None


Amount2DecimalType._CF_pattern = pyxb.binding.facets.CF_pattern()
Amount2DecimalType._CF_pattern.addPattern(
    pattern='[\\-]?[0-9]{1,11}\\.[0-9]{2}')
Amount2DecimalType._InitializeFacetMap(Amount2DecimalType._CF_pattern)
Namespace.addCategoryObject(
    'typeBinding', 'Amount2DecimalType', Amount2DecimalType)

# Complex type
# {http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v2.0}DatiFatturaHeaderType
# with content type ELEMENT_ONLY


class DatiFatturaHeaderType (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v2.0}DatiFatturaHeaderType with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(
        Namespace, 'DatiFatturaHeaderType')
    _XSDLocation = pyxb.utils.utility.Location(
        '../data/datifatture/DatiFatturav2.0.xsd', 34, 2)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType

    # Element ProgressivoInvio uses Python identifier ProgressivoInvio
    __ProgressivoInvio = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(
        None, 'ProgressivoInvio'), 'ProgressivoInvio', '__httpivaservizi_agenziaentrate_gov_itdocsxsdfatturev2_0_DatiFatturaHeaderType_ProgressivoInvio', False, pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 36, 6), )

    ProgressivoInvio = property(
        __ProgressivoInvio.value, __ProgressivoInvio.set, None, None)

    # Element Dichiarante uses Python identifier Dichiarante
    __Dichiarante = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(
        None, 'Dichiarante'), 'Dichiarante', '__httpivaservizi_agenziaentrate_gov_itdocsxsdfatturev2_0_DatiFatturaHeaderType_Dichiarante', False, pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 37, 6), )

    Dichiarante = property(__Dichiarante.value, __Dichiarante.set, None, None)

    # Element IdSistema uses Python identifier IdSistema
    __IdSistema = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(
        None, 'IdSistema'), 'IdSistema', '__httpivaservizi_agenziaentrate_gov_itdocsxsdfatturev2_0_DatiFatturaHeaderType_IdSistema', False, pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 38, 6), )

    IdSistema = property(__IdSistema.value, __IdSistema.set, None, None)

    _ElementMap.update({
        __ProgressivoInvio.name(): __ProgressivoInvio,
        __Dichiarante.name(): __Dichiarante,
        __IdSistema.name(): __IdSistema
    })
    _AttributeMap.update({

    })


Namespace.addCategoryObject(
    'typeBinding', 'DatiFatturaHeaderType', DatiFatturaHeaderType)


# Complex type
# {http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v2.0}DichiaranteType
# with content type ELEMENT_ONLY
class DichiaranteType (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v2.0}DichiaranteType with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'DichiaranteType')
    _XSDLocation = pyxb.utils.utility.Location(
        '../data/datifatture/DatiFatturav2.0.xsd', 42, 2)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType

    # Element CodiceFiscale uses Python identifier CodiceFiscale
    __CodiceFiscale = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(
        None, 'CodiceFiscale'), 'CodiceFiscale', '__httpivaservizi_agenziaentrate_gov_itdocsxsdfatturev2_0_DichiaranteType_CodiceFiscale', False, pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 44, 6), )

    CodiceFiscale = property(__CodiceFiscale.value,
                             __CodiceFiscale.set, None, None)

    # Element Carica uses Python identifier Carica
    __Carica = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(
        None, 'Carica'), 'Carica', '__httpivaservizi_agenziaentrate_gov_itdocsxsdfatturev2_0_DichiaranteType_Carica', False, pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 45, 6), )

    Carica = property(__Carica.value, __Carica.set, None, None)

    _ElementMap.update({
        __CodiceFiscale.name(): __CodiceFiscale,
        __Carica.name(): __Carica
    })
    _AttributeMap.update({

    })


Namespace.addCategoryObject('typeBinding', 'DichiaranteType', DichiaranteType)


# Complex type
# {http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v2.0}DTEType
# with content type ELEMENT_ONLY
class DTEType (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v2.0}DTEType with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'DTEType')
    _XSDLocation = pyxb.utils.utility.Location(
        '../data/datifatture/DatiFatturav2.0.xsd', 49, 2)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType

    # Element CedentePrestatoreDTE uses Python identifier CedentePrestatoreDTE
    __CedentePrestatoreDTE = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(
        None, 'CedentePrestatoreDTE'), 'CedentePrestatoreDTE', '__httpivaservizi_agenziaentrate_gov_itdocsxsdfatturev2_0_DTEType_CedentePrestatoreDTE', False, pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 51, 6), )

    CedentePrestatoreDTE = property(
        __CedentePrestatoreDTE.value, __CedentePrestatoreDTE.set, None, None)

    # Element CessionarioCommittenteDTE uses Python identifier
    # CessionarioCommittenteDTE
    __CessionarioCommittenteDTE = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'CessionarioCommittenteDTE'), 'CessionarioCommittenteDTE',
                                                                          '__httpivaservizi_agenziaentrate_gov_itdocsxsdfatturev2_0_DTEType_CessionarioCommittenteDTE', True, pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 52, 6), )

    CessionarioCommittenteDTE = property(
        __CessionarioCommittenteDTE.value, __CessionarioCommittenteDTE.set, None, None)

    # Element Rettifica uses Python identifier Rettifica
    __Rettifica = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(
        None, 'Rettifica'), 'Rettifica', '__httpivaservizi_agenziaentrate_gov_itdocsxsdfatturev2_0_DTEType_Rettifica', False, pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 53, 6), )

    Rettifica = property(__Rettifica.value, __Rettifica.set, None, None)

    _ElementMap.update({
        __CedentePrestatoreDTE.name(): __CedentePrestatoreDTE,
        __CessionarioCommittenteDTE.name(): __CessionarioCommittenteDTE,
        __Rettifica.name(): __Rettifica
    })
    _AttributeMap.update({

    })


Namespace.addCategoryObject('typeBinding', 'DTEType', DTEType)


# Complex type
# {http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v2.0}DTRType
# with content type ELEMENT_ONLY
class DTRType (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v2.0}DTRType with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'DTRType')
    _XSDLocation = pyxb.utils.utility.Location(
        '../data/datifatture/DatiFatturav2.0.xsd', 57, 2)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType

    # Element CessionarioCommittenteDTR uses Python identifier
    # CessionarioCommittenteDTR
    __CessionarioCommittenteDTR = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'CessionarioCommittenteDTR'), 'CessionarioCommittenteDTR',
                                                                          '__httpivaservizi_agenziaentrate_gov_itdocsxsdfatturev2_0_DTRType_CessionarioCommittenteDTR', False, pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 59, 6), )

    CessionarioCommittenteDTR = property(
        __CessionarioCommittenteDTR.value, __CessionarioCommittenteDTR.set, None, None)

    # Element CedentePrestatoreDTR uses Python identifier CedentePrestatoreDTR
    __CedentePrestatoreDTR = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(
        None, 'CedentePrestatoreDTR'), 'CedentePrestatoreDTR', '__httpivaservizi_agenziaentrate_gov_itdocsxsdfatturev2_0_DTRType_CedentePrestatoreDTR', True, pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 60, 6), )

    CedentePrestatoreDTR = property(
        __CedentePrestatoreDTR.value, __CedentePrestatoreDTR.set, None, None)

    # Element Rettifica uses Python identifier Rettifica
    __Rettifica = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(
        None, 'Rettifica'), 'Rettifica', '__httpivaservizi_agenziaentrate_gov_itdocsxsdfatturev2_0_DTRType_Rettifica', False, pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 61, 6), )

    Rettifica = property(__Rettifica.value, __Rettifica.set, None, None)

    _ElementMap.update({
        __CessionarioCommittenteDTR.name(): __CessionarioCommittenteDTR,
        __CedentePrestatoreDTR.name(): __CedentePrestatoreDTR,
        __Rettifica.name(): __Rettifica
    })
    _AttributeMap.update({

    })


Namespace.addCategoryObject('typeBinding', 'DTRType', DTRType)


# Complex type
# {http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v2.0}ANNType
# with content type ELEMENT_ONLY
class ANNType (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v2.0}ANNType with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'ANNType')
    _XSDLocation = pyxb.utils.utility.Location(
        '../data/datifatture/DatiFatturav2.0.xsd', 65, 2)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType

    # Element IdFile uses Python identifier IdFile
    __IdFile = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(
        None, 'IdFile'), 'IdFile', '__httpivaservizi_agenziaentrate_gov_itdocsxsdfatturev2_0_ANNType_IdFile', False, pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 67, 6), )

    IdFile = property(__IdFile.value, __IdFile.set, None, None)

    # Element Posizione uses Python identifier Posizione
    __Posizione = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(
        None, 'Posizione'), 'Posizione', '__httpivaservizi_agenziaentrate_gov_itdocsxsdfatturev2_0_ANNType_Posizione', False, pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 68, 6), )

    Posizione = property(__Posizione.value, __Posizione.set, None, None)

    _ElementMap.update({
        __IdFile.name(): __IdFile,
        __Posizione.name(): __Posizione
    })
    _AttributeMap.update({

    })


Namespace.addCategoryObject('typeBinding', 'ANNType', ANNType)


# Complex type
# {http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v2.0}CedentePrestatoreDTEType
# with content type ELEMENT_ONLY
class CedentePrestatoreDTEType (pyxb.binding.basis.complexTypeDefinition):
    """Blocco relativo ai dati del Cedente / Prestatore"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(
        Namespace, 'CedentePrestatoreDTEType')
    _XSDLocation = pyxb.utils.utility.Location(
        '../data/datifatture/DatiFatturav2.0.xsd', 72, 2)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType

    # Element IdentificativiFiscali uses Python identifier
    # IdentificativiFiscali
    __IdentificativiFiscali = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(
        None, 'IdentificativiFiscali'), 'IdentificativiFiscali', '__httpivaservizi_agenziaentrate_gov_itdocsxsdfatturev2_0_CedentePrestatoreDTEType_IdentificativiFiscali', False, pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 75, 6), )

    IdentificativiFiscali = property(
        __IdentificativiFiscali.value, __IdentificativiFiscali.set, None, None)

    # Element AltriDatiIdentificativi uses Python identifier
    # AltriDatiIdentificativi
    __AltriDatiIdentificativi = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'AltriDatiIdentificativi'), 'AltriDatiIdentificativi',
                                                                        '__httpivaservizi_agenziaentrate_gov_itdocsxsdfatturev2_0_CedentePrestatoreDTEType_AltriDatiIdentificativi', False, pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 76, 6), )

    AltriDatiIdentificativi = property(
        __AltriDatiIdentificativi.value, __AltriDatiIdentificativi.set, None, None)

    _ElementMap.update({
        __IdentificativiFiscali.name(): __IdentificativiFiscali,
        __AltriDatiIdentificativi.name(): __AltriDatiIdentificativi
    })
    _AttributeMap.update({

    })


Namespace.addCategoryObject(
    'typeBinding', 'CedentePrestatoreDTEType', CedentePrestatoreDTEType)


# Complex type
# {http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v2.0}CedentePrestatoreDTRType
# with content type ELEMENT_ONLY
class CedentePrestatoreDTRType (pyxb.binding.basis.complexTypeDefinition):
    """Blocco relativo ai dati del Cedente / Prestatore"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(
        Namespace, 'CedentePrestatoreDTRType')
    _XSDLocation = pyxb.utils.utility.Location(
        '../data/datifatture/DatiFatturav2.0.xsd', 80, 2)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType

    # Element IdentificativiFiscali uses Python identifier
    # IdentificativiFiscali
    __IdentificativiFiscali = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(
        None, 'IdentificativiFiscali'), 'IdentificativiFiscali', '__httpivaservizi_agenziaentrate_gov_itdocsxsdfatturev2_0_CedentePrestatoreDTRType_IdentificativiFiscali', False, pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 83, 6), )

    IdentificativiFiscali = property(
        __IdentificativiFiscali.value, __IdentificativiFiscali.set, None, None)

    # Element AltriDatiIdentificativi uses Python identifier
    # AltriDatiIdentificativi
    __AltriDatiIdentificativi = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'AltriDatiIdentificativi'), 'AltriDatiIdentificativi',
                                                                        '__httpivaservizi_agenziaentrate_gov_itdocsxsdfatturev2_0_CedentePrestatoreDTRType_AltriDatiIdentificativi', False, pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 84, 6), )

    AltriDatiIdentificativi = property(
        __AltriDatiIdentificativi.value, __AltriDatiIdentificativi.set, None, None)

    # Element DatiFatturaBodyDTR uses Python identifier DatiFatturaBodyDTR
    __DatiFatturaBodyDTR = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(
        None, 'DatiFatturaBodyDTR'), 'DatiFatturaBodyDTR', '__httpivaservizi_agenziaentrate_gov_itdocsxsdfatturev2_0_CedentePrestatoreDTRType_DatiFatturaBodyDTR', True, pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 85, 6), )

    DatiFatturaBodyDTR = property(
        __DatiFatturaBodyDTR.value, __DatiFatturaBodyDTR.set, None, None)

    _ElementMap.update({
        __IdentificativiFiscali.name(): __IdentificativiFiscali,
        __AltriDatiIdentificativi.name(): __AltriDatiIdentificativi,
        __DatiFatturaBodyDTR.name(): __DatiFatturaBodyDTR
    })
    _AttributeMap.update({

    })


Namespace.addCategoryObject(
    'typeBinding', 'CedentePrestatoreDTRType', CedentePrestatoreDTRType)


# Complex type
# {http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v2.0}CessionarioCommittenteDTEType
# with content type ELEMENT_ONLY
class CessionarioCommittenteDTEType (pyxb.binding.basis.complexTypeDefinition):
    """Blocco relativo ai dati del Cessionario / Committente"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(
        Namespace, 'CessionarioCommittenteDTEType')
    _XSDLocation = pyxb.utils.utility.Location(
        '../data/datifatture/DatiFatturav2.0.xsd', 89, 2)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType

    # Element IdentificativiFiscali uses Python identifier
    # IdentificativiFiscali
    __IdentificativiFiscali = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(
        None, 'IdentificativiFiscali'), 'IdentificativiFiscali', '__httpivaservizi_agenziaentrate_gov_itdocsxsdfatturev2_0_CessionarioCommittenteDTEType_IdentificativiFiscali', False, pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 92, 6), )

    IdentificativiFiscali = property(
        __IdentificativiFiscali.value, __IdentificativiFiscali.set, None, None)

    # Element AltriDatiIdentificativi uses Python identifier
    # AltriDatiIdentificativi
    __AltriDatiIdentificativi = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'AltriDatiIdentificativi'), 'AltriDatiIdentificativi',
                                                                        '__httpivaservizi_agenziaentrate_gov_itdocsxsdfatturev2_0_CessionarioCommittenteDTEType_AltriDatiIdentificativi', False, pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 93, 6), )

    AltriDatiIdentificativi = property(
        __AltriDatiIdentificativi.value, __AltriDatiIdentificativi.set, None, None)

    # Element DatiFatturaBodyDTE uses Python identifier DatiFatturaBodyDTE
    __DatiFatturaBodyDTE = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(
        None, 'DatiFatturaBodyDTE'), 'DatiFatturaBodyDTE', '__httpivaservizi_agenziaentrate_gov_itdocsxsdfatturev2_0_CessionarioCommittenteDTEType_DatiFatturaBodyDTE', True, pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 94, 6), )

    DatiFatturaBodyDTE = property(
        __DatiFatturaBodyDTE.value, __DatiFatturaBodyDTE.set, None, None)

    _ElementMap.update({
        __IdentificativiFiscali.name(): __IdentificativiFiscali,
        __AltriDatiIdentificativi.name(): __AltriDatiIdentificativi,
        __DatiFatturaBodyDTE.name(): __DatiFatturaBodyDTE
    })
    _AttributeMap.update({

    })


Namespace.addCategoryObject(
    'typeBinding', 'CessionarioCommittenteDTEType', CessionarioCommittenteDTEType)


# Complex type
# {http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v2.0}CessionarioCommittenteDTRType
# with content type ELEMENT_ONLY
class CessionarioCommittenteDTRType (pyxb.binding.basis.complexTypeDefinition):
    """Blocco relativo ai dati del Cessionario / Committente"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(
        Namespace, 'CessionarioCommittenteDTRType')
    _XSDLocation = pyxb.utils.utility.Location(
        '../data/datifatture/DatiFatturav2.0.xsd', 98, 2)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType

    # Element IdentificativiFiscali uses Python identifier
    # IdentificativiFiscali
    __IdentificativiFiscali = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(
        None, 'IdentificativiFiscali'), 'IdentificativiFiscali', '__httpivaservizi_agenziaentrate_gov_itdocsxsdfatturev2_0_CessionarioCommittenteDTRType_IdentificativiFiscali', False, pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 101, 6), )

    IdentificativiFiscali = property(
        __IdentificativiFiscali.value, __IdentificativiFiscali.set, None, None)

    # Element AltriDatiIdentificativi uses Python identifier
    # AltriDatiIdentificativi
    __AltriDatiIdentificativi = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'AltriDatiIdentificativi'), 'AltriDatiIdentificativi',
                                                                        '__httpivaservizi_agenziaentrate_gov_itdocsxsdfatturev2_0_CessionarioCommittenteDTRType_AltriDatiIdentificativi', False, pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 102, 6), )

    AltriDatiIdentificativi = property(
        __AltriDatiIdentificativi.value, __AltriDatiIdentificativi.set, None, None)

    _ElementMap.update({
        __IdentificativiFiscali.name(): __IdentificativiFiscali,
        __AltriDatiIdentificativi.name(): __AltriDatiIdentificativi
    })
    _AttributeMap.update({

    })


Namespace.addCategoryObject(
    'typeBinding', 'CessionarioCommittenteDTRType', CessionarioCommittenteDTRType)


# Complex type
# {http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v2.0}DatiFatturaBodyDTEType
# with content type ELEMENT_ONLY
class DatiFatturaBodyDTEType (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v2.0}DatiFatturaBodyDTEType with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(
        Namespace, 'DatiFatturaBodyDTEType')
    _XSDLocation = pyxb.utils.utility.Location(
        '../data/datifatture/DatiFatturav2.0.xsd', 106, 2)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType

    # Element DatiGenerali uses Python identifier DatiGenerali
    __DatiGenerali = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(
        None, 'DatiGenerali'), 'DatiGenerali', '__httpivaservizi_agenziaentrate_gov_itdocsxsdfatturev2_0_DatiFatturaBodyDTEType_DatiGenerali', False, pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 108, 6), )

    DatiGenerali = property(__DatiGenerali.value,
                            __DatiGenerali.set, None, None)

    # Element DatiRiepilogo uses Python identifier DatiRiepilogo
    __DatiRiepilogo = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(
        None, 'DatiRiepilogo'), 'DatiRiepilogo', '__httpivaservizi_agenziaentrate_gov_itdocsxsdfatturev2_0_DatiFatturaBodyDTEType_DatiRiepilogo', True, pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 109, 6), )

    DatiRiepilogo = property(__DatiRiepilogo.value,
                             __DatiRiepilogo.set, None, None)

    _ElementMap.update({
        __DatiGenerali.name(): __DatiGenerali,
        __DatiRiepilogo.name(): __DatiRiepilogo
    })
    _AttributeMap.update({

    })


Namespace.addCategoryObject(
    'typeBinding', 'DatiFatturaBodyDTEType', DatiFatturaBodyDTEType)


# Complex type
# {http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v2.0}DatiFatturaBodyDTRType
# with content type ELEMENT_ONLY
class DatiFatturaBodyDTRType (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v2.0}DatiFatturaBodyDTRType with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(
        Namespace, 'DatiFatturaBodyDTRType')
    _XSDLocation = pyxb.utils.utility.Location(
        '../data/datifatture/DatiFatturav2.0.xsd', 113, 2)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType

    # Element DatiGenerali uses Python identifier DatiGenerali
    __DatiGenerali = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(
        None, 'DatiGenerali'), 'DatiGenerali', '__httpivaservizi_agenziaentrate_gov_itdocsxsdfatturev2_0_DatiFatturaBodyDTRType_DatiGenerali', False, pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 115, 6), )

    DatiGenerali = property(__DatiGenerali.value,
                            __DatiGenerali.set, None, None)

    # Element DatiRiepilogo uses Python identifier DatiRiepilogo
    __DatiRiepilogo = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(
        None, 'DatiRiepilogo'), 'DatiRiepilogo', '__httpivaservizi_agenziaentrate_gov_itdocsxsdfatturev2_0_DatiFatturaBodyDTRType_DatiRiepilogo', True, pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 116, 6), )

    DatiRiepilogo = property(__DatiRiepilogo.value,
                             __DatiRiepilogo.set, None, None)

    _ElementMap.update({
        __DatiGenerali.name(): __DatiGenerali,
        __DatiRiepilogo.name(): __DatiRiepilogo
    })
    _AttributeMap.update({

    })


Namespace.addCategoryObject(
    'typeBinding', 'DatiFatturaBodyDTRType', DatiFatturaBodyDTRType)


# Complex type
# {http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v2.0}RettificaType
# with content type ELEMENT_ONLY
class RettificaType (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v2.0}RettificaType with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'RettificaType')
    _XSDLocation = pyxb.utils.utility.Location(
        '../data/datifatture/DatiFatturav2.0.xsd', 120, 2)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType

    # Element IdFile uses Python identifier IdFile
    __IdFile = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(
        None, 'IdFile'), 'IdFile', '__httpivaservizi_agenziaentrate_gov_itdocsxsdfatturev2_0_RettificaType_IdFile', False, pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 122, 6), )

    IdFile = property(__IdFile.value, __IdFile.set, None, None)

    # Element Posizione uses Python identifier Posizione
    __Posizione = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(
        None, 'Posizione'), 'Posizione', '__httpivaservizi_agenziaentrate_gov_itdocsxsdfatturev2_0_RettificaType_Posizione', False, pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 123, 6), )

    Posizione = property(__Posizione.value, __Posizione.set, None, None)

    _ElementMap.update({
        __IdFile.name(): __IdFile,
        __Posizione.name(): __Posizione
    })
    _AttributeMap.update({

    })


Namespace.addCategoryObject('typeBinding', 'RettificaType', RettificaType)


# Complex type
# {http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v2.0}IdentificativiFiscaliType
# with content type ELEMENT_ONLY
class IdentificativiFiscaliType (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v2.0}IdentificativiFiscaliType with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(
        Namespace, 'IdentificativiFiscaliType')
    _XSDLocation = pyxb.utils.utility.Location(
        '../data/datifatture/DatiFatturav2.0.xsd', 127, 2)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType

    # Element IdFiscaleIVA uses Python identifier IdFiscaleIVA
    __IdFiscaleIVA = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(
        None, 'IdFiscaleIVA'), 'IdFiscaleIVA', '__httpivaservizi_agenziaentrate_gov_itdocsxsdfatturev2_0_IdentificativiFiscaliType_IdFiscaleIVA', False, pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 129, 6), )

    IdFiscaleIVA = property(__IdFiscaleIVA.value,
                            __IdFiscaleIVA.set, None, None)

    # Element CodiceFiscale uses Python identifier CodiceFiscale
    __CodiceFiscale = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(
        None, 'CodiceFiscale'), 'CodiceFiscale', '__httpivaservizi_agenziaentrate_gov_itdocsxsdfatturev2_0_IdentificativiFiscaliType_CodiceFiscale', False, pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 130, 6), )

    CodiceFiscale = property(__CodiceFiscale.value,
                             __CodiceFiscale.set, None, None)

    _ElementMap.update({
        __IdFiscaleIVA.name(): __IdFiscaleIVA,
        __CodiceFiscale.name(): __CodiceFiscale
    })
    _AttributeMap.update({

    })


Namespace.addCategoryObject(
    'typeBinding', 'IdentificativiFiscaliType', IdentificativiFiscaliType)


# Complex type
# {http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v2.0}IdentificativiFiscaliITType
# with content type ELEMENT_ONLY
class IdentificativiFiscaliITType (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v2.0}IdentificativiFiscaliITType with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(
        Namespace, 'IdentificativiFiscaliITType')
    _XSDLocation = pyxb.utils.utility.Location(
        '../data/datifatture/DatiFatturav2.0.xsd', 134, 2)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType

    # Element IdFiscaleIVA uses Python identifier IdFiscaleIVA
    __IdFiscaleIVA = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(
        None, 'IdFiscaleIVA'), 'IdFiscaleIVA', '__httpivaservizi_agenziaentrate_gov_itdocsxsdfatturev2_0_IdentificativiFiscaliITType_IdFiscaleIVA', False, pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 136, 6), )

    IdFiscaleIVA = property(__IdFiscaleIVA.value,
                            __IdFiscaleIVA.set, None, None)

    # Element CodiceFiscale uses Python identifier CodiceFiscale
    __CodiceFiscale = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(
        None, 'CodiceFiscale'), 'CodiceFiscale', '__httpivaservizi_agenziaentrate_gov_itdocsxsdfatturev2_0_IdentificativiFiscaliITType_CodiceFiscale', False, pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 137, 6), )

    CodiceFiscale = property(__CodiceFiscale.value,
                             __CodiceFiscale.set, None, None)

    _ElementMap.update({
        __IdFiscaleIVA.name(): __IdFiscaleIVA,
        __CodiceFiscale.name(): __CodiceFiscale
    })
    _AttributeMap.update({

    })


Namespace.addCategoryObject(
    'typeBinding', 'IdentificativiFiscaliITType', IdentificativiFiscaliITType)


# Complex type
# {http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v2.0}IdentificativiFiscaliNoIVAType
# with content type ELEMENT_ONLY
class IdentificativiFiscaliNoIVAType (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v2.0}IdentificativiFiscaliNoIVAType with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(
        Namespace, 'IdentificativiFiscaliNoIVAType')
    _XSDLocation = pyxb.utils.utility.Location(
        '../data/datifatture/DatiFatturav2.0.xsd', 141, 2)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType

    # Element IdFiscaleIVA uses Python identifier IdFiscaleIVA
    __IdFiscaleIVA = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(
        None, 'IdFiscaleIVA'), 'IdFiscaleIVA', '__httpivaservizi_agenziaentrate_gov_itdocsxsdfatturev2_0_IdentificativiFiscaliNoIVAType_IdFiscaleIVA', False, pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 143, 6), )

    IdFiscaleIVA = property(__IdFiscaleIVA.value,
                            __IdFiscaleIVA.set, None, None)

    # Element CodiceFiscale uses Python identifier CodiceFiscale
    __CodiceFiscale = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(
        None, 'CodiceFiscale'), 'CodiceFiscale', '__httpivaservizi_agenziaentrate_gov_itdocsxsdfatturev2_0_IdentificativiFiscaliNoIVAType_CodiceFiscale', False, pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 144, 6), )

    CodiceFiscale = property(__CodiceFiscale.value,
                             __CodiceFiscale.set, None, None)

    _ElementMap.update({
        __IdFiscaleIVA.name(): __IdFiscaleIVA,
        __CodiceFiscale.name(): __CodiceFiscale
    })
    _AttributeMap.update({

    })


Namespace.addCategoryObject(
    'typeBinding', 'IdentificativiFiscaliNoIVAType', IdentificativiFiscaliNoIVAType)


# Complex type
# {http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v2.0}AltriDatiIdentificativiNoSedeType
# with content type ELEMENT_ONLY
class AltriDatiIdentificativiNoSedeType (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v2.0}AltriDatiIdentificativiNoSedeType with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(
        Namespace, 'AltriDatiIdentificativiNoSedeType')
    _XSDLocation = pyxb.utils.utility.Location(
        '../data/datifatture/DatiFatturav2.0.xsd', 148, 2)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType

    # Element Denominazione uses Python identifier Denominazione
    __Denominazione = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(
        None, 'Denominazione'), 'Denominazione', '__httpivaservizi_agenziaentrate_gov_itdocsxsdfatturev2_0_AltriDatiIdentificativiNoSedeType_Denominazione', False, pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 152, 10), )

    Denominazione = property(__Denominazione.value,
                             __Denominazione.set, None, None)

    # Element Nome uses Python identifier Nome
    __Nome = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(
        None, 'Nome'), 'Nome', '__httpivaservizi_agenziaentrate_gov_itdocsxsdfatturev2_0_AltriDatiIdentificativiNoSedeType_Nome', False, pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 155, 10), )

    Nome = property(__Nome.value, __Nome.set, None, None)

    # Element Cognome uses Python identifier Cognome
    __Cognome = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(
        None, 'Cognome'), 'Cognome', '__httpivaservizi_agenziaentrate_gov_itdocsxsdfatturev2_0_AltriDatiIdentificativiNoSedeType_Cognome', False, pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 156, 10), )

    Cognome = property(__Cognome.value, __Cognome.set, None, None)

    # Element Sede uses Python identifier Sede
    __Sede = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(
        None, 'Sede'), 'Sede', '__httpivaservizi_agenziaentrate_gov_itdocsxsdfatturev2_0_AltriDatiIdentificativiNoSedeType_Sede', False, pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 159, 6), )

    Sede = property(__Sede.value, __Sede.set, None, None)

    # Element StabileOrganizzazione uses Python identifier
    # StabileOrganizzazione
    __StabileOrganizzazione = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(
        None, 'StabileOrganizzazione'), 'StabileOrganizzazione', '__httpivaservizi_agenziaentrate_gov_itdocsxsdfatturev2_0_AltriDatiIdentificativiNoSedeType_StabileOrganizzazione', False, pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 160, 3), )

    StabileOrganizzazione = property(
        __StabileOrganizzazione.value, __StabileOrganizzazione.set, None, None)

    # Element RappresentanteFiscale uses Python identifier
    # RappresentanteFiscale
    __RappresentanteFiscale = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(
        None, 'RappresentanteFiscale'), 'RappresentanteFiscale', '__httpivaservizi_agenziaentrate_gov_itdocsxsdfatturev2_0_AltriDatiIdentificativiNoSedeType_RappresentanteFiscale', False, pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 161, 3), )

    RappresentanteFiscale = property(
        __RappresentanteFiscale.value, __RappresentanteFiscale.set, None, None)

    _ElementMap.update({
        __Denominazione.name(): __Denominazione,
        __Nome.name(): __Nome,
        __Cognome.name(): __Cognome,
        __Sede.name(): __Sede,
        __StabileOrganizzazione.name(): __StabileOrganizzazione,
        __RappresentanteFiscale.name(): __RappresentanteFiscale
    })
    _AttributeMap.update({

    })


Namespace.addCategoryObject(
    'typeBinding', 'AltriDatiIdentificativiNoSedeType', AltriDatiIdentificativiNoSedeType)


# Complex type
# {http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v2.0}AltriDatiIdentificativiNoCAPType
# with content type ELEMENT_ONLY
class AltriDatiIdentificativiNoCAPType (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v2.0}AltriDatiIdentificativiNoCAPType with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(
        Namespace, 'AltriDatiIdentificativiNoCAPType')
    _XSDLocation = pyxb.utils.utility.Location(
        '../data/datifatture/DatiFatturav2.0.xsd', 165, 2)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType

    # Element Denominazione uses Python identifier Denominazione
    __Denominazione = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(
        None, 'Denominazione'), 'Denominazione', '__httpivaservizi_agenziaentrate_gov_itdocsxsdfatturev2_0_AltriDatiIdentificativiNoCAPType_Denominazione', False, pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 169, 10), )

    Denominazione = property(__Denominazione.value,
                             __Denominazione.set, None, None)

    # Element Nome uses Python identifier Nome
    __Nome = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(
        None, 'Nome'), 'Nome', '__httpivaservizi_agenziaentrate_gov_itdocsxsdfatturev2_0_AltriDatiIdentificativiNoCAPType_Nome', False, pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 172, 10), )

    Nome = property(__Nome.value, __Nome.set, None, None)

    # Element Cognome uses Python identifier Cognome
    __Cognome = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(
        None, 'Cognome'), 'Cognome', '__httpivaservizi_agenziaentrate_gov_itdocsxsdfatturev2_0_AltriDatiIdentificativiNoCAPType_Cognome', False, pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 173, 10), )

    Cognome = property(__Cognome.value, __Cognome.set, None, None)

    # Element Sede uses Python identifier Sede
    __Sede = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(
        None, 'Sede'), 'Sede', '__httpivaservizi_agenziaentrate_gov_itdocsxsdfatturev2_0_AltriDatiIdentificativiNoCAPType_Sede', False, pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 176, 6), )

    Sede = property(__Sede.value, __Sede.set, None, None)

    # Element StabileOrganizzazione uses Python identifier
    # StabileOrganizzazione
    __StabileOrganizzazione = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(
        None, 'StabileOrganizzazione'), 'StabileOrganizzazione', '__httpivaservizi_agenziaentrate_gov_itdocsxsdfatturev2_0_AltriDatiIdentificativiNoCAPType_StabileOrganizzazione', False, pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 177, 3), )

    StabileOrganizzazione = property(
        __StabileOrganizzazione.value, __StabileOrganizzazione.set, None, None)

    # Element RappresentanteFiscale uses Python identifier
    # RappresentanteFiscale
    __RappresentanteFiscale = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(
        None, 'RappresentanteFiscale'), 'RappresentanteFiscale', '__httpivaservizi_agenziaentrate_gov_itdocsxsdfatturev2_0_AltriDatiIdentificativiNoCAPType_RappresentanteFiscale', False, pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 178, 3), )

    RappresentanteFiscale = property(
        __RappresentanteFiscale.value, __RappresentanteFiscale.set, None, None)

    _ElementMap.update({
        __Denominazione.name(): __Denominazione,
        __Nome.name(): __Nome,
        __Cognome.name(): __Cognome,
        __Sede.name(): __Sede,
        __StabileOrganizzazione.name(): __StabileOrganizzazione,
        __RappresentanteFiscale.name(): __RappresentanteFiscale
    })
    _AttributeMap.update({

    })


Namespace.addCategoryObject(
    'typeBinding', 'AltriDatiIdentificativiNoCAPType', AltriDatiIdentificativiNoCAPType)


# Complex type
# {http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v2.0}IndirizzoNoCAPType
# with content type ELEMENT_ONLY
class IndirizzoNoCAPType (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v2.0}IndirizzoNoCAPType with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(
        Namespace, 'IndirizzoNoCAPType')
    _XSDLocation = pyxb.utils.utility.Location(
        '../data/datifatture/DatiFatturav2.0.xsd', 182, 2)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType

    # Element Indirizzo uses Python identifier Indirizzo
    __Indirizzo = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(
        None, 'Indirizzo'), 'Indirizzo', '__httpivaservizi_agenziaentrate_gov_itdocsxsdfatturev2_0_IndirizzoNoCAPType_Indirizzo', False, pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 184, 6), )

    Indirizzo = property(__Indirizzo.value, __Indirizzo.set, None, None)

    # Element NumeroCivico uses Python identifier NumeroCivico
    __NumeroCivico = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(
        None, 'NumeroCivico'), 'NumeroCivico', '__httpivaservizi_agenziaentrate_gov_itdocsxsdfatturev2_0_IndirizzoNoCAPType_NumeroCivico', False, pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 185, 6), )

    NumeroCivico = property(__NumeroCivico.value,
                            __NumeroCivico.set, None, None)

    # Element CAP uses Python identifier CAP
    __CAP = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(
        None, 'CAP'), 'CAP', '__httpivaservizi_agenziaentrate_gov_itdocsxsdfatturev2_0_IndirizzoNoCAPType_CAP', False, pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 186, 6), )

    CAP = property(__CAP.value, __CAP.set, None, None)

    # Element Comune uses Python identifier Comune
    __Comune = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(
        None, 'Comune'), 'Comune', '__httpivaservizi_agenziaentrate_gov_itdocsxsdfatturev2_0_IndirizzoNoCAPType_Comune', False, pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 187, 6), )

    Comune = property(__Comune.value, __Comune.set, None, None)

    # Element Provincia uses Python identifier Provincia
    __Provincia = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(
        None, 'Provincia'), 'Provincia', '__httpivaservizi_agenziaentrate_gov_itdocsxsdfatturev2_0_IndirizzoNoCAPType_Provincia', False, pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 188, 6), )

    Provincia = property(__Provincia.value, __Provincia.set, None, None)

    # Element Nazione uses Python identifier Nazione
    __Nazione = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(
        None, 'Nazione'), 'Nazione', '__httpivaservizi_agenziaentrate_gov_itdocsxsdfatturev2_0_IndirizzoNoCAPType_Nazione', False, pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 189, 6), )

    Nazione = property(__Nazione.value, __Nazione.set, None, None)

    _ElementMap.update({
        __Indirizzo.name(): __Indirizzo,
        __NumeroCivico.name(): __NumeroCivico,
        __CAP.name(): __CAP,
        __Comune.name(): __Comune,
        __Provincia.name(): __Provincia,
        __Nazione.name(): __Nazione
    })
    _AttributeMap.update({

    })


Namespace.addCategoryObject(
    'typeBinding', 'IndirizzoNoCAPType', IndirizzoNoCAPType)


# Complex type
# {http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v2.0}IndirizzoType
# with content type ELEMENT_ONLY
class IndirizzoType (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v2.0}IndirizzoType with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'IndirizzoType')
    _XSDLocation = pyxb.utils.utility.Location(
        '../data/datifatture/DatiFatturav2.0.xsd', 193, 2)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType

    # Element Indirizzo uses Python identifier Indirizzo
    __Indirizzo = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(
        None, 'Indirizzo'), 'Indirizzo', '__httpivaservizi_agenziaentrate_gov_itdocsxsdfatturev2_0_IndirizzoType_Indirizzo', False, pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 195, 6), )

    Indirizzo = property(__Indirizzo.value, __Indirizzo.set, None, None)

    # Element NumeroCivico uses Python identifier NumeroCivico
    __NumeroCivico = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(
        None, 'NumeroCivico'), 'NumeroCivico', '__httpivaservizi_agenziaentrate_gov_itdocsxsdfatturev2_0_IndirizzoType_NumeroCivico', False, pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 196, 6), )

    NumeroCivico = property(__NumeroCivico.value,
                            __NumeroCivico.set, None, None)

    # Element CAP uses Python identifier CAP
    __CAP = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(
        None, 'CAP'), 'CAP', '__httpivaservizi_agenziaentrate_gov_itdocsxsdfatturev2_0_IndirizzoType_CAP', False, pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 197, 6), )

    CAP = property(__CAP.value, __CAP.set, None, None)

    # Element Comune uses Python identifier Comune
    __Comune = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(
        None, 'Comune'), 'Comune', '__httpivaservizi_agenziaentrate_gov_itdocsxsdfatturev2_0_IndirizzoType_Comune', False, pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 198, 6), )

    Comune = property(__Comune.value, __Comune.set, None, None)

    # Element Provincia uses Python identifier Provincia
    __Provincia = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(
        None, 'Provincia'), 'Provincia', '__httpivaservizi_agenziaentrate_gov_itdocsxsdfatturev2_0_IndirizzoType_Provincia', False, pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 199, 6), )

    Provincia = property(__Provincia.value, __Provincia.set, None, None)

    # Element Nazione uses Python identifier Nazione
    __Nazione = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(
        None, 'Nazione'), 'Nazione', '__httpivaservizi_agenziaentrate_gov_itdocsxsdfatturev2_0_IndirizzoType_Nazione', False, pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 200, 6), )

    Nazione = property(__Nazione.value, __Nazione.set, None, None)

    _ElementMap.update({
        __Indirizzo.name(): __Indirizzo,
        __NumeroCivico.name(): __NumeroCivico,
        __CAP.name(): __CAP,
        __Comune.name(): __Comune,
        __Provincia.name(): __Provincia,
        __Nazione.name(): __Nazione
    })
    _AttributeMap.update({

    })


Namespace.addCategoryObject('typeBinding', 'IndirizzoType', IndirizzoType)


# Complex type
# {http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v2.0}RappresentanteFiscaleType
# with content type ELEMENT_ONLY
class RappresentanteFiscaleType (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v2.0}RappresentanteFiscaleType with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(
        Namespace, 'RappresentanteFiscaleType')
    _XSDLocation = pyxb.utils.utility.Location(
        '../data/datifatture/DatiFatturav2.0.xsd', 204, 2)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType

    # Element IdFiscaleIVA uses Python identifier IdFiscaleIVA
    __IdFiscaleIVA = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(
        None, 'IdFiscaleIVA'), 'IdFiscaleIVA', '__httpivaservizi_agenziaentrate_gov_itdocsxsdfatturev2_0_RappresentanteFiscaleType_IdFiscaleIVA', False, pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 206, 6), )

    IdFiscaleIVA = property(__IdFiscaleIVA.value,
                            __IdFiscaleIVA.set, None, None)

    # Element Denominazione uses Python identifier Denominazione
    __Denominazione = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(
        None, 'Denominazione'), 'Denominazione', '__httpivaservizi_agenziaentrate_gov_itdocsxsdfatturev2_0_RappresentanteFiscaleType_Denominazione', False, pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 209, 10), )

    Denominazione = property(__Denominazione.value,
                             __Denominazione.set, None, None)

    # Element Nome uses Python identifier Nome
    __Nome = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(
        None, 'Nome'), 'Nome', '__httpivaservizi_agenziaentrate_gov_itdocsxsdfatturev2_0_RappresentanteFiscaleType_Nome', False, pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 212, 10), )

    Nome = property(__Nome.value, __Nome.set, None, None)

    # Element Cognome uses Python identifier Cognome
    __Cognome = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(
        None, 'Cognome'), 'Cognome', '__httpivaservizi_agenziaentrate_gov_itdocsxsdfatturev2_0_RappresentanteFiscaleType_Cognome', False, pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 213, 10), )

    Cognome = property(__Cognome.value, __Cognome.set, None, None)

    _ElementMap.update({
        __IdFiscaleIVA.name(): __IdFiscaleIVA,
        __Denominazione.name(): __Denominazione,
        __Nome.name(): __Nome,
        __Cognome.name(): __Cognome
    })
    _AttributeMap.update({

    })


Namespace.addCategoryObject(
    'typeBinding', 'RappresentanteFiscaleType', RappresentanteFiscaleType)


# Complex type
# {http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v2.0}RappresentanteFiscaleITType
# with content type ELEMENT_ONLY
class RappresentanteFiscaleITType (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v2.0}RappresentanteFiscaleITType with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(
        Namespace, 'RappresentanteFiscaleITType')
    _XSDLocation = pyxb.utils.utility.Location(
        '../data/datifatture/DatiFatturav2.0.xsd', 219, 2)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType

    # Element IdFiscaleIVA uses Python identifier IdFiscaleIVA
    __IdFiscaleIVA = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(
        None, 'IdFiscaleIVA'), 'IdFiscaleIVA', '__httpivaservizi_agenziaentrate_gov_itdocsxsdfatturev2_0_RappresentanteFiscaleITType_IdFiscaleIVA', False, pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 221, 6), )

    IdFiscaleIVA = property(__IdFiscaleIVA.value,
                            __IdFiscaleIVA.set, None, None)

    # Element Denominazione uses Python identifier Denominazione
    __Denominazione = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(
        None, 'Denominazione'), 'Denominazione', '__httpivaservizi_agenziaentrate_gov_itdocsxsdfatturev2_0_RappresentanteFiscaleITType_Denominazione', False, pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 224, 10), )

    Denominazione = property(__Denominazione.value,
                             __Denominazione.set, None, None)

    # Element Nome uses Python identifier Nome
    __Nome = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(
        None, 'Nome'), 'Nome', '__httpivaservizi_agenziaentrate_gov_itdocsxsdfatturev2_0_RappresentanteFiscaleITType_Nome', False, pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 227, 10), )

    Nome = property(__Nome.value, __Nome.set, None, None)

    # Element Cognome uses Python identifier Cognome
    __Cognome = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(
        None, 'Cognome'), 'Cognome', '__httpivaservizi_agenziaentrate_gov_itdocsxsdfatturev2_0_RappresentanteFiscaleITType_Cognome', False, pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 228, 10), )

    Cognome = property(__Cognome.value, __Cognome.set, None, None)

    _ElementMap.update({
        __IdFiscaleIVA.name(): __IdFiscaleIVA,
        __Denominazione.name(): __Denominazione,
        __Nome.name(): __Nome,
        __Cognome.name(): __Cognome
    })
    _AttributeMap.update({

    })


Namespace.addCategoryObject(
    'typeBinding', 'RappresentanteFiscaleITType', RappresentanteFiscaleITType)


# Complex type
# {http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v2.0}DatiGeneraliType
# with content type ELEMENT_ONLY
class DatiGeneraliType (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v2.0}DatiGeneraliType with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'DatiGeneraliType')
    _XSDLocation = pyxb.utils.utility.Location(
        '../data/datifatture/DatiFatturav2.0.xsd', 234, 2)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType

    # Element TipoDocumento uses Python identifier TipoDocumento
    __TipoDocumento = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(
        None, 'TipoDocumento'), 'TipoDocumento', '__httpivaservizi_agenziaentrate_gov_itdocsxsdfatturev2_0_DatiGeneraliType_TipoDocumento', False, pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 236, 6), )

    TipoDocumento = property(__TipoDocumento.value,
                             __TipoDocumento.set, None, None)

    # Element Data uses Python identifier Data
    __Data = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(
        None, 'Data'), 'Data', '__httpivaservizi_agenziaentrate_gov_itdocsxsdfatturev2_0_DatiGeneraliType_Data', False, pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 237, 6), )

    Data = property(__Data.value, __Data.set, None, None)

    # Element Numero uses Python identifier Numero
    __Numero = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(
        None, 'Numero'), 'Numero', '__httpivaservizi_agenziaentrate_gov_itdocsxsdfatturev2_0_DatiGeneraliType_Numero', False, pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 238, 6), )

    Numero = property(__Numero.value, __Numero.set, None, None)

    _ElementMap.update({
        __TipoDocumento.name(): __TipoDocumento,
        __Data.name(): __Data,
        __Numero.name(): __Numero
    })
    _AttributeMap.update({

    })


Namespace.addCategoryObject(
    'typeBinding', 'DatiGeneraliType', DatiGeneraliType)


# Complex type
# {http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v2.0}DatiGeneraliDTRType
# with content type ELEMENT_ONLY
class DatiGeneraliDTRType (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v2.0}DatiGeneraliDTRType with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(
        Namespace, 'DatiGeneraliDTRType')
    _XSDLocation = pyxb.utils.utility.Location(
        '../data/datifatture/DatiFatturav2.0.xsd', 242, 2)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType

    # Element TipoDocumento uses Python identifier TipoDocumento
    __TipoDocumento = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(
        None, 'TipoDocumento'), 'TipoDocumento', '__httpivaservizi_agenziaentrate_gov_itdocsxsdfatturev2_0_DatiGeneraliDTRType_TipoDocumento', False, pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 244, 6), )

    TipoDocumento = property(__TipoDocumento.value,
                             __TipoDocumento.set, None, None)

    # Element Data uses Python identifier Data
    __Data = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(
        None, 'Data'), 'Data', '__httpivaservizi_agenziaentrate_gov_itdocsxsdfatturev2_0_DatiGeneraliDTRType_Data', False, pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 245, 6), )

    Data = property(__Data.value, __Data.set, None, None)

    # Element Numero uses Python identifier Numero
    __Numero = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(
        None, 'Numero'), 'Numero', '__httpivaservizi_agenziaentrate_gov_itdocsxsdfatturev2_0_DatiGeneraliDTRType_Numero', False, pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 246, 6), )

    Numero = property(__Numero.value, __Numero.set, None, None)

    # Element DataRegistrazione uses Python identifier DataRegistrazione
    __DataRegistrazione = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(
        None, 'DataRegistrazione'), 'DataRegistrazione', '__httpivaservizi_agenziaentrate_gov_itdocsxsdfatturev2_0_DatiGeneraliDTRType_DataRegistrazione', False, pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 247, 6), )

    DataRegistrazione = property(
        __DataRegistrazione.value, __DataRegistrazione.set, None, None)

    _ElementMap.update({
        __TipoDocumento.name(): __TipoDocumento,
        __Data.name(): __Data,
        __Numero.name(): __Numero,
        __DataRegistrazione.name(): __DataRegistrazione
    })
    _AttributeMap.update({

    })


Namespace.addCategoryObject(
    'typeBinding', 'DatiGeneraliDTRType', DatiGeneraliDTRType)


# Complex type
# {http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v2.0}DatiRiepilogoType
# with content type ELEMENT_ONLY
class DatiRiepilogoType (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v2.0}DatiRiepilogoType with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'DatiRiepilogoType')
    _XSDLocation = pyxb.utils.utility.Location(
        '../data/datifatture/DatiFatturav2.0.xsd', 251, 2)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType

    # Element ImponibileImporto uses Python identifier ImponibileImporto
    __ImponibileImporto = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(
        None, 'ImponibileImporto'), 'ImponibileImporto', '__httpivaservizi_agenziaentrate_gov_itdocsxsdfatturev2_0_DatiRiepilogoType_ImponibileImporto', False, pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 253, 6), )

    ImponibileImporto = property(
        __ImponibileImporto.value, __ImponibileImporto.set, None, None)

    # Element DatiIVA uses Python identifier DatiIVA
    __DatiIVA = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(
        None, 'DatiIVA'), 'DatiIVA', '__httpivaservizi_agenziaentrate_gov_itdocsxsdfatturev2_0_DatiRiepilogoType_DatiIVA', False, pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 254, 6), )

    DatiIVA = property(__DatiIVA.value, __DatiIVA.set, None, None)

    # Element Natura uses Python identifier Natura
    __Natura = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(
        None, 'Natura'), 'Natura', '__httpivaservizi_agenziaentrate_gov_itdocsxsdfatturev2_0_DatiRiepilogoType_Natura', False, pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 255, 6), )

    Natura = property(__Natura.value, __Natura.set, None, None)

    # Element Detraibile uses Python identifier Detraibile
    __Detraibile = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(
        None, 'Detraibile'), 'Detraibile', '__httpivaservizi_agenziaentrate_gov_itdocsxsdfatturev2_0_DatiRiepilogoType_Detraibile', False, pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 256, 6), )

    Detraibile = property(__Detraibile.value, __Detraibile.set, None, None)

    # Element Deducibile uses Python identifier Deducibile
    __Deducibile = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(
        None, 'Deducibile'), 'Deducibile', '__httpivaservizi_agenziaentrate_gov_itdocsxsdfatturev2_0_DatiRiepilogoType_Deducibile', False, pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 257, 6), )

    Deducibile = property(__Deducibile.value, __Deducibile.set, None, None)

    # Element EsigibilitaIVA uses Python identifier EsigibilitaIVA
    __EsigibilitaIVA = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(
        None, 'EsigibilitaIVA'), 'EsigibilitaIVA', '__httpivaservizi_agenziaentrate_gov_itdocsxsdfatturev2_0_DatiRiepilogoType_EsigibilitaIVA', False, pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 258, 6), )

    EsigibilitaIVA = property(__EsigibilitaIVA.value,
                              __EsigibilitaIVA.set, None, None)

    _ElementMap.update({
        __ImponibileImporto.name(): __ImponibileImporto,
        __DatiIVA.name(): __DatiIVA,
        __Natura.name(): __Natura,
        __Detraibile.name(): __Detraibile,
        __Deducibile.name(): __Deducibile,
        __EsigibilitaIVA.name(): __EsigibilitaIVA
    })
    _AttributeMap.update({

    })


Namespace.addCategoryObject(
    'typeBinding', 'DatiRiepilogoType', DatiRiepilogoType)


# Complex type
# {http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v2.0}DatiIVAType
# with content type ELEMENT_ONLY
class DatiIVAType (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v2.0}DatiIVAType with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'DatiIVAType')
    _XSDLocation = pyxb.utils.utility.Location(
        '../data/datifatture/DatiFatturav2.0.xsd', 262, 2)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType

    # Element Imposta uses Python identifier Imposta
    __Imposta = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(
        None, 'Imposta'), 'Imposta', '__httpivaservizi_agenziaentrate_gov_itdocsxsdfatturev2_0_DatiIVAType_Imposta', False, pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 264, 6), )

    Imposta = property(__Imposta.value, __Imposta.set, None, None)

    # Element Aliquota uses Python identifier Aliquota
    __Aliquota = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(
        None, 'Aliquota'), 'Aliquota', '__httpivaservizi_agenziaentrate_gov_itdocsxsdfatturev2_0_DatiIVAType_Aliquota', False, pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 265, 6), )

    Aliquota = property(__Aliquota.value, __Aliquota.set, None, None)

    _ElementMap.update({
        __Imposta.name(): __Imposta,
        __Aliquota.name(): __Aliquota
    })
    _AttributeMap.update({

    })


Namespace.addCategoryObject('typeBinding', 'DatiIVAType', DatiIVAType)


# Complex type
# {http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v2.0}IdFiscaleType
# with content type ELEMENT_ONLY
class IdFiscaleType (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v2.0}IdFiscaleType with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'IdFiscaleType')
    _XSDLocation = pyxb.utils.utility.Location(
        '../data/datifatture/DatiFatturav2.0.xsd', 269, 2)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType

    # Element IdPaese uses Python identifier IdPaese
    __IdPaese = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(
        None, 'IdPaese'), 'IdPaese', '__httpivaservizi_agenziaentrate_gov_itdocsxsdfatturev2_0_IdFiscaleType_IdPaese', False, pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 271, 3), )

    IdPaese = property(__IdPaese.value, __IdPaese.set, None, None)

    # Element IdCodice uses Python identifier IdCodice
    __IdCodice = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(
        None, 'IdCodice'), 'IdCodice', '__httpivaservizi_agenziaentrate_gov_itdocsxsdfatturev2_0_IdFiscaleType_IdCodice', False, pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 272, 3), )

    IdCodice = property(__IdCodice.value, __IdCodice.set, None, None)

    _ElementMap.update({
        __IdPaese.name(): __IdPaese,
        __IdCodice.name(): __IdCodice
    })
    _AttributeMap.update({

    })


Namespace.addCategoryObject('typeBinding', 'IdFiscaleType', IdFiscaleType)


# Complex type
# {http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v2.0}IdFiscaleITType
# with content type ELEMENT_ONLY
class IdFiscaleITType (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v2.0}IdFiscaleITType with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'IdFiscaleITType')
    _XSDLocation = pyxb.utils.utility.Location(
        '../data/datifatture/DatiFatturav2.0.xsd', 276, 2)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType

    # Element IdPaese uses Python identifier IdPaese
    __IdPaese = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(
        None, 'IdPaese'), 'IdPaese', '__httpivaservizi_agenziaentrate_gov_itdocsxsdfatturev2_0_IdFiscaleITType_IdPaese', False, pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 278, 3), )

    IdPaese = property(__IdPaese.value, __IdPaese.set, None, None)

    # Element IdCodice uses Python identifier IdCodice
    __IdCodice = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(
        None, 'IdCodice'), 'IdCodice', '__httpivaservizi_agenziaentrate_gov_itdocsxsdfatturev2_0_IdFiscaleITType_IdCodice', False, pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 279, 3), )

    IdCodice = property(__IdCodice.value, __IdCodice.set, None, None)

    _ElementMap.update({
        __IdPaese.name(): __IdPaese,
        __IdCodice.name(): __IdCodice
    })
    _AttributeMap.update({

    })


Namespace.addCategoryObject('typeBinding', 'IdFiscaleITType', IdFiscaleITType)


# Complex type
# {http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v2.0}IdFiscaleITIvaType
# with content type ELEMENT_ONLY
class IdFiscaleITIvaType (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v2.0}IdFiscaleITIvaType with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(
        Namespace, 'IdFiscaleITIvaType')
    _XSDLocation = pyxb.utils.utility.Location(
        '../data/datifatture/DatiFatturav2.0.xsd', 283, 2)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType

    # Element IdPaese uses Python identifier IdPaese
    __IdPaese = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(
        None, 'IdPaese'), 'IdPaese', '__httpivaservizi_agenziaentrate_gov_itdocsxsdfatturev2_0_IdFiscaleITIvaType_IdPaese', False, pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 285, 3), )

    IdPaese = property(__IdPaese.value, __IdPaese.set, None, None)

    # Element IdCodice uses Python identifier IdCodice
    __IdCodice = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(
        None, 'IdCodice'), 'IdCodice', '__httpivaservizi_agenziaentrate_gov_itdocsxsdfatturev2_0_IdFiscaleITIvaType_IdCodice', False, pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 286, 3), )

    IdCodice = property(__IdCodice.value, __IdCodice.set, None, None)

    _ElementMap.update({
        __IdPaese.name(): __IdPaese,
        __IdCodice.name(): __IdCodice
    })
    _AttributeMap.update({

    })


Namespace.addCategoryObject(
    'typeBinding', 'IdFiscaleITIvaType', IdFiscaleITIvaType)


# Complex type
# {http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v2.0}DatiFatturaType
# with content type ELEMENT_ONLY
class DatiFatturaType (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v2.0}DatiFatturaType with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'DatiFatturaType')
    _XSDLocation = pyxb.utils.utility.Location(
        '../data/datifatture/DatiFatturav2.0.xsd', 21, 2)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType

    # Element DatiFatturaHeader uses Python identifier DatiFatturaHeader
    __DatiFatturaHeader = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(
        None, 'DatiFatturaHeader'), 'DatiFatturaHeader', '__httpivaservizi_agenziaentrate_gov_itdocsxsdfatturev2_0_DatiFatturaType_DatiFatturaHeader', False, pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 23, 6), )

    DatiFatturaHeader = property(
        __DatiFatturaHeader.value, __DatiFatturaHeader.set, None, None)

    # Element DTE uses Python identifier DTE
    __DTE = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(
        None, 'DTE'), 'DTE', '__httpivaservizi_agenziaentrate_gov_itdocsxsdfatturev2_0_DatiFatturaType_DTE', False, pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 25, 5), )

    DTE = property(__DTE.value, __DTE.set, None, None)

    # Element DTR uses Python identifier DTR
    __DTR = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(
        None, 'DTR'), 'DTR', '__httpivaservizi_agenziaentrate_gov_itdocsxsdfatturev2_0_DatiFatturaType_DTR', False, pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 26, 5), )

    DTR = property(__DTR.value, __DTR.set, None, None)

    # Element ANN uses Python identifier ANN
    __ANN = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(
        None, 'ANN'), 'ANN', '__httpivaservizi_agenziaentrate_gov_itdocsxsdfatturev2_0_DatiFatturaType_ANN', False, pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 27, 5), )

    ANN = property(__ANN.value, __ANN.set, None, None)

    # Element {http://www.w3.org/2000/09/xmldsig#}Signature uses Python
    # identifier Signature
    __Signature = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(_Namespace_ds, 'Signature'), 'Signature', '__httpivaservizi_agenziaentrate_gov_itdocsxsdfatturev2_0_DatiFatturaType_httpwww_w3_org200009xmldsigSignature',
                                                          False, pyxb.utils.utility.Location('http://www.w3.org/TR/2002/REC-xmldsig-core-20020212/xmldsig-core-schema.xsd', 43, 0), )

    Signature = property(__Signature.value, __Signature.set, None, None)

    # Attribute versione uses Python identifier versione
    __versione = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(
        None, 'versione'), 'versione', '__httpivaservizi_agenziaentrate_gov_itdocsxsdfatturev2_0_DatiFatturaType_versione', VersioneType, required=True)
    __versione._DeclarationLocation = pyxb.utils.utility.Location(
        '../data/datifatture/DatiFatturav2.0.xsd', 31, 4)
    __versione._UseLocation = pyxb.utils.utility.Location(
        '../data/datifatture/DatiFatturav2.0.xsd', 31, 4)

    versione = property(__versione.value, __versione.set, None, None)

    _ElementMap.update({
        __DatiFatturaHeader.name(): __DatiFatturaHeader,
        __DTE.name(): __DTE,
        __DTR.name(): __DTR,
        __ANN.name(): __ANN,
        __Signature.name(): __Signature
    })
    _AttributeMap.update({
        __versione.name(): __versione
    })


Namespace.addCategoryObject('typeBinding', 'DatiFatturaType', DatiFatturaType)


DatiFattura = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'DatiFattura'), DatiFatturaType,
                                         documentation='XML schema fatture emesse e ricevute ex D.Lgs. 127/205 (art.1, c.3) 2.0', location=pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 12, 2))
Namespace.addCategoryObject(
    'elementBinding', DatiFattura.name().localName(), DatiFattura)


DatiFatturaHeaderType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'ProgressivoInvio'), String10Type,
                                                             scope=DatiFatturaHeaderType, location=pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 36, 6)))

DatiFatturaHeaderType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'Dichiarante'), DichiaranteType,
                                                             scope=DatiFatturaHeaderType, location=pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 37, 6)))

DatiFatturaHeaderType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'IdSistema'), CodiceFiscaleType,
                                                             scope=DatiFatturaHeaderType, location=pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 38, 6)))


def _BuildAutomaton():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton
    del _BuildAutomaton
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location(
        '../data/datifatture/DatiFatturav2.0.xsd', 36, 6))
    counters.add(cc_0)
    cc_1 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location(
        '../data/datifatture/DatiFatturav2.0.xsd', 37, 6))
    counters.add(cc_1)
    cc_2 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location(
        '../data/datifatture/DatiFatturav2.0.xsd', 38, 6))
    counters.add(cc_2)
    states = []
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_0, False))
    symbol = pyxb.binding.content.ElementUse(DatiFatturaHeaderType._UseForTag(pyxb.namespace.ExpandedName(
        None, 'ProgressivoInvio')), pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 36, 6))
    st_0 = fac.State(symbol, is_initial=True,
                     final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_1, False))
    symbol = pyxb.binding.content.ElementUse(DatiFatturaHeaderType._UseForTag(pyxb.namespace.ExpandedName(
        None, 'Dichiarante')), pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 37, 6))
    st_1 = fac.State(symbol, is_initial=True,
                     final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(DatiFatturaHeaderType._UseForTag(pyxb.namespace.ExpandedName(
        None, 'IdSistema')), pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 38, 6))
    st_2 = fac.State(symbol, is_initial=True,
                     final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    transitions = []
    transitions.append(fac.Transition(st_0, [
        fac.UpdateInstruction(cc_0, True)]))
    transitions.append(fac.Transition(st_1, [
        fac.UpdateInstruction(cc_0, False)]))
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_0, False)]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_1, [
        fac.UpdateInstruction(cc_1, True)]))
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_1, False)]))
    st_1._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_2, True)]))
    st_2._set_transitionSet(transitions)
    return fac.Automaton(states, counters, True, containing_state=None)


DatiFatturaHeaderType._Automaton = _BuildAutomaton()


DichiaranteType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'CodiceFiscale'), CodiceFiscaleType,
                                                       scope=DichiaranteType, location=pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 44, 6)))

DichiaranteType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'Carica'), CaricaType,
                                                       scope=DichiaranteType, location=pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 45, 6)))


def _BuildAutomaton_():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_
    del _BuildAutomaton_
    import pyxb.utils.fac as fac

    counters = set()
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(DichiaranteType._UseForTag(pyxb.namespace.ExpandedName(
        None, 'CodiceFiscale')), pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 44, 6))
    st_0 = fac.State(symbol, is_initial=True,
                     final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(DichiaranteType._UseForTag(pyxb.namespace.ExpandedName(
        None, 'Carica')), pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 45, 6))
    st_1 = fac.State(symbol, is_initial=False,
                     final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    transitions = []
    transitions.append(fac.Transition(st_1, [
    ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    st_1._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)


DichiaranteType._Automaton = _BuildAutomaton_()


DTEType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'CedentePrestatoreDTE'), CedentePrestatoreDTEType,
                                               scope=DTEType, location=pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 51, 6)))

DTEType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'CessionarioCommittenteDTE'),
                                               CessionarioCommittenteDTEType, scope=DTEType, location=pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 52, 6)))

DTEType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'Rettifica'), RettificaType,
                                               scope=DTEType, location=pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 53, 6)))


def _BuildAutomaton_2():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_2
    del _BuildAutomaton_2
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=1, max=1000, metadata=pyxb.utils.utility.Location(
        '../data/datifatture/DatiFatturav2.0.xsd', 52, 6))
    counters.add(cc_0)
    cc_1 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location(
        '../data/datifatture/DatiFatturav2.0.xsd', 53, 6))
    counters.add(cc_1)
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(DTEType._UseForTag(pyxb.namespace.ExpandedName(
        None, 'CedentePrestatoreDTE')), pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 51, 6))
    st_0 = fac.State(symbol, is_initial=True,
                     final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_0, False))
    symbol = pyxb.binding.content.ElementUse(DTEType._UseForTag(pyxb.namespace.ExpandedName(
        None, 'CessionarioCommittenteDTE')), pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 52, 6))
    st_1 = fac.State(symbol, is_initial=False,
                     final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_1, False))
    symbol = pyxb.binding.content.ElementUse(DTEType._UseForTag(pyxb.namespace.ExpandedName(
        None, 'Rettifica')), pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 53, 6))
    st_2 = fac.State(symbol, is_initial=False,
                     final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    transitions = []
    transitions.append(fac.Transition(st_1, [
    ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_1, [
        fac.UpdateInstruction(cc_0, True)]))
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_0, False)]))
    st_1._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_1, True)]))
    st_2._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)


DTEType._Automaton = _BuildAutomaton_2()


DTRType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'CessionarioCommittenteDTR'),
                                               CessionarioCommittenteDTRType, scope=DTRType, location=pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 59, 6)))

DTRType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'CedentePrestatoreDTR'), CedentePrestatoreDTRType,
                                               scope=DTRType, location=pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 60, 6)))

DTRType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'Rettifica'), RettificaType,
                                               scope=DTRType, location=pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 61, 6)))


def _BuildAutomaton_3():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_3
    del _BuildAutomaton_3
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=1, max=1000, metadata=pyxb.utils.utility.Location(
        '../data/datifatture/DatiFatturav2.0.xsd', 60, 6))
    counters.add(cc_0)
    cc_1 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location(
        '../data/datifatture/DatiFatturav2.0.xsd', 61, 6))
    counters.add(cc_1)
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(DTRType._UseForTag(pyxb.namespace.ExpandedName(
        None, 'CessionarioCommittenteDTR')), pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 59, 6))
    st_0 = fac.State(symbol, is_initial=True,
                     final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_0, False))
    symbol = pyxb.binding.content.ElementUse(DTRType._UseForTag(pyxb.namespace.ExpandedName(
        None, 'CedentePrestatoreDTR')), pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 60, 6))
    st_1 = fac.State(symbol, is_initial=False,
                     final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_1, False))
    symbol = pyxb.binding.content.ElementUse(DTRType._UseForTag(pyxb.namespace.ExpandedName(
        None, 'Rettifica')), pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 61, 6))
    st_2 = fac.State(symbol, is_initial=False,
                     final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    transitions = []
    transitions.append(fac.Transition(st_1, [
    ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_1, [
        fac.UpdateInstruction(cc_0, True)]))
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_0, False)]))
    st_1._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_1, True)]))
    st_2._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)


DTRType._Automaton = _BuildAutomaton_3()


ANNType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'IdFile'), String18Type,
                                               scope=ANNType, location=pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 67, 6)))

ANNType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'Posizione'), PosizioneType,
                                               scope=ANNType, location=pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 68, 6)))


def _BuildAutomaton_4():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_4
    del _BuildAutomaton_4
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location(
        '../data/datifatture/DatiFatturav2.0.xsd', 68, 6))
    counters.add(cc_0)
    states = []
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(ANNType._UseForTag(pyxb.namespace.ExpandedName(
        None, 'IdFile')), pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 67, 6))
    st_0 = fac.State(symbol, is_initial=True,
                     final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_0, False))
    symbol = pyxb.binding.content.ElementUse(ANNType._UseForTag(pyxb.namespace.ExpandedName(
        None, 'Posizione')), pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 68, 6))
    st_1 = fac.State(symbol, is_initial=False,
                     final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    transitions = []
    transitions.append(fac.Transition(st_1, [
    ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_1, [
        fac.UpdateInstruction(cc_0, True)]))
    st_1._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)


ANNType._Automaton = _BuildAutomaton_4()


CedentePrestatoreDTEType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'IdentificativiFiscali'), IdentificativiFiscaliITType,
                                                                scope=CedentePrestatoreDTEType, location=pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 75, 6)))

CedentePrestatoreDTEType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'AltriDatiIdentificativi'), AltriDatiIdentificativiNoSedeType,
                                                                scope=CedentePrestatoreDTEType, location=pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 76, 6)))


def _BuildAutomaton_5():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_5
    del _BuildAutomaton_5
    import pyxb.utils.fac as fac

    counters = set()
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(CedentePrestatoreDTEType._UseForTag(pyxb.namespace.ExpandedName(
        None, 'IdentificativiFiscali')), pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 75, 6))
    st_0 = fac.State(symbol, is_initial=True,
                     final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(CedentePrestatoreDTEType._UseForTag(pyxb.namespace.ExpandedName(
        None, 'AltriDatiIdentificativi')), pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 76, 6))
    st_1 = fac.State(symbol, is_initial=False,
                     final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    transitions = []
    transitions.append(fac.Transition(st_1, [
    ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    st_1._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)


CedentePrestatoreDTEType._Automaton = _BuildAutomaton_5()


CedentePrestatoreDTRType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'IdentificativiFiscali'), IdentificativiFiscaliType,
                                                                scope=CedentePrestatoreDTRType, location=pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 83, 6)))

CedentePrestatoreDTRType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'AltriDatiIdentificativi'), AltriDatiIdentificativiNoCAPType,
                                                                scope=CedentePrestatoreDTRType, location=pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 84, 6)))

CedentePrestatoreDTRType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'DatiFatturaBodyDTR'), DatiFatturaBodyDTRType,
                                                                scope=CedentePrestatoreDTRType, location=pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 85, 6)))


def _BuildAutomaton_6():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_6
    del _BuildAutomaton_6
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=1, max=1000, metadata=pyxb.utils.utility.Location(
        '../data/datifatture/DatiFatturav2.0.xsd', 85, 6))
    counters.add(cc_0)
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(CedentePrestatoreDTRType._UseForTag(pyxb.namespace.ExpandedName(
        None, 'IdentificativiFiscali')), pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 83, 6))
    st_0 = fac.State(symbol, is_initial=True,
                     final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(CedentePrestatoreDTRType._UseForTag(pyxb.namespace.ExpandedName(
        None, 'AltriDatiIdentificativi')), pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 84, 6))
    st_1 = fac.State(symbol, is_initial=False,
                     final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_0, False))
    symbol = pyxb.binding.content.ElementUse(CedentePrestatoreDTRType._UseForTag(pyxb.namespace.ExpandedName(
        None, 'DatiFatturaBodyDTR')), pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 85, 6))
    st_2 = fac.State(symbol, is_initial=False,
                     final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    transitions = []
    transitions.append(fac.Transition(st_1, [
    ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
    ]))
    st_1._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_0, True)]))
    st_2._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)


CedentePrestatoreDTRType._Automaton = _BuildAutomaton_6()


CessionarioCommittenteDTEType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'IdentificativiFiscali'), IdentificativiFiscaliNoIVAType,
                                                                     scope=CessionarioCommittenteDTEType, location=pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 92, 6)))

CessionarioCommittenteDTEType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'AltriDatiIdentificativi'), AltriDatiIdentificativiNoCAPType,
                                                                     scope=CessionarioCommittenteDTEType, location=pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 93, 6)))

CessionarioCommittenteDTEType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'DatiFatturaBodyDTE'), DatiFatturaBodyDTEType,
                                                                     scope=CessionarioCommittenteDTEType, location=pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 94, 6)))


def _BuildAutomaton_7():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_7
    del _BuildAutomaton_7
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location(
        '../data/datifatture/DatiFatturav2.0.xsd', 92, 6))
    counters.add(cc_0)
    cc_1 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location(
        '../data/datifatture/DatiFatturav2.0.xsd', 93, 6))
    counters.add(cc_1)
    cc_2 = fac.CounterCondition(min=1, max=1000, metadata=pyxb.utils.utility.Location(
        '../data/datifatture/DatiFatturav2.0.xsd', 94, 6))
    counters.add(cc_2)
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(CessionarioCommittenteDTEType._UseForTag(pyxb.namespace.ExpandedName(
        None, 'IdentificativiFiscali')), pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 92, 6))
    st_0 = fac.State(symbol, is_initial=True,
                     final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(CessionarioCommittenteDTEType._UseForTag(pyxb.namespace.ExpandedName(
        None, 'AltriDatiIdentificativi')), pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 93, 6))
    st_1 = fac.State(symbol, is_initial=True,
                     final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(CessionarioCommittenteDTEType._UseForTag(pyxb.namespace.ExpandedName(
        None, 'DatiFatturaBodyDTE')), pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 94, 6))
    st_2 = fac.State(symbol, is_initial=True,
                     final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    transitions = []
    transitions.append(fac.Transition(st_0, [
        fac.UpdateInstruction(cc_0, True)]))
    transitions.append(fac.Transition(st_1, [
        fac.UpdateInstruction(cc_0, False)]))
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_0, False)]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_1, [
        fac.UpdateInstruction(cc_1, True)]))
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_1, False)]))
    st_1._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_2, True)]))
    st_2._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)


CessionarioCommittenteDTEType._Automaton = _BuildAutomaton_7()


CessionarioCommittenteDTRType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'IdentificativiFiscali'), IdentificativiFiscaliITType,
                                                                     scope=CessionarioCommittenteDTRType, location=pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 101, 6)))

CessionarioCommittenteDTRType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'AltriDatiIdentificativi'), AltriDatiIdentificativiNoSedeType,
                                                                     scope=CessionarioCommittenteDTRType, location=pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 102, 6)))


def _BuildAutomaton_8():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_8
    del _BuildAutomaton_8
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location(
        '../data/datifatture/DatiFatturav2.0.xsd', 102, 6))
    counters.add(cc_0)
    states = []
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(CessionarioCommittenteDTRType._UseForTag(pyxb.namespace.ExpandedName(
        None, 'IdentificativiFiscali')), pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 101, 6))
    st_0 = fac.State(symbol, is_initial=True,
                     final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_0, False))
    symbol = pyxb.binding.content.ElementUse(CessionarioCommittenteDTRType._UseForTag(pyxb.namespace.ExpandedName(
        None, 'AltriDatiIdentificativi')), pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 102, 6))
    st_1 = fac.State(symbol, is_initial=False,
                     final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    transitions = []
    transitions.append(fac.Transition(st_1, [
    ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_1, [
        fac.UpdateInstruction(cc_0, True)]))
    st_1._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)


CessionarioCommittenteDTRType._Automaton = _BuildAutomaton_8()


DatiFatturaBodyDTEType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'DatiGenerali'), DatiGeneraliType,
                                                              scope=DatiFatturaBodyDTEType, location=pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 108, 6)))

DatiFatturaBodyDTEType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'DatiRiepilogo'), DatiRiepilogoType,
                                                              scope=DatiFatturaBodyDTEType, location=pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 109, 6)))


def _BuildAutomaton_9():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_9
    del _BuildAutomaton_9
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=1, max=1000, metadata=pyxb.utils.utility.Location(
        '../data/datifatture/DatiFatturav2.0.xsd', 109, 6))
    counters.add(cc_0)
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(DatiFatturaBodyDTEType._UseForTag(pyxb.namespace.ExpandedName(
        None, 'DatiGenerali')), pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 108, 6))
    st_0 = fac.State(symbol, is_initial=True,
                     final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_0, False))
    symbol = pyxb.binding.content.ElementUse(DatiFatturaBodyDTEType._UseForTag(pyxb.namespace.ExpandedName(
        None, 'DatiRiepilogo')), pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 109, 6))
    st_1 = fac.State(symbol, is_initial=False,
                     final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    transitions = []
    transitions.append(fac.Transition(st_1, [
    ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_1, [
        fac.UpdateInstruction(cc_0, True)]))
    st_1._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)


DatiFatturaBodyDTEType._Automaton = _BuildAutomaton_9()


DatiFatturaBodyDTRType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'DatiGenerali'), DatiGeneraliDTRType,
                                                              scope=DatiFatturaBodyDTRType, location=pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 115, 6)))

DatiFatturaBodyDTRType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'DatiRiepilogo'), DatiRiepilogoType,
                                                              scope=DatiFatturaBodyDTRType, location=pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 116, 6)))


def _BuildAutomaton_10():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_10
    del _BuildAutomaton_10
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=1, max=1000, metadata=pyxb.utils.utility.Location(
        '../data/datifatture/DatiFatturav2.0.xsd', 116, 6))
    counters.add(cc_0)
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(DatiFatturaBodyDTRType._UseForTag(pyxb.namespace.ExpandedName(
        None, 'DatiGenerali')), pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 115, 6))
    st_0 = fac.State(symbol, is_initial=True,
                     final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_0, False))
    symbol = pyxb.binding.content.ElementUse(DatiFatturaBodyDTRType._UseForTag(pyxb.namespace.ExpandedName(
        None, 'DatiRiepilogo')), pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 116, 6))
    st_1 = fac.State(symbol, is_initial=False,
                     final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    transitions = []
    transitions.append(fac.Transition(st_1, [
    ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_1, [
        fac.UpdateInstruction(cc_0, True)]))
    st_1._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)


DatiFatturaBodyDTRType._Automaton = _BuildAutomaton_10()


RettificaType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'IdFile'), String18Type,
                                                     scope=RettificaType, location=pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 122, 6)))

RettificaType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'Posizione'), PosizioneType,
                                                     scope=RettificaType, location=pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 123, 6)))


def _BuildAutomaton_11():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_11
    del _BuildAutomaton_11
    import pyxb.utils.fac as fac

    counters = set()
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(RettificaType._UseForTag(pyxb.namespace.ExpandedName(
        None, 'IdFile')), pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 122, 6))
    st_0 = fac.State(symbol, is_initial=True,
                     final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(RettificaType._UseForTag(pyxb.namespace.ExpandedName(
        None, 'Posizione')), pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 123, 6))
    st_1 = fac.State(symbol, is_initial=False,
                     final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    transitions = []
    transitions.append(fac.Transition(st_1, [
    ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    st_1._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)


RettificaType._Automaton = _BuildAutomaton_11()


IdentificativiFiscaliType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'IdFiscaleIVA'), IdFiscaleType,
                                                                 scope=IdentificativiFiscaliType, location=pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 129, 6)))

IdentificativiFiscaliType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'CodiceFiscale'), CodiceFiscaleType,
                                                                 scope=IdentificativiFiscaliType, location=pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 130, 6)))


def _BuildAutomaton_12():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_12
    del _BuildAutomaton_12
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location(
        '../data/datifatture/DatiFatturav2.0.xsd', 130, 6))
    counters.add(cc_0)
    states = []
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(IdentificativiFiscaliType._UseForTag(pyxb.namespace.ExpandedName(
        None, 'IdFiscaleIVA')), pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 129, 6))
    st_0 = fac.State(symbol, is_initial=True,
                     final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_0, False))
    symbol = pyxb.binding.content.ElementUse(IdentificativiFiscaliType._UseForTag(pyxb.namespace.ExpandedName(
        None, 'CodiceFiscale')), pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 130, 6))
    st_1 = fac.State(symbol, is_initial=False,
                     final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    transitions = []
    transitions.append(fac.Transition(st_1, [
    ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_1, [
        fac.UpdateInstruction(cc_0, True)]))
    st_1._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)


IdentificativiFiscaliType._Automaton = _BuildAutomaton_12()


IdentificativiFiscaliITType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'IdFiscaleIVA'), IdFiscaleITType,
                                                                   scope=IdentificativiFiscaliITType, location=pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 136, 6)))

IdentificativiFiscaliITType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'CodiceFiscale'), CodiceFiscaleType,
                                                                   scope=IdentificativiFiscaliITType, location=pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 137, 6)))


def _BuildAutomaton_13():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_13
    del _BuildAutomaton_13
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location(
        '../data/datifatture/DatiFatturav2.0.xsd', 137, 6))
    counters.add(cc_0)
    states = []
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(IdentificativiFiscaliITType._UseForTag(pyxb.namespace.ExpandedName(
        None, 'IdFiscaleIVA')), pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 136, 6))
    st_0 = fac.State(symbol, is_initial=True,
                     final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_0, False))
    symbol = pyxb.binding.content.ElementUse(IdentificativiFiscaliITType._UseForTag(pyxb.namespace.ExpandedName(
        None, 'CodiceFiscale')), pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 137, 6))
    st_1 = fac.State(symbol, is_initial=False,
                     final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    transitions = []
    transitions.append(fac.Transition(st_1, [
    ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_1, [
        fac.UpdateInstruction(cc_0, True)]))
    st_1._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)


IdentificativiFiscaliITType._Automaton = _BuildAutomaton_13()


IdentificativiFiscaliNoIVAType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(
    None, 'IdFiscaleIVA'), IdFiscaleType, scope=IdentificativiFiscaliNoIVAType, location=pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 143, 6)))

IdentificativiFiscaliNoIVAType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(
    None, 'CodiceFiscale'), CodiceFiscaleType, scope=IdentificativiFiscaliNoIVAType, location=pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 144, 6)))


def _BuildAutomaton_14():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_14
    del _BuildAutomaton_14
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location(
        '../data/datifatture/DatiFatturav2.0.xsd', 143, 6))
    counters.add(cc_0)
    cc_1 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location(
        '../data/datifatture/DatiFatturav2.0.xsd', 144, 6))
    counters.add(cc_1)
    states = []
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_0, False))
    symbol = pyxb.binding.content.ElementUse(IdentificativiFiscaliNoIVAType._UseForTag(pyxb.namespace.ExpandedName(
        None, 'IdFiscaleIVA')), pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 143, 6))
    st_0 = fac.State(symbol, is_initial=True,
                     final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_1, False))
    symbol = pyxb.binding.content.ElementUse(IdentificativiFiscaliNoIVAType._UseForTag(pyxb.namespace.ExpandedName(
        None, 'CodiceFiscale')), pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 144, 6))
    st_1 = fac.State(symbol, is_initial=True,
                     final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    transitions = []
    transitions.append(fac.Transition(st_0, [
        fac.UpdateInstruction(cc_0, True)]))
    transitions.append(fac.Transition(st_1, [
        fac.UpdateInstruction(cc_0, False)]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_1, [
        fac.UpdateInstruction(cc_1, True)]))
    st_1._set_transitionSet(transitions)
    return fac.Automaton(states, counters, True, containing_state=None)


IdentificativiFiscaliNoIVAType._Automaton = _BuildAutomaton_14()


AltriDatiIdentificativiNoSedeType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(
    None, 'Denominazione'), String80LatinType, scope=AltriDatiIdentificativiNoSedeType, location=pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 152, 10)))

AltriDatiIdentificativiNoSedeType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(
    None, 'Nome'), String60LatinType, scope=AltriDatiIdentificativiNoSedeType, location=pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 155, 10)))

AltriDatiIdentificativiNoSedeType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(
    None, 'Cognome'), String60LatinType, scope=AltriDatiIdentificativiNoSedeType, location=pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 156, 10)))

AltriDatiIdentificativiNoSedeType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(
    None, 'Sede'), IndirizzoType, scope=AltriDatiIdentificativiNoSedeType, location=pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 159, 6)))

AltriDatiIdentificativiNoSedeType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(
    None, 'StabileOrganizzazione'), IndirizzoType, scope=AltriDatiIdentificativiNoSedeType, location=pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 160, 3)))

AltriDatiIdentificativiNoSedeType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'RappresentanteFiscale'), RappresentanteFiscaleITType,
                                                                         scope=AltriDatiIdentificativiNoSedeType, location=pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 161, 3)))


def _BuildAutomaton_15():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_15
    del _BuildAutomaton_15
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location(
        '../data/datifatture/DatiFatturav2.0.xsd', 159, 6))
    counters.add(cc_0)
    cc_1 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location(
        '../data/datifatture/DatiFatturav2.0.xsd', 160, 3))
    counters.add(cc_1)
    cc_2 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location(
        '../data/datifatture/DatiFatturav2.0.xsd', 161, 3))
    counters.add(cc_2)
    states = []
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(AltriDatiIdentificativiNoSedeType._UseForTag(pyxb.namespace.ExpandedName(
        None, 'Denominazione')), pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 152, 10))
    st_0 = fac.State(symbol, is_initial=True,
                     final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(AltriDatiIdentificativiNoSedeType._UseForTag(pyxb.namespace.ExpandedName(
        None, 'Nome')), pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 155, 10))
    st_1 = fac.State(symbol, is_initial=True,
                     final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(AltriDatiIdentificativiNoSedeType._UseForTag(pyxb.namespace.ExpandedName(
        None, 'Cognome')), pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 156, 10))
    st_2 = fac.State(symbol, is_initial=False,
                     final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_0, False))
    symbol = pyxb.binding.content.ElementUse(AltriDatiIdentificativiNoSedeType._UseForTag(pyxb.namespace.ExpandedName(
        None, 'Sede')), pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 159, 6))
    st_3 = fac.State(symbol, is_initial=False,
                     final_update=final_update, is_unordered_catenation=False)
    states.append(st_3)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_1, False))
    symbol = pyxb.binding.content.ElementUse(AltriDatiIdentificativiNoSedeType._UseForTag(pyxb.namespace.ExpandedName(
        None, 'StabileOrganizzazione')), pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 160, 3))
    st_4 = fac.State(symbol, is_initial=False,
                     final_update=final_update, is_unordered_catenation=False)
    states.append(st_4)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(AltriDatiIdentificativiNoSedeType._UseForTag(pyxb.namespace.ExpandedName(
        None, 'RappresentanteFiscale')), pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 161, 3))
    st_5 = fac.State(symbol, is_initial=False,
                     final_update=final_update, is_unordered_catenation=False)
    states.append(st_5)
    transitions = []
    transitions.append(fac.Transition(st_3, [
    ]))
    transitions.append(fac.Transition(st_4, [
    ]))
    transitions.append(fac.Transition(st_5, [
    ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
    ]))
    st_1._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
    ]))
    transitions.append(fac.Transition(st_4, [
    ]))
    transitions.append(fac.Transition(st_5, [
    ]))
    st_2._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_0, True)]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_0, False)]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_0, False)]))
    st_3._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_1, True)]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_1, False)]))
    st_4._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, True)]))
    st_5._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)


AltriDatiIdentificativiNoSedeType._Automaton = _BuildAutomaton_15()


AltriDatiIdentificativiNoCAPType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(
    None, 'Denominazione'), String80LatinType, scope=AltriDatiIdentificativiNoCAPType, location=pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 169, 10)))

AltriDatiIdentificativiNoCAPType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(
    None, 'Nome'), String60LatinType, scope=AltriDatiIdentificativiNoCAPType, location=pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 172, 10)))

AltriDatiIdentificativiNoCAPType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(
    None, 'Cognome'), String60LatinType, scope=AltriDatiIdentificativiNoCAPType, location=pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 173, 10)))

AltriDatiIdentificativiNoCAPType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(
    None, 'Sede'), IndirizzoNoCAPType, scope=AltriDatiIdentificativiNoCAPType, location=pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 176, 6)))

AltriDatiIdentificativiNoCAPType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(
    None, 'StabileOrganizzazione'), IndirizzoType, scope=AltriDatiIdentificativiNoCAPType, location=pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 177, 3)))

AltriDatiIdentificativiNoCAPType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'RappresentanteFiscale'), RappresentanteFiscaleType,
                                                                        scope=AltriDatiIdentificativiNoCAPType, location=pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 178, 3)))


def _BuildAutomaton_16():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_16
    del _BuildAutomaton_16
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location(
        '../data/datifatture/DatiFatturav2.0.xsd', 177, 3))
    counters.add(cc_0)
    cc_1 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location(
        '../data/datifatture/DatiFatturav2.0.xsd', 178, 3))
    counters.add(cc_1)
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(AltriDatiIdentificativiNoCAPType._UseForTag(pyxb.namespace.ExpandedName(
        None, 'Denominazione')), pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 169, 10))
    st_0 = fac.State(symbol, is_initial=True,
                     final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(AltriDatiIdentificativiNoCAPType._UseForTag(pyxb.namespace.ExpandedName(
        None, 'Nome')), pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 172, 10))
    st_1 = fac.State(symbol, is_initial=True,
                     final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(AltriDatiIdentificativiNoCAPType._UseForTag(pyxb.namespace.ExpandedName(
        None, 'Cognome')), pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 173, 10))
    st_2 = fac.State(symbol, is_initial=False,
                     final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(AltriDatiIdentificativiNoCAPType._UseForTag(pyxb.namespace.ExpandedName(
        None, 'Sede')), pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 176, 6))
    st_3 = fac.State(symbol, is_initial=False,
                     final_update=final_update, is_unordered_catenation=False)
    states.append(st_3)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_0, False))
    symbol = pyxb.binding.content.ElementUse(AltriDatiIdentificativiNoCAPType._UseForTag(pyxb.namespace.ExpandedName(
        None, 'StabileOrganizzazione')), pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 177, 3))
    st_4 = fac.State(symbol, is_initial=False,
                     final_update=final_update, is_unordered_catenation=False)
    states.append(st_4)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_1, False))
    symbol = pyxb.binding.content.ElementUse(AltriDatiIdentificativiNoCAPType._UseForTag(pyxb.namespace.ExpandedName(
        None, 'RappresentanteFiscale')), pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 178, 3))
    st_5 = fac.State(symbol, is_initial=False,
                     final_update=final_update, is_unordered_catenation=False)
    states.append(st_5)
    transitions = []
    transitions.append(fac.Transition(st_3, [
    ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
    ]))
    st_1._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
    ]))
    st_2._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_4, [
    ]))
    transitions.append(fac.Transition(st_5, [
    ]))
    st_3._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_0, True)]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_0, False)]))
    st_4._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_1, True)]))
    st_5._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)


AltriDatiIdentificativiNoCAPType._Automaton = _BuildAutomaton_16()


IndirizzoNoCAPType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'Indirizzo'), String60LatinType,
                                                          scope=IndirizzoNoCAPType, location=pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 184, 6)))

IndirizzoNoCAPType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'NumeroCivico'), NumeroCivicoType,
                                                          scope=IndirizzoNoCAPType, location=pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 185, 6)))

IndirizzoNoCAPType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(
    None, 'CAP'), CAPType, scope=IndirizzoNoCAPType, location=pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 186, 6)))

IndirizzoNoCAPType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'Comune'), String60LatinType,
                                                          scope=IndirizzoNoCAPType, location=pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 187, 6)))

IndirizzoNoCAPType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'Provincia'), ProvinciaType,
                                                          scope=IndirizzoNoCAPType, location=pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 188, 6)))

IndirizzoNoCAPType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'Nazione'), NazioneType,
                                                          scope=IndirizzoNoCAPType, location=pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 189, 6)))


def _BuildAutomaton_17():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_17
    del _BuildAutomaton_17
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location(
        '../data/datifatture/DatiFatturav2.0.xsd', 185, 6))
    counters.add(cc_0)
    cc_1 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location(
        '../data/datifatture/DatiFatturav2.0.xsd', 186, 6))
    counters.add(cc_1)
    cc_2 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location(
        '../data/datifatture/DatiFatturav2.0.xsd', 188, 6))
    counters.add(cc_2)
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(IndirizzoNoCAPType._UseForTag(pyxb.namespace.ExpandedName(
        None, 'Indirizzo')), pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 184, 6))
    st_0 = fac.State(symbol, is_initial=True,
                     final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(IndirizzoNoCAPType._UseForTag(pyxb.namespace.ExpandedName(
        None, 'NumeroCivico')), pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 185, 6))
    st_1 = fac.State(symbol, is_initial=False,
                     final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(IndirizzoNoCAPType._UseForTag(pyxb.namespace.ExpandedName(
        None, 'CAP')), pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 186, 6))
    st_2 = fac.State(symbol, is_initial=False,
                     final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(IndirizzoNoCAPType._UseForTag(pyxb.namespace.ExpandedName(
        None, 'Comune')), pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 187, 6))
    st_3 = fac.State(symbol, is_initial=False,
                     final_update=final_update, is_unordered_catenation=False)
    states.append(st_3)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(IndirizzoNoCAPType._UseForTag(pyxb.namespace.ExpandedName(
        None, 'Provincia')), pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 188, 6))
    st_4 = fac.State(symbol, is_initial=False,
                     final_update=final_update, is_unordered_catenation=False)
    states.append(st_4)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(IndirizzoNoCAPType._UseForTag(pyxb.namespace.ExpandedName(
        None, 'Nazione')), pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 189, 6))
    st_5 = fac.State(symbol, is_initial=False,
                     final_update=final_update, is_unordered_catenation=False)
    states.append(st_5)
    transitions = []
    transitions.append(fac.Transition(st_1, [
    ]))
    transitions.append(fac.Transition(st_2, [
    ]))
    transitions.append(fac.Transition(st_3, [
    ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_1, [
        fac.UpdateInstruction(cc_0, True)]))
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_0, False)]))
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_0, False)]))
    st_1._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_1, True)]))
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_1, False)]))
    st_2._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_4, [
    ]))
    transitions.append(fac.Transition(st_5, [
    ]))
    st_3._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True)]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, False)]))
    st_4._set_transitionSet(transitions)
    transitions = []
    st_5._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)


IndirizzoNoCAPType._Automaton = _BuildAutomaton_17()


IndirizzoType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'Indirizzo'), String60LatinType,
                                                     scope=IndirizzoType, location=pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 195, 6)))

IndirizzoType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'NumeroCivico'), NumeroCivicoType,
                                                     scope=IndirizzoType, location=pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 196, 6)))

IndirizzoType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'CAP'), CAPType,
                                                     scope=IndirizzoType, location=pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 197, 6)))

IndirizzoType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'Comune'), String60LatinType,
                                                     scope=IndirizzoType, location=pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 198, 6)))

IndirizzoType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'Provincia'), ProvinciaType,
                                                     scope=IndirizzoType, location=pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 199, 6)))

IndirizzoType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'Nazione'), NazioneType,
                                                     scope=IndirizzoType, location=pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 200, 6)))


def _BuildAutomaton_18():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_18
    del _BuildAutomaton_18
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location(
        '../data/datifatture/DatiFatturav2.0.xsd', 196, 6))
    counters.add(cc_0)
    cc_1 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location(
        '../data/datifatture/DatiFatturav2.0.xsd', 199, 6))
    counters.add(cc_1)
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(IndirizzoType._UseForTag(pyxb.namespace.ExpandedName(
        None, 'Indirizzo')), pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 195, 6))
    st_0 = fac.State(symbol, is_initial=True,
                     final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(IndirizzoType._UseForTag(pyxb.namespace.ExpandedName(
        None, 'NumeroCivico')), pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 196, 6))
    st_1 = fac.State(symbol, is_initial=False,
                     final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(IndirizzoType._UseForTag(pyxb.namespace.ExpandedName(
        None, 'CAP')), pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 197, 6))
    st_2 = fac.State(symbol, is_initial=False,
                     final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(IndirizzoType._UseForTag(pyxb.namespace.ExpandedName(
        None, 'Comune')), pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 198, 6))
    st_3 = fac.State(symbol, is_initial=False,
                     final_update=final_update, is_unordered_catenation=False)
    states.append(st_3)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(IndirizzoType._UseForTag(pyxb.namespace.ExpandedName(
        None, 'Provincia')), pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 199, 6))
    st_4 = fac.State(symbol, is_initial=False,
                     final_update=final_update, is_unordered_catenation=False)
    states.append(st_4)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(IndirizzoType._UseForTag(pyxb.namespace.ExpandedName(
        None, 'Nazione')), pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 200, 6))
    st_5 = fac.State(symbol, is_initial=False,
                     final_update=final_update, is_unordered_catenation=False)
    states.append(st_5)
    transitions = []
    transitions.append(fac.Transition(st_1, [
    ]))
    transitions.append(fac.Transition(st_2, [
    ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_1, [
        fac.UpdateInstruction(cc_0, True)]))
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_0, False)]))
    st_1._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
    ]))
    st_2._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_4, [
    ]))
    transitions.append(fac.Transition(st_5, [
    ]))
    st_3._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_1, True)]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_1, False)]))
    st_4._set_transitionSet(transitions)
    transitions = []
    st_5._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)


IndirizzoType._Automaton = _BuildAutomaton_18()


RappresentanteFiscaleType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'IdFiscaleIVA'), IdFiscaleType,
                                                                 scope=RappresentanteFiscaleType, location=pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 206, 6)))

RappresentanteFiscaleType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'Denominazione'), String80LatinType,
                                                                 scope=RappresentanteFiscaleType, location=pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 209, 10)))

RappresentanteFiscaleType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'Nome'), String60LatinType,
                                                                 scope=RappresentanteFiscaleType, location=pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 212, 10)))

RappresentanteFiscaleType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'Cognome'), String60LatinType,
                                                                 scope=RappresentanteFiscaleType, location=pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 213, 10)))


def _BuildAutomaton_19():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_19
    del _BuildAutomaton_19
    import pyxb.utils.fac as fac

    counters = set()
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(RappresentanteFiscaleType._UseForTag(pyxb.namespace.ExpandedName(
        None, 'IdFiscaleIVA')), pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 206, 6))
    st_0 = fac.State(symbol, is_initial=True,
                     final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(RappresentanteFiscaleType._UseForTag(pyxb.namespace.ExpandedName(
        None, 'Denominazione')), pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 209, 10))
    st_1 = fac.State(symbol, is_initial=False,
                     final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(RappresentanteFiscaleType._UseForTag(pyxb.namespace.ExpandedName(
        None, 'Nome')), pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 212, 10))
    st_2 = fac.State(symbol, is_initial=False,
                     final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(RappresentanteFiscaleType._UseForTag(pyxb.namespace.ExpandedName(
        None, 'Cognome')), pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 213, 10))
    st_3 = fac.State(symbol, is_initial=False,
                     final_update=final_update, is_unordered_catenation=False)
    states.append(st_3)
    transitions = []
    transitions.append(fac.Transition(st_1, [
    ]))
    transitions.append(fac.Transition(st_2, [
    ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    st_1._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
    ]))
    st_2._set_transitionSet(transitions)
    transitions = []
    st_3._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)


RappresentanteFiscaleType._Automaton = _BuildAutomaton_19()


RappresentanteFiscaleITType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'IdFiscaleIVA'), IdFiscaleITIvaType,
                                                                   scope=RappresentanteFiscaleITType, location=pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 221, 6)))

RappresentanteFiscaleITType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'Denominazione'), String80LatinType,
                                                                   scope=RappresentanteFiscaleITType, location=pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 224, 10)))

RappresentanteFiscaleITType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(
    None, 'Nome'), String60LatinType, scope=RappresentanteFiscaleITType, location=pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 227, 10)))

RappresentanteFiscaleITType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'Cognome'), String60LatinType,
                                                                   scope=RappresentanteFiscaleITType, location=pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 228, 10)))


def _BuildAutomaton_20():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_20
    del _BuildAutomaton_20
    import pyxb.utils.fac as fac

    counters = set()
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(RappresentanteFiscaleITType._UseForTag(pyxb.namespace.ExpandedName(
        None, 'IdFiscaleIVA')), pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 221, 6))
    st_0 = fac.State(symbol, is_initial=True,
                     final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(RappresentanteFiscaleITType._UseForTag(pyxb.namespace.ExpandedName(
        None, 'Denominazione')), pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 224, 10))
    st_1 = fac.State(symbol, is_initial=False,
                     final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(RappresentanteFiscaleITType._UseForTag(pyxb.namespace.ExpandedName(
        None, 'Nome')), pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 227, 10))
    st_2 = fac.State(symbol, is_initial=False,
                     final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(RappresentanteFiscaleITType._UseForTag(pyxb.namespace.ExpandedName(
        None, 'Cognome')), pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 228, 10))
    st_3 = fac.State(symbol, is_initial=False,
                     final_update=final_update, is_unordered_catenation=False)
    states.append(st_3)
    transitions = []
    transitions.append(fac.Transition(st_1, [
    ]))
    transitions.append(fac.Transition(st_2, [
    ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    st_1._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
    ]))
    st_2._set_transitionSet(transitions)
    transitions = []
    st_3._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)


RappresentanteFiscaleITType._Automaton = _BuildAutomaton_20()


DatiGeneraliType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'TipoDocumento'), TipoDocumentoType,
                                                        scope=DatiGeneraliType, location=pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 236, 6)))

DatiGeneraliType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'Data'), DataFatturaType,
                                                        scope=DatiGeneraliType, location=pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 237, 6)))

DatiGeneraliType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'Numero'), String20Type,
                                                        scope=DatiGeneraliType, location=pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 238, 6)))


def _BuildAutomaton_21():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_21
    del _BuildAutomaton_21
    import pyxb.utils.fac as fac

    counters = set()
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(DatiGeneraliType._UseForTag(pyxb.namespace.ExpandedName(
        None, 'TipoDocumento')), pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 236, 6))
    st_0 = fac.State(symbol, is_initial=True,
                     final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(DatiGeneraliType._UseForTag(pyxb.namespace.ExpandedName(
        None, 'Data')), pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 237, 6))
    st_1 = fac.State(symbol, is_initial=False,
                     final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(DatiGeneraliType._UseForTag(pyxb.namespace.ExpandedName(
        None, 'Numero')), pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 238, 6))
    st_2 = fac.State(symbol, is_initial=False,
                     final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    transitions = []
    transitions.append(fac.Transition(st_1, [
    ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
    ]))
    st_1._set_transitionSet(transitions)
    transitions = []
    st_2._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)


DatiGeneraliType._Automaton = _BuildAutomaton_21()


DatiGeneraliDTRType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'TipoDocumento'), TipoDocumentoType,
                                                           scope=DatiGeneraliDTRType, location=pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 244, 6)))

DatiGeneraliDTRType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'Data'), DataFatturaType,
                                                           scope=DatiGeneraliDTRType, location=pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 245, 6)))

DatiGeneraliDTRType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'Numero'), String20Type,
                                                           scope=DatiGeneraliDTRType, location=pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 246, 6)))

DatiGeneraliDTRType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'DataRegistrazione'), DataFatturaType,
                                                           scope=DatiGeneraliDTRType, location=pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 247, 6)))


def _BuildAutomaton_22():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_22
    del _BuildAutomaton_22
    import pyxb.utils.fac as fac

    counters = set()
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(DatiGeneraliDTRType._UseForTag(pyxb.namespace.ExpandedName(
        None, 'TipoDocumento')), pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 244, 6))
    st_0 = fac.State(symbol, is_initial=True,
                     final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(DatiGeneraliDTRType._UseForTag(pyxb.namespace.ExpandedName(
        None, 'Data')), pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 245, 6))
    st_1 = fac.State(symbol, is_initial=False,
                     final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(DatiGeneraliDTRType._UseForTag(pyxb.namespace.ExpandedName(
        None, 'Numero')), pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 246, 6))
    st_2 = fac.State(symbol, is_initial=False,
                     final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(DatiGeneraliDTRType._UseForTag(pyxb.namespace.ExpandedName(
        None, 'DataRegistrazione')), pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 247, 6))
    st_3 = fac.State(symbol, is_initial=False,
                     final_update=final_update, is_unordered_catenation=False)
    states.append(st_3)
    transitions = []
    transitions.append(fac.Transition(st_1, [
    ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
    ]))
    st_1._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
    ]))
    st_2._set_transitionSet(transitions)
    transitions = []
    st_3._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)


DatiGeneraliDTRType._Automaton = _BuildAutomaton_22()


DatiRiepilogoType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'ImponibileImporto'), Amount2DecimalType,
                                                         scope=DatiRiepilogoType, location=pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 253, 6)))

DatiRiepilogoType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'DatiIVA'), DatiIVAType,
                                                         scope=DatiRiepilogoType, location=pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 254, 6)))

DatiRiepilogoType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'Natura'), NaturaType,
                                                         scope=DatiRiepilogoType, location=pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 255, 6)))

DatiRiepilogoType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'Detraibile'), RateType,
                                                         scope=DatiRiepilogoType, location=pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 256, 6)))

DatiRiepilogoType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'Deducibile'), DeducibileType,
                                                         scope=DatiRiepilogoType, location=pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 257, 6)))

DatiRiepilogoType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'EsigibilitaIVA'), EsigibilitaIVAType,
                                                         scope=DatiRiepilogoType, location=pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 258, 6)))


def _BuildAutomaton_23():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_23
    del _BuildAutomaton_23
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location(
        '../data/datifatture/DatiFatturav2.0.xsd', 255, 6))
    counters.add(cc_0)
    cc_1 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location(
        '../data/datifatture/DatiFatturav2.0.xsd', 256, 6))
    counters.add(cc_1)
    cc_2 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location(
        '../data/datifatture/DatiFatturav2.0.xsd', 257, 6))
    counters.add(cc_2)
    cc_3 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location(
        '../data/datifatture/DatiFatturav2.0.xsd', 258, 6))
    counters.add(cc_3)
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(DatiRiepilogoType._UseForTag(pyxb.namespace.ExpandedName(
        None, 'ImponibileImporto')), pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 253, 6))
    st_0 = fac.State(symbol, is_initial=True,
                     final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(DatiRiepilogoType._UseForTag(pyxb.namespace.ExpandedName(
        None, 'DatiIVA')), pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 254, 6))
    st_1 = fac.State(symbol, is_initial=False,
                     final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_0, False))
    symbol = pyxb.binding.content.ElementUse(DatiRiepilogoType._UseForTag(pyxb.namespace.ExpandedName(
        None, 'Natura')), pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 255, 6))
    st_2 = fac.State(symbol, is_initial=False,
                     final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_1, False))
    symbol = pyxb.binding.content.ElementUse(DatiRiepilogoType._UseForTag(pyxb.namespace.ExpandedName(
        None, 'Detraibile')), pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 256, 6))
    st_3 = fac.State(symbol, is_initial=False,
                     final_update=final_update, is_unordered_catenation=False)
    states.append(st_3)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(DatiRiepilogoType._UseForTag(pyxb.namespace.ExpandedName(
        None, 'Deducibile')), pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 257, 6))
    st_4 = fac.State(symbol, is_initial=False,
                     final_update=final_update, is_unordered_catenation=False)
    states.append(st_4)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_3, False))
    symbol = pyxb.binding.content.ElementUse(DatiRiepilogoType._UseForTag(pyxb.namespace.ExpandedName(
        None, 'EsigibilitaIVA')), pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 258, 6))
    st_5 = fac.State(symbol, is_initial=False,
                     final_update=final_update, is_unordered_catenation=False)
    states.append(st_5)
    transitions = []
    transitions.append(fac.Transition(st_1, [
    ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
    ]))
    transitions.append(fac.Transition(st_3, [
    ]))
    transitions.append(fac.Transition(st_4, [
    ]))
    transitions.append(fac.Transition(st_5, [
    ]))
    st_1._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_0, True)]))
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_0, False)]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_0, False)]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_0, False)]))
    st_2._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_1, True)]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_1, False)]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_1, False)]))
    st_3._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True)]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, False)]))
    st_4._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_3, True)]))
    st_5._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)


DatiRiepilogoType._Automaton = _BuildAutomaton_23()


DatiIVAType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'Imposta'), Amount2DecimalType,
                                                   scope=DatiIVAType, location=pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 264, 6)))

DatiIVAType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'Aliquota'), RateType,
                                                   scope=DatiIVAType, location=pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 265, 6)))


def _BuildAutomaton_24():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_24
    del _BuildAutomaton_24
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location(
        '../data/datifatture/DatiFatturav2.0.xsd', 264, 6))
    counters.add(cc_0)
    cc_1 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location(
        '../data/datifatture/DatiFatturav2.0.xsd', 265, 6))
    counters.add(cc_1)
    states = []
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_0, False))
    symbol = pyxb.binding.content.ElementUse(DatiIVAType._UseForTag(pyxb.namespace.ExpandedName(
        None, 'Imposta')), pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 264, 6))
    st_0 = fac.State(symbol, is_initial=True,
                     final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_1, False))
    symbol = pyxb.binding.content.ElementUse(DatiIVAType._UseForTag(pyxb.namespace.ExpandedName(
        None, 'Aliquota')), pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 265, 6))
    st_1 = fac.State(symbol, is_initial=True,
                     final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    transitions = []
    transitions.append(fac.Transition(st_0, [
        fac.UpdateInstruction(cc_0, True)]))
    transitions.append(fac.Transition(st_1, [
        fac.UpdateInstruction(cc_0, False)]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_1, [
        fac.UpdateInstruction(cc_1, True)]))
    st_1._set_transitionSet(transitions)
    return fac.Automaton(states, counters, True, containing_state=None)


DatiIVAType._Automaton = _BuildAutomaton_24()


IdFiscaleType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'IdPaese'), NazioneType,
                                                     scope=IdFiscaleType, location=pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 271, 3)))

IdFiscaleType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'IdCodice'), CodiceType,
                                                     scope=IdFiscaleType, location=pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 272, 3)))


def _BuildAutomaton_25():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_25
    del _BuildAutomaton_25
    import pyxb.utils.fac as fac

    counters = set()
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(IdFiscaleType._UseForTag(pyxb.namespace.ExpandedName(
        None, 'IdPaese')), pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 271, 3))
    st_0 = fac.State(symbol, is_initial=True,
                     final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(IdFiscaleType._UseForTag(pyxb.namespace.ExpandedName(
        None, 'IdCodice')), pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 272, 3))
    st_1 = fac.State(symbol, is_initial=False,
                     final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    transitions = []
    transitions.append(fac.Transition(st_1, [
    ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    st_1._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)


IdFiscaleType._Automaton = _BuildAutomaton_25()


IdFiscaleITType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'IdPaese'), NazioneITType,
                                                       scope=IdFiscaleITType, location=pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 278, 3)))

IdFiscaleITType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'IdCodice'), CodiceType,
                                                       scope=IdFiscaleITType, location=pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 279, 3)))


def _BuildAutomaton_26():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_26
    del _BuildAutomaton_26
    import pyxb.utils.fac as fac

    counters = set()
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(IdFiscaleITType._UseForTag(pyxb.namespace.ExpandedName(
        None, 'IdPaese')), pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 278, 3))
    st_0 = fac.State(symbol, is_initial=True,
                     final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(IdFiscaleITType._UseForTag(pyxb.namespace.ExpandedName(
        None, 'IdCodice')), pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 279, 3))
    st_1 = fac.State(symbol, is_initial=False,
                     final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    transitions = []
    transitions.append(fac.Transition(st_1, [
    ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    st_1._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)


IdFiscaleITType._Automaton = _BuildAutomaton_26()


IdFiscaleITIvaType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'IdPaese'), NazioneITType,
                                                          scope=IdFiscaleITIvaType, location=pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 285, 3)))

IdFiscaleITIvaType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'IdCodice'), CodiceIvaType,
                                                          scope=IdFiscaleITIvaType, location=pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 286, 3)))


def _BuildAutomaton_27():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_27
    del _BuildAutomaton_27
    import pyxb.utils.fac as fac

    counters = set()
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(IdFiscaleITIvaType._UseForTag(pyxb.namespace.ExpandedName(
        None, 'IdPaese')), pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 285, 3))
    st_0 = fac.State(symbol, is_initial=True,
                     final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(IdFiscaleITIvaType._UseForTag(pyxb.namespace.ExpandedName(
        None, 'IdCodice')), pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 286, 3))
    st_1 = fac.State(symbol, is_initial=False,
                     final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    transitions = []
    transitions.append(fac.Transition(st_1, [
    ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    st_1._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)


IdFiscaleITIvaType._Automaton = _BuildAutomaton_27()


DatiFatturaType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'DatiFatturaHeader'), DatiFatturaHeaderType,
                                                       scope=DatiFatturaType, location=pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 23, 6)))

DatiFatturaType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'DTE'), DTEType,
                                                       scope=DatiFatturaType, location=pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 25, 5)))

DatiFatturaType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'DTR'), DTRType,
                                                       scope=DatiFatturaType, location=pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 26, 5)))

DatiFatturaType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'ANN'), ANNType,
                                                       scope=DatiFatturaType, location=pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 27, 5)))

DatiFatturaType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(_Namespace_ds, 'Signature'), _ImportedBinding__ds.SignatureType,
                                                       scope=DatiFatturaType, location=pyxb.utils.utility.Location('http://www.w3.org/TR/2002/REC-xmldsig-core-20020212/xmldsig-core-schema.xsd', 43, 0)))


def _BuildAutomaton_28():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_28
    del _BuildAutomaton_28
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location(
        '../data/datifatture/DatiFatturav2.0.xsd', 23, 6))
    counters.add(cc_0)
    cc_1 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location(
        '../data/datifatture/DatiFatturav2.0.xsd', 29, 6))
    counters.add(cc_1)
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(DatiFatturaType._UseForTag(pyxb.namespace.ExpandedName(
        None, 'DatiFatturaHeader')), pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 23, 6))
    st_0 = fac.State(symbol, is_initial=True,
                     final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(DatiFatturaType._UseForTag(pyxb.namespace.ExpandedName(
        None, 'DTE')), pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 25, 5))
    st_1 = fac.State(symbol, is_initial=True,
                     final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(DatiFatturaType._UseForTag(pyxb.namespace.ExpandedName(
        None, 'DTR')), pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 26, 5))
    st_2 = fac.State(symbol, is_initial=True,
                     final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(DatiFatturaType._UseForTag(pyxb.namespace.ExpandedName(
        None, 'ANN')), pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 27, 5))
    st_3 = fac.State(symbol, is_initial=True,
                     final_update=final_update, is_unordered_catenation=False)
    states.append(st_3)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_1, False))
    symbol = pyxb.binding.content.ElementUse(DatiFatturaType._UseForTag(pyxb.namespace.ExpandedName(
        _Namespace_ds, 'Signature')), pyxb.utils.utility.Location('../data/datifatture/DatiFatturav2.0.xsd', 29, 6))
    st_4 = fac.State(symbol, is_initial=False,
                     final_update=final_update, is_unordered_catenation=False)
    states.append(st_4)
    transitions = []
    transitions.append(fac.Transition(st_0, [
        fac.UpdateInstruction(cc_0, True)]))
    transitions.append(fac.Transition(st_1, [
        fac.UpdateInstruction(cc_0, False)]))
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_0, False)]))
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_0, False)]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_4, [
    ]))
    st_1._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_4, [
    ]))
    st_2._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_4, [
    ]))
    st_3._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_1, True)]))
    st_4._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)


DatiFatturaType._Automaton = _BuildAutomaton_28()
