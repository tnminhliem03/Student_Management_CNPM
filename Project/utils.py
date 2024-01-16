import hashlib
import math

from Project.models import User, UserRole, Employee, Admin, UserRoles, Student, UserContact, LoaiTTLL, \
    ChangedNotification, Grade, Students_Classes, ScoreDetails, Score, ScoreType
from flask import session
from Project import db, dao, app
from flask_login import current_user


def check_user(username, password, type):
    enc_pass = hashlib.md5(str(password).encode("utf-8")).hexdigest()
    user = User.query.filter(User.username.__eq__(username.strip()),
                             User.password.__eq__(enc_pass)).first()
    if type != "HOCSINH" and user:
        roles = UserRoles.query.filter(UserRoles.user_id.__eq__(user.id)).all()
        for r in roles:
            if UserRole[type] == r.role:
                print('True')
                session['role'] = type
                return user

    session['role'] = None
    return user
def check_user_by_name(name):
    return User.query.filter(User.name.__eq__(name)).first()

def student_registered(name, gender, address, birthdate, username, password, **kwargs):

    password = hashlib.md5(str(password).encode('utf-8')).hexdigest()
    name = name.split(' ')
    family_name = ""
    for i in range(len(name)):
        if i < len(name)-1:
            family_name += name[i]
            if i < len(name)-2:
                family_name += " "
        else:
            first_name = name[i]
    user = User(family_name = family_name,
                first_name = first_name,
                gender = gender,
                address = address,
                birthdate = birthdate,
                image = kwargs.get('image'),
                username = username,
                password = password)
    db.session.add(user)
    db.session.commit()
    role = UserRoles(user_id = user.id, role = UserRole.HOCSINH)
    semester_id = dao.get_latest_semester().id
    hocsinh_info = Student(user_id = user.id, semester_id = semester_id, grade = Grade[kwargs.get('grade')])
    if kwargs.get("email"):
        email = UserContact(user_id = user.id, contactType = LoaiTTLL.EMAIL, contactData = kwargs.get('email'))
        db.session.add(email)
    if kwargs.get("phone"):
        phone = UserContact(user_id = user.id, contactType = LoaiTTLL.DTCANHAN, contactData = kwargs.get('phone'))
        db.session.add(phone)
    db.session.add_all([role, hocsinh_info])
    db.session.commit()

def commit_changes(content):
    user_id = current_user.id
    user_role = session.get('role')
    change = ChangedNotification(user_id = user_id, user_role = UserRole[user_role], content = content)
    db.session.add(change)
    db.session.commit()
def objectRegister(obj):
    name = obj['name']
    gender = obj['gender']
    address = obj['address']
    birthdate = obj['birthdate']
    image = obj['image']
    email = obj['email']
    phone = obj['phone']
    grade = obj['grade']

    temp = remove_accents(name).lower().split(" ")
    username = ""
    password = ""
    for i in range(len(temp)):
        if i < len(temp) - 1:
            username += temp[i][0]
        else:
            username += temp[i]
        password += temp[i]

    try:
        student_registered(name=name, gender=gender,
                                 address=address, birthdate=birthdate, image=image,
                                 username=username, password=password, email=email,
                                 phone=phone, grade = grade)
    except Exception as ex:
        msg = {"status": "failed", "message": f"Hệ thống lỗi: {ex}"}
    else:
        msg = {"status": "success", "message": f"Thêm thành công"}
    return msg

def add_students_to_classes(students, classes, max):

    availables = []
    for i in classes:
        if dao.load_students_count(i.id) < max:
            availables.append(i.id)
    i = 0
    while len(availables) >0 and len(students) > 0:
        student = students[0]
        class_id = availables[i]
        temp = Students_Classes(class_id=class_id, student_id=student.user_id)
        db.session.add(temp)
        db.session.commit()
        students.pop(0)
        if dao.load_students_count(class_id) == max:
            availables.pop(availables.index(class_id))
        i = 0 if i >= len(availables) - 1 else i + 1
def pageTags(total, page):
    pages = math.ceil(total / app.config['CN_PAGE_SIZE'])
    page = int(page)
    if page == 1:
        tags = {'start': 1,'end': pages if 3>pages else 3}
    elif page == pages:
        tags = {'start': page-2 if page-2>0 else 1, 'end': page}
    else:
        tags = {'start': page-1,'end' : page if page+1 > pages else page+1}
    return tags

def update_score_record(record, list):
    if len(list) > 0:
        if list[0] == "":
            db.session.delete(record)
            db.session.commit()
        else:
            record.score = float(list[0])
        db.session.commit()
        list.pop(0)
def overall_score(student_id, year):
    semester = dao.get_semester(year)
    avg_smt=[]
    for s in semester:
        score_label = Score.query.filter(Score.student_id.__eq__(student_id), Score.semester_id.__eq__(s.id)).all()
        avg_sj=[]
        if len(score_label) == 0:
            return 0
        for sc in score_label:
            avg, total = 0, 0
            for d in sc.details:
                match d.score_type:
                    case ScoreType.MINS15:
                        avg += d.score
                        total += 1
                    case ScoreType.MINS45:
                        avg += (d.score) * 2
                        total += 2
                    case ScoreType.FINAL:
                        avg += (d.score) * 3
                        total += 3
            avg = float(avg / total) if total!=0 else 0
            avg_sj.append(avg)
        avg = float(sum(avg_sj)/len(avg_sj)) if len(avg_sj)>0 else 0
        avg_smt.append(avg)
    return float(sum(avg_smt)/len(avg_smt)) if len(avg_smt)>0 else 0


def add_score_record(list, Scoretype, score):
    for sd in list:
        if sd != '':
            temp = ScoreDetails(score_id=score.id, score_type=Scoretype, score=float(sd))
            db.session.add(temp)
            db.session.commit()
s1 = u'ÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚÝàáâãèéêìíòóôõùúýĂăĐđĨĩŨũƠơƯưẠạẢảẤấẦầẨẩẪẫẬậẮắẰằẲẳẴẵẶặẸẹẺẻẼẽẾếỀềỂểỄễỆệỈỉỊịỌọỎỏỐốỒồỔổỖỗỘộỚớỜờỞởỠỡỢợỤụỦủỨứỪừỬửỮữỰựỲỳỴỵỶỷỸỹ'
s0 = u'AAAAEEEIIOOOOUUYaaaaeeeiioooouuyAaDdIiUuOoUuAaAaAaAaAaAaAaAaAaAaAaAaEeEeEeEeEeEeEeEeIiIiOoOoOoOoOoOoOoOoOoOoOoOoUuUuUuUuUuUuUuYyYyYyYy'
def remove_accents(input_str):
	s = ""
	for c in input_str:
		if c in s1:
			s += s0[s1.index(c)]
		else:
			s += c
	return s