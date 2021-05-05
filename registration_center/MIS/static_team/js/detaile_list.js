function limitInput(k, obj) {
    switch (k) {
        case 'ru':
            obj.value = obj.value.replace(/[^а-яА-ЯёЁ0-9 -]/ig, '');
            break;
        case 'en':
            obj.value = obj.value.replace(/[^a-zA-Z0-9 -]/ig, '');
            break;
    }
}

function Validator(id_) {
    if (confirm("Вы подтверждаете операцию?")) {
        document.getElementById(id_).submit();
        return (true);
    } else {
        return (false);
    }
}

function del_el(name_class, id) {
    $(name_class).remove();
    let urls = "/archive/" + id + "/";
    $.ajax({
        type: 'GET',
        url: urls,
        success: function (data) { },
        error: function (jqXHR, text, error) {
            alert(error);
        }
    }); return false;
}

function take_off_the_board(name_class, id) {
    $(name_class).remove();
    let urls = "/take_off_the_board/" + id + "/";
    $.ajax({
        type: 'GET',
        url: urls,
        success: function (data) { },
        error: function (jqXHR, text, error) {
            alert(error);
        }
    }); return false;
}


var tab; // заголовок вкладки
var tabContent; // блок содержащий контент вкладки


window.onload = function () {
    tabContent = document.getElementsByClassName('tabContent');
    tab = document.getElementsByClassName('tab');
    hideTabsContent(1);
}

document.getElementById('tabs').onclick = function (event) {
    var target = event.target;
    if (target.className == 'tab') {
        for (var i = 0; i < tab.length; i++) {
            if (target == tab[i]) {
                showTabsContent(i);
                break;
            }
        }
    }
}

function hideTabsContent(a) {
    for (var i = a; i < tabContent.length; i++) {
        tabContent[i].classList.remove('show');
        tabContent[i].classList.add("hide");
        tab[i].classList.remove('whiteborder');
    }
}

function showTabsContent(b) {
    if (tabContent[b].classList.contains('hide')) {
        hideTabsContent(0);
        tab[b].classList.add('whiteborder');
        tabContent[b].classList.remove('hide');
        tabContent[b].classList.add('show');
    }
}


function off(t_start, t_end, id) {
    var str1 = document.getElementById(t_start);
    var str2 = document.getElementById(t_end);
    if (str1.disabled & str2.disabled) {
        str1.removeAttribute('disabled');
        str2.removeAttribute('disabled');
        str1.style.cssText = " border: 1px solid black;width: 55px;";
        str2.style.cssText = " border: 1px solid black;width: 55px;";
    }
    else {
        // alert(str1.value);
        // alert(str2.value);
        $.ajax({
            type: 'GET',
            url: "/set-time/" + String(id) + "/" + String(str1.value) + "/" + String(str2.value) + "/",
            success: function (data) {
                str1.setAttribute('disabled', 'true');
                str2.setAttribute('disabled', 'true');
                str1.style.cssText = "border: 1px solid white;width: 55px;background: white;";
                str2.style.cssText = "border: 1px solid white;width: 55px;background: white;";
            },
            error: function (jqXHR, text, error) {
                alert('Error');
                alert(error);
            }
        }); return false;

    }
}
var modal = document.getElementById('modal-id');

window.onclick = function (event) {
    if (event.target == modal) {
        modal.style.display = "none";
    }
}
var modal = document.getElementById('modal_edit');

window.onclick = function (event) {
    if (event.target == modal) {
        modal.style.display = "none";
    }
}
    (function ($) {
        function setChecked(target) {
            var checked = $(target).find("input[type='checkbox']:checked").length;

            if (checked) {
                if (checked > 0) {
                    $('.set_address').removeAttr('disabled')
                }
                else {
                    $('.set_address').setAttribute('disabled')
                }
                $(target).find('select option:first').html('Выбрано: ' + checked);

            } else {
                $(target).find('select option:first').html('Выберите из списка');

            }
        }

        $.fn.checkselect = function () {
            this.wrapInner('<div class="checkselect-popup"></div>');
            this.prepend(
                '<div class="checkselect-control">' +
                '<select class="form-control"><option></option></select>' +
                '<div class="checkselect-over"></div>' +
                '</div>'
            );

            this.each(function () {
                setChecked(this);
            });
            this.find('input[type="checkbox"]').click(function () {
                setChecked($(this).parents('.checkselect'));
            });

            this.parent().find('.checkselect-control').on('click', function () {
                $popup = $(this).next();
                $('.checkselect-popup').not($popup).css('display', 'none');
                if ($popup.is(':hidden')) {
                    $popup.css('display', 'block');
                    $(this).find('select').focus();
                } else {
                    $popup.css('display', 'none');
                }
            });

            $('html, body').on('click', function (e) {
                if ($(e.target).closest('.checkselect').length == 0) {
                    $('.checkselect-popup').css('display', 'none');
                }
            });
        };
    })(jQuery);

$('.checkselect').checkselect();

var ward_id;
function Open_edit_ward(ward){
    ward_id = ward
    event.preventDefault();
    document.getElementById('ward-modal-edit').style.display = "block";

    urls = "/ward/" + ward + "/";
    $.ajax({
            type: 'GET',
            url: urls,
            dataType: 'JSON',
            success: function (data) {
                $('#ward_edit_number').val(data.number);
                $('#ward_edit_description').val(data.description);
                $('#ward_edit_type').val(data.type);
                
            },
            error: function (jqXHR, text, error) {
            }
        });
}

function Did_Edit_ward(){
    var ward = $('#ward_edit_number').val()
    var des = $('#ward_edit_description').val()
    var type =  $('#ward_edit_type').val()
    var dataString = '&ward_edit_number=' + ward+'&ward_edit_description=' + des + '&ward_edit_type='+type;
    var urls = "/ward/update/" + ward_id + "/";

    $.ajax({
        type: "GET", // метод
        url: urls,
        data: dataString,
        cache: false,	
        dataType: 'json',
        success: function (response) {
        },error: function (jqXHR, text, error) {
        }
    });

}

var expanded = false;

	function showCheckboxes() {
		var checkboxes = document.getElementById("checkboxes_edit_group");
		if (!expanded) {
			checkboxes.style.display = "block";
			expanded = true;
		} else {
			checkboxes.style.display = "none";
			expanded = false;
		}
	}


	$(function () {
		$('.edit_form').on('click', function () {
			let str = $(this).parents('div').children('.desk');
			let block_info = str.children('.content');
			let topic = $.trim(block_info.children('.header').text());
			let text = $.trim((block_info.children('.description').text()));
			let id_task = $.trim(block_info.children('.id_task').text());
			let url_update = '/edit-notice/' + id_task + '/';
			$('#modal_edit').css('display', 'block');
			$('#change_data_form').attr('action', url_update);
			$('#input_edit_note_topic').val(topic);
			$('#text_edit_note_topic').val(text);

		});
		$(document).mouseup(function (e) { // событие клика по веб-документу
			var div = $("#change_data"); // тут указываем ID элемента
			if (!div.is(e.target) // если клик был не по нашему блоку
				&& div.has(e.target).length === 0) { // и не по его дочерним элементам
				div.css('display', 'none');// скрываем его
			}
		});
	})