/*---------------------------------------------------------
 * Odoo allow to edit lines when grouped in tree view
 *---------------------------------------------------------*/

openerp.web_view_list_editable_grouped = function(instance) {
    instance.web.ListView.include({
        editable: function () {
            this._super.apply(this,arguments);
            return !this.options.disable_editable_mode
                && (this.fields_view.arch.attrs.editable
                || this._context_editable
                || this.options.editable);
        },
    });
};
