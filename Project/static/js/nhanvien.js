
function delete_from_list(id, obj){
    if (confirm("Bạn chắc chắn muốn xóa") == true){
        obj.disabled = true;
        fetch(`/api/user_pending/${id}`, {
            method: 'DELETE'
        }).then(function(res){
            return res.json()
        }).then(function(data){
            console.log(data)
            obj.disabled = false
            document.getElementById(id).style.display = "none"
        })
    }
}

function validate(id, obj){
    if (confirm("Xác nhận lưu học sinh này?")==true){
        obj.disabled = true;
        fetch(`/api/validate_user/${id}`, {
            method: 'POST'
        }).then(function(res) {
            return res.json()
        }).then(function(data){
            console.log(data)
            obj.disabled = false
            if (data['status'] == "success") document.getElementById(id).style.display = "none"
            alert(data['message'])
        })
    }
}
function validate_all(obj){
    if (confirm("Xác nhận sao lưu tất cả học sinh trong hàng chờ")==true){
        obj.disabled = true
        fetch('/api/validate_user', {
            method: 'POST'
        }).then(function(res){
            return res.json()
        }).then(function(data){
            obj.disabled = false
            console.log(data)
            if (data['status'] == 'failed')
                alert(data['message'])
            else{
                alert("Lưu hoàn thành")
                for(var i = 1; i <= data['success'].length; i++)
                    document.getElementById(i).style.display = 'none'
            }
        })
    }
}

function get_non_class_user_by_grade(){
grade = document.getElementById('grade').value
console.log(grade)
if (grade!="NULL")
    fetch(`/api/non_class_student/${grade}`)
    .then(function(res){
        return res.json()
    }).then(function(data){
        document.getElementById('amount').value = data.length
        html = ""
        for(var i = 0; i<data.length; i++){
            html += `<li class="list-group-item" style="height: 20%; display: flex; justify-content: space-between">
                <div style="width: 5%">${data[i]['id']}</div>
                <div style="width: 20%">${data[i]['name']}</div>
                <div style="width: 10%">Khối ${data[i]['grade']}</div>
                <div style="width: 20%">${data[i]['semester']}</div>
            </li>`
        }
        document.getElementById('student_panel_get').innerHTML = html
        console.log(data)
    })
else
    document.getElementById('amount').value = ""
    document.getElementById('student_panel_get').innerHTML = "<h2 style='display: flex; justify-content: center; align-items: center'>Vui lòng chọn khối lớp</h2>"
}

function change_teacher(id_class){
    teacher = document.getElementById('teacher_id').value
    console.log(teacher)
    if (confirm("Xác nhận thay đổi") == true){
        fetch(`/api/change_class/${id_class}`, {
            method: "PUT",
            body: JSON.stringify({
                'change' : "teacher",
                "teacher_id": teacher
            }),
            headers: {
                "Content-Type": "application/json"
            }
        }).then(res => res.json()).then(function(data){
            alert(data['message'])
            location.reload()
        })
    }
}
function toggleLockClass(id_class){
    if (confirm("Xác nhận thay đổi") == true){
        fetch(`/api/change_class/${id_class}`, {
            method: "PUT",
            body: JSON.stringify({
                'change' : "active",
            }),
            headers: {
                "Content-Type": "application/json"
            }
        }).then(res => res.json()).then(function(data){
            alert(data['message'])
            location.reload()
        })
    }
}

function subjectTeacher(subject_id, id){

    fetch(`/api/subject_teacher/${subject_id}`
    ).then(res => res.json()).then(function(data){
        html = "<option value=''>Chọn giáo viên</option>"
        for(var i =0; i<data.length; i++)
            html += `<option value='${data[i]['id']}'>${data[i]['name']}</option>`
        document.getElementById(id).innerHTML = html
    })
}

function subject_teacher_on_change(id_src, dest){
    subject_id = document.getElementById(id_src).value
    subjectTeacher(subject_id, dest)
}
function update_plan_teacher(subject_id, class_id)
{
    if(confirm("Xác nhận thay đổi") == true){
        teacher_id = document.getElementById(`subject_teacher_${subject_id}`).value
        if (teacher_id == "")
        return
        console.log(teacher_id)
        fetch(`/api/change_class/${class_id}`, {
            method: "PUT",
            body: JSON.stringify({
                'change' : "teacher_subject",
                'teacher_id': teacher_id,
                'subject_id': subject_id,
            }),
            headers: {
                "Content-Type": "application/json"
            }
        }).then(res => res.json()).then(function(data){
            alert(data['message'])
        })
    }

}

function Edit(){
    document.getElementById(`plan_edit_btn`).style.display = "none"
    document.getElementById(`plan_exit_btn`).style.display = "block"
    document.getElementById(`plan_edit`).style.display = "block"
    document.getElementById(`plan_result`).style.display = "none"
}

function Exit(){
    location.reload()
}

function delete_plan(subject_id, class_id){
if(confirm("Xác nhận xóa môn này!")){
    fetch(`/api/change_class/${class_id}`, {
            method: "DELETE",
            body: JSON.stringify({
                'change' : "subject",
                'subject_id': subject_id,
            }),
            headers: {
                "Content-Type": "application/json"
            }
        }).then(res => res.json()).then(function(data){
            alert(data['message'])
            document.getElementById(`plan_subject${subject_id}`).style.display = "none"
        })
        }
}

function create_new_plan(class_id){

if(confirm("Xác nhận thêm môn này!")){
    subject_id = document.getElementById("subject_select").value
    teacher_id = document.getElementById("teacher_select").value
    console.log(subject_id, teacher_id)
    fetch(`/api/change_class/${class_id}`, {
            method: "POST",
            body: JSON.stringify({
                'change' : "subject",
                'subject_id': subject_id,
                'teacher_id': teacher_id,
            }),
            headers: {
                "Content-Type": "application/json"
            }
        }).then(res => res.json()).then(function(data){
            alert(data['message'])
            location.reload()
        })
        }
}

function delete_student(class_id, student_id){
    if(confirm("Xóa học sinh này?")){
        fetch(`/api/change_class/${class_id}`, {
            method: "DELETE",
            body: JSON.stringify({
                'change' : "student",
                'student_id': student_id,
            }),
            headers: {
                "Content-Type": "application/json"
            }
        }).then(res => res.json()).then(function(data){
            alert(data['message'])
            document.getElementById(`student_${student_id}`).style.display = "none"
        })
    }
}

function add_student_list(grade, year){

    kw = document.getElementById('student_name').value
    console.log(kw)
    fetch(`/api/non_class_student/${grade}?kw=${kw}`,{
        method: "POST",
        body: JSON.stringify({
            'year': year
        }),
        headers: {
            'Content-Type': 'application/json'
        }
    }).then((res) => res.json()).then(function(data){
        console.log(data)
        temp = ""
        for(var i = 0; i<data.length; i++){
            temp += `<li  class="list-group-item" style="height: 20%; display: flex; justify-content: space-between;">
                        <input id="s${data[i].id}" onclick="add_to_student('s${data[i].id}')" class="form-check-input" type="checkbox" value="${data[i].id}">
                        <div style='width: 3%'>${data[i].id}</div>
                        <div style='width: 40%'>${data[i].name}</div>
                        <div style='width: 12%'>Khối ${data[i].grade}</div>
                        <div style='width: 30%'>${data[i].semester}</div>
                     </li>`
        }
        document.getElementById("non_student_list").innerHTML = temp
        for (var i =0; i<student_append.length; i++)
            document.getElementById(`s${student_append[i]}`).checked = true
    })
}
var student_append = []

function add_to_student(id){
    check = document.getElementById(id)
    if (check.checked){
        student_append.push(parseInt(check.value))
    }
    else{
        index = student_append.indexOf(parseInt(check.value))
        if ( index >-1)
            student_append.splice(index, 1)
    }
    console.log(student_append)
}

function add_to_class(class_id){
    if(student_append.length == 0){
        alert("Vui lòng chọn sinh viên !")
        return
    }
    if (confirm("Xác nhận thêm sinh viên?")){
        fetch(`/api/change_class/${class_id}`, {
            method: "POST",
            body: JSON.stringify({
                'change' : "student",
                'students_id': student_append,
            }),
            headers: {
                "Content-Type": "application/json"
            }
        }).then(res => res.json()).then(function(data){
            alert(data['message'])
            location.reload()
        })
    }
}