// Date to simple date
function formatDate(date) {
    try {
        var dd = date.getDate();
        if (dd < 10) dd = '0' + dd;

        var mm = date.getMonth() + 1;
        if (mm < 10) mm = '0' + mm;

        var yy = date.getFullYear() % 100;
        if (yy < 10) yy = '0' + yy;

        return dd + '.' + mm + '.' + yy;
    } catch (error) {
        return 'none';
    }
}

//Detect day of week
function date_to_dayofweek(date){
    var days = [
                'Воскресенье',
                'Понедельник',
                'Вторник',
                'Среда',
                'Четверг',
                'Пятница',
                'Суббота'
                ];
    var d = new Date(date);
    return days[d.getDay()]
}

function calculate_start_week(date){
    var d = date;
    var n = d.getDay();
    var start_week;
    if (n > 1){
        start_week = new Date(d.getFullYear(),d.getMonth(),d.getDate() - (n - 1));
    }
    else if (n < 1){
        start_week = new Date(d.getFullYear(),d.getMonth(),d.getDate() -6);
    }
    else{
        start_week = d;
    }
    return start_week
}

function calculate_end_week(date){
    var d = date;
    var n = d.getDay();
    var end_week;
    end_week = new Date(d.getFullYear(),d.getMonth(),d.getDate() + 6);
    return end_week
}

function open_modal(day){
    $.ajax({
			url: "/get_info_doctor_chedule/" + day + "/",
			dataType: 'json',
			success: function (response) {
				var data_mess = '';
				var data = '';
				for (i in response) {
					list = {
                        'id': response[i].id,
						'date': response[i].date,
						'start_date_of_appointment': response[i].start_work,
						'appointment_end_date': response[i].end_work,
						'count_of_minute_on_one_see': response[i].count_of_minute_on_one_see,
                        'weekend' : response[i].weekend,
                        'work_period_start' : response[i].work_period_start,
                        'end_work_period' : response[i].end_work_period,
					}
				}
                let form = document.getElementById('form_change_day');
                let url = '/edit_chedule_a_doctor/' + list.id + '/';
                form.action = url;
                $('#date').val(list.date);
                $('#start_date_of_appointment').val(list.start_date_of_appointment);
                $('#appointment_end_date').val(list.appointment_end_date);

                $('#work_period_start').val(list.work_period_start);
                $('#end_work_period').val(list.end_work_period);
                $('#exist').text(list.date);
                $('#count_of_minute_on_one_see').val(list.count_of_minute_on_one_see);
                if(list.weekend == true){
                    $("#weekend").prop("checked", true);
                }else{
                    $("#weekend").prop("checked", false);
                }
			}
		});
    document.getElementById('doctor_workchedule_modal_edit').style.display = 'block'
}

$("#weekend").click(function(){ // задаем функцию при нажатиии на элемент <button>
    if ($('#weekend').is(':checked') == false){
        $('.show_input_refuse').css('display' , 'block')
        $('#show_input_refuse_input').attr('required', 'required');
    } else {
        $('.show_input_refuse').css('display' , 'none')
        $('#show_input_refuse_input').attr('required', '');
        $('#start_date_of_appointment').attr('required', '');
        $('#appointment_end_date').attr('required', '');
    }
});