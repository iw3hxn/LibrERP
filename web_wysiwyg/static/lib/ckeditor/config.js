/*
Copyright (c) 2003-2009, CKSource - Frederico Knabben. All rights reserved.
For licensing, see LICENSE.html or http://ckeditor.com/license
*/


CKEDITOR.editorConfig = function( config )
{

    config.width = '93%';
    config.height = 200;
    config.disableObjectResizing = true;
    config.resize_enabled = false;
    
    config.toolbar = 'Mine';

    config.toolbar_Mine =
    [
      ['Bold','Italic','Underline','-','Subscript','Superscript'],
      ['NumberedList','BulletedList','-','Outdent','Indent'],
      ['JustifyLeft','JustifyCenter','JustifyRight','JustifyBlock'],
      ['Link','Unlink','Image','Table','SpecialChar'],
      ['Font','FontSize','TextColor'],
      ['SpellChecker']
    ];
};
