from Project import app, dao
from Project.models import *
from flask_admin.contrib.sqla import ModelView
from flask_admin import Admin, BaseView, expose, AdminIndexView
from flask_login import logout_user, current_user
from flask import redirect, request, session


class MyAdminIndex(AdminIndexView):
    @expose('/')
    def index(self):
        return self.render('admin/index.html', user_count = dao.user_count())


admin = Admin(app=app, name='QUẢN TRỊ VIÊN', template_mode='bootstrap4', index_view=MyAdminIndex())


class AuthenticatedUser(BaseView):
    def is_accessible(self):
        return current_user.is_authenticated


class AuthenticatedAdmin(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and session.get("role") == 'ADMIN'


Principle.id.in_([1,2,3])
class EditPrincipleView(AuthenticatedAdmin):
    column_list = ['description', 'data']
    column_searchable_list = ['description']
    can_create = False
    can_delete = False

    column_labels = {
        'data': 'Giá trị',
        'description': 'Quy định'
    }
    # Lấy view từ thằng cha xong ghi đè để lấy mỗi thằng tuổi với số lượng học sinh
    def get_query(self):
        query = super().get_query()
        return query.filter(Principle.id.in_([1, 2, 3]))
class ManageSubjectView(AuthenticatedAdmin):
    column_list = ['name', 'grade', 'mins15', 'mins45', 'final']
    column_searchable_list = ['name']
    column_labels = {
        'name': 'Tên môn học',
        'grade': 'Khối',
        'mins15': 'Số cột điểm 15p',
        'mins45': 'Số cột điểm 45p',
        'final': 'Số cột cuối kỳ'
    }


class MyStatsView(AuthenticatedUser):
    @expose("/")
    def index(self):

        subject_id = request.args.get('subject') if request.args.get('subject') != "" else None
        semester_id = request.args.get('semester') if request.args.get('semester') != "" else None
        grade = request.args.get('grade') if request.args.get('grade') else None
        subject_list = dao.load_subject_all(grade = grade)
        semester_list = dao.get_semester()

        subject = Subject.query.get(subject_id) if subject_id else None
        semester = Semester.query.get(semester_id) if semester_id else None
        if semester:
            semester = f'Học kì {semester.semester} năm {semester.year}'


        return self.render('admin/stats.html', subject = subject, semester = semester, subject_list = subject_list, semester_list = semester_list, Grade = Grade, subject_report= dao.subject_report(subject_id = subject_id,
                                                                                  semester_id = semester_id))


class MyLogoutView(AuthenticatedUser):
    @expose("/")
    def index(self):
        logout_user()
        return redirect('/')


admin.add_view(EditPrincipleView(Principle, db.session, name="Chỉnh sửa quy định"))
admin.add_view(ManageSubjectView(Subject, db.session, name="Quản lý môn học"))
admin.add_view(MyStatsView(name='Thống kê báo cáo'))
admin.add_view(MyLogoutView(name='Đăng xuất'))
