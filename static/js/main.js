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
