odoo.define('skit_customer_code.pos_model',function(require){
    "use strict";
	var models = require('point_of_sale.models');
	var screens = require('point_of_sale.screens');
	var gui = require('point_of_sale.gui');
	var core = require('web.core');
	var _t  = core._t;
	var QWeb = core.qweb;

	var _super_posmodel = models.PosModel.prototype;

    // Add new Column
	models.PosModel = models.PosModel.extend({
	    initialize: function (session, attributes) {
	    	
	    	/** Partner Model **/	      
	        var partner_model = _.find(this.models, function(model){
	            return model.model === 'res.partner';
	        });
	        partner_model.fields.push('code');
	       // partner_model.fields.push('equipments_ids');
//	        partner_model.fields.push('equipments_ids');

	        return _super_posmodel.initialize.call(this, session, attributes);
	    },
	});
});
