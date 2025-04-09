from entity.appointment import Appointment
from dao.hospitalserviceimpl import HospitalServiceImpl
from exception.patientnumbernotfoundexception import PatientNumberNotFoundException


def main():
    service = HospitalServiceImpl()

    while True:  # 🔁 Outer loop to allow re-login
        print("\n---- Hospital Management System Login ----")
        print("1. Admin Login")
        print("2. Doctor Login")
        print("3. Patient Login")
        print("4. Exit")
        login_type = input("Select Login Type (1/2/3/4): ")

        is_admin = False
        is_doctor = False
        is_patient = False

        if login_type == '1':
            username = input("Enter admin username: ")
            password = input("Enter admin password: ")
            if username == "admin" and password == "admin123":
                is_admin = True
            else:
                print("❌ Invalid admin credentials.")
                continue

        elif login_type == '2':
            username = input("Enter doctor username: ")
            password = input("Enter doctor password: ")
            if username == "doctor" and password == "doc123":
                is_doctor = True
            else:
                print("❌ Invalid doctor credentials.")
                continue

        elif login_type == '3':
            username = input("Enter patient username: ")
            password = input("Enter patient password: ")
            if username == "patient" and password == "pat123":
                is_patient = True
            else:
                print("❌ Invalid patient credentials.")
                continue

        elif login_type == '4':
            print("✅ Exiting the system. Goodbye!")
            break

        else:
            print("❌ Invalid login type.")
            continue

        # 🔁 Inner loop: operations after login
        while True:
            print("\n---- Hospital Management System ----")
            if is_admin:
                print("1. Schedule Appointment")
            print("2. View Appointment by ID")
            print("3. View Appointments by Patient ID")
            print("4. View Appointments by Doctor ID")
            if is_admin:
                print("5. Update Appointment")
                print("6. Cancel Appointment")
            print("7. Logout")

            choice = input("Enter your choice: ")

            try:
                if choice == '1' and is_admin:
                    pid = int(input("Patient ID: "))
                    did = int(input("Doctor ID: "))
                    date = input("Date (YYYY-MM-DD): ")
                    desc = input("Description: ")
                    appt = Appointment(None, pid, did, date, desc)
                    service.schedule_appointment(appt)

                elif choice == '2':
                    aid = int(input("Enter Appointment ID: "))
                    appt = service.get_appointment_by_id(aid)
                    print(appt if appt else "No appointment found.")

                elif choice == '3':
                    pid = int(input("Enter Patient ID: "))
                    appts = service.get_appointments_for_patient(pid)
                    for a in appts:
                        print(a)

                elif choice == '4':
                    did = int(input("Enter Doctor ID: "))
                    appts = service.get_appointments_for_doctor(did)
                    for a in appts:
                        print(a)

                elif choice == '5' and is_admin:
                    print("\n-- Update Appointment --")
                    print("1. Change Doctor")
                    print("2. Change Appointment Date")
                    print("3. Exit")
                    sub_choice = input("Enter your choice (1 or 2 or 3): ")

                    if sub_choice == '1':
                        aid = int(input("Enter Appointment ID: "))
                        new_did = int(input("Enter New Doctor ID: "))
                        service.update_appointment_doctor(aid, new_did)

                    elif sub_choice == '2':
                        aid = int(input("Enter Appointment ID: "))
                        new_date = input("Enter New Appointment Date (YYYY-MM-DD): ")
                        service.update_appointment_date(aid, new_date)

                elif choice == '6' and is_admin:
                    aid = int(input("Appointment ID to cancel: "))
                    service.cancel_appointment(aid)

                elif choice == '7':
                    print("🔁 Logging out...")
                    break  # exits inner loop, returns to login menu

                else:
                    print("Invalid option or access denied.")

            except PatientNumberNotFoundException as e:
                print("Error:", e)
            except ValueError:
                print("Invalid input type.")
            except Exception as e:
                print("An unexpected error occurred:", e)

if __name__ == "__main__":
    main()
