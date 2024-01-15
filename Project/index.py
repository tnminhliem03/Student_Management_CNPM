import hashlib
import math
from datetime import date

import cloudinary.uploader
from flask import render_template, redirect, url_for, request, session, jsonify
from flask_login import  current_user, login_user, login_required, logout_user
from Project import app, login, dao, utils, db
from Project.models import UserRole, Grade, Class, Students_Classes, TeachingPlan, ScoreType, Score, ScoreDetails
from Project.forms import LoginForm, AddUserForm
from Project.decorator import role_only

@login.user_loader
def user_load(user_id):
    return dao.load_user(user_id)

@app.route("/")
def index():

    if current_user.is_authenticated:
        if session.get('role') == 'ADMIN':
            return redirect('/admin')
        return redirect(url_for("auth"))

    return redirect(url_for("login"))

@app.route("/login", methods = ["POST", "GET"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = LoginForm()
    msg = ""
    if request.method == "POST" and form.is_submitted():
        username = form.username.data
        password = form.password.data
        type = form.userType.data
        user = utils.check_user(username, password, type)
        if user and session.get('role'):
            login_user(user)
            return redirect(url_for("index"))
        msg = "Đăng nhập thất bại"
    return render_template("login.html", msg = msg, form = form)
@app.route("/home/")
@login_required
def auth():
    filter = request.args.get("filter")
    page = request.args.get("page")
    page = page if page else 1
    changed = dao.load_changed_notification(filter=filter, page=page)

    total = dao.load_changed_notifications_count()
    tags = utils.pageTags(total, page)
    return render_template("menu.html", tags = tags, notifications=changed)
@app.route('/nhanvien/quan_ly_sinh_vien')
@login_required
@role_only('NHANVIEN')
def student_management():

    kw = request.args.get('kw')
    grade = request.args.get('grade')
    page = request.args.get("page")
    page = page if page else 1
    students = dao.load_students_all(grade=grade, kw=kw, page=page)
    total = dao.load_students_count()
    tags = utils.pageTags(total, page)
    return render_template('nhanvien/StudentManagement.html', stuList = students, tags = tags)

@app.route('/nhanvien/them_hoc_sinh')
@login_required
@role_only('NHANVIEN')
def add_student():
    form = AddUserForm()
    # session['pending_users'] = None
    session_pending = session.get('pending_users')
    if session_pending is None:
        session_pending = {}
        session_pending['msg'] = {}
        session_pending['total'] = 0
        session['pending_users'] = session_pending
    users_pending = []
    for c in session['pending_users'].values():
        if c != session['pending_users']['msg'] and c!= session['pending_users']['total']:
            users_pending.append(c)
    msg = session_pending['msg']
    amount = session_pending['total']
    return render_template('nhanvien/AddStudent.html', form = form, users_pending = users_pending, msg = msg, amount= amount)
@app.route('/nhanvien/quan_ly_lop_hoc')
@login_required
@role_only('NHANVIEN')
def class_management():
    kw = request.args.get('kw')
    grade = request.args.get('grade')
    page = request.args.get("page")
    page = page if page else 1
    classes = dao.load_classes_all(grade=grade, kw=kw, page=page)
    total = dao.load_classes_count()

    tags = utils.pageTags(total, page)
    return render_template('nhanvien/ClassesManagement.html', clsList= classes, tags=tags)

@app.route('/nhanvien/them_lop_hoc', methods = ['GET', 'POST'])
@login_required
@role_only('NHANVIEN')
def add_classes():
    msg = None
    if request.method == "POST":
        grade = request.form.get('grade')
        class_size = dao.load_principles_name('CLASS_MAX').data
        amount = request.form.get('amount')
        students = dao.load_non_class_students(grade)
        year = dao.get_latest_semester().year
        try:
            if Grade[grade] == Grade.K10:
                current_classes = dao.load_classes_all(grade = grade, year=year)
                if len(current_classes) != 0:
                    utils.add_students_to_classes(students=students, classes=current_classes, max = class_size)

                if len(students) > 0:
                    class_amount = math.ceil(len(students) / class_size)
                    counter = dao.load_classes_count(year)
                    classes = []
                    for i in range(class_amount):
                        name = f"{Grade[grade].value}A{"{:02}".format(counter+i+1)}"
                        tempClass = Class(name= name, amount = class_size,
                                          grade = Grade[grade], year = year)
                        db.session.add(tempClass)
                        db.session.commit()
                        classes.append(tempClass)
                    utils.commit_changes(f"tạo {class_amount} lớp")
                    utils.add_students_to_classes(students=students, classes=classes, max=class_size)
            else:
                for s in students:
                    old_class = dao.get_the_latest_class_of_student(s[0].id).name
                    index_class = old_class[-2:]
                    name = str(Grade[grade].value)
                    match Grade[grade]:
                        case Grade.K11:
                            name += "B"
                        case Grade.K12:
                            name += "C"
                    name += index_class
                    now_class = dao.load_class(name=name)
                    if now_class:
                        temp = Students_Classes(class_id = now_class.id, student_id = s[0].id)
                        db.session.add(temp)
                        db.session.commit()
                    else:
                        tempClass = Class(name = name,amount = class_size, grade = Grade[grade], year = year)
                        db.session.add(tempClass)
                        db.session.commit()
                        utils.commit_changes("tạo 1 lớp")
                        temp = Students_Classes(class_id = tempClass.id, student_id = s[0].id)
                        db.session.add(temp)
                        db.session.commit()
        except Exception as exc:
            msg = {
                'status' : "failed",
                'message' : exc
            }
        else:
            utils.commit_changes(f"phân lớp cho {amount} sinh viên")
            msg = {
                'status': "success",
                'message': "Tạo thành công"
            }
    return render_template('nhanvien/AddClasses.html', Grade = Grade, msg = msg)
@app.route("/logout/")
def logout():
    logout_user()
    return redirect(url_for("index"))

@app.route("/user/<user_id>")
@login_required
def info(user_id):
    user = dao.load_user(user_id)
    role = None

    student_class = ""
    for r in user.roles:
        if r.role == UserRole.HOCSINH:
            role = UserRole.HOCSINH.value
            student_class = dao.get_the_latest_class_of_student(user.id)
            student_class = student_class.name if student_class else "Chưa được xếp lớp"
            break
        if r.role == UserRole.GIAOVIEN:
            role = UserRole.GIAOVIEN.value

    return render_template('user_detail.html', user = user, UserRole = UserRole, role = role, student_class = student_class)

@app.route("/class/<class_id>")
@login_required
def class_info(class_id):
    myClass = dao.load_class(class_id)
    isEditable = UserRole[session.get('role')] == UserRole.NHANVIEN
    teachers = dao.load_non_homeroom_teacher(myClass.year)
    subjects = dao.load_subject_all(myClass.grade, non_plan=True, class_id=myClass.id)
    content = f'{dao.load_students_count(myClass.id)}/{int(dao.load_principles_name("CLASS_MAX").data)}'
    return render_template('class_detail.html', myClass = myClass, isEditable = isEditable, teachers = teachers,
                           subjects = subjects, student_count = content)
@app.context_processor
def common_things():
    missions = []
    msg = ""
    if current_user.is_authenticated:
        role = session.get('role')
        match role:
            case 'NHANVIEN':
                msg = "Xin chào nhân viên %s" % current_user.name
                missions = [
                    {'name': 'Quản lý sinh viên',
                     'link': "/nhanvien/quan_ly_sinh_vien"},
                    {'name': 'Quản lý lớp',
                     'link': '/nhanvien/quan_ly_lop_hoc'},
                    {'name': 'Quy định chung',
                     'link': '#'}
                ]
            case 'GIAOVIEN':
                msg = "Xin chào giáo viên %s" % current_user.name
                missions = [
                    {'name': 'Nhập điểm',
                     'link': '/giaovien/nhap_diem'},
                    {'name': 'Xuất Điểm',
                     'link': '/giaovien/xuat_diem'},
                    {'name': 'Quy định chung',
                     'link': '#'}
                ]
    return {
        'missions': missions,
        'msg' : msg
    }

#API
@app.route('/api/user_pending', methods = ["POST"])
@login_required
def pending():
    list = session.get('pending_users')
    age_start = dao.load_principles_name("AGE_START")
    age_end = dao.load_principles_name("AGE_END")

    name = request.form.get('name')
    gender = int(request.form.get('gender'))
    image = request.files.get('image')
    birthdate = request.form.get('birthdate')
    address = request.form.get('address')
    email = request.form.get('email')
    phone = request.form.get('phone')
    grade = request.form.get('grade')
    birthyear = int(birthdate[:4])
    birthmonth = int(birthdate[5:7])
    birthday = int(birthdate[8:10])
    acceptable = True
    error = ""


    age = date.today().year - birthyear
    if age < int(age_start.data) or age > int(age_end.data):
        acceptable = False
        error = "Số tuổi không đúng quy định"

    for i in range(1, list['total']+1):
        if list[str(i)]['name'] == name:
            acceptable = False
            error = "Người dùng đã được thêm vào hàng chờ"
    if utils.check_user_by_name(name):
        acceptable = False
        error = "Tên người dùng đã tồn tại"



    if not acceptable:
        list['msg'] = {
            'status': "failed",
            'message': error
        }
    else:
        if image:
            res = cloudinary.uploader.upload(image)
            image = res['secure_url']
        else:
            image = "https://res.cloudinary.com/dzm6ikgbo/image/upload/v1703999894/okrajh0yr69c5fmo3swn.png"
        list[str(list["total"]+1)] = {
            'id': list["total"]+1,
            'name': name,
            'gender': gender,
            'image': image,
            'birthdate': f'{birthday}-{birthmonth}-{birthyear}',
            'address': address,
            'email': email,
            'phone': phone,
            'grade': grade
        }
        list['msg'] = {
            'status': "success",
            'message': "Người dùng được thêm vào hàng chờ"
        }
    list['total'] = len(list)-2
    session['pending_users'] = list
    return redirect(url_for("add_student"))
@app.route('/api/user_pending/<id>', methods = ["DELETE"])

def pending_del(id):
    users_pending = session.get('pending_users')
    if users_pending and id in users_pending:
        image = users_pending[id]['image'].split("/")
        public_id = image[-1][:-4]
        cloudinary.uploader.destroy(public_id)
        users_pending['total'] -= 1
        del users_pending[id]
    session['pending_users'] = users_pending
    return jsonify(users_pending)
@app.route('/api/validate_user/<id>', methods = ["POST"])
def validate_user(id):
    users_pending = session.get('pending_users')
    if users_pending and id in users_pending:
        msg = utils.objectRegister(users_pending[id])
        if msg and msg['status']=='success':
            utils.commit_changes("Thêm 1 học sinh")
            users_pending['total'] -= 1
            del users_pending[id]
        session['pending_users'] = users_pending
    return jsonify(msg)
@app.route('/api/validate_user', methods = ["POST"])
def validate_all():
    user = []
    count = 0
    overview = {
        "status" : "success",
        "failed" : [],
        "success" : []
    }
    session_pending = session.get('pending_users')
    for pu in session['pending_users'].values():
        if pu != session['pending_users']['total'] and pu!= session['pending_users']['msg']:
            user.append(pu)
    if user == []:
        overview = {"status": "failed", "message":"Danh sách rỗng!"}
        return jsonify(overview)    
    for u in user:
        msg = utils.objectRegister(u)
        if msg and msg['status']=='success':
            overview['success'].append(u['id'])
            count += 1
            del session_pending[str(u['id'])]
            session_pending['total'] -= 1
        else:
            overview['failed'].append(u['name'])
    utils.commit_changes(f"thêm {count} học sinh")
    session['pending_users'] = session_pending
    return jsonify(overview)

@app.route('/api/non_class_student/<grade>', methods = ['GET', 'POST'])
def get_non_class(grade):
    kw = request.args.get('kw')
    year = request.json.get('year') if request.method=='POST' else None
    students = dao.load_non_class_students(grade, kw, year)
    list = []
    for s in students:
        temp = {
            'id': s.student_info.id,
            'name': s.student_info.name,
            'grade': s.grade.value,
            'semester': f"Học kì {s.semester.semester} năm {s.semester.year}"
        }
        list.append(temp)
    return jsonify(list)
@app.route('/api/change_class/<class_id>', methods = ['PUT', 'DELETE', 'POST'])
def change_info(class_id):
    myClass = dao.load_class(class_id)
    data = request.json
    change = data.get('change')
    failed = {
        "status": "failed",
        "message": ""
    }
    success = {
        "status": "success",
        "message": "Thay đổi thành công"
    }
    msg = {}
    if request.method == "PUT":
        match change:
            case "teacher":
                teacher_id = data.get('teacher_id')
                try:
                    myClass.teacher_id = teacher_id
                    db.session.commit()
                except Exception as exc:
                    msg = failed
                    msg['message'] = str(exc)
                else:
                    msg = success
                    utils.commit_changes(f"điều chỉnh giáo viên của lớp {myClass.name} - {myClass.year}")
            case "active":
                try:
                    myClass.active = not myClass.active
                    db.session.commit()
                except Exception as exc:
                    msg = failed
                    msg['message'] = str(exc)
                else:
                    msg = success
                    utils.commit_changes(f"điều chỉnh trạng thái của lớp {myClass.name} - {myClass.year}")
            case "teacher_subject":
                teacher_id = data.get('teacher_id')
                subject_id = data.get('subject_id')
                msg = failed
                msg['message'] = "Không tìm thấy"
                for pl in myClass.teaching_plan:
                    if pl.subject_id == subject_id:
                        try:
                            pl.teacher_id = teacher_id
                            db.session.commit()
                        except Exception as exc:
                            msg = failed
                            msg['message'] = str(exc)
                        else:
                            msg = success
                            utils.commit_changes(f"điều chỉnh giáo viên dạy môn {pl.subject_detail.name}"
                                                 f" của lớp {myClass.name} - {myClass.year}")
    elif request.method == "DELETE":
        match change:
            case "subject":
                subject_id = data.get("subject_id")
                msg =failed
                msg['message'] = "Không tìm thấy"
                for pl in myClass.teaching_plan:
                    if pl.subject_id == subject_id:
                        try:
                            name = pl.subject_detail.name
                            db.session.delete(pl)
                            db.session.commit()
                        except Exception as exc:
                            msg = failed
                            msg['message'] = str(exc)
                        else:
                            msg = success
                            utils.commit_changes(f"Xóa môn {name} khỏi lớp {myClass.name} - {myClass.year}")

            case "student":
                student_id = data.get('student_id')
                msg = failed
                msg['message'] = "Không tìm thấy"
                for s in myClass.students:
                    if s.student_id == student_id:
                        try:
                            name = s.student_detail.student_info.name
                            db.session.delete(s)
                            db.session.commit()
                        except Exception as exc:
                            msg = failed
                            msg['message'] = str(exc)
                        else:
                            msg = success
                            utils.commit_changes(f"xóa học sinh {name} khỏi lớp {myClass.name} - {myClass.year} ")
    else:
        match change:
            case "subject":
                subject_id = data.get('subject_id')
                teacher_id = data.get('teacher_id')
                try:
                    temp = TeachingPlan(teacher_id = teacher_id, subject_id = subject_id, class_id=class_id)
                    db.session.add(temp)
                    db.session.commit()
                except Exception as exc:
                    msg = failed
                    msg['message'] = str(exc)
                else:
                    msg = success
                    utils.commit_changes(f"thêm môn {temp.subject_detail.name} vào lớp {myClass.name} - {myClass.year}")
            case "student":
                students = data.get('students_id')
                print(students)
                class_max = dao.load_principles_name("CLASS_MAX").data
                if dao.load_students_count(myClass.id) + len(students) <= class_max:
                    try:
                        for s_id in students:
                            temp = Students_Classes(student_id = s_id, class_id = myClass.id)

                            db.session.add(temp)
                            db.session.commit()
                        myClass.amount = dao.load_students_count(myClass.id)
                        db.session.commit()
                    except Exception as exc:
                        msg = failed
                        msg['message'] = str(exc)
                    else:
                        msg = success
                        utils.commit_changes(f"thêm {len(students)} vào lớp {myClass.name} - {myClass.year}")
                else:
                    msg = failed
                    msg['message'] = "Lớp đầy, không thể thêm"
    return jsonify(msg)
@app.route('/api/subject_teacher/<subject_id>')
def get_subject_teacher(subject_id):
    teachers = dao.load_teachers_of_subject(subject_id)
    list = []
    for t in teachers:
        temp = {
            "id": t.user_id,
            "name": t.teacher_info.name
        }
        list.append(temp)
    return jsonify(list)

##GIAO VIEN
@app.route('/giaovien/nhap_diem')
@login_required
@role_only('GIAOVIEN')
def input_score():
    semesters = dao.get_semester()
    classes = dao.load_classes_all()
    teachers_subjects = dao.load_teachers_subjects()
    return render_template('/giaovien/inputScore.html', semesters = semesters,
                           classes = classes, teachers_subjects = teachers_subjects, grade = Grade)

@app.route('/giaovien/xuat_diem')
@login_required
@role_only('GIAOVIEN')
def output_score():
    semesters = dao.load_years_of_semester()
    print(semesters)
    classes = dao.load_classes_all()
    teachers_subjects = dao.load_teachers_subjects()
    return render_template('/giaovien/outputScore.html', semesters=semesters,
                           classes=classes, teachers_subjects=teachers_subjects, grade=Grade)


@app.route("/api/teaching_plan/<teacher_id>", methods = ['POST'])
def get_info(teacher_id):
    data = request.json
    semester = data.get("semester")
    grade = data.get("grade")
    subject = data.get("subject")
    myClass = data.get("myClass")
    type = data.get("type")
    msg = {
        "myClass": [] if myClass == "" else myClass,
        "subject": [] if subject == "" else subject
    }
    if myClass == "":
        listClass = []
        if type == "input":
            myClass = dao.load_class_of_teacher(teacher_id, semester, grade)
        else:
            myClass = dao.load_class_of_teacher(teacher_id, grade= grade, year= semester)
        for cl in myClass:
            temp = {
                "id": cl.id,
                "name": cl.name
            }
            listClass.append(temp)
        msg["myClass"] = listClass

    elif subject == "":
        listSubject = []
        mySubject = dao.load_subject_planned_teacher(teacher_id, myClass)
        for sb in mySubject:
            temp = {
                "id": sb.id,
                "name": sb.name
            }
            listSubject.append(temp)
        msg["subject"] = listSubject

    elif type == "input":
        teaching_plan = dao.load_teaching_plan(teacher_id, myClass, subject)[0]
        myStu = []
        for s in teaching_plan.class_detail.students:
            student_score = dao.load_score_of_student(teaching_plan.id, s.student_detail.user_id, semester)

            mins15, mins45, final = [], [], []
            if student_score:
                for s_c in student_score.details:
                    match s_c.score_type:
                        case ScoreType.MINS15:
                            mins15.append(s_c.score)
                        case ScoreType.MINS45:
                            mins45.append(s_c.score)
                        case ScoreType.FINAL:
                            final.append(s_c.score)
            temp = {
                "id": s.student_detail.user_id,
                "name": s.student_detail.student_info.name,
                "mins15": mins15,
                "mins45": mins45,
                "final": final
            }
            myStu.append(temp)
        temp = {
            "id": teaching_plan.id,
            "class_name": teaching_plan.class_detail.name,
            "subject_name": teaching_plan.subject_detail.name,
            "semester": dao.load_semester_by_id(semester).semester,
            "semester_year": dao.load_semester_by_id(semester).year,
            "students": myStu,
            "mins15": teaching_plan.subject_detail.mins15,
            "mins45": teaching_plan.subject_detail.mins45,
            "final": teaching_plan.subject_detail.final
        }
        msg["teaching_plan"] = temp
    else:
        print(data)
        myClass = dao.load_class(id=myClass)
        semester = dao.get_semester(semester)
        teaching_plan = dao.load_teaching_plan(teacher_id,myClass.id,subject)[0]
        subject = teaching_plan.subject_detail
        len_required = subject.mins15 + subject.mins45 + subject.final
        print(subject, len_required)
        stuList = []
        for s in myClass.students:
            student = {
                "id": s.student_detail.user_id,
                "name": s.student_detail.student_info.name,
                "class": myClass.name,
                "avg1": "hiện không khả dụng",
                "avg2": "hiện không khả dụng",
            }
            for sm in semester:
                stuScore = dao.load_score_of_student(teaching_plan.id,s.student_detail.user_id,sm.id)
                dtb = 0
                sum=0
                if stuScore is None or stuScore.details == [] or len(stuScore.details) < len_required:
                    student[f'avg{sm.semester}'] = f"Chưa đầy đủ điểm học kì {sm.semester} năm {sm.year}"
                    continue
                for sc in stuScore.details:
                    match sc.score_type:
                        case ScoreType.MINS15:
                            dtb += sc.score
                            sum += 1
                        case ScoreType.MINS45:
                            dtb += (sc.score*2)
                            sum += 2
                        case ScoreType.FINAL:
                            dtb += (sc.score*3)
                            sum += 3
                dtb = float(dtb/sum) if sum!= 0 else 0
                student[f'avg{sm.semester}'] = format(dtb, '.2f')
            stuList.append(student)
        temp = {
            "semester_year": semester[0].year,
            "students": stuList
        }
        msg["overview"] = temp
    return jsonify(msg)

@app.route("/api/score_validate", methods = ["POST"])
def validate_score():
    data = request.json
    plan_id = data.get('plan_id')
    students = data.get('students')
    semester_id = data.get('semester_id')
    class_id = data.get('class_id')
    print(class_id)
    myClass = dao.load_class(class_id)
    print(students)
    failed = {
         "status": "failed",
         "message": ""
    }
    success = {
         "status": "success",
         "message": "Xác nhận thành công"
    }
    for s in students:
        print(type(plan_id), type(int(s['id'])), type(semester_id))
        score_label = dao.load_score_of_student(plan_id, int(s['id']), semester_id)

        if score_label is None:
            try:
                score_label = Score(plan_id = plan_id, student_id = int(s['id']), semester_id = semester_id)
                db.session.add(score_label)
                db.session.commit()
            except Exception as exc:
                msg = failed
                msg['message'] = str(exc)
                return jsonify(msg)
        print(score_label.id)
        if len(score_label.details) > 0:
            for s_d in score_label.details:
                match s_d.score_type:
                    case ScoreType.MINS15:
                        utils.update_score_record(s_d, s['mins15'])
                    case ScoreType.MINS45:
                        utils.update_score_record(s_d, s['mins45'])
                    case ScoreType.FINAL:
                        utils.update_score_record(s_d, s['final'])

        utils.add_score_record(s['mins15'], ScoreType.MINS15, score_label)
        utils.add_score_record(s['mins45'], ScoreType.MINS45, score_label)
        utils.add_score_record(s['final'], ScoreType.FINAL, score_label)
    utils.commit_changes(f"thay đổi điểm của lớp {myClass.name}")
    msg = success
    return jsonify(msg)

@app.route("/api/subjects/<grade>")
def subject_of_grade(grade):
    grade = Grade[grade]
    subjects = dao.load_subject_all(grade=grade)
    res = []
    for s in subjects:
        temp = {
            'id' : s.id,
            'name': s.name
        }
        res.append(temp)
    return jsonify(res)

@app.route("/api/change_password/<user_id>", methods = ["POST"])
def change_password(user_id):
    data = request.json
    oldPw = data.get("old")
    newPw = data.get("new")
    user = dao.load_user(user_id)
    if hashlib.md5(oldPw.encode("utf-8")).hexdigest() == user.password:
        user.password = hashlib.md5(newPw.encode("utf-8")).hexdigest()
        db.session.commit()
        msg = {
            "message": "Cập nhật thành công"
        }
    else:
        msg = {
            "message": "Mật khẩu không đúng, vui lòng thử lại"
        }
    return jsonify(msg)
@app.route('/api/change_avatar/<user_id>', methods = ["POST"])
def change_avt(user_id):
   file = request.files.get('newFile')
   user = dao.load_user(user_id)
   if file:
        image = cloudinary.uploader.upload(file)
        path = image['secure_url']
        oldPath = user.image.split("/")
        public_key = oldPath[-1][:-4]
        user.image = path
        cloudinary.uploader.destroy(public_key)
        db.session.commit()
   return redirect(f'/user/{user_id}')

if __name__ == "__main__":
    from Project.admin import *
    app.run()