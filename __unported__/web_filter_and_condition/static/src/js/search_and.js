/*---------------------------------------------------------
 * OpenERP replace filters by and condition "and"
 *---------------------------------------------------------*/

openerp.web_filter_and_condition = function(instance) {

instance.web.search.FilterGroup = instance.web.search.FilterGroup.extend({
	    get_domain: function (facet) {
	        this._super.apply(this,arguments);
	        var domains = facet.values.chain()
	            .map(function (f) { return f.get('value').attrs.domain; })
	            .without('[]')
	            .reject(_.isEmpty)
	            .value();
	        var filter_conditions = facet.values.chain()
	            .map(function (f) { return f.get('value').attrs.filter_condition; })
	            .without('|')
	            .reject(_.isEmpty)
	            .value();
	        if (filter_conditions.length) {
	            filter_conditions = '&';
	        } else {
	            filter_conditions = '|';
	        }
	        if (!domains.length) { return; }
	        if (domains.length === 1) { return domains[0]; }
	        for (var i=domains.length; --i;) {
	            domains.unshift([filter_conditions]);
	        }
	        return _.extend(new instance.web.CompoundDomain(), {
	            __domains: domains
	        });
	    },
    });
};