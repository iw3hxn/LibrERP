# -*- coding: utf-8 -*-
# © 2018-2019 Didotech srl (www.didotech.com)

# from os.path import abspath
import os
import subprocess
# import sys
import logging
# from tools.translate import _
import time
import tempfile
import shutil

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

_logger = logging.getLogger(__name__)


class DocumentConversionException(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


# class UnknownPropertyException(Exception):
#     def __init__(self, message):
#         self.message = message
#
#     def __str__(self):
#         return self.message


# class PropertyValue(object):
#     pass


# class XOutputStream:
#     pass
#
#
# class OutputStreamWrapper(XOutputStream):
#     """ Minimal Implementation of XOutputStream """
#     def __init__(self, debug=True):
#         self.debug = debug
#         self.data = StringIO()
#         self.position = 0
#         if self.debug:
#             sys.stderr.write("__init__ OutputStreamWrapper.\n")
#
#     def writeBytes(self, bytes):
#         if self.debug:
#             sys.stderr.write("writeBytes %i bytes.\n" % len(bytes.value))
#         self.data.write(bytes.value)
#         self.position += len(bytes.value)
#
#     def close(self):
#         if self.debug:
#             sys.stderr.write("Closing output. %i bytes written.\n" % self.position)
#         self.data.close()
#
#     def flush(self):
#         if self.debug:
#             sys.stderr.write("Flushing output.\n")
#         pass
#
#     def closeOutput(self):
#         if self.debug:
#             sys.stderr.write("Closing output.\n")
#         pass
#
#
# class ComponentContext:
#     def ServiceManager(self):
#         pass

class DummyLock(object):
    def __enter__(self):
        print("Enter dummy lock")

    def __exit__(self, one, two, three):
        print("Exit dummy lock")


class DocumentConverter(object):
    def __init__(self, soffice, prefix='aeroo-', dir_tmp='/tmp', suffix='.odt'):
        self.path = dir_tmp
        self.prefix = prefix
        self.suffix = suffix

        self.lock = DummyLock()

        self.command = u"{bin} -env:UserInstallation=file://{tmpdir} --headless --convert-to {format} --outdir {outdir} {source}".format(
            bin=soffice,
            format='{format}',
            outdir=dir_tmp,
            source='{file_name}',
            tmpdir='{tmp_dir}'
        )

    def putDocument(self, data):
        self.document = tempfile.NamedTemporaryFile(
            prefix=self.prefix, dir=self.path, suffix=self.suffix
        )

        self.document.write(data)
        self.document.flush()

    def closeDocument(self):
        self.document.close()

        if os.path.isfile(self.new_file):
            os.unlink(self.new_file)

    def saveByStream(self, filter_name='writer_pdf_Export'):
        filters = {
            u'writer_pdf_Export': {
                'ext': 'pdf'
            },
            u'MS Word 97': {
                'ext': 'doc'
            }
        }

        document = self.document

        try:
            tmp_dir = tempfile.mkdtemp()
            conversion = subprocess.Popen(self.command.format(
                format=filters[filter_name]['ext'],
                file_name=self.document.name,
                tmp_dir=tmp_dir
            ), shell=True, stdin=None, stdout=None, stderr=None)
            conversion.wait()
            shutil.rmtree(tmp_dir)
        except:
            _logger.error("Failed to convert document to '{}' format".format(filter_name))

        self.document = document
        self.new_file = os.path.splitext(self.document.name)[0] + '.{ext}'.format(ext=filters[filter_name]['ext'])

        for count in range(1, 10):
            if os.path.isfile(self.new_file):
                with open(self.new_file) as new_document:
                    data = new_document.read()
                _logger.info("Conversion to '{ext}' done".format(ext=filters[filter_name]['ext']))
                return data
            else:
                print 'Counter:', count
                time.sleep(1)
        else:
            _logger.error('Conversion to PDF failed')
            return ''

    def insertSubreports(self, oo_subreports):
        """
        Inserts the given file into the current document.
        The file contents will replace the placeholder text.
        """
        # import os
        #
        # for subreport in oo_subreports:
        #     fd = file(subreport, 'rb')
        #     placeholder_text = "<insert_doc('%s')>" % subreport
        #     subdata = fd.read()
        #     subStream = self.serviceManager.createInstanceWithContext("com.sun.star.io.SequenceInputStream",
        #                                                               self.localContext)
        #     subStream.initialize((uno.ByteSequence(subdata),))
        #
        #     search = self.document.createSearchDescriptor()
        #     search.SearchString = placeholder_text
        #     found = self.document.findFirst(search)
        #     # while found:
        #     try:
        #         found.insertDocumentFromURL('private:stream',
        #                                     self._toProperties(InputStream=subStream, FilterName="writer8"))
        #     except Exception, ex:
        #         print (_("Error inserting file %s on the OpenOffice document: %s") % (subreport, ex))
        #     # found = self.document.findNext(found, search)
        #
        #     os.unlink(subreport)
        if oo_subreports:
            _logger.warning('DocumentConverter.insertSubreports is not yet implemented')

    def joinDocuments(self, docs):
        _logger.warning('DocumentConverter.joinDocuments is not yet implemented')
        # while (docs):
        #     subStream = self.serviceManager.createInstanceWithContext("com.sun.star.io.SequenceInputStream",
        #                                                               self.localContext)
        #     subStream.initialize((uno.ByteSequence(docs.pop()),))
        #     try:
        #         self.document.Text.getEnd().insertDocumentFromURL('private:stream',
        #                                                           self._toProperties(InputStream=subStream,
        #                                                                              FilterName="writer8"))
        #     except Exception, ex:
        #         print (_("Error inserting file %s on the OpenOffice document: %s") % (docs, ex))

    def convertByPath(self, inputFile, outputFile):
        _logger.warning('DocumentConverter.convertByPath is not yet implemented')

        # inputUrl = self._toFileUrl(inputFile)
        # outputUrl = self._toFileUrl(outputFile)
        # document = self.desktop.loadComponentFromURL(inputUrl, "_blank", 8, self._toProperties(Hidden=True))
        # try:
        #     document.refresh()
        # except AttributeError:
        #     pass
        # try:
        #     document.storeToURL(outputUrl, self._toProperties(FilterName="writer_pdf_Export"))
        # finally:
        #     document.close(True)

    # def _toFileUrl(self, path):
    #     return uno.systemPathToFileUrl(abspath(path))
    #
    # def _toProperties(self, **args):
    #     props = []
    #     for key in args:
    #         prop = PropertyValue()
    #         prop.Name = key
    #         prop.Value = args[key]
    #         props.append(prop)
    #     return tuple(props)

    def _restart_ooo(self):
        # if not self._ooo_restart_cmd:
        #     _logger.warning('No LibreOffice/OpenOffice restart script configured')
        #     return False
        # _logger.info('Restarting LibreOffice/OpenOffice background process')
        # try:
        #     _logger.info('Executing restart script "%s"' % self._ooo_restart_cmd)
        #     retcode = subprocess.call(self._ooo_restart_cmd, shell=True)
        #     if retcode == 0:
        #         _logger.warning('Restart successfull')
        #         time.sleep(4)  # Let some time for LibO/OOO to be fully started
        #     else:
        #         _logger.error('Restart script failed with return code %d' % retcode)
        # except OSError, e:
        #     _logger.error('Failed to execute the restart script. OS error: %s' % e)
        return True
