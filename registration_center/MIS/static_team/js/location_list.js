function redirect(id_locations, id_polyclinic) {
    let urls = "/registration/activity_tracking/" + id_locations + "/" + id_polyclinic + "/";
    $.ajax({
        type: 'GET',
        url: urls,
        success: function (data) { },
        error: function (jqXHR, text, error) {
            alert(error);
        }
    }); return false;
}