function CloseTable(){
    document.getElementById('address_modal').style.display='none'
    $('#address tr').remove()
}
function addRow(list){
    var tbody = document.getElementById('addr_table').getElementsByTagName("TBODY")[0];
    var row = document.createElement("TR")
    els_list = [list.polyclinic, list.building, list.street, list.branch ,list.zone, list.email, list.contact, list.recording]
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
}