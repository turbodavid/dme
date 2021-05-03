//Nombre de nuestro módulo pos_rochin
//Basado http://frederic.vanderessen.com/client-side-development-with-openerp/
openerp.pos_rochin = function(instance) {
	//Sobreescribir método search_and_categories del módulo point_of_sale de la clase ProductCategoriesWidget
	instance.point_of_sale.ProductCategoriesWidget.include({
		search_and_categories: function(category){
			var self = this;
            // find all products belonging to the current category
            var products = this.pos.db.get_product_by_category(this.category.id);
            self.pos.get('products').reset(products);

            // filter the products according to the search string
            this.$('.searchbox input').keyup(function(event){
				//console.log('.searchbox input KEYUP',event); 
                query = $(this).val().toLowerCase();
                if(query){
					//es un enter
                    if(event.which === 13){
						//Trae un elemento por lo menos
                        if( self.pos.get('products').size() === 1 ){
							//Revisa que sea longitud 13 y sea número, toma la cantidad
							if (query.length == 13 && !isNaN(query)){			
								var cant = query.slice(7,12)/1000
								self.pos.get('selectedOrder').addProduct(self.pos.get('products').at(0), {quantity:cant});
							}
							else
							{
								self.pos.get('selectedOrder').addProduct(self.pos.get('products').at(0));
							}
							//Limpia la pantalla
							self.clear_search();						                
                        }
                    }else{
						//Revisa que sea longitud 13 y sea número, toma el código
						if (query.length == 13 && !isNaN(query)){
							query=query.slice(2,7)
						}			
						var products = self.pos.db.search_product_in_category(self.category.id, query);//
						self.pos.get('products').reset(products);
						self.$('.search-clear').fadeIn();
                    }
                }else{
					//Obtiene los productos de la categoria actual
                    var products = self.pos.db.get_product_by_category(self.category.id);
                    self.pos.get('products').reset(products);
                    self.$('.search-clear').fadeOut();
                }
            });		

			//reset the search when clicking on reset
            this.$('.search-clear').click(function(){
                self.clear_search();
            });           
        },
    });
};
