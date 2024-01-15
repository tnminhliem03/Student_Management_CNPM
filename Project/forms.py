from wtforms.fields import StringField, SubmitField, PasswordField, SelectField, DateField, FileField, EmailField, IntegerField
from flask_wtf import FlaskForm
from wtforms.validators import InputRequired, Length, NumberRange
class LoginForm(FlaskForm):
    userType = SelectField("Đăng nhập theo: ", choices=[("NHANVIEN", "Nhân viên"), ("ADMIN", "Người quản trị"), ("GIAOVIEN", "Giáo viên")])
    username = StringField(validators=[InputRequired(), Length(min=1, max=15)], render_kw={"placeholder": "Tên đăng nhập"})
    password = PasswordField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Mật khẩu"})
    submit = SubmitField("Đăng nhập")

class AddUserForm(FlaskForm):
    name = StringField("Họ và tên: ", validators=[InputRequired()])
    gender = SelectField("Giới tính: ", validators=[InputRequired()], choices=[(1, "Nam"), (0, "Nữ")])
    address = StringField("Địa chỉ: ", validators=[InputRequired()])
    birthdate = DateField("Ngày sinh: ", validators=[InputRequired()], format="%d-%m-%y")
    image = FileField("Hình ảnh đại diện: ")
    email = EmailField("Email: ")
    phone = StringField("Số điện thoại: ", validators = [Length(max=11)])
    grade = SelectField("Khối lớp: ", choices=[("K10","Khối 10"),("K11","Khối 11"), ("K12","Khối 12") ])
    submit = SubmitField("Thêm")

class AddClassesForm(FlaskForm):
    grade = SelectField("Khối lớp: ", choices=[("K10","Khối 10"),("K11","Khối 11"), ("K12","Khối 12") ])
    submit = SubmitField("Tạo Lớp")

