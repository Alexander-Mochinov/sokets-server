function CloseTable(){
	document.getElementById('address_modal').style.display='none'
	$('#address tr').remove()
}
function addRow(list){
	var tbody = document.getElementById('addr_table').getElementsByTagName("TBODY")[0];
	var row = document.createElement("TR")
	els_list = [list.polyclinic, list.building, list.street, list.zone, list.email, list.contact, list.recording]
	for (let i = 0; i < els_list.length; i++) {
		var td = document.createElement("TD")
		if(i === els_list.length-1){
			td.innerHTML = els_list[i]
		}
		else{
			td.appendChild(document.createTextNode(els_list[i]))
		}
		row.appendChild(td);
		tbody.appendChild(row);
	}
}
function Search_address(){
    document.getElementById('address_modal').style.display='block';
    if ($('#search_street').val() & $('#search_branch').val()){
        $.ajax({
            url: "/get_list_locations/?street=" + $('#search_street').val() + "&num=" + $('#search_house').val() + "&bra=" + $('#search_branch').val(),
            dataType: 'json',
            async: true,
            success: function (response) {
                var list = [];
                for (i in response) {
                    list.push({
                        'polyclinic': response[i].polyclinic,
                        'building': response[i].building,
                        'street': response[i].street,
                        'branch': response[i].branch,
                        'zone': response[i].zone,
                        'email': response[i].email,
                        'contact': response[i].contact,
                        'recording': response[i].recording,
                    })
                }
                list.forEach(element => {
                    addRow(element)
                });
            }   
        });
    } else {
        let tr_not_found = document.getElementById('text_not_found');
        tr_not_found.innerHTML = "Нет такой записи !";
    }
}

function GetJson(id) {
    $.ajax({
        url: "/filter/" + String(id) + "/",
        dataType: 'json',
        success: function (response) {
            var data = data;
            var list = []
            var data_mess = '';
            for (i in response) {
                list[i] = [{ 'id': response[i].id, 'fio': response[i].fio, 'zone': response[i].zone }]
            }
            var opts = '<option value="">-----</option>';
            for (i in list) {
                for (t of list[i]) {
                    opts += '<option value="' + t.id + '">' + t.fio + '</option>';
                }
            }
            document.getElementById('select_a_doctor').innerHTML = opts;
        }
    });
}

var languagesSelect = filter.select_polyclinic;
    function changeOption() {
 
        var selection = document.getElementById("select_a_doctor");
        var selectedOption = languagesSelect.options[languagesSelect.selectedIndex];
        GetJson(selectedOption.value)
    }
    languagesSelect.addEventListener("change", changeOption);
 
 
    function cancell_call(id_button, id_pacient) {
        var buttonValue = document.getElementById(id_button)
        if (buttonValue.checked) {
        }
        else {
 
            document.getElementById('modal_edit').style.display = 'block'
            let url_update = '/cancell-call/' + id_pacient + '/';
            $('#modal_edit').css('display', 'block');
            $('#change_data_form').attr('action', url_update);
        }
 
        $(document).mouseup(function (e) { // событие клика по веб-документу
            var div = $("#change_data"); // тут указываем ID элемента
            if (!div.is(e.target) // если клик был не по нашему блоку
                && div.has(e.target).length === 0) { // и не по его дочерним элементам
                div.css('display', 'none');// скрываем его
                buttonValue.checked = false;
            }
        });
 
    }
    function cheked_box(id_box, id_pacient) {
        var buttonValue = document.getElementById(id_box);
        if (buttonValue.checked) {
            url = '/set-type-call/' + id_pacient + '/' + buttonValue.value + '/';
            window.location.href = url
        } else {
            url = '/set-type-call/' + id_pacient + '/0/';
            window.location.href = url
        }
    }
    
    $('input[type="checkbox"]').on('change', function () {
        let str = $(this).parents('td');
        if (input.checked) {
            $('input[name="' + this.name + '"]').prop('checked', false);
        }
        else {
            $('input[name="' + this.name + '"]').not(this).prop('checked', false);
        }
        // $('input[name="' + this.name + '"]').not(this).prop('checked', false);
    });