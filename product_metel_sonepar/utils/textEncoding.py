# -*- coding: utf-8 -*-
'''
Created on 19/set/2011

@author: Marco Tosato
'''


def checkEncoding(dataString, stringEncoding = 'ascii'):
    """
        This method check if the given string is in ASCII encoding or not.
        
        If the given string is not an ASCII string the method returns a list
        of lines that contains invalid ASCII characters.
        
        If the given string contains only ASCII characters the method returns
        None.
        
        Since METEL standard states that strings are encoded in ASCII but many
        suppliers use different codings, this method is useful for find data
        that is not encoded as ASCII; the list of strings returned by this method
        is useful to test different encodings to find the right one.
    """
    
    LINE_FEED = '\n'
    CARRIAGE_RETURN = '\r'
    
    # List containing non ASCII string found in dataString
    stringsList = []
    
    # Detect line separator before splitting the string
    lfCount = dataString.count(LINE_FEED)
    crCount = dataString.count(CARRIAGE_RETURN)
    
    if lfCount == crCount:
        dataSeparator = CARRIAGE_RETURN + LINE_FEED
    elif lfCount > crCount:
        dataSeparator = LINE_FEED
    else:
        dataSeparator = CARRIAGE_RETURN
        
    # Try to decode each line from ASCII to UTF-8, if
    # some error occurs then the string was not in ASCII
    # format
    for line in dataString.split(dataSeparator):
        try:
            # Rimozione spazi bianchi iniziali e finali
            # e dei caratteri LineFeed (1n) e CarriageReturn (\r)
            line = line.strip()
            
            # Tentativo di decodifica della stringa
            line.decode(stringEncoding)
            
        except UnicodeDecodeError:
            stringsList.append(line)
    
    # Return the list of invalid strings or an empty list if the
    # conversion did not raise errors
    if len(stringsList) > 0:
        return stringsList
    
    else:
        return []
    # end if
    
# end checkEncoding())