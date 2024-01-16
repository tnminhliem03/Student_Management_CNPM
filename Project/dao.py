from sqlalchemy import func

from Project.models import User, ChangedNotification, UserRole, Student, Principle, Semester, Class, Grade, \
    Students_Classes, TeachingPlan, Subject, Teacher, Teachers_Subjects, Score, ScoreDetails, ScoreType, UserRoles
from Project import app, db
import hashlib

def load_user(user_id):
    return User.query.get(user_id)
def load_user_all():
    return User.query.all()
def load_changed_notification(filter = None, page = None):
    mylist = ChangedNotification.query

    if filter:
        mylist = ChangedNotification.query.filter(ChangedNotification.user_role.__eq__(UserRole[filter]))
    if page:
        mylist = mylist.order_by(ChangedNotification.id.desc())
        page = int(page)
        page_size = app.config['CN_PAGE_SIZE']
        start = (page-1)*page_size
        mylist = mylist[start: start+page_size]
        return mylist
    return mylist.order_by(ChangedNotification.id.desc())

def load_changed_notifications_count():
    return ChangedNotification.query.count()

def load_students_all(grade = None, page = None, kw = None, semester=None):
    students = db.session.query(Student).join(User)
    if semester:
        students = students.filter(Student.semester_id.__eq__(semester))
    if grade:
        students = students.filter(Student.grade.__eq__(Grade[grade]))
    if kw:
        students = students.filter(User.name.icontains(kw))
    if page:
        students = students.order_by(User.first_name.asc())
        page = int(page)
        page_size = app.config['CN_PAGE_SIZE']
        start = (page-1)*page_size
        students = students[start: start+page_size]
        return students
    return students.order_by(User.first_name.asc()).all()
def load_students_count(id_class = None):
    counter = Student.query
    if id_class:
        counter = Students_Classes.query.filter(Students_Classes.class_id.__eq__(id_class))
    return counter.count()


def load_non_class_students(grade, kw = None, year = None):

    grade = Grade[grade]
    year = get_latest_semester().year if year == None else year
    class_students = (db.session.query(Student.user_id)
                .join(Students_Classes)
                .join(Class)
                .filter(Student.grade.__eq__(Class.grade),
                        Class.year.__eq__(year)))
    non_class_students = db.session.query(Student).join(User).join(Semester).filter(Student.user_id.not_in(class_students),
                                                                           Semester.year.__eq__(year),
                                                                           Student.grade.__eq__(grade))
    if kw:
        non_class_students = non_class_students.filter(User.name.icontains(kw))
    return non_class_students.order_by(User.first_name).all()

def load_priciples_all():
    return Principle.query.all()
def load_principles_name(name):
    return Principle.query.filter(Principle.type.__eq__(name)).first()

def get_latest_semester():
    return Semester.query.order_by(Semester.id.desc()).first()

def get_previous_semester():
    return Semester.query.order_by(Semester.id.desc()).all()[1]

def get_semester(year = None):
    semester = Semester.query
    if year:
        semester = semester.filter(Semester.year.__eq__(year))
    return semester.all()
def load_semester_by_id(id):
    return Semester.query.filter(Semester.id.__eq__(id)).first()
def load_years_of_semester():
    return db.session.query(Semester.year).distinct().all()

def load_classes_all(grade = None, kw = None, page = None, year = None):
    classes = Class.query
    if grade:
        classes = classes.filter(Student.grade.__eq__(Grade[grade]))
    if kw:
        classes = classes.filter(Class.name.icontains(kw))
    if year:
        classes = classes.filter(Class.year.__eq__(year))
    if page:
        classes = classes.all()
        page = int(page)
        page_size = app.config['CN_PAGE_SIZE']
        start = (page-1)*page_size
        classes = classes[start: start+page_size]
        return classes
    return classes.all()
def load_classes_count(year = None):
    counter = Class.query
    if year:
        counter = counter.filter(Class.year.__eq__(year))
    return counter.count()


def get_the_latest_class_of_student(student_id):
    year = load_user(student_id).student[0].semester.year
    return (db.session.query(Class)
            .join(Students_Classes)
            .filter(Students_Classes.student_id.__eq__(student_id), Class.year.__eq__(year))
            .first())
def load_class(id = None, name = None):
    if id:
        return Class.query.filter(Class.id.__eq__(id)).first()
    if name:
        return Class.query.filter(Class.name.__eq__(name)).first()
    return None
def load_non_homeroom_teacher(year):
    myIDList = db.session.query(Teacher.user_id).join(Class).filter(Class.year.__eq__(year))
    myList = db.session.query(Teacher).filter(Teacher.user_id.not_in(myIDList)).all()
    return myList
def load_class_of_teacher(id, semester = None, grade = None, year = None):
    myclass = db.session.query(Class).join(TeachingPlan).filter(TeachingPlan.teacher_id==id)
    if semester:
        semester = load_semester_by_id(semester)
        myclass = myclass.filter(Class.year.__eq__(semester.year))
    if year:
        myclass = myclass.filter(Class.year.__eq__(year))
    if grade:
        myclass = myclass.filter(Class.grade.__eq__(Grade[grade]))
    return myclass.all()
def load_subject_planned_teacher(id, class_id = None):
    subjects = db.session.query(Subject).join(TeachingPlan).filter(TeachingPlan.teacher_id == id,TeachingPlan.class_id == class_id).all()
    return subjects

def load_teachers_of_subject(id):
    return db.session.query(Teacher).join(Teachers_Subjects).filter(Teachers_Subjects.subject_id.__eq__(id)).all()

def load_subject_all(grade = None, non_plan = False, class_id=None):
    subjects = Subject.query
    if grade:
        subjects = subjects.filter(Subject.grade.__eq__(grade))
    if non_plan:
        alr_subjects = db.session.query(Subject.id).join(TeachingPlan).filter(TeachingPlan.class_id.__eq__(class_id))
        subjects = subjects.filter(Subject.id.not_in(alr_subjects))
    return subjects.all()

def load_teaching_plan(teacher_id, class_id = None, subject_id = None):
    myPlan = TeachingPlan.query.filter(TeachingPlan.teacher_id.__eq__(teacher_id))
    if class_id:
        myPlan = myPlan.filter(TeachingPlan.class_id.__eq__(class_id))

    if subject_id:
        myPlan = myPlan.filter(TeachingPlan.subject_id.__eq__(subject_id))

    return myPlan.all()
def load_teachers_subjects():
    return Teachers_Subjects.query.all()

def load_score_of_student(teaching_plan_id, student_id, semester):
    return Score.query.filter(Score.plan_id.__eq__(teaching_plan_id),
                              Score.student_id.__eq__(student_id),
                              Score.semester_id.__eq__(semester)).first()

def subject_report(subject_id=None, semester_id = None):
    with app.app_context():
        data = []
        if subject_id and semester_id:
            score_semester = db.session.query(Semester.id, Semester.year).filter(Semester.id.__eq__(semester_id)).first()
            classes = db.session.query(Class.id, Class.name).filter(Class.year == score_semester.year).distinct().all()
            plans = db.session.query(TeachingPlan).join(Class).filter(TeachingPlan.subject_id.__eq__(subject_id), Class.year.__eq__(score_semester.year)).all()
            if len(plans) == 0:
                return data
            print(plans)
            avg_final_results = []
            number_students = []
            students_passed = []
            passing_rate = []
            for plan in plans:

                students_query = db.session.query(Student).join(Score).filter(
                    Score.plan_id.__eq__(plan.id)).all()
                print(students_query)
                if students_query == []:
                    return data
                total = len(students_query)
                number_students.append(total)

                passed = 0
                for s in students_query:
                    avg = 0
                    sum = 0
                    s_score = db.session.query(Score).join(TeachingPlan).filter(Score.student_id.__eq__(s.user_id), Score.semester_id.__eq__(semester_id), TeachingPlan.subject_id.__eq__(subject_id)).first()
                    if s_score is None or s_score.details == []:
                        avg = 0
                    else:
                        for s_d in s_score.details:
                            match s_d.score_type:
                                case ScoreType.MINS15:
                                    avg += s_d.score
                                    sum += 1
                                case ScoreType.MINS45:
                                    avg += (s_d.score)*2
                                    sum += 2
                                case ScoreType.FINAL:
                                    avg += (s_d.score)*3
                                    sum += 3
                        avg = float(avg/sum)
                    avg_min = load_principles_name("AVG_MIN").data
                    if avg >= avg_min:
                        passed += 1
                    avg_final_results.append((s.user_id, avg))
                students_passed.append(passed)
                rate = passed/total *100 if total > 0 else 0
                passing_rate.append(rate)


            for i in range(len(classes)):
                data.append({
                    'class_name': classes[i].name,
                    'number_students': number_students[i],
                    'students_passed': students_passed[i],
                    'passing_rate': passing_rate[i]
                })
        return data

def user_count():
    with app.app_context():
        return db.session.query(UserRoles.role, func.count(UserRoles.id)).group_by(UserRoles.role).all()



