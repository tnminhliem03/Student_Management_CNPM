function done() {
       validate()
      alert("Thành công! Quá trình nhập điểm đã hoàn thành!");
}

function save() {
    alert("Thành công! Đã lưu vào nháp!");
}

function deleteScore() {
    alert("Thành công! Đã xóa hết điểm của học sinh!");
}


document.getElementById("btnPrint").onclick = function () {
    printElement(document.getElementById("printThis"));
}

function printElement(elem) {
    var domClone = elem.cloneNode(true);

    var $printSection = document.getElementById("printSection");

    if (!$printSection) {
        var $printSection = document.createElement("div");
        $printSection.id = "printSection";
        document.body.appendChild($printSection);
    }

    $printSection.innerHTML = "";
    $printSection.appendChild(domClone);
    window.print();
}
var teaching_plan_id = null
var list_student_id = []
var mins15 = 0, mins45 = 0, final = 0
function init(){
    teaching_plan_id = null
    list_student_id = []
    mins15, mins45, final = 0, 0, 0
}
function load(teacher_id, reset, part) {
    if (reset) {
        document.getElementById("class").innerHTML = "<option selected value=''>--- LỚP HỌC ---</option>"
        document.getElementById("subject").innerHTML = "<option selected value=''>--- MÔN HỌC ---</option>"
        init()
    }
    list_student_id = []
    semester = document.getElementById("semester").value
    grade = document.getElementById("grade").value
    myClass = document.getElementById("class").value
    subject = document.getElementById("subject").value
   if (myClass == "") {
        document.getElementById("subject").innerHTML = "<option selected value=''>--- MÔN HỌC ---</option>"
        init()
   }
    type = part ? "input" : "output"
    if (semester != "" && grade != "" ) {
        fetch(`/api/teaching_plan/${teacher_id}`, {
            method: "POST",
            body: JSON.stringify({
                "semester": semester,
                "grade": grade,
                "myClass": myClass,
                "subject": subject,
                "type": type
            }), headers: {
                "Content-Type": "application/json"
            }
        }).then(res => res.json()).then(function(data) {

            if (myClass == "") {
                temp = ""
                for (i = 0; i < data.myClass.length; i++) {
                    temp += `<option selected value="${data.myClass[i].id}">${data.myClass[i].name}</option>`
                }
                temp += "<option selected value=''>--- LỚP HỌC ---</option>"
                document.getElementById("class").innerHTML = temp
            }

            else if (subject == "") {
                temp = ""
                for (i = 0; i < data.subject.length; i++) {
                    temp += `<option selected value="${data.subject[i].id}">${data.subject[i].name}</option>`
                }
                temp += "<option selected value=''>--- MÔN HỌC ---</option>"
                document.getElementById("subject").innerHTML = temp
            }

            else if (type == "input"){

                if (part){
                cname = data.teaching_plan.class_name
                document.getElementById("doc_class_name").innerText = "Lớp: " + cname

                sname = data.teaching_plan.subject_name
                document.getElementById("doc_subject_name").innerText = "Môn: " + sname

                ss = data.teaching_plan.semester
                document.getElementById("doc_semester").innerText = "Học kỳ: " + ss
                }

                sy = data.teaching_plan.semester_year
                document.getElementById("doc_semester_year").innerText = "Năm học: " + sy

                students = data.teaching_plan.students
                temp = ""

                table = document.getElementById("stu_score")
                 if (table.rows.length > 4){
                    len = table.rows.length
                    for(var i = 4; i<len; i++)
                        table.deleteRow(4)
                }
                teaching_plan_id = data.teaching_plan.id
                mins15 = data.teaching_plan.mins15
                mins45 = data.teaching_plan.mins45
                final = data.teaching_plan.final
                for (i = 0; i < students.length; i++) {
                    row = table.insertRow(-1)
                    list_student_id.push(students[i].id)
                    temp = `
                    <tr>
                        <td>
                            <input class="hidden-border" type="text" name="STT" id="STT" value="${i + 1}" style="width:30px" readonly>
                        </td>

                        <td>
                            <input class="hidden-border" type="text" name="name_stu" id="name_stu" value="${students[i].name}" readonly>
                        </td>

                        <td>
                        `
                        for(var j = 0; j<mins15; j++)
                            if (j<students[i].mins15.length)
                            temp += `<input type="number" name="15min-1" id="${students[i].id}_15min_${j}" step="0.1" min="0" max="10" pattern="[0-9]*[,]?[0-9]" value=${students[i].mins15[j]}>`
                            else
                            temp += `<input type="number" name="15min-1" id="${students[i].id}_15min_${j}" step="0.1" min="0" max="10" pattern="[0-9]*[,]?[0-9]">`

                        temp+= `
                        </td>

                        <td>`
                        for(var j = 0; j<mins45; j++)
                            if (j<students[i].mins45.length)
                            temp += `<input type="number" name="45min-1" id="${students[i].id}_45min_${j}" step="0.1" min="0" max="10" pattern="[0-9]*[,]?[0-9]" value="${students[i].mins45[j]}">`
                            else
                            temp += `<input type="number" name="45min-1" id="${students[i].id}_45min_${j}" step="0.1" min="0" max="10" pattern="[0-9]*[,]?[0-9]">`

                        temp+=`
                        </td>

                        <td>`
                        for(var j = 0; j<final; j++)
                            if (j<students[i].final.length)
                            temp += `<input type="number" name="45min-1" id="${students[i].id}_final_${j}" step="0.1" min="0" max="10" pattern="[0-9]*[,]?[0-9]" value="${students[i].final[j]}">`
                            else
                            temp += `<input type="number" name="45min-1" id="${students[i].id}_final_${j}" step="0.1" min="0" max="10" pattern="[0-9]*[,]?[0-9]">`
                        temp +=`
                        </td>
                        </tr>`
                    row.innerHTML = temp
                }
            }
            else{
                console.log(data)
                sy = data.overview.semester_year
                document.getElementById("doc_semester_year").innerText = "Năm học: " + sy
                students = data.overview.students
                table = document.getElementById("stu_score")
                if (table.rows.length > 3){
                    len = table.rows.length
                    for(var i = 3; i<len; i++)
                        table.deleteRow(3)
                }
                for (i = 0; i < students.length; i++) {
                    row = table.insertRow(-1)
                    temp = `
                    <tr>
                        <td>
                            <input class="hidden-border" type="text" name="STT" id="STT" value="${i + 1}" style="width:30px" readonly>
                        </td>
                         <td>
                            <input class="hidden-border" type="text" name="name_stu" id="name_stu" value="${students[i].name}" readonly>
                        </td>
                         <td>
                            <input class="hidden-border" type="text" name="name_stu" id="name_stu" value="${students[i].class}" readonly>
                        </td>
                         <td>
                            <input class="hidden-border" type="text" name="name_stu" id="name_stu" value="${students[i].avg1}" readonly>
                        </td>
                         <td>
                            <input class="hidden-border" type="text" name="name_stu" id="name_stu" value="${students[i].avg2}" readonly>
                        </td>
                    </tr>`
                    row.innerHTML = temp
                }
            }
        })
    }

    else {
        document.getElementById("class").innerHTML = "<option selected value=''>--- LỚP HỌC ---</option>"
        document.getElementById("subject").innerHTML = "<option selected value=''>--- MÔN HỌC ---</option>"
    }
}

function validate(){
    if(confirm("Xác nhận chỉnh sửa điềm")){semester_id = document.getElementById("semester").value

    if (teaching_plan_id == null){
        alert("Vui lòng chọn lớp")
        return
    }
    stuList = []
    for(let i =0; i<list_student_id.length; i++){
        mins15_score = []
        for(let j = 0; j<mins15; j++){
            id = `${list_student_id[i]}_15min_${j}`
            temp = document.getElementById(id).value
            mins15_score.push(temp)
        }
        mins45_score = []
        for(let j = 0; j<mins45; j++){
            id = `${list_student_id[i]}_45min_${j}`
            temp = document.getElementById(id).value
            mins45_score.push(temp)
        }
        final_score = []
        for(let j = 0; j<final; j++){
            id = `${list_student_id[i]}_final_${j}`
            temp = document.getElementById(id).value
            final_score.push(temp)
            }
        temp = {
            "id": list_student_id[i],
             "mins15": mins15_score,
             "mins45": mins45_score,
             "final": final_score
        }
        stuList.push(temp)
    }
    console.log(stuList)
    class_id = document.getElementById("class").value
    fetch("/api/score_validate", {
        method: "POST",
        body: JSON.stringify({
            'plan_id': teaching_plan_id,
            'semester_id': semester_id,
            'students': stuList,
            'class_id': class_id
        }),
        headers: {
            "Content-Type": "application/json"
        }
    }).then(res => res.json()).then(function(data){
        console.log(data)
        alert(data['message'])
    })

}
}
//function checkScore() {
//    score_15_1_in = document.getElementById("15min-1").value
//    score_preriod_1_in = document.getElementById("period-1").value
//    score_midterm_in = document.getElementById("midterm").value
//    if (score_15_1_in == "" || score_preriod_1_in == "" || score_midterm_in == "")
//        alert("Vui lòng không bỏ sót sinh viên")
//    else
//        alert("Thành công! Quá trình nhập điểm đã hoàn thành!");
//
//}

//<tr>
//    <td>
//        <input class="hidden-border" type="text" name="STT" id="STT" value="${i + 1}" style="width:30px" readonly>
//    </td>
//
//    <td>
//        <input class="hidden-border" type="text" name="name_stu" id="name_stu" value="${students[i].name}" readonly>
//    </td>

//    <td>
//        <input class="hidden_border" type="text" name="stu_class" id="stu_class" value="" readonly>
//    </td>
//
//    <td>
//        <input class="hidden_border" type="text" name="score-sem-1" id="score-sem-1" value="" readonly>
//    </td>
//
//    <td>
//        <input class="hidden_border" type="text" name="score-sem-2" id="score-sem-2" value="" readonly>
//    </td>
//</tr>