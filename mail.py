import smtplib
import ssl
from email.message import EmailMessage

from_addr = "airportabcd@gmail.com"
password = "fspyxaxnkptjxfrg"


# email_arr = ["randompassenger1@gmail.com"]
# departure_time = "2023, 4, 1, 5:30"
# origin = "Canada"
# destination = "USA"
# name_arr = ["sleepy Joe"]

def email_all(email_arr, name_arr, origin, destination, departure_time):
    for i in range(len(email_arr)):
        txt = email_arr[i]
        end = txt.split("@")
        if end[-1] == "gmail.com":
            subject = "flight notifiation"
            message = "hello " + name_arr[i] + " your flight from " + origin + " to " + destination + " will depart at " + departure_time + " please be there at least 2 hours in advance to check in your bags. Enjoy your flight ;)"

            em = EmailMessage()
            em['From'] = from_addr
            em['To'] = email_arr[i]
            em['Subject'] = subject
            em.set_content(message)

            context = ssl.create_default_context()

            with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
                smtp.login(from_addr, password)
                smtp.sendmail(from_addr, email_arr[i], em.as_string())