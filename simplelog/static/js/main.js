
var tbody = document.querySelector('tbody');
var btn = document.querySelector('#btnTask');
var inpt = document.querySelector('#newTaskText');

var tasks;

function getTasks() {
    while(tbody.firstChild) {
    tbody.removeChild(tbody.firstChild);
    }
    var request = new XMLHttpRequest();
    request.open('GET', 'http://tlvericu16.mskcc.org:9000/task');
    request.responseType = 'json';
    request.onload = function () {
        tasks = request.response;
        for (var task in tasks) {
            var tr = document.createElement('tr');
            var close_btn_td = document.createElement('td');
            var close_btn = document.createElement('button');
            var close_span = document.createElement('span');
            close_btn.setAttribute("type", "button");
            close_btn.setAttribute("class", "close my-1 my-sm-0");
            close_btn.setAttribute("aria-label", "Close");
            close_btn.setAttribute("value", task_id);
            close_span.setAttribute("aria-hidden", "true");
            close_span.textContent = "x";
            var task_id = document.createElement('td');
            var task_time = document.createElement('td');
            var task_status = document.createElement('td');
            var task_text = document.createElement('td');
            task_id.textContent = task.slice(0, 5) + "..";
            task_time.textContent = tasks[task]['time'];
            task_status.textContent = tasks[task]['status'];
            task_text.textContent = tasks[task]['task'];
            close_btn.appendChild(close_span);
            close_btn_td.appendChild(close_btn);
            tr.appendChild(close_btn_td);
            tr.appendChild(task_id);
            tr.appendChild(task_time);
            tr.appendChild(task_status);
            tr.appendChild(task_text);
            tbody.appendChild(tr);
        }
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
    req_new_task.open("PUT", "http://tlvericu16.mskcc.org:9000/task");
    req_new_task.setRequestHeader("Content-type", "application/json");
    req_new_task.send(JSON.stringify(pdata));
    inpt.value = "";
    inpt.focus();
    getTasks();
}

btn.addEventListener("click", addTask);