$(document).ready(() => {
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
	/*console.log(paymentStatus);*/

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
		$('#invoice-row' + rowNumber).hide();
	}

	var invoiceRowNumber = 1;

	$('.button-invoice').on('click', function() {
		console.log(invoiceRowNumber)
		$('#invoice-row' + invoiceRowNumber).show();
		if(invoiceRowNumber < 20) {
			$('#add' + (invoiceRowNumber - 1)).hide();
		}
		invoiceRowNumber++;
		console.log(invoiceRowNumber);		
	})
	
	//Set unit_price and amount for default product at Add Invoice View
	var valProductOne = $('#product_one').find(':selected').text();
	var valQuantityOne = $('#quantity_one').find(':selected').text();
	$.ajax({
			type: 'GET',
			url: '/get_unit_price',
			data: {'product': valProductOne},
			dataType: 'json',
			success: function(response) {
				
				$('#unit_price_one').html(response.toFixed(2));
				$('#amount_one').html((response*valQuantityOne).toFixed(2));
			}
	})

	//Give dynamic behavior unit_prices and amounts when product is changed at Add Invoice View
	$('#product_one').find('select').change(function() {
		var valProductOne = $('#product_one').find(':selected').text();
		var valQuantityOne = $('#quantity_one').find(':selected').text();
		$.ajax({
			type: 'GET',
			url: '/get_unit_price',
			data: {'product': valProductOne},
			dataType: 'json',
			success: function(response) {
				
				$('#unit_price_one').html(response.toFixed(2));
				$('#amount_one').html((response*valQuantityOne).toFixed(2));
				
			}
		})
	});

	//Give dynamic behavior to amounts when unit_price is changed at Add Invoice View
	$('#quantity_one').find('select').change(function() {
		var valUnitPriceOne = $('#unit_price_one').html();
		var valQuantityOne = $('#quantity_one').find(':selected').text();
		$('#amount_one').html((valUnitPriceOne*valQuantityOne).toFixed(2));	
	});


	//Testing
	$('#submit_add_invoice').on('click', event => {
		var valUnitPriceOne = $('#unit_price_one').html();
		$.ajax({
			type: 'POST',
            url: '/add_invoice_private_clients',
            data : JSON.stringify({
                price: valUnitPriceOne
            }),
            dataType: 'json',
            contentType: 'application/json',
            success: function (data) {
                console.log(data);
                window.location = '/manage_invoices_private_clients';
            },
        })
	});
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



