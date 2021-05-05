$('.edit_subdiv').on('click', function () {
    let str = $(this).parents('tr')[0];
    var subdiv_id = str.getElementsByClassName('id_subdiv')[0].textContent;
    urls = "/get/subdiv/"+ subdiv_id +"/",
    $.ajax({
        type: 'GET',
        url: urls,
        dataType: 'JSON',
        success: function (data) {
            $('#subdiv_name').val(data.name_sub);
            $('#type_edit').val(data.branch);
            $('#email').val(data.email_sub);
            $('#contact_data').val(data.contact_sub);

            let url = '/edit/subdiv/' + subdiv_id + '/';
            $('.form_edit_subdiv').attr('action', url);
        },
        error: function (jqXHR, text, error) {
        }
    });
});