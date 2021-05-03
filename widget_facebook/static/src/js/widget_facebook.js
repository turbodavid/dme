openerp.WidgetFacebook = function (instance){ 
	console.log("entrando a resource");
	//Se agrega el nuevo widget, con 'test' como identificador de este.
	instance.web.form.widgets.add('WidgetFacebook', 'instance.web.form.Mywidget');
	//Se hereda de el campo Char, para crear el widget 
    instance.web.form.Mywidget = instance.web.form.FieldChar.extend({
	//Se manda llamar el template con el nombre 'test_template' creado el xml 	
		    template : "template_facebook",
	//Se inicializa la funcion.
		    init: function (view, code) {
		        this._super(view, code);
		        console.log('loading...');
			}
	});
}

