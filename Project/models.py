import enum
import hashlib

from sqlalchemy.ext.hybrid import hybrid_property

from Project import db
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Enum, Text, Float, Date, UniqueConstraint
from sqlalchemy.orm import relationship
from flask_login import UserMixin
from datetime import datetime
#ENUM
class UserRole(enum.Enum):
    HOCSINH = "học sinh"
    NHANVIEN = "nhân viên"
    GIAOVIEN = "giáo viên"
    ADMIN = "người quản trị"

class LoaiTTLL(enum.Enum):
    EMAIL = "Email"
    DTCANHAN = "Số điện thoại"
class Grade(enum.Enum):
    K10 = 10
    K11 = 11
    K12 = 12
class ScoreType(enum.Enum):
    MINS15 = 0
    MINS45 = 1
    FINAL = 2
#DATABASE ORM
class BaseModel(db.Model):
    __abstract__ = True

    id = Column(Integer, primary_key= True, autoincrement= True)
    created_date = Column(DateTime, default=datetime.now())
    active = Column(Boolean, default= True)

class User(BaseModel, UserMixin):

    family_name = Column(String(50), nullable= False)
    first_name = Column(String(10), nullable=False)
    gender = Column(Boolean)
    address = Column(Text)
    birthdate = Column(String(10))
    username = Column(String(20), nullable= False, unique=True)
    password = Column(String(100), nullable=False)
    image = Column(String(100), default="https://res.cloudinary.com/dzm6ikgbo/image/upload/v1703999894/okrajh0yr69c5fmo3swn.png")
    @hybrid_property
    def name(self):
        return self.family_name+" " +self.first_name
    student = relationship("Student", backref="student_info", lazy=True)
    employee = relationship('Employee', backref="employee_info", lazy= True)
    contacts = relationship('UserContact', backref = "user", lazy=True)

    roles = relationship("UserRoles", backref="user_info", lazy=True)
    admin = relationship("Admin", backref="admin_info", lazy=True)
    teacher = relationship("Teacher", backref="teacher_info", lazy=True)
    changes = relationship("ChangedNotification", backref="user_detail", lazy=True)

class UserContact(BaseModel):
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)
    contactType = Column(Enum(LoaiTTLL))
    contactData = Column(String(30))

class ActorBase(db.Model):
    __abstract__ = True

    started_date = Column(DateTime, default=datetime.now())
    active = Column(Boolean, default=True)
class Employee(ActorBase):
    user_id = Column(Integer, ForeignKey(User.id), primary_key=True, nullable= False, unique= True)


class UserRoles(BaseModel):
    user_id = Column(Integer, ForeignKey(User.id), nullable= False)
    role = Column(Enum(UserRole))

class Admin(ActorBase):
    user_id = Column(Integer, ForeignKey(User.id), primary_key=True,unique=True, nullable=False)

class Teacher(ActorBase):
    user_id = Column(Integer, ForeignKey(User.id), primary_key=True, unique=True, nullable=False)
    vanBang = Column(Text)

    classes = relationship("Class", backref="teacher_detail", lazy=True)
    subjects = relationship("Teachers_Subjects", backref="teacher_detail", lazy=True)
    teaching_plan = relationship("TeachingPlan", backref="teacher_detail", lazy=True)
class Semester(db.Model):
    id = Column(String(3), primary_key=True, nullable=False)
    semester = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)

    students = relationship("Student", backref="semester", lazy=True)
    scores = relationship("Score", backref="semester", lazy=True)
class Class(BaseModel):
    __table_args__ = (UniqueConstraint('name', 'year'),)
    name = Column(String(5), nullable=False)
    amount = Column(Integer, default=0)
    grade = Column(Enum(Grade), nullable=False)
    year = Column(Integer, nullable=False)
    teacher_id = Column(Integer, ForeignKey(Teacher.user_id))

    students = relationship("Students_Classes", backref="class_detail", lazy=True)
    teaching_plan = relationship("TeachingPlan", backref="class_detail", lazy=True)
class Student(ActorBase):
    user_id = Column(Integer, ForeignKey(User.id), primary_key=True, unique=True, nullable=False)
    grade = Column(Enum(Grade), nullable=False, default=Grade.K10)
    semester_id = Column(String(3), ForeignKey(Semester.id), nullable=False)


    classes = relationship("Students_Classes", backref="student_detail", lazy=True)
    scores = relationship("Score", backref="student_detail", lazy=True)
class Students_Classes(db.Model):
    id = Column(Integer, primary_key=True, nullable=False)
    class_id = Column(Integer, ForeignKey(Class.id), nullable=False)
    student_id = Column(Integer, ForeignKey(Student.user_id), nullable=False)

class Subject(BaseModel):
    name = Column(String(20), nullable=False, unique = True)
    grade = Column(Enum(Grade), nullable=False)
    mins15 = Column(Integer, default=1)
    mins45 = Column(Integer, default=1)
    final = Column(Integer, default=1)
    teachers = relationship("Teachers_Subjects", backref="subject_detail", lazy=True)
    teaching_plan = relationship("TeachingPlan", backref="subject_detail", lazy=True)

class Teachers_Subjects(db.Model):
    __table_args__ = (UniqueConstraint('teacher_id', 'subject_id'),)
    id = Column(Integer, primary_key=True)
    teacher_id = Column(Integer, ForeignKey(Teacher.user_id), nullable=False)
    subject_id = Column(Integer,ForeignKey(Subject.id), nullable=False)


class TeachingPlan(BaseModel):
    teacher_id = Column(Integer,ForeignKey(Teacher.user_id), nullable=False)
    subject_id = Column(Integer, ForeignKey(Subject.id), nullable=False)
    class_id = Column(Integer, ForeignKey(Class.id), nullable=False)

    student_scores = relationship("Score", backref="plan_detail", lazy=True)
class Score(BaseModel):
    plan_id = Column(Integer, ForeignKey(TeachingPlan.id), nullable=False)
    student_id = Column(Integer, ForeignKey(Student.user_id), nullable=False)
    semester_id = Column(String(3), ForeignKey(Semester.id), nullable=False)


    details = relationship("ScoreDetails", backref="info", lazy=True)
class ScoreDetails(BaseModel):
    score_id = Column(Integer, ForeignKey(Score.id), nullable=False)
    score_type = Column(Enum(ScoreType), nullable=False)
    score = Column(Float)

class Principle(BaseModel):
    type = Column(String(20), nullable=False, unique=True)
    data = Column(Float)
    description = Column(Text)

class ChangedNotification(BaseModel):
    user_id = Column(Integer, ForeignKey(User.id))
    user_role = Column(Enum(UserRole), nullable=False)
    content = Column(Text)
if __name__ == "__main__":
    from Project import  app
    with app.app_context():
        # db.create_all()
        # u1 = User(family_name="Nguyễn Thị Ngọc", first_name = "Mai", gender=False, address="Nha Trang", birthdate="11-11-1990",
        #           username = "ntnmai", password = hashlib.md5("123456".encode("utf-8")).hexdigest())
        # db.session.add(u1)
        # db.session.commit()
        # gv1 = UserRoles(user_id = u1.id, role = UserRole.GIAOVIEN)
        # db.session.add(gv1)
        # db.session.commit()
        # pcp3 = Principle(type="CLASS_AMOUNT",data=45, description="Lớp học có tối đa 45 học sinh")
        # db.session.add(pcp3)
        # db.session.commit()
        import hashlib
        u1 = User(family_name = "Mai Hoàng", first_name = "Phát", gender = True, address = "Nha Trang", birthdate = "08-11-2003",
                  username = "mhphat", password = hashlib.md5("123456".encode("utf-8")).hexdigest())
        u2 = User(family_name = "Nguyễn Văn", first_name = "A", gender=True, address="TP. Hồ Chí Minh",
                  birthdate='10-11-2003',
                  username="nva", password=hashlib.md5('123456'.encode("utf-8")).hexdigest())
        u3 = User(family_name = "Trần Văn", first_name = "B", gender=True, address="TP. Hồ Chí Minh",
                  birthdate='25-08-2003',
                  username="tvb", password=hashlib.md5("123456".encode("utf-8")).hexdigest())
        u4 = User(family_name = "Dương Thùy Bảo", first_name = "Trâm", gender=False, address="Nha Trang, Khánh Hòa",
                  birthdate='06-10-2003',
                  username="dtbtram", password=hashlib.md5("123456".encode("utf-8")).hexdigest())

        hs1 = UserRoles(user_id = 4, role = UserRole.HOCSINH)
        nv1 = UserRoles(user_id = 1, role = UserRole.NHANVIEN)
        nv2 = UserRoles(user_id= 2, role = UserRole.NHANVIEN)
        ad1 = UserRoles(user_id = 2, role = UserRole.ADMIN)
        gv1 = UserRoles(user_id = 3, role = UserRole.GIAOVIEN)

        # db.session.add_all([u1, u2, u3, u4])
        # db.session.commit()
        # db.session.add_all([nv1, nv2, ad1, gv1])
        # db.session.commit()
        #
        no1 = ChangedNotification(user_id = 1, user_role = UserRole.NHANVIEN, content = "thay đổi giao diện front end" )
        no2 = ChangedNotification(user_id=1, user_role=UserRole.NHANVIEN, content="thay đổi models")
        no3 = ChangedNotification(user_id=1, user_role=UserRole.NHANVIEN, content="thay đổi templates")
        # # no4 = ChangedNotification(user_id=3, user_role=UserRole.GIAOVIEN, content="nhập điểm")
        # # for i in range(10):
        # #     db.session.add_all([no4])
        # #     db.session.commit()
        # db.session.add_all([no1, no2, no3])
        # db.session.commit()
        import cloudinary.uploader
        # path = cloudinary.uploader.upload('Project/static/anonymous.png')
        # path = cloudinary.uploader.upload('https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcROw75hblsK4_TpFmVKfNFNiAAonmyJ-xP1FzIIrl3XUg&s')
        # print(path['secure_url'])
        contact_u1_01 = UserContact(user_id = 1, contactType = LoaiTTLL.EMAIL, contactData = "mhphat.c17nvt@gmail.com")
        contact_u1_02 = UserContact(user_id = 1, contactType = LoaiTTLL.DTCANHAN, contactData="0365051699")
        k21 = Semester(id = '211', semester = 1, year = '2021')
        student1 = Student(user_id = 4, grade = Grade.K10, semester_id = k21.id)
        pcp1 = Principle(type="AGE_START", data = 15, description = "Tuổi học sinh được tiếp nhận từ 15 tuổi đến 20 tuổi")
        pcp2 = Principle(type="AGE_END", data=20, description="Tuổi học sinh được tiếp nhận từ 15 tuổi đến 20 tuổi")
        db.session.add_all([pcp1, pcp2])
        db.session.commit()