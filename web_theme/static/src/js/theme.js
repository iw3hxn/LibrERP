/*---------------------------------------------------------
 * OpenERP web_theme module
 * Developed by Poiesis Consulting (www.poiesisconsulting.com)
 * AGPL ...of course
 * Changing logos should not be against the license (https://bugs.launchpad.net/openobject-doc/+bug/948402) 
 *---------------------------------------------------------*/

openerp.web_theme = function(openerp) {

var link_color = '#9A0404';
	
openerp.web.Header = openerp.web.Header.extend({

	start: function() {

	    this._super.apply(this,arguments);
	    
	    var picture = 'logo_default.png';
	    var self = this;
	    var func = new openerp.web.Model("res.users").get_func("read");
	    return func(self.session.uid, ["company_id"]).pipe(function(res) {
	    	var color_set = 0;
	    	var logo_web = '';
	    	var company_id = res['company_id'][0];
            return new openerp.web.Model("res.company").get_func("read")(company_id, ['name', 'logo_web', 'color_set', 'color_top', 'color_mid', 'color_low', 'button_top', 'button_mid', 'link_top']).pipe(function(result) {
        		//alert(JSON.stringify(result));
            	color_set = result['color_set'][0];
            	if (color_set != 0){
            		link_color = result['link_top'];
            		var border_buttons = '1px solid ' + result['button_mid'];
            		var gradient_topbar = '';
            		var gradient_buttons = '';
            		if (/chrome/i.test( navigator.userAgent )) {
            			gradient_topbar = '-webkit-linear-gradient(top, ' + result['color_top'] + ' 0%,' + result['color_mid'] + ' 8%,' + result['color_low'] + ' 100%)';
                		gradient_buttons = '-webkit-linear-gradient(top, ' + result['button_top'] + ' 0%,' + result['button_mid'] + ' 60%)';
            		}
            		else {
            			
                		switch (navigator.appCodeName)
                		{
                			//ToDo: Case sensitiveness on all different browsers    
                			case 'Mozilla':
                				gradient_topbar = '-moz-linear-gradient(top, ' + result['color_top'] + ' 0%, ' + result['color_mid'] + ' 8%, ' + result['color_low'] + ' 100%)';
                    			gradient_buttons = '-moz-linear-gradient(top, ' + result['button_top'] + ' 0%, ' + result['button_mid'] + ' 60%)';
                			default:
                				gradient_topbar = result['color_mid'];
                    			gradient_buttons = result['button_mid'];
                		}
            			
            		}
            		
            		$('.openerp .menu').css('background', gradient_topbar);
            		$('.openerp .menu a').css('background', gradient_buttons);
            		$('.openerp .menu a').css('border', border_buttons);
            	}
            	
            	var image_url = '';
            	logo_web = result['logo_web'];
		    	if (logo_web != ''){
			    	image_url = 'url("data:image/png;base64,' + logo_web + '")';
			    	
			    } else if (picture != ''){
			    	image_url = 'url("/web_theme/static/src/img/' + picture + '")';
			    }
		    	if (image_url != ''){
		    		$('.openerp .company_logo').css('background-image', image_url);
		    		$('.openerp .company_logo').css('background-size', '100%');
		    		$('.openerp .company_logo').css('height', '100%');
		    		$('.openerp .company_logo').css('background-repeat', 'no-repeat');
		    	}
		    	
            });
	    });
	    
	}
});

openerp.web.FormView = openerp.web.FormView.extend({
	on_loaded: function() {

	    this._super.apply(this,arguments);
	    
		//$('.openerp .oe_forms input').css('border', '2px inset #E9E9E9');
		//$('.openerp .oe_forms select').css('border', '2px inset #E9E9E9');
		//$('.openerp .oe_forms textarea').css('border', '2px inset #E9E9E9');
		//$('.openerp .oe_forms input[type="text"],.openerp .oe_forms input[type="password"],.openerp .oe_forms input[type="file"],.openerp .oe_forms select,.openerp .oe_forms textarea').css('border', '2px inset #E9E9E9');
		
	}
});

openerp.web.PageView = openerp.web.PageView.extend({
	on_loaded: function() {

	    this._super.apply(this,arguments);
	    
	    $('.openerp a.oe_form_uri ').css('color', link_color);
	    $('.openerp a.oe_form_uri').css('text-decoration', 'none');
	    // $('.openerp a.oe_form_uri').css('text-shadow', '#CCC 1px 1px 1px');
		
	}
});



};
