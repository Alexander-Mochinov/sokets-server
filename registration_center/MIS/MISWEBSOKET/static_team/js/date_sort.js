var asc = true;

function sortTable_Date(count_table) {
    var tbl = document.getElementById("myTable_two").tBodies[0];
    var store = [];
    for (var i = 0, len = tbl.rows.length; i < len; i++) {
        var row = tbl.rows[i];
        var rowdatedata = row.cells[count_table].textContent;
        var splits = rowdatedata.split(' ')
        var rowdatesplit = splits[0].split('-');
        var rowdatetimedplite = splits[1].split(':');
        var rowdatetimestamp = new Date(parseInt(rowdatesplit[0], 10), parseInt(rowdatesplit[1], 10) - 1, parseInt(rowdatesplit[2], 10), rowdatetimedplite[0], rowdatetimedplite[1], 0).getTime() / 1000;
        if (!isNaN(rowdatetimestamp)) store.push([rowdatetimestamp, row]);
    }

    if (asc) {
        store.sort(function (x, y) {
            return x[0] - y[0];
        });
        asc = false;
    }
    else {
        store.sort(function (x, y) {
            return y[0] - x[0];
        });
        asc = true;
    }

    for (var i = 0, len = store.length; i < len; i++) {
        var idno = i + 1;
        tbl.appendChild(store[i][1]);
    }
    store = null;
}