odoo.define('skit_customer_code.pos_db', function (require) {
    "use strict";

    var PosDB = require('point_of_sale.DB'); // To extend db.js file 
    var core = require('web.core');
    PosDB.include({
		name: 'openerp_pos_db', //the prefix of the localstorage data
	    limit: 100,  // the maximum number of results returned by a search
	    init: function(options){
	    	this._super(options);	    	
	    },
	    _partner_search_string: function(partner){	    	
	    	var self = this;
	        this._super(partner);
	        var str =  partner.name;
	        if(partner.barcode){
	            str += '|' + partner.barcode;
	        }
	        if(partner.address){
	            str += '|' + partner.address;
	        }
	        if(partner.phone){
	            str += '|' + partner.phone.split(' ').join('');
	        }
	        if(partner.mobile){
	            str += '|' + partner.mobile.split(' ').join('');
	        }
	        if(partner.email){
	            str += '|' + partner.email;
	        }
	        if(partner.code){
	            str += '|' + partner.code;
	        }
	        str = '' + partner.id + ':' + str.replace(':','') + '\n';
	        return str;
	    }, 
	    
	});
	return PosDB;	
});