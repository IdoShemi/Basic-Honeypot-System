import unittest
import time
from imports import *

class TestUserReporting(unittest.TestCase):
    def test_insertion(self):
        admin = UsersReportingData("Ido", "password1", "stam@gmail.com")
        UserCreation.create_user_reporting_table(admin)
        admin2 = UsersReportingHandler().select_user_reporting_by_mail("stam@gmail.com")
        self.assertEqual(admin.admin_name, admin2.admin_name)
        admin3 = UsersReportingHandler().select_user_reporting_by_name("Ido")
        self.assertEqual(admin.mail, admin3.mail)
        
    def test_trylogin(self):
        admin = UsersReportingHandler().select_user_reporting_by_mail("stam@gmail.com")
        res, errMessage = user_validation.User_Validation.TryLogin(service="reporting", password="password1", username="Ido")
        self.assertTrue(res)

        res, errMessage = user_validation.User_Validation.TryLogin(service="reporting", password="password12", username="Ido")
        self.assertFalse(res)
        res, errMessage = user_validation.User_Validation.TryLogin(service="reporting", password="password12", username="Ido")
        self.assertFalse(res)
        res, errMessage = user_validation.User_Validation.TryLogin(service="reporting", password="password12", username="Ido")
        self.assertFalse(res)
        res, errMessage = user_validation.User_Validation.TryLogin(service="reporting", password="password12", username="Ido")
        self.assertEqual(errMessage, "user is blocked")
        
        time.sleep(60)
        res, errMessage = user_validation.User_Validation.TryLogin(service="reporting", password="password12", username="Ido")
        self.assertFalse(res)
        
        res, errMessage = user_validation.User_Validation.TryLogin(service="reporting", password="password1", username="Ido")
        self.assertTrue(res)

        
if __name__ == '__main__':
    unittest.main()
    