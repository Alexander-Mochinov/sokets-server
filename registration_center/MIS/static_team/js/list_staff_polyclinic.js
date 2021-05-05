
	function close_window(){
		document.getElementById('doctor_modal_edit').style.display='none';
		let inputs = $('.edit_zone');
		for (let i = 0; i < inputs.length; i++) {
			inputs[i].checked = false;
		}
	}
	
	$(function () {
		$('#chek_chekbox_zone').on('click', function () {
			let str = $('.edit_zone');
			list = []
			for (let i = 0; i < str.length; i++) {
				if (str[i].checked) {
					let id = str[i].value;
					list.push(id)
				}
			}
			class_form = '.modal_edit_doctor'
			let res = get_info_zone(list, class_form);
		});
	})

	$(function () {
		$('#add_doctors').on('click', function () {
			let str = $('.add_zone');
			list = []
			for (let i = 0; i < str.length; i++) {
				if (str[i].checked) {
					let id = str[i].value;
					list.push(id)
				}
			}
			class_form = '.modal_add_doctors'
			let res = get_info_zone(list, class_form);
		});
	})

	
	$(function () {
		$('.modal_add_address_zone_id').on('click', function () {
			let str = $(this).parents('div');
			var inputs = str.children('span').html();
			let vars = $('.zone_id')[0];
			$('.zone_id').attr('value', inputs);
			$('#modal_add_address').css('display', 'block');
		});
		$(document).mouseup(function (e) { // событие клика по веб-документу
			var div = $("#change_data"); // тут указываем ID элемента
			if (!div.is(e.target) // если клик был не по нашему блоку
				&& div.has(e.target).length === 0) { // и не по его дочерним элементам
				div.css('display', 'none');// скрываем его
			}
		});
	})


	$(function () {
		$('.address_zone_id').on('click', function () {
			let str = $(this).parents('div');
			var inputs = str.children('span').html();
			list_address(inputs);
		});
	})

	$(function () {
		$('#clear_inputs').on('click', function () {
			let inputs = $('.edit_zone');
			for (let i = 0; i < inputs.length; i++) {
				inputs[i].checked = false;
			}
		});
	})
	
	$(function () {
		$('.edit_staff').on('click', function () {
			let str = $(this).parents('tr')[0];
			var inputs = str.getElementsByClassName('id_staff')[0].textContent;
			get_a_staff_info(inputs);
		});
	})

	$(function () {
		$('.edit_doctor').on('click', function () {
			let str = $(this).parents('tr')[0];
			var inputs = str.getElementsByClassName('id_doctor')[0].textContent;
			get_info_a_doctor(inputs);
		});
	})

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