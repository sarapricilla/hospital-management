from dao.hospitalservice import IHospitalService
from entity.appointment import Appointment
from entity.patient import Patient
from entity.doctor import Doctor
from exception.patientnumbernotfoundexception import PatientNumberNotFoundException
from exception.appointmentnotfoundexception import AppointmentNotFoundException
from util.dbconnection import DBConnection

class HospitalServiceImpl(IHospitalService):

    def __init__(self):
        self.conn = DBConnection.get_connection()
        self.cursor = self.conn.cursor()
        self._setup_table()

    def _setup_table(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS appointment (
                                appointment_id INTEGER PRIMARY KEY,
                                patient_id INTEGER,
                                doctor_id INTEGER,
                                appointment_date TEXT,
                                description TEXT)''')
        self.conn.commit()

   
    def get_appointment_by_id(self, appointment_id: int) -> Appointment:
        try:
            query = "SELECT appointmentid, patientid, doctorid, appointmentdate, description FROM appointment WHERE appointmentid = %s"
            self.cursor.execute(query, (appointment_id,))
            row = self.cursor.fetchone()

            if row:
                appointment = Appointment(*row)
                print("\n📋  Appointment Details")
                print("─────────────────────────────────────────")
                print("🆔 Appointment ID   : ", appointment.get_appointment_id())
                print("🧑‍⚕️ Patient ID       : ", appointment.get_patient_id())
                print("👨‍⚕️ Doctor ID        : ", appointment.get_doctor_id())
                print("📅 Date             : ", appointment.get_appointment_date())
                print("📝 Description      : ", appointment.get_description())
                print("─────────────────────────────────────────")
                return appointment
            else:
                raise PatientNumberNotFoundException(f"No appointment found with ID: {appointment_id}")

        except PatientNumberNotFoundException as e:
            print("❌", e)
            return None
        except Exception as e:
            print("⚠️  An unexpected error occurred while retrieving the appointment:", e)
            return None



    def get_appointments_for_patient(self, patient_id: int):
        try:
            query = """
                SELECT 
                    a.appointmentid, a.patientid, a.doctorid, a.appointmentdate, a.description,
                    p.firstname, p.lastname, p.address
                FROM 
                    appointment a
                JOIN 
                    patient p ON a.patientid = p.patientid
                WHERE 
                    a.patientid = %s
            """
            self.cursor.execute(query, (patient_id,))
            rows = self.cursor.fetchall()

            if not rows:
                self.cursor.execute("SELECT firstname, lastname, address FROM patient WHERE patientid = %s", (patient_id,))
                patient_info = self.cursor.fetchone()
                if patient_info:
                    patient = Patient(patient_id, patient_info[0], patient_info[1], None, None, None, patient_info[2])
                    print(f"\nHello {patient.get_first_name()} {patient.get_last_name()} from {patient.get_address()}, you have no appointments.")
                else:
                    raise PatientNumberNotFoundException(f"No patient found with ID: {patient_id}")
                return []

            # Build patient object from first row
            patient = Patient(patient_id, rows[0][5], rows[0][6], None, None, None, rows[0][7])
            print(f"\nHello {patient.get_first_name()} {patient.get_last_name()} from {patient.get_address()}, you have {len(rows)} appointment(s).")

            appointments = []

            for row in rows:
                appointment = Appointment(row[0], row[1], row[2], row[3], row[4])
                print("\n📋  Appointment Details")
                print("─────────────────────────────────────────────")
                print("🆔 Appointment ID   : ", appointment.get_appointment_id())
                print("🧑‍⚕️ Patient ID       : ", appointment.get_patient_id())
                print("🙍‍♂️ Patient Name     : ", patient.get_first_name(), patient.get_last_name())
                print("👨‍⚕️ Doctor ID        : ", appointment.get_doctor_id())
                print("📅 Appointment Date : ", appointment.get_appointment_date())
                print("📝 Description      : ", appointment.get_description())
                print("─────────────────────────────────────────────")

                appointments.append(appointment)

            return appointments

        except PatientNumberNotFoundException as e:
            print("Error:", e)
            return []

        except Exception as e:
            print("An unexpected error occurred:", e)
            return []


   

    def get_appointments_for_doctor(self, doctor_id: int):
        try:
            query = """
                SELECT 
                    a.appointmentid, a.patientid, a.doctorid, a.appointmentdate, a.description,
                    p.firstname, p.lastname,
                    d.firstname, d.lastname
                FROM 
                    appointment a
                JOIN 
                    patient p ON a.patientid = p.patientid
                JOIN 
                    doctor d ON a.doctorid = d.doctorid
                WHERE 
                    a.doctorid = %s
            """
            self.cursor.execute(query, (doctor_id,))
            rows = self.cursor.fetchall()

            if not rows:
                # Check if doctor exists
                self.cursor.execute("SELECT firstname, lastname FROM doctor WHERE doctorid = %s", (doctor_id,))
                doctor = self.cursor.fetchone()
                if doctor:
                    print(f"\nHello Dr. {doctor[0]} {doctor[1]}, you have no appointments scheduled.")
                else:
                    raise PatientNumberNotFoundException(f"No doctor found with ID: {doctor_id}")
                return []

            # Extract doctor name
            doctor_fname = rows[0][7]
            doctor_lname = rows[0][8]
            print(f"\nHello Dr. {doctor_fname} {doctor_lname}, you have {len(rows)} appointment(s) to undertake:")

            appointments = []

            for row in rows:
                appointment = Appointment(row[0], row[1], row[2], row[3], row[4])
                patient_fname = row[5]
                patient_lname = row[6]

                print("\n📋  Appointment Details")
                print("─────────────────────────────────────────────")
                print("🆔 Appointment ID   : ", appointment.get_appointment_id())
                print("🙍‍♂️ Patient Name     : ", patient_fname, patient_lname)
                print("👨‍⚕️ Doctor Name      : ", doctor_fname, doctor_lname)
                print("📅 Appointment Date : ", appointment.get_appointment_date())
                print("📝 Description      : ", appointment.get_description())
                print("─────────────────────────────────────────────")

                appointments.append(appointment)

            return appointments

        except PatientNumberNotFoundException as e:
            print("Error:", e)
            return []

        except Exception as e:
            print("\nAn unexpected error occurred while retrieving doctor's appointments:", str(e))
            return []


    def schedule_appointment(self, appointment: Appointment) -> bool:
        try:
            # ✅ Validate patient
            self.cursor.execute("SELECT 1 FROM patient WHERE patientid = %s", (appointment.get_patient_id(),))
            if not self.cursor.fetchone():
                raise PatientNumberNotFoundException(f"❌ Patient with ID {appointment.get_patient_id()} not found.")

            # ✅ Validate doctor
            self.cursor.execute("SELECT 1 FROM doctor WHERE doctorid = %s", (appointment.get_doctor_id(),))
            if not self.cursor.fetchone():
                print(f"⚠ Warning: Doctor with ID {appointment.get_doctor_id()} not found. Proceeding anyway.")

            # ✅ Insert (excluding appointmentid since it's AUTO_INCREMENT)
            self.cursor.execute(
                """
                INSERT INTO appointment (patientid, doctorid, appointmentdate, description)
                VALUES (%s, %s, %s, %s)
                """,
                (
                    appointment.get_patient_id(),
                    appointment.get_doctor_id(),
                    appointment.get_appointment_date(),
                    appointment.get_description()
                )
            )
            self.conn.commit()

            # ✅ Retrieve generated appointmentid
            generated_id = self.cursor.lastrowid

            # ✅ Display confirmation
            print("\n✅ Appointment Scheduled Successfully!")
            print("📌  Added Appointment Details")
            print("─────────────────────────────────────────────")
            print("🆔 Appointment ID   : ", generated_id)
            print("🧑‍⚕️ Patient ID       : ", appointment.get_patient_id())
            print("👨‍⚕️ Doctor ID        : ", appointment.get_doctor_id())
            print("📅 Appointment Date : ", appointment.get_appointment_date())
            print("📝 Description      : ", appointment.get_description())
            print("─────────────────────────────────────────────")

            return True

        except PatientNumberNotFoundException as e:
            print(e)
            return False

        except Exception as e:
            print("❌ An unexpected error occurred while scheduling the appointment:", str(e))
            return False


    def update_appointment_doctor(self, appointment_id: int, new_doctor_id: int) -> bool:
        try:
            self.cursor.execute("SELECT 1 FROM appointment WHERE appointmentid = %s", (appointment_id,))
            if not self.cursor.fetchone():
                raise PatientNumberNotFoundException(f"Appointment ID {appointment_id} not found.")

            self.cursor.execute(
                "UPDATE appointment SET doctorid = %s WHERE appointmentid = %s",
                (new_doctor_id, appointment_id)
            )
            self.conn.commit()

            updated = self.get_appointment_by_id(appointment_id)
            print("\n✅ Doctor update attempted. Current Appointment Details:")
            print("Appointment ID     :", updated.get_appointment_id())
            print("Patient ID         :", updated.get_patient_id())
            print("Doctor ID          :", updated.get_doctor_id())
            print("Appointment Date   :", updated.get_appointment_date())
            print("Description        :", updated.get_description())

            return True

        except PatientNumberNotFoundException as e:
            print("❌ Error:", e)
            return False

        except Exception as e:
            print("❌ Error updating doctor:", str(e))
            return False


    def update_appointment_date(self, appointment_id: int, new_date: str) -> bool:
        try:
            # Check if appointment exists
            self.cursor.execute("SELECT 1 FROM appointment WHERE appointmentid = %s", (appointment_id,))
            if not self.cursor.fetchone():
                raise PatientNumberNotFoundException(f"Appointment ID {appointment_id} not found.")

            # Perform update
            self.cursor.execute(
                "UPDATE appointment SET appointmentdate = %s WHERE appointmentid = %s",
                (new_date, appointment_id)
            )
            self.conn.commit()

            if self.cursor.rowcount > 0:
                print("\n✅ Appointment date updated successfully. Updated Appointment:")
                updated = self.get_appointment_by_id(appointment_id)
                print("Appointment ID     :", updated.get_appointment_id())
                print("Patient ID         :", updated.get_patient_id())
                print("Doctor ID          :", updated.get_doctor_id())
                print("Appointment Date   :", updated.get_appointment_date())
                print("Description        :", updated.get_description())
                return True
            return False

        except PatientNumberNotFoundException as e:
            print("❌ Error:", e)
            return False

        except Exception as e:
            print("❌ Error updating appointment date:", str(e))
            return False


    def cancel_appointment(self, appointment_id: int) -> bool:
        try:
            self.cursor.execute("DELETE FROM appointment WHERE appointmentid = %s", (appointment_id,))
            self.conn.commit()

            if self.cursor.rowcount == 0:
                raise AppointmentNotFoundException(f"Appointment ID {appointment_id} not found.")

            print("\n ✅Appointment cancelled successfully.")
            print("💸 Please collect your refund amount: ₹500")
            return True

        except AppointmentNotFoundException as e:
            print("❌", e)
            return False

        except Exception as e:
            print("❌ Error cancelling appointment:", str(e))
            return False
