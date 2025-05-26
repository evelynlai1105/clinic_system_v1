from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date, timedelta, time
import os
from dotenv import load_dotenv
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

# 載入環境變數
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here') # 從環境變數讀取 SECRET_KEY

# MySQL 配置
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:1234@127.0.0.1:3306/clinic_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_size': 10,
    'pool_recycle': 3600,
    'pool_pre_ping': True
}

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login' # 設定登入頁面路由
login_manager.login_message_category = 'info'
login_manager.login_message = '請登入以訪問此頁面。'

# 使用者載入器
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# 角色模型
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False, comment='角色名稱') # 例如: super_admin, doctor, assistant
    description = db.Column(db.String(255), comment='角色描述')
    users = db.relationship('User', backref='role', lazy=True)

# 使用者模型
class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, comment='使用者名稱')
    password_hash = db.Column(db.String(128), nullable=False, comment='密碼雜湊')
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False, comment='角色ID')
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(), comment='建立時間')
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(), onupdate=lambda: datetime.now(), comment='更新時間')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# 資料模型定義
class Patient(db.Model):
    __tablename__ = 'patients'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False, comment='病患姓名')
    gender = db.Column(db.String(10), nullable=False, comment='性別')
    birthday = db.Column(db.Date, nullable=False, comment='生日')
    phone = db.Column(db.String(20), nullable=False, comment='聯絡電話')
    address = db.Column(db.Text, nullable=False, comment='聯絡地址')
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(), comment='建立時間')
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(), onupdate=lambda: datetime.now(), comment='更新時間')
    appointments = db.relationship('Appointment', backref='patient', lazy=True)

class Doctor(db.Model):
    __tablename__ = 'doctors'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False, comment='醫師姓名')
    department = db.Column(db.String(50), nullable=False, comment='科別')
    specialty = db.Column(db.String(100), nullable=False, comment='專長')
    schedule = db.Column(db.Text, nullable=False, comment='排班時段')
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(), comment='建立時間')
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(), onupdate=lambda: datetime.now(), comment='更新時間')
    appointments = db.relationship('Appointment', backref='doctor', lazy=True)

class Appointment(db.Model):
    __tablename__ = 'appointments'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False, comment='病患ID')
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False, comment='醫師ID')
    datetime = db.Column(db.DateTime, nullable=False, comment='掛號時間')
    complaint = db.Column(db.Text, nullable=False, comment='主訴')
    status = db.Column(db.String(20), default='pending', comment='狀態：pending/completed/cancelled')
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(), comment='建立時間')
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(), onupdate=lambda: datetime.now(), comment='更新時間')
    diagnosis = db.relationship('Diagnosis', backref='appointment', uselist=False)

class Diagnosis(db.Model):
    __tablename__ = 'diagnoses'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointments.id'), nullable=False, comment='掛號ID')
    diagnosis_text = db.Column(db.Text, nullable=False, comment='診斷內容')
    doctor_advice = db.Column(db.Text, nullable=False, comment='醫師建議')
    diagnosis_time = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(), comment='診斷時間')
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(), comment='建立時間')
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(), onupdate=lambda: datetime.now(), comment='更新時間')
    prescriptions = db.relationship('Prescription', backref='diagnosis', lazy=True)

class Medicine(db.Model):
    __tablename__ = 'medicines'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False, comment='藥品名稱')
    unit = db.Column(db.String(20), nullable=False, comment='單位')
    stock = db.Column(db.Integer, nullable=False, default=0, comment='庫存量')
    supplier = db.Column(db.String(100), nullable=False, comment='供應商')
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(), comment='建立時間')
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(), onupdate=lambda: datetime.now(), comment='更新時間')
    prescriptions = db.relationship('Prescription', backref='medicine', lazy=True)

class Prescription(db.Model):
    __tablename__ = 'prescriptions'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    diagnosis_id = db.Column(db.Integer, db.ForeignKey('diagnoses.id'), nullable=False, comment='診斷ID')
    medicine_id = db.Column(db.Integer, db.ForeignKey('medicines.id'), nullable=False, comment='藥品ID')
    dosage = db.Column(db.String(50), nullable=False, comment='劑量')
    days = db.Column(db.Integer, nullable=False, comment='服用天數')
    frequency = db.Column(db.String(50), nullable=False, comment='服用頻率')
    prescribed_time = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(), comment='開立時間')
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(), comment='建立時間')
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(), onupdate=lambda: datetime.now(), comment='更新時間')

# 路由定義
@app.route('/')
@login_required # 確保只有登入使用者才能訪問主頁
def index():
    return render_template('index.html', current_user=current_user)

# 新增登入路由
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            flash('登入成功！', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        else:
            flash('無效的使用者名稱或密碼。', 'danger')
    return render_template('login.html') # 需要創建 login.html 模板

# 新增登出路由
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# 病患相關路由
@app.route('/patients')
@login_required # 需要登入才能訪問
def patients():
    patients = Patient.query.all()
    return render_template('patients.html', patients=patients)

# 查看病患詳細資訊
@app.route('/patients/<int:id>')
@login_required
def patient_details(id):
    patient = Patient.query.get_or_404(id)
    return render_template('patient_details.html', patient=patient)

# 新增病患路由 (已重新添加)
@app.route('/add_patient', methods=['POST'])
@login_required # 需要登入才能訪問
def add_patient():
    # 這裡可能需要進一步檢查使用者角色，例如只有管理者或醫師助理可以新增病患
    try:
        new_patient = Patient(
            name=request.form['name'],
            gender=request.form['gender'],
            birthday=datetime.strptime(request.form['birthday'], '%Y-%m-%d').date(),
            phone=request.form['phone'],
            address=request.form['address']
        )
        db.session.add(new_patient)
        db.session.commit()
        flash('病患資料新增成功！', 'success')
    except Exception as e:
        db.session.rollback() # 新增失敗時回滾事務
        flash(f'新增失敗：{str(e)}', 'danger')
    return redirect(url_for('patients'))

@app.route('/edit_patient/<int:id>', methods=['GET', 'POST'])
@login_required # 需要登入才能訪問
def edit_patient(id):
    patient = Patient.query.get_or_404(id)
    # 這裡可能需要進一步檢查使用者角色
    if request.method == 'POST':
        try:
            patient.name = request.form['name']
            # 注意：gender 從表單獲取時是字串，直接賦值即可
            patient.gender = request.form['gender']
            patient.birthday = datetime.strptime(request.form['birthday'], '%Y-%m-%d').date()
            patient.phone = request.form['phone']
            patient.address = request.form['address']
            db.session.commit()
            flash('病患資料更新成功！', 'success')
            return redirect(url_for('patients')) # 更新成功後重定向回病患列表頁面
        except Exception as e:
            db.session.rollback()
            flash(f'更新失敗：{str(e)}', 'danger')
            # 更新失敗後重新渲染編輯頁面，保留使用者輸入的資料
            return render_template('edit_patient.html', patient=patient)
    
    # GET 請求時顯示編輯表單
    return render_template('edit_patient.html', patient=patient)

@app.route('/delete_patient/<int:id>', methods=['POST'])
@login_required # 需要登入才能訪問
def delete_patient(id):
    # 這裡可能需要進一步檢查使用者角色，例如只有管理者可以刪除病患
    patient = Patient.query.get_or_404(id)
    try:
        db.session.delete(patient)
        db.session.commit()
        flash('病患資料刪除成功！', 'success')
    except Exception as e:
        db.session.rollback() # 刪除失敗時回滾事務
        flash(f'刪除失敗：{str(e)}', 'danger')
    return redirect(url_for('patients'))

# 醫師相關路由
@app.route('/doctors')
@login_required # 需要登入才能訪問
def doctors():
    doctors = Doctor.query.all()
    return render_template('doctors.html', doctors=doctors)

# 查看醫師詳細資訊
@app.route('/doctors/<int:id>')
@login_required
def doctor_details(id):
    doctor = Doctor.query.get_or_404(id)
    return render_template('doctor_details.html', doctor=doctor)

# 編輯醫師資訊
@app.route('/edit_doctor/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_doctor(id):
    # 這裡可能需要進一步檢查使用者角色
    doctor = Doctor.query.get_or_404(id)
    if request.method == 'POST':
        try:
            doctor.name = request.form['name']
            doctor.department = request.form['department']
            doctor.specialty = request.form['specialty']
            doctor.schedule = request.form['schedule']
            db.session.commit()
            flash('醫師資料更新成功！', 'success')
            return redirect(url_for('doctors'))
        except Exception as e:
            db.session.rollback()
            flash(f'更新失敗：{str(e)}', 'danger')
            return render_template('edit_doctor.html', doctor=doctor)

    return render_template('edit_doctor.html', doctor=doctor)

# 刪除醫師
@app.route('/delete_doctor/<int:id>', methods=['POST'])
@login_required
def delete_doctor(id):
    # 這裡可能需要進一步檢查使用者角色
    doctor = Doctor.query.get_or_404(id)
    try:
        db.session.delete(doctor)
        db.session.commit()
        flash('醫師資料刪除成功！', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'刪除失敗：{str(e)}', 'danger')
    return redirect(url_for('doctors'))

@app.route('/add_doctor', methods=['POST'])
@login_required # 需要登入才能訪問
def add_doctor():
     # 這裡可能需要進一步檢查使用者角色，例如只有管理者或醫師可以新增醫師
    try:
        new_doctor = Doctor(
            name=request.form['name'],
            department=request.form['department'],
            specialty=request.form['specialty'],
            schedule=request.form['schedule']
        )
        db.session.add(new_doctor)
        db.session.commit()
        flash('醫師資料新增成功！', 'success')
    except Exception as e:
        flash(f'新增失敗：{str(e)}', 'danger')
    return redirect(url_for('doctors'))

# 掛號相關路由
@app.route('/appointments')
@login_required # 需要登入才能訪問
def appointments():
    appointments = Appointment.query.all()
    return render_template('appointments.html', appointments=appointments)

# 查看掛號詳細資訊
@app.route('/appointments/<int:id>')
@login_required
def appointment_details(id):
    appointment = Appointment.query.get_or_404(id)
    return render_template('appointment_details.html', appointment=appointment)

# 編輯掛號資訊
@app.route('/edit_appointment/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_appointment(id):
    # 這裡可能需要進一步檢查使用者角色
    appointment = Appointment.query.get_or_404(id)
    patients = Patient.query.order_by(Patient.name).all() # 獲取所有病患列表供下拉選單使用
    doctors = Doctor.query.order_by(Doctor.name).all() # 獲取所有醫師列表供下拉選單使用

    if request.method == 'POST':
        try:
            appointment.patient_id = request.form['patient_id']
            appointment.doctor_id = request.form['doctor_id']
            appointment.datetime = datetime.strptime(request.form['datetime'], '%Y-%m-%dT%H:%M')
            appointment.complaint = request.form['complaint']
            appointment.status = request.form['status'] # 如果需要在編輯時修改狀態，則需要這個欄位

            db.session.commit()
            flash('掛號資訊更新成功！', 'success')
            return redirect(url_for('appointments'))
        except Exception as e:
            db.session.rollback()
            flash(f'更新失敗：{str(e)}', 'danger')
            # 更新失敗後重新渲染編輯頁面，保留使用者輸入的資料
            return render_template('edit_appointment.html', appointment=appointment, patients=patients, doctors=doctors)

    return render_template('edit_appointment.html', appointment=appointment, patients=patients, doctors=doctors)

# 刪除掛號
@app.route('/delete_appointment/<int:id>', methods=['POST'])
@login_required
def delete_appointment(id):
    # 這裡可能需要進一步檢查使用者角色
    appointment = Appointment.query.get_or_404(id)
    try:
        db.session.delete(appointment)
        db.session.commit()
        flash('掛號記錄刪除成功！', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'刪除失敗：{str(e)}', 'danger')
    return redirect(url_for('appointments'))

@app.route('/add_appointment', methods=['POST'])
@login_required # 需要登入才能訪問
def add_appointment():
    # 這裡可能需要進一步檢查使用者角色，例如只有醫師助理可以新增掛號
    try:
        new_appointment = Appointment(
            patient_id=request.form['patient_id'],
            doctor_id=request.form['doctor_id'],
            datetime=datetime.strptime(request.form['datetime'], '%Y-%m-%dT%H:%M'),
            complaint=request.form['complaint']
        )
        db.session.add(new_appointment)
        db.session.commit()
        flash('掛號成功！', 'success')
    except Exception as e:
        flash(f'掛號失敗：{str(e)}', 'danger')
    return redirect(url_for('appointments'))

# 藥品相關路由
@app.route('/medicines')
@login_required # 需要登入才能訪問
def medicines():
    medicines = Medicine.query.all()
    return render_template('medicines.html', medicines=medicines)

# 查看藥品詳細資訊
@app.route('/medicines/<int:id>')
@login_required
def medicine_details(id):
    medicine = Medicine.query.get_or_404(id)
    return render_template('medicine_details.html', medicine=medicine)

# 編輯藥品資訊
@app.route('/edit_medicine/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_medicine(id):
    # 這裡可能需要進一步檢查使用者角色
    medicine = Medicine.query.get_or_404(id)
    if request.method == 'POST':
        try:
            medicine.name = request.form['name']
            medicine.unit = request.form['unit']
            medicine.stock = int(request.form['stock']) # 確保庫存量是整數
            medicine.supplier = request.form['supplier']
            db.session.commit()
            flash('藥品資料更新成功！', 'success')
            return redirect(url_for('medicines'))
        except ValueError:
            flash('庫存量必須為整數。', 'danger')
            db.session.rollback() # 回滾無效輸入
            return render_template('edit_medicine.html', medicine=medicine)
        except Exception as e:
            db.session.rollback()
            flash(f'更新失敗：{str(e)}', 'danger')
            return render_template('edit_medicine.html', medicine=medicine)

    return render_template('edit_medicine.html', medicine=medicine)

# 刪除藥品
@app.route('/delete_medicine/<int:id>', methods=['POST'])
@login_required
def delete_medicine(id):
    # 這裡可能需要進一步檢查使用者角色
    medicine = Medicine.query.get_or_404(id)
    try:
        db.session.delete(medicine)
        db.session.commit()
        flash('藥品資料刪除成功！', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'刪除失敗：{str(e)}', 'danger')
    return redirect(url_for('medicines'))

@app.route('/add_medicine', methods=['POST'])
@login_required # 需要登入才能訪問
def add_medicine():
     # 這裡可能需要進一步檢查使用者角色，例如只有管理者可以新增藥品
    try:
        new_medicine = Medicine(
            name=request.form['name'],
            unit=request.form['unit'],
            stock=int(request.form['stock']),
            supplier=request.form['supplier']
        )
        db.session.add(new_medicine)
        db.session.commit()
        flash('藥品資料新增成功！', 'success')
    except Exception as e:
        flash(f'新增失敗：{str(e)}', 'danger')
    return redirect(url_for('medicines'))

# 使用者管理相關路由 (只有超級管理員可見和操作)
@app.route('/users')
@login_required
def users():
    # 這裡需要檢查使用者角色是否為超級管理員
    if current_user.role.name != 'super_admin':
        flash('您沒有權限訪問此頁面。', 'warning')
        return redirect(url_for('index'))
    users = User.query.all()
    roles = Role.query.all() # 獲取角色列表供新增或修改使用者時選擇
    return render_template('users.html', users=users, roles=roles) # 需要創建 users.html 模板

@app.route('/add_user', methods=['POST'])
@login_required
def add_user():
     # 這裡需要檢查使用者角色是否為超級管理員
    if current_user.role.name != 'super_admin':
        flash('您沒有權限執行此操作。', 'warning')
        return redirect(url_for('index'))
    try:
        username = request.form['username']
        password = request.form['password']
        role_id = request.form['role_id']
        # 檢查使用者名稱是否已存在
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('使用者名稱已存在。', 'danger')
            return redirect(url_for('users'))

        new_user = User(
            username=username,
            role_id=role_id
        )
        new_user.set_password(password) # 加密密碼

        db.session.add(new_user)
        db.session.commit()
        flash('使用者新增成功！', 'success')
    except Exception as e:
        flash(f'新增失敗：{str(e)}', 'danger')
    return redirect(url_for('users'))

# 編輯使用者路由 (假設只有超級管理員可以編輯，且不能修改自己的角色)
@app.route('/edit_user/<int:id>', methods=['POST'])
@login_required
def edit_user(id):
    if current_user.role.name != 'super_admin' or current_user.id == id: # 不允許編輯自己的角色
        flash('您沒有權限執行此操作或無法修改自己的角色。', 'warning')
        return redirect(url_for('users'))

    user = User.query.get_or_404(id)
    try:
        user.username = request.form['username']
        # 如果提供了新密碼才更新
        new_password = request.form.get('password')
        if new_password:
             user.set_password(new_password)
        user.role_id = request.form['role_id']
        db.session.commit()
        flash('使用者資料更新成功！', 'success')
    except Exception as e:
        flash(f'更新失敗：{str(e)}', 'danger')
    return redirect(url_for('users'))

# 刪除使用者路由 (假設只有超級管理員可以刪除，且不能刪除自己)
@app.route('/delete_user/<int:id>')
@login_required
def delete_user(id):
    if current_user.role.name != 'super_admin' or current_user.id == id: # 不允許刪除自己
        flash('您沒有權限執行此操作或無法刪除自己。', 'warning')
        return redirect(url_for('users'))

    user = User.query.get_or_404(id)
    try:
        db.session.delete(user)
        db.session.commit()
        flash('使用者刪除成功！', 'success')
    except Exception as e:
        flash(f'刪除失敗：{str(e)}', 'danger')
    return redirect(url_for('users'))

# 查詢功能相關路由
@app.route('/queries')
@login_required
def queries_index():
    # 可能需要根據使用者角色顯示不同的查詢選項
    return render_template('queries.html')

# 查詢 1：查詢特定日期的掛號紀錄
@app.route('/queries/appointments_by_date', methods=['GET', 'POST'])
@login_required
def query1_appointments_by_date():
    form_submitted = False
    appointments = []
    selected_date = None

    if request.method == 'POST':
        form_submitted = True
        date_str = request.form.get('query_date')
        if date_str:
            try:
                selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                # 這裡進行 SQLAlchemy 查詢
                # 注意：Appointment.datetime 是 datetime 物件，需要處理日期的比較
                # 我們可以使用 date() 方法來比較日期部分
                appointments = Appointment.query.filter(db.func.date(Appointment.datetime) == selected_date).all()
            except ValueError:
                flash('無效的日期格式。', 'danger')
        else:
            flash('請輸入日期。', 'warning')

    return render_template('query1_appointments_by_date.html', appointments=appointments, form_submitted=form_submitted, selected_date=selected_date)

# 查詢 2：某位病患的歷史看診紀錄與診斷
@app.route('/queries/patient_history', methods=['GET', 'POST'])
@login_required
def query2_patient_history():
    patients = Patient.query.order_by(Patient.name).all() # 獲取所有病患列表供下拉選單使用
    selected_patient = None
    appointments = []
    form_submitted = False

    if request.method == 'POST':
        form_submitted = True
        patient_id = request.form.get('patient_id')
        if patient_id:
            selected_patient = Patient.query.get(patient_id)
            if selected_patient:
                # 查詢該病患的掛號紀錄，並預載入相關的診斷資訊
                appointments = Appointment.query.filter_by(patient_id=patient_id).order_by(Appointment.datetime.desc()).all()
            else:
                flash('找不到指定的病患。', 'danger')
        else:
            flash('請選擇病患。', 'warning')

    return render_template('query2_patient_history.html', patients=patients, selected_patient=selected_patient, appointments=appointments, form_submitted=form_submitted)

# 查詢 3：某診斷的處方用藥明細
@app.route('/queries/prescription_by_diagnosis', methods=['GET', 'POST'])
@login_required
def query3_prescription_by_diagnosis():
    diagnoses = Diagnosis.query.order_by(Diagnosis.diagnosis_time.desc()).all() # 獲取所有診斷列表供下拉選單使用
    selected_diagnosis = None
    prescriptions = []
    form_submitted = False

    if request.method == 'POST':
        form_submitted = True
        diagnosis_id = request.form.get('diagnosis_id')
        if diagnosis_id:
            selected_diagnosis = Diagnosis.query.get(diagnosis_id)
            if selected_diagnosis:
                # 查詢該診斷的處方用藥
                prescriptions = Prescription.query.filter_by(diagnosis_id=diagnosis_id).all()
            else:
                flash('找不到指定的診斷。', 'danger')
        else:
            flash('請選擇診斷。', 'warning')

    return render_template('query3_prescription_by_diagnosis.html', diagnoses=diagnoses, selected_diagnosis=selected_diagnosis, prescriptions=prescriptions, form_submitted=form_submitted)

# 查詢 4：查詢藥品庫存不足（低於門檻）
@app.route('/queries/low_stock_medicines', methods=['GET', 'POST'])
@login_required
def query4_low_stock_medicines():
    low_stock_medicines = []
    threshold = None
    form_submitted = False

    if request.method == 'POST':
        form_submitted = True
        threshold_str = request.form.get('threshold')
        if threshold_str:
            try:
                threshold = int(threshold_str)
                # 查詢庫存量低於門檻的藥品
                low_stock_medicines = Medicine.query.filter(Medicine.stock < threshold).all()
            except ValueError:
                flash('無效的門檻值。請輸入一個整數。', 'danger')
        else:
            flash('請輸入庫存門檻值。', 'warning')

    return render_template('query4_low_stock_medicines.html', low_stock_medicines=low_stock_medicines, threshold=threshold, form_submitted=form_submitted)

# 查詢 5：某醫師本週排班與掛號病患
@app.route('/queries/doctor_schedule_appointments', methods=['GET', 'POST'])
@login_required
def query5_doctor_schedule_appointments():
    doctors = Doctor.query.order_by(Doctor.name).all() # 獲取所有醫師列表供下拉選單使用
    selected_doctor = None
    weekly_appointments = []
    form_submitted = False

    if request.method == 'POST':
        form_submitted = True
        doctor_id = request.form.get('doctor_id')
        if doctor_id:
            selected_doctor = Doctor.query.get(doctor_id)
            if selected_doctor:
                # 計算本週的開始和結束日期
                today = date.today()
                start_of_week = today - timedelta(days=today.weekday())
                end_of_week = start_of_week + timedelta(days=6)

                # 查詢該醫師本週的掛號紀錄
                weekly_appointments = Appointment.query.filter_by(doctor_id=doctor_id).filter(Appointment.datetime.between(start_of_week, datetime.combine(end_of_week, time.max))).order_by(Appointment.datetime).all()

            else:
                flash('找不到指定的醫師。', 'danger')
        else:
            flash('請選擇醫師。', 'warning')

    return render_template('query5_doctor_schedule_appointments.html', doctors=doctors, selected_doctor=selected_doctor, weekly_appointments=weekly_appointments, form_submitted=form_submitted)

# 查詢 6：查詢開立最多的藥品排名
@app.route('/queries/top_prescribed_medicines')
@login_required
def query6_top_prescribed_medicines():
    # 查詢開立次數最多的藥品排名
    # 這裡我們計算 Prescription 表中 medicine_id 出現的次數，並按次數降序排列
    top_medicines = db.session.query(Medicine.name, db.func.count(Prescription.medicine_id).label('prescription_count'))\
                        .join(Prescription, Medicine.id == Prescription.medicine_id)\
                        .group_by(Medicine.name)\
                        .order_by(db.desc('prescription_count'))\
                        .all()

    return render_template('query6_top_prescribed_medicines.html', top_medicines=top_medicines)

# 報表功能路由

# 報表 1：當日醫師看診報表
@app.route('/reports/doctor_daily_appointments', methods=['GET', 'POST'])
@login_required
def report_doctor_daily_appointments():
    doctors = Doctor.query.order_by(Doctor.name).all() # 獲取所有醫師列表供下拉選單使用
    appointments = []
    selected_doctor = None
    selected_date = None
    form_submitted = False

    if request.method == 'POST':
        form_submitted = True
        doctor_id = request.form.get('doctor_id')
        date_str = request.form.get('report_date')

        if doctor_id and date_str:
            try:
                selected_doctor = Doctor.query.get(doctor_id)
                selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()

                if selected_doctor:
                    # 查詢特定醫生在特定日期的掛號記錄
                    appointments = Appointment.query.filter_by(doctor_id=doctor_id).filter(db.func.date(Appointment.datetime) == selected_date).order_by(Appointment.datetime).all()
                else:
                    flash('找不到指定的醫師。', 'danger')
            except ValueError:
                flash('無效的日期格式。', 'danger')
        else:
            flash('請選擇醫師和日期。', 'warning')

    return render_template('report_doctor_daily_appointments.html', doctors=doctors, appointments=appointments, selected_doctor=selected_doctor, selected_date=selected_date, form_submitted=form_submitted)

# 報表 2：藥品補貨單
@app.route('/reports/medicine_reorder_list', methods=['GET'])
@login_required
def report_medicine_reorder_list():
    # 設定低庫存閾值
    LOW_STOCK_THRESHOLD = 10 # 可以根據需要調整

    # 查詢庫存低於閾值的藥品
    low_stock_medicines = Medicine.query.filter(Medicine.stock < LOW_STOCK_THRESHOLD).order_by(Medicine.stock).all()

    return render_template('report_medicine_reorder_list.html', low_stock_medicines=low_stock_medicines, threshold=LOW_STOCK_THRESHOLD)

if __name__ == '__main__':
    with app.app_context():
        db.create_all() # 會根據模型建立新的表格 (users, roles)
        # 在這裡可以考慮添加初始化角色和管理員帳戶的邏輯
    print("資料庫初始化完成 (包含使用者和角色表格)")
    print("正在啟動伺服器...")
    # 將 port 改回 5000，因為 Flask 預設是 5000
    app.run(debug=True, host='127.0.0.1', port=5000) 