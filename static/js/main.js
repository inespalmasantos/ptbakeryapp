$(document).ready(function () {

	window.APP = {};
		
	//Read the form information
	$.fn.serializeObject = function() {
        var o = {};
        var a = this.serializeArray();
        $.each(a, function() {
            if (o[this.name]) {
                if (!o[this.name].push) {
                    o[this.name] = [o[this.name]];
                }
                o[this.name].push(this.value || '');
            } else {
                o[this.name] = this.value || '';
            }
        });
        return o;
    };

	$('.dash-img').on('mouseenter', event => {
		$(event.currentTarget).removeClass('bg-light').addClass('bg-brown');
	});
	$('.dash-img').on('mouseleave', event => {
		$(event.currentTarget).removeClass('bg-brown').addClass('bg-light').addClass('fill-class');
	});
	$('.dash-img2').on('mouseenter', event => {
		$(event.currentTarget).removeClass('bg-light').addClass('bg-brown');
	});
	$('.dash-img2').on('mouseleave', event => {
		$(event.currentTarget).removeClass('bg-brown').addClass('bg-light').addClass('fill-class');
	});
	$('.btn').on('mouseenter', event => {
		$(event.currentTarget).addClass('button-color');
		$(event.target).children().addClass('color');
	});
	$('.btn').on('mouseleave', event => {
		$(event.currentTarget).removeClass('button-color');
		$(event.target).children().removeClass('color');
	});
	
	//Give dynamic behavior to Add Price and Edit Price Views
	var clientType = $('#client_type').find(':selected').text();
	var priceType = $('#price_type').find(':selected').text();
	var clientName = $('#client_name').find(':selected').text();
	/*console.log(clientType, priceType, clientName);*/

	if(clientType === 'Retail') {
		$('#price_type').show();
		if(priceType === 'Standard') {
			$('#client_name').hide();
		} else if(priceType === 'Special') {
			$('#client_name').show();
		};
	} else {
		$('#price_type').hide();
		$('#client_name').hide();
	}

	$('#client_type').find('select').change(function() {
		var valClientType = $('#client_type').find(':selected').text();
		var valClientName = $('#client_name').find(':selected').text();
		var valPriceType = $('#price_type').find(':selected').text();
		if(valClientType === 'Private') {
			$('#price_type').hide();
			$('#client_name').hide();
		} else if(valClientType === 'Retail') {
			$('#price_type').show();
			var valPriceType = $('#price_type').find(':selected').text();
			if(valPriceType === 'Special') {
				$('#client_name').show();
			} else {
				$('#client_name').hide();
			}
		}
	});

	$('#price_type').find('select').change(function() {
		var valPriceType = $('#price_type').find(':selected').text();
				if(valPriceType === 'Special') {
					$('#client_name').show();
				} else {
					$('#client_name').hide();
				}
	})

	//Give dynamic behavior to Edit Invoice Private Client View
	var paymentStatus = $('#payment_status').find(':selected').text();

	document.querySelector('#delivery_day').type = "date";
	document.querySelector('#delivery_day').required = "date";

	if(paymentStatus === 'Paid') {
		$('#payment_date').show();
		$('#payment_method').show();
		$('#payment_details').show();
	} else {
		$('#payment_date').hide();
		$('#payment_method').hide();
		$('#payment_details').hide();
	}

	$('#payment_status').find('select').change(function() {
		var valPaymentStatus = $('#payment_status').find(':selected').text();
		if(valPaymentStatus === 'Paid') {
		    $('#payment_date').show();
		    $('#payment_method').show();
		    $('#payment_details').show();
	    } else {
		    $('#payment_date').hide();
		    $('#payment_method').hide();
		    $('#payment_details').hide();
	    }
	});
	
    //Add lines to Add Invoice View
	var invoiceTableRows = $('#invoice-body tr');

	for(var rowNumber = 1; rowNumber <= invoiceTableRows.length; rowNumber++) {
		$('#invoice-row-' + rowNumber).hide();
	}

	var invoiceRowNumber = 0;

	$('#minus-0').hide();
	$('#add-19').hide();

	$('.button-invoice').on('click', function(event) {
		if(event.target.id === 'add-' + (invoiceRowNumber)) {
			$('#invoice-row-' + (invoiceRowNumber + 1)).show();
			$('#add-' + (invoiceRowNumber)).hide();
			$('#minus-' + (invoiceRowNumber)).hide();
			invoiceRowNumber++;
		} else if(event.target.id === 'minus-' + (invoiceRowNumber)) {
			$('#invoice-row-' + (invoiceRowNumber)).hide();
			$('#items-' + invoiceRowNumber + '-product').val('(...)');
			$('#items-' + invoiceRowNumber + '-quantity').val('0');
			$('#unit_price-' + invoiceRowNumber).text('0.00');
			$('#amount-' + invoiceRowNumber).text('0.00');
			$('#add-' + (invoiceRowNumber - 1)).show();
			if(invoiceRowNumber > 1) {
				$('#minus-' + (invoiceRowNumber - 1)).show();
			}
			getTotalAmount();
			invoiceRowNumber--;
		}
	})

	function getTotalAmount () {
	 		var list, arr, rows;
	 		var sum = 0;
	 		list = document.querySelectorAll('.total-amount');
			arr = Array.prototype.slice.call(list);
			rows = $('.invoice-row');

			arr.forEach(function(cur, i, array) {
				sum += parseFloat(cur.outerText);
			})
			
			if(isNaN(sum)) {

			} else {
				document.querySelector('.total-invoice').textContent = sum.toFixed(2);	
			}

 		}
	
	window.APP.initAddInvoicePrivateClient  = function initAddInvoicePrivateClient() {
    	console.log('Init invoice');
    	var invoiceRows = $('.invoice-row');
 		function getUnitPriceForProduct (invoiceRow) {
			var index = invoiceRow.attr('id').split('-')[2];
			var product = $('#product-' + index).find('select').find(':selected').text();
			var quantity = $('#quantity-' + index).find('select').find(':selected').text();
			$.ajax({
				type: 'GET',
				url: '/get_unit_price',
				data: {
					product: product
				},
				dataType: 'json',
				success: function (response) {
					$('#unit_price-' + index).html(response.toFixed(2));
					$('#amount-' + index).html((response * quantity).toFixed(2));
					getTotalAmount();
					//$('#delivery_day').datepicker();
	 			}
	 		});
 		}

 		//Set unit_price for default products  at Add Invoice View
 		$.each(invoiceRows, function (index, invoiceRow) {
			getUnitPriceForProduct($(invoiceRow));
		});

 		//Give dynamic behavior unit_prices and amounts when product is changed at Add Invoice View
		$('.form-product').find('select').change(function () {
			var invoiceRow = $(this).closest('.invoice-row');
			getUnitPriceForProduct(invoiceRow);
			getTotalAmount();
		});

		//Give dynamic behavior to amounts when quantity is changed at Add Invoice View
		$('.form-quantity').find('select').change(function () {
			var invoiceRow = $(this).closest('.invoice-row');
			var index = invoiceRow.attr('id').split('-')[2];
			var quantity = $('#quantity-' + index).find('select').find(':selected').text();
			var unitPrice = $('#unit_price-' + index).html();
			$('#amount-' + index).html((unitPrice * quantity).toFixed(2));
			getTotalAmount();
		});
		
		//Save invoice information to the backend
		$('#add_invoice_form').submit(function (event) {
			event.preventDefault();
			var items = [];
			var invoiceTable = $('#invoice-body');
			var formData = $(this).serializeObject();
			var totalAmount = $('.total-invoice').html();
			$.each(invoiceTable.children('tr'), function (index) {
				var product = $('#product-' + index).find('select').find(':selected').text();
				var quantity = $('#quantity-' + index).find('select').find(':selected').text();
				var unitPrice = $('#unit_price-' + index).html();
				var amount = $('#amount-' + index).html();
				items.push({product, quantity, unitPrice, amount});
			});
			$.ajax({
				type: 'POST',
				url: '/add_invoice_private_clients',
				data : JSON.stringify({
					client_id: formData.client_id,
					delivery_day: formData.delivery_day,
					total_amount: totalAmount,
					items: items
				}),
				dataType: 'json',
				contentType: 'application/json',
				success: function (data) {
					console.log(data);
					window.location = '/manage_invoices_private_clients';
				},
			})
		});
	};

});

	

//Give dynamic to add_product and edit_product views
$(function() {
    var val = $("#nr_pieces_per_bag").val();
    if(val > 1){
        $("#aggregrate_to_field").show();
    }
    else if (val == 1){
      	$("#aggregrate_to_field").hide();
    }

    $("#name").attr("required", true);
	   
    $('#nr_pieces_per_bag').change(function() {
    	var val = $(this).val();
        if(val > 1){
            $("#aggregrate_to_field").show();
        }
        else if (val == 1){
            $("#aggregrate_to_field").hide();
        }
    });
});



