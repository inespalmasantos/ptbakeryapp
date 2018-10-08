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
	console.log(clientType, priceType, clientName);

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
			/*$('#price_type').find('select').change(function() {
				var valPriceType = $('#price_type').find(':selected').text();
				if(valPriceType === 'Special') {
					$('#client_name').show();
				} else {
					$('#client_name').hide();
				}
			})*/
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

	/*$('#price_type').find('select').change(function() {
		var valPriceType = $('#price_type').find(':selected').text();
		if(valPriceType === 'Special') {
			$('#client_name').show();
		} else {
			$('#client_name').hide();
		}
	}*/ 
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



//Give dynamic to add_price and edit_price views
/*$(function() {
    var val = $("#client_type").val();
    if(val == "Retail"){
        $("#price_type").show();
    }
    else if (val == "Private"){
      	$("#price_type").hide();
    }
*/
    /*$("#name").attr("required", true);
	*/   
/*    $('#client_type').change(function() {
    	var val = $(this).val();
        if(val == "Retail"){
            $("#price_type").show();
        }
        else if (val == "Private"){
            $("#price_type").hide();
        }
    });
});
*/

// Ajax code by Hacks Hand session - to be deleted - for future reference
// $(function() {
//     $("#aggregate_to").val("-");
//     $("#aggregate_to").attr("disabled", true);
//     $('#nr_pieces_per_bag').change(function() {
//         var val = $(this).val();
        
//         if(val > 1){
//             $("#aggregate_to").attr("disabled", false);
//             $("#aggregate_to").val("");
//             var data = {"number_pieces": val};
//             data = JSON.stringify(data);
//             $.ajax({
//                 url: '/ajax/get/aggregrates',
//                 data: data,
//                 type: 'POST',
//                 success: function(response) {
//                     console.log(response);
//                 },
//                 error: function(error) {
//                     console.log(error);
//                 }
//             });
//         }
//         else{
//             $("#aggregate_to").val("-");
//             $("#aggregate_to").attr("disabled", true);
//         }
    
//     });
// });
