from app import app, db, Patient, Doctor, Appointment, Diagnosis, Medicine, Prescription, Role, User
from datetime import datetime, date
from werkzeug.security import generate_password_hash

def seed_database():
    with app.app_context():
        print("正在使用提供的資料填充資料庫...")

        # 清空現有資料 (可選，但建議確保數據是您提供的)
        print("清空現有資料...")
        db.drop_all()
        db.create_all()
        print("資料庫表格已重建。")

        # === 0. 建立預設角色 ===
        print("建立預設角色...")
        roles = {
            'super_admin': Role(name='super_admin', description='總管理者'),
            'doctor': Role(name='doctor', description='醫師'),
            'assistant': Role(name='assistant', description='醫師助理')
        }
        for role in roles.values():
            db.session.add(role)
        db.session.commit()
        print("預設角色建立完成。")

        # 獲取建立的角色以便後續使用
        inserted_roles = Role.query.all()
        role_map = {r.name: r for r in inserted_roles}

        # === 0.5 建立預設總管理者使用者 ===
        print("建立預設總管理者使用者...")
        if 'super_admin' in role_map:
            admin_role = role_map['super_admin']
            # 檢查是否已存在 admin 使用者，避免重複建立
            if User.query.filter_by(username='admin').first() is None:
                admin_user = User(
                    username='admin',
                    role_id=admin_role.id
                )
                admin_user.set_password('123') # 設定預設密碼
                db.session.add(admin_user)
                db.session.commit()
                print("預設總管理者使用者 'admin' 建立完成 (密碼為 '123')")
            else:
                print("預設總管理者使用者 'admin' 已存在。")
        else:
            print("錯誤：找不到 'super_admin' 角色，無法建立預設管理員使用者。")

        # === 1. 提供的病患資料 ===
        print("填充病患資料...")
        patients_data = [
            {'name': '病患1', 'gender': '女', 'birthday': '2003-03-21', 'phone': '0938231036', 'address': '台北市範例路1號'},
            {'name': '病患2', 'gender': '女', 'birthday': '2007-01-27', 'phone': '0984602207', 'address': '台北市範例路2號'},
            {'name': '病患3', 'gender': '男', 'birthday': '1987-09-10', 'phone': '0966460766', 'address': '台北市範例路3號'},
            {'name': '病患4', 'gender': '女', 'birthday': '1983-08-20', 'phone': '0980613449', 'address': '台北市範例路4號'},
            {'name': '病患5', 'gender': '女', 'birthday': '2002-09-03', 'phone': '0914107809', 'address': '台北市範例路5號'},
            {'name': '病患6', 'gender': '女', 'birthday': '1980-08-09', 'phone': '0947286829', 'address': '台北市範例路6號'},
            {'name': '病患7', 'gender': '女', 'birthday': '1975-07-19', 'phone': '0922204073', 'address': '台北市範例路7號'},
            {'name': '病患8', 'gender': '女', 'birthday': '1988-10-08', 'phone': '0997894354', 'address': '台北市範例路8號'},
            {'name': '病患9', 'gender': '女', 'birthday': '2006-07-19', 'phone': '0972947467', 'address': '台北市範例路9號'},
            {'name': '病患10', 'gender': '男', 'birthday': '1979-01-25', 'phone': '0940590205', 'address': '台北市範例路10號'},
        ]
        patients = []
        for data in patients_data:
            # 將生日字串轉換為 date 物件
            data['birthday'] = datetime.strptime(data['birthday'], '%Y-%m-%d').date()
            patients.append(Patient(**data))

        db.session.add_all(patients)
        db.session.commit()
        # 獲取已插入的病患物件，以便後續關聯
        inserted_patients = Patient.query.all()
        patient_map = {p.name: p for p in inserted_patients}
        print("病患資料填充完成。")

        # === 2. 提供的醫師資料 ===
        print("填充醫師資料...")
        doctors_data = [
            {'name': '醫師1', 'department': '小兒科', 'specialty': '糖尿病', 'schedule': '一上午,三下午'},
            {'name': '醫師2', 'department': '外科', 'specialty': '胃痛', 'schedule': '一上午,三下午'},
            {'name': '醫師3', 'department': '小兒科', 'specialty': '高血壓', 'schedule': '一上午,三下午'},
            {'name': '醫師4', 'department': '內科', 'specialty': '糖尿病', 'schedule': '一上午,三下午'},
            {'name': '醫師5', 'department': '小兒科', 'specialty': '胃痛', 'schedule': '一上午,三下午'},
        ]
        doctors = [Doctor(**data) for data in doctors_data]
        db.session.add_all(doctors)
        db.session.commit()
         # 獲取已插入的醫師物件，以便後續關聯
        inserted_doctors = Doctor.query.all()
        doctor_map = {d.name: d for d in inserted_doctors}
        print("醫師資料填充完成。")

        # === 3. 提供的藥品資料 ===
        print("填充藥品資料...")
        medicines_data = [
            {'name': '藥品1', 'unit': '包', 'stock': 74, 'supplier': '供應商1'},
            {'name': '藥品2', 'unit': 'ml', 'stock': 82, 'supplier': '供應商2'},
            {'name': '藥品3', 'unit': '包', 'stock': 13, 'supplier': '供應商3'},
            {'name': '藥品4', 'unit': '包', 'stock': 47, 'supplier': '供應商4'},
            {'name': '藥品5', 'unit': 'ml', 'stock': 91, 'supplier': '供應商5'},
            {'name': '藥品6', 'unit': '顆', 'stock': 18, 'supplier': '供應商6'},
            {'name': '藥品7', 'unit': '包', 'stock': 42, 'supplier': '供應商7'},
            {'name': '藥品8', 'unit': 'ml', 'stock': 98, 'supplier': '供應商8'},
            {'name': '藥品9', 'unit': 'ml', 'stock': 29, 'supplier': '供應商9'},
            {'name': '藥品10', 'unit': 'ml', 'stock': 100, 'supplier': '供應商10'},
        ]
        medicines = [Medicine(**data) for data in medicines_data]

        db.session.add_all(medicines)
        db.session.commit()
         # 獲取已插入的藥品物件，以便後續關聯
        inserted_medicines = Medicine.query.all()
        medicine_map = {m.name: m for m in inserted_medicines}
        print("藥品資料填充完成。")

        # === 4. 提供的掛號資料 ===
        print("填充掛號資料...")
        appointments_data = [
            {'patient_name': '病患3', 'doctor_name': '醫師5', 'datetime': '2024-03-22 00:00:00', 'complaint': '發燒', 'status': 'completed'},
            {'patient_name': '病患1', 'doctor_name': '醫師1', 'datetime': '2024-07-30 00:00:00', 'complaint': '頭痛', 'status': 'completed'},
            {'patient_name': '病患4', 'doctor_name': '醫師2', 'datetime': '2024-10-29 00:00:00', 'complaint': '腹瀉', 'status': 'completed'},
            {'patient_name': '病患5', 'doctor_name': '醫師1', 'datetime': '2024-11-04 00:00:00', 'complaint': '咳嗽', 'status': 'completed'},
            {'patient_name': '病患3', 'doctor_name': '醫師1', 'datetime': '2024-05-01 00:00:00', 'complaint': '頭痛', 'status': 'cancelled'},
            {'patient_name': '病患5', 'doctor_name': '醫師4', 'datetime': '2024-08-29 00:00:00', 'complaint': '發燒', 'status': 'cancelled'},
            {'patient_name': '病患1', 'doctor_name': '醫師2', 'datetime': '2024-01-02 00:00:00', 'complaint': '腹瀉', 'status': 'cancelled'},
            {'patient_name': '病患3', 'doctor_name': '醫師4', 'datetime': '2024-12-28 00:00:00', 'complaint': '咳嗽', 'status': 'completed'},
            {'patient_name': '病患1', 'doctor_name': '醫師5', 'datetime': '2024-04-05 00:00:00', 'complaint': '發燒', 'status': 'cancelled'},
            {'patient_name': '病患10', 'doctor_name': '醫師2', 'datetime': '2024-04-07 00:00:00', 'complaint': '腹瀉', 'status': 'completed'},
            {'patient_name': '病患10', 'doctor_name': '醫師3', 'datetime': '2024-01-12 00:00:00', 'complaint': '腹瀉', 'status': 'completed'},
            {'patient_name': '病患1', 'doctor_name': '醫師5', 'datetime': '2024-08-21 00:00:00', 'complaint': '腹瀉', 'status': 'cancelled'},
            {'patient_name': '病患1', 'doctor_name': '醫師1', 'datetime': '2024-09-09 00:00:00', 'complaint': '腹瀉', 'status': 'cancelled'},
            {'patient_name': '病患2', 'doctor_name': '醫師5', 'datetime': '2024-06-14 00:00:00', 'complaint': '咳嗽', 'status': 'cancelled'},
            {'patient_name': '病患5', 'doctor_name': '醫師3', 'datetime': '2024-06-09 00:00:00', 'complaint': '咳嗽', 'status': 'cancelled'},
        ]
        appointments = []
        # 為了使用提供的資料，我們需要確保病患和醫師已存在且對應
        for data in appointments_data:
            patient = patient_map.get(data['patient_name'])
            doctor = doctor_map.get(data['doctor_name'])
            if patient and doctor:
                appointment = Appointment(
                    patient_id=patient.id,
                    doctor_id=doctor.id,
                    datetime=datetime.strptime(data['datetime'], '%Y-%m-%d %H:%M:%S'),
                    complaint=data['complaint'],
                    status=data['status']
                )
                appointments.append(appointment)
            else:
                print(f"警告：找不到病患 {data['patient_name']} 或醫師 {data['doctor_name']}，跳過此掛號記錄。")

        db.session.add_all(appointments)
        db.session.commit()
         # 獲取已插入的掛號物件，以便後續關聯
        inserted_appointments = Appointment.query.all()
        # 創建一個映射，以便通過診斷數據中的掛號 ID 找到對應的掛號物件
        # 注意：這裡假設掛號資料的順序與原始提供的順序一致，以便後續診斷資料的匹配
        appointment_map_by_order = {i: a for i, a in enumerate(inserted_appointments)}
        print("掛號資料填充完成。")

        # === 5. 提供的診斷資料 ===
        print("填充診斷資料...")
        diagnoses_data = [
            {'appointment_id': 1, 'diagnosis_text': '上呼吸道感染', 'doctor_advice': '服藥三天', 'diagnosis_time': '2025-05-26 03:40:55'},
            {'appointment_id': 2, 'diagnosis_text': '腸胃炎', 'doctor_advice': '觀察症狀變化', 'diagnosis_time': '2025-05-26 03:40:55'},
            {'appointment_id': 3, 'diagnosis_text': '上呼吸道感染', 'doctor_advice': '服藥三天', 'diagnosis_time': '2025-05-26 03:40:55'},
            {'appointment_id': 4, 'diagnosis_text': '感冒病毒感染', 'doctor_advice': '觀察症狀變化', 'diagnosis_time': '2025-05-26 03:40:55'},
            {'appointment_id': 5, 'diagnosis_text': '上呼吸道感染', 'doctor_advice': '觀察症狀變化', 'diagnosis_time': '2025-05-26 03:40:55'},
            {'appointment_id': 6, 'diagnosis_text': '感冒病毒感染', 'doctor_advice': '觀察症狀變化', 'diagnosis_time': '2025-05-26 03:40:55'},
            {'appointment_id': 7, 'diagnosis_text': '感冒病毒感染', 'doctor_advice': '觀察症狀變化', 'diagnosis_time': '2025-05-26 03:40:55'},
            {'appointment_id': 8, 'diagnosis_text': '上呼吸道感染', 'doctor_advice': '觀察症狀變化', 'diagnosis_time': '2025-05-26 03:40:55'},
            {'appointment_id': 9, 'diagnosis_text': '感冒病毒感染', 'doctor_advice': '服藥三天', 'diagnosis_time': '2025-05-26 03:40:55'},
            {'appointment_id': 10, 'diagnosis_text': '上呼吸道感染', 'doctor_advice': '多喝水休息', 'diagnosis_time': '2025-05-26 03:40:55'},
        ]
        diagnoses = []
        # 根據提供的診斷數據和已插入的掛號順序來建立診斷記錄
        for i, data in enumerate(diagnoses_data):
            # 假設提供的診斷數據順序與掛號數據的插入順序一致且一一對應
            if i < len(inserted_appointments):
                appointment = inserted_appointments[i] # 根據順序匹配
                diagnosis = Diagnosis(
                    appointment_id=appointment.id, # 使用實際插入的掛號 ID
                    diagnosis_text=data['diagnosis_text'],
                    doctor_advice=data['doctor_advice'],
                    diagnosis_time=datetime.strptime(data['diagnosis_time'], '%Y-%m-%d %H:%M:%S')
                )
                diagnoses.append(diagnosis)
            else:
                print(f"警告：提供的診斷資料 (順序 {i+1}) 多於已插入的掛號數量，跳過此診斷記錄。")

        db.session.add_all(diagnoses)
        db.session.commit()
        # 獲取已插入的診斷物件，以便後續關聯
        inserted_diagnoses = Diagnosis.query.all()
        # 創建一個映射，以便通過處方數據中的診斷 ID 找到對應的診斷物件
        # 這裡假設原始 SQL 中的 diagnosis_id 和實際插入的順序是一致的。
        # 例如，原始 SQL 中 diagnosis_id 為 1 的對應實際插入的第一個診斷記錄。
        diagnosis_map_by_order = {i+1: d for i, d in enumerate(inserted_diagnoses)}
        print("診斷資料填充完成。")

        # === 6. 提供的處方資料 ===
        print("填充處方資料...")
        prescriptions_data = [
             {'diagnosis_id': 1, 'medicine_name': '藥品6', 'dosage': '5ml/次', 'days': 5, 'frequency': '每日兩次', 'prescribed_time': '2025-05-26 03:40:55'},
             {'diagnosis_id': 2, 'medicine_name': '藥品10', 'dosage': '1顆/次', 'days': 3, 'frequency': '飯後服用', 'prescribed_time': '2025-05-26 03:40:55'},
             {'diagnosis_id': 3, 'medicine_name': '藥品8', 'dosage': '1顆/次', 'days': 4, 'frequency': '飯後服用', 'prescribed_time': '2025-05-26 03:40:55'},
             {'diagnosis_id': 4, 'medicine_name': '藥品2', 'dosage': '5ml/次', 'days': 7, 'frequency': '飯後服用', 'prescribed_time': '2025-05-26 03:40:55'},
             {'diagnosis_id': 5, 'medicine_name': '藥品3', 'dosage': '1顆/次', 'days': 3, 'frequency': '每日兩次', 'prescribed_time': '2025-05-26 03:40:55'},
             {'diagnosis_id': 6, 'medicine_name': '藥品7', 'dosage': '1包/天', 'days': 7, 'frequency': '飯後服用', 'prescribed_time': '2025-05-26 03:40:55'},
             {'diagnosis_id': 7, 'medicine_name': '藥品7', 'dosage': '1顆/次', 'days': 7, 'frequency': '每日兩次', 'prescribed_time': '2025-05-26 03:40:55'},
             {'diagnosis_id': 8, 'medicine_name': '藥品2', 'dosage': '1顆/次', 'days': 7, 'frequency': '飯後服用', 'prescribed_time': '2025-05-26 03:40:55'},
             {'diagnosis_id': 9, 'medicine_name': '藥品7', 'dosage': '1包/天', 'days': 3, 'frequency': '每日三次', 'prescribed_time': '2025-05-26 03:40:55'},
             {'diagnosis_id': 10, 'medicine_name': '藥品5', 'dosage': '5ml/次', 'days': 5, 'frequency': '飯後服用', 'prescribed_time': '2025-05-26 03:40:55'},
        ]
        prescriptions = []
         # 根據提供的處方數據、診斷映射和藥品映射來建立處方記錄
        for data in prescriptions_data:
             original_diagnosis_id = data['diagnosis_id']
             # 根據原始診斷 ID 從映射中獲取實際插入的診斷物件
         # 為了使用提供的資料並確保關聯正確，我們需要找到對應的診斷和藥品物件
         # 注意：這裡提供的 diagnosis_id 是基於原始 SQL 插入順序的假設 ID。
         # 我們需要根據處方數據中的 diagnosis_id (假設是原始 SQL 插入順序) 來找到
         # 對應的診斷物件，並根據 medicine_name 找到藥品物件。

        # 創建一個映射，以便通過原始 SQL 中的診斷 ID 找到實際插入的診斷物件
        # 這裡假設原始 SQL 中的 diagnosis_id 和實際插入的順序是一致的。
        # 例如，原始 SQL 中 diagnosis_id 為 1 的對應實際插入的第一個診斷記錄。
        diagnosis_by_original_id = {i+1: d for i, d in enumerate(inserted_diagnoses)}


        for data in prescriptions_data:
             original_diagnosis_id = data['diagnosis_id']
             diagnosis = diagnosis_by_original_id.get(original_diagnosis_id)
             medicine = medicine_map.get(data['medicine_name'])

             if diagnosis and medicine:
                 prescription = Prescription(
                     diagnosis_id=diagnosis.id, # 使用實際插入的診斷 ID
                     medicine_id=medicine.id, # 使用實際插入的藥品 ID
                     dosage=data['dosage'],
                     days=data['days'],
                     frequency=data['frequency'],
                     prescribed_time=datetime.strptime(data['prescribed_time'], '%Y-%m-%d %H:%M:%S')
                 )
                 prescriptions.append(prescription)
             else:
                  print(f"警告：找不到診斷 (原始 ID: {original_diagnosis_id}) 或藥品 {data['medicine_name']}，跳過此處方記錄。")


        db.session.add_all(prescriptions)
        db.session.commit()
        print("處方資料填充完成。")

        print("資料庫填充完成！")

if __name__ == '__main__':
    seed_database() 