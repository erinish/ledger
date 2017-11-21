
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
                var task_status = document.createElement('td');
                var task_text = document.createElement('td');
                task_id.textContent = task.slice(0, 5) + "..";
                task_time.textContent = tasks[task]['time'];
                task_status.textContent = tasks[task]['status'];
                task_text.textContent = tasks[task]['task'];

                close_btn.appendChild(close_span);
                delete_btn.appendChild(delete_span);
                btn_td.appendChild(close_btn);
                btn_td.appendChild(delete_btn);

                tr.appendChild(btn_td);
                tr.appendChild(task_id);
                tr.appendChild(task_time);
                tr.appendChild(task_status);
                tr.appendChild(task_text);
                tbody.appendChild(tr);
            }
        }

        sortTable(document.querySelector('tbody'), 2);
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
    req_new_task.open("PUT", "task");
    req_new_task.setRequestHeader("Content-Type", "application/json");
    req_new_task.send(JSON.stringify(pdata));
    inpt.value = "";
    inpt.focus();
    getTasks();
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
    req_delete_task.open("DELETE", task_url);
    req_delete_task.send();
    getTasks(currentView);
}

function closeTask(taskid) {
    var pdata = {};
    pdata["status"] = "closed";
    var req_close_task = new XMLHttpRequest();
    var task_url = "task/" + taskid;
    req_close_task.open("PUT", task_url);
    req_close_task.setRequestHeader("Content-Type", "application/json");
    req_close_task.send(JSON.stringify(pdata));
    getTasks(currentView);
}

function sortTable(table, keyrow) {
   var rows;
   var current, next;
   var swap = true;
   var makeswap;
   
   while(swap) {
        swap = false;
        rows = table.rows;

        for (var i = 0; i < rows.length - 1; i++) {
            makeswap = false;
            current = rows[i].querySelectorAll('td')[keyrow];
            next = rows[i + 1].querySelectorAll('td')[keyrow];

            if (Number(current.textContent) > Number(next.textContent)) {
                makeswap = true;
                break;
            }
        }
        if (makeswap) {
            rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
            swap = true;
        }
   }
}

btn.addEventListener("click", addTask);
