'''
Created on 30/set/2011

@author: Marco Tosato
'''

#===============================================================================
# Functions
#===============================================================================
def getViewID( pool, cr, uid, context, moduleName, viewName):
    
    # Get the object that represents the ir.model.data
    data_obj = pool.get('ir.model.data')
    
    searchFilter = [('module', '=', moduleName),('name', '=', viewName),]
    resultsList = data_obj.search(cr, uid, searchFilter)
    
    if len(resultsList) <= 0:
        raise ViewNotFoundException('Non esiste nessuna vista con nome ' + viewName + ' nel modulo ' + moduleName)
    
    else:
        viewID = data_obj.browse(cr, uid, resultsList[0], context=context).res_id
        return viewID
    # end if
    
# end getViewID()

#===============================================================================
# Exceptions
#===============================================================================
class ViewNotFoundException(Exception):
    pass
# end class ViewNotFoundException