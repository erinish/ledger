
var tbody = document.querySelector('tbody');
var btn = document.querySelector('#btnTask');
var inpt = document.querySelector('#newTaskText');
var currentView = "open";

inpt.addEventListener("keyup", enterAddTask);

document.querySelector('#lnkTodo').addEventListener("click", function() {
    currentView = "open";
    $('li').removeClass('active');
    $("#lnkTodo").addClass('active');
    getTasks("open");
});
document.querySelector('#lnkClosed').addEventListener("click", function() {
    currentView = "closed";
    $('li').removeClass('active');
    $("#lnkClosed").addClass('active');
    getTasks("closed");
});

var tasks;

function getTasks(status = "open") {
    //clear everything in the table
    if (status == "closed") {
        reversed = true;
    } else {
        reversed = false;
    }

    while(tbody.firstChild) {
        tbody.removeChild(tbody.firstChild);
    }

    var request = new XMLHttpRequest();
    request.open('GET', 'task');
    request.responseType = 'json';
    request.onload = function () {
        tasks = request.response;
        for (var task in tasks) {
            if (tasks[task]['status'] == status) {
                var tr = document.createElement('tr');
                var btn_td = document.createElement('td');
//                btn_td.setAttribute("class", "col-md-2-2");
                var delete_btn = document.createElement('button');
                var delete_span = document.createElement('span');
                delete_btn.setAttribute("type", "button");
                delete_btn.setAttribute("class", "close");
                delete_btn.setAttribute("aria-label", "Delete");
                delete_btn.setAttribute("value", String(task));
                delete_btn.addEventListener("click", function() {deleteTask(this.value)});
                delete_span.setAttribute("aria-hidden", "true");
                delete_span.textContent = "x";

                var close_btn = document.createElement('button');
                var close_span = document.createElement('span');
                close_btn.setAttribute("type", "button");
                close_btn.setAttribute("class", "close");
                close_btn.setAttribute("aria-label", "Delete");
                close_btn.setAttribute("value", String(task));
                close_btn.addEventListener("click", function() {closeTask(this.value)});
                close_span.setAttribute("aria-hidden", "true");
                close_span.innerHTML = "&#10004;";
                var task_id = document.createElement('td');
                var task_time = document.createElement('td');
                var task_timestamp = document.createElement('td');
                var task_status = document.createElement('td');
                var task_text = document.createElement('td');
                task_id.textContent = task.slice(0, 5) + "..";
                task_time.textContent = timestampToDate(tasks[task]['time']);
                task_timestamp.textContent = tasks[task]['time'];
                task_timestamp.hidden = true;
                task_status.textContent = tasks[task]['status'];
                task_text.textContent = tasks[task]['task'];

                close_btn.appendChild(close_span);
                delete_btn.appendChild(delete_span);
                btn_td.appendChild(close_btn);
                btn_td.appendChild(delete_btn);

                tr.appendChild(btn_td);
                tr.appendChild(task_id);
                tr.appendChild(task_time);
                tr.appendChild(task_timestamp);
                tr.appendChild(task_status);
                tr.appendChild(task_text);
                tbody.appendChild(tr);
            }
        }

        sortTable(document.querySelector('tbody'), 3, reversed);
    }
    request.send();
}

getTasks();

function addTask() {
    var pdata = {"task": inpt.value,
                "time": String(Math.floor(Date.now() / 1000 )),
                "status": "open"
                }
    var req_new_task = new XMLHttpRequest();

    req_new_task.onreadystatechange = function() {
        if(this.readyState === XMLHttpRequest.DONE && this.status === 201) {
            getTasks(currentView);
        }
    }

    req_new_task.open("PUT", "task");
    req_new_task.setRequestHeader("Content-Type", "application/json");
    req_new_task.send(JSON.stringify(pdata));
    inpt.value = "";
    inpt.focus();
}

function enterAddTask(event) {
    event.preventDefault();
    if (event.keyCode == 13) {
        addTask();
    }
}

function deleteTask(taskid) {
    var req_delete_task = new XMLHttpRequest();
    var task_url = "task/" + taskid;

    req_delete_task.onreadystatechange = function() {
        if(this.readyState === XMLHttpRequest.DONE && this.status === 200) {
            getTasks(currentView);
        }
    }

    req_delete_task.open("DELETE", task_url);
    req_delete_task.send();
//    getTasks(currentView);
}

function closeTask(taskid) {
    var pdata = {};
    pdata["status"] = "closed";
    var req_close_task = new XMLHttpRequest();
    var task_url = "task/" + taskid;

    req_close_task.onreadystatechange = function() {
        if(this.readyState === XMLHttpRequest.DONE && this.status === 201) {
            getTasks(currentView);
        }
    }

    req_close_task.open("PUT", task_url);
    req_close_task.setRequestHeader("Content-Type", "application/json");
    req_close_task.send(JSON.stringify(pdata));
//    getTasks(currentView);
}

function mergesort(li) {
    // a single-length list is sorted
    if (li.length === 1) {
        return li;
    }

    var mid = Math.floor(li.length / 2);
    var left = li.slice(0, mid);
    var right = li.slice(mid);

    return merge(mergesort(left), mergesort(right));

    function merge(left, right) {
        var result = [];
        var lidx = 0;
        var ridx = 0;

        // assuming we're getting a tuple of [index, value] so we can return the proper index order
        while (lidx < left.length && ridx < right.length) {
            if (left[lidx][1] < right[ridx][1]) {
                result.push(left[lidx]);
                lidx++;
            } else {
                result.push(right[ridx]);
                ridx++;
            }
        }
        // concat adds the remainder of the left or right array to the end when you reach the length of one of the sides
        return result.concat(left.slice(lidx).concat(right.slice(ridx)));
    }
}

function sortTable(table, keyrow, reversed = false) {
    var rows = Array.prototype.slice.call(table.rows);
    var workarray = [];
    var sortedkeys = [];
    var data = {};

    for (var i = 0; i < rows.length; i++) {
        workarray.push([i, rows[i].querySelectorAll('td')[keyrow].textContent]);
    }

    sortedkeys = mergesort(workarray);

    // clear the current table
    while (tbody.firstChild) {
        tbody.removeChild(tbody.firstChild);
    }

    for (var i = 0; i < workarray.length; i++) {
        tbody.appendChild(rows[sortedkeys[i][0]])
    }

//   var current, next;
//   var swap = true;
//   var makeswap;
//   
//   while(swap) {
//        swap = false;
//        rows = table.rows;
//
//        for (var i = 0; i < rows.length - 1; i++) {
//            makeswap = false;
//            current = rows[i].querySelectorAll('td')[keyrow];
//            next = rows[i + 1].querySelectorAll('td')[keyrow];
//
//            if (reversed) {
//                if (Number(current.textContent) < Number(next.textContent)) {
//                    makeswap = true;
//                    break;
//                }
//            } else {
//                if (Number(current.textContent) > Number(next.textContent)) {
//                    makeswap = true;
//                    break;
//                }
//            }
//        }
//        if (makeswap) {
//            rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
//            swap = true;
//        }
//   }
}

function timestampToDate(timestamp) {
                var taskDate = new Date(timestamp * 1000);
                var daysOfWeek = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat' ];  
                var monthsOfYear = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
                var taskHours = "0" + taskDate.getHours();
                var taskMinutes = "0" + taskDate.getMinutes();
                var taskSeconds = "0" + taskDate.getSeconds();
                var taskYear = taskDate.getFullYear();
                var taskDay = daysOfWeek[taskDate.getDay()];
                var taskDayNum = taskDate.getDate();
                var taskMonth = monthsOfYear[taskDate.getMonth()];

                var formattedDate = taskMonth + " " + taskDayNum + " " + taskHours.substr(-2) + ":" + taskMinutes.substr(-2) + ":" + taskSeconds.substr(-2);

                return formattedDate;
}

btn.addEventListener("click", addTask);
