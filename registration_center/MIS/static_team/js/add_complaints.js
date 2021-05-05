function chek_fields(personal_info) {
    for (var i = 0; i < personal_info.length; i++) {
        if (personal_info[i] == '') {
            return false;
        }
    }
    return true;
}

$('#conf').click(function () {
    var modals = document.getElementById('modals');
    var name = document.getElementById('id_fio').value;
    var phone = document.getElementById('id_phone').value;
    var text = document.getElementById('id_text').value;
    var institution = document.getElementById('id_institution').value;
    var personal_info = [name, institution, phone, text];
    if (chek_fields(personal_info)) {
        $("#allowed").prop("disabled", false);
    } else {
        $("#allowed").prop("disabled", true);
    }
    modals.innerHTML = '\
                <p>Убедитесь что данные заполненны верно ! <br>\
                Фамилия Имя Очество: ' + name + ' <br>\
                Учреждение: ' + institution + ' <br>\
                Телефон: ' + phone + ' <br>\
                Жалоба: ' + text;
});