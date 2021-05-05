$('.edit_receiving_staff').on('click', function () {
    let str = $(this).parents('tr')[0];
    var inputs = str.getElementsByClassName('id_receiving_staff')[0].textContent;
    get_a_receiving_staff_info(inputs);
});


$('.edit_staff').on('click', function () {
    let str = $(this).parents('tr')[0];
    var inputs = str.getElementsByClassName('id_staff')[0].textContent;
    get_a_staff_info(inputs);
});


function close_modal_receiving(event) {
    event.PreventDefault;
    document.getElementById('receiving-staff-edit-modal').style.display='none';
}
function get_a_receiving_staff_info(id_receiving) {
    $.ajax({
        url: "/get_a_receiving_staff_info/" + id_receiving + "/",
        dataType: 'json',
        success: function (response) {
            list = {
                'day_week' : response.day_week,
                'begin_work' : response.begin_work,
                'end_work' : response.end_work,
                'numb' : response.numb,
            }

            let url = '/edit_receiving_staff/' + id_receiving;
            $('.modal_edit_receiving_staff').attr('action', url);

            $('#day_week').val(list.day_week);
            $('#begin_work').val(list.begin_work);
            $('#end_work').val(list.end_work);
            $('#numb').val(list.numb);
        }
    })
}