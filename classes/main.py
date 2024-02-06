from imports import *
from mailService import *
import os
def Mail_Testing():
    mail_repo = Mail_Handler()

    mail = Mail_Data("example@example.com", "secure_password")
    mail_repo.insert_mail(mail)

    retrieved_mail = mail_repo.get_mail_by_user("example@example.com")

    if retrieved_mail:
        print(f"Retrieved Mail: {retrieved_mail}")
    else:
        print("Mail not found.")
        
        
def Admin_Testing():
    admin = Admin_Data("Ido", "for now not salted hashed and with history", "stam@gmail.com")
    
    
    handler = Admin_Handler()
    res = handler.insert_admin(admin)
    print(res) 
    
    retrieved_mail = handler.get_admin_by_mail("stam@gmail.com")

    if retrieved_mail:
        print(f"Retrieved Mail: {retrieved_mail}")
    else:
        print("Mail not found.")
    
    admin.admin_mail = "stam_updated@gmail.com"
    res = handler.update_admin("Ido", admin)
    print(res)
    
    input("waiting for keypress to delete admin")
    
    res = handler.delete_admin("Ido")
    print(res)

def Events_Testing():
    event = Event_Data(ip="127.0.0.1", location="Tel aviv", service="Test2", additional_data="Test")
    print("Test 1: inserting")
    handler = Event_Handler()
    res = handler.insert_event(event)
    print(res)
    
    
    print("Test 2: selecting event by id")
    retrieved_event = handler.select_event(event.event_id)
    if retrieved_event:
        print(f"Retrieved Event: {retrieved_event}")
    else:
        print("Event not found.")
    
    print("Test 3: select_events_by_date_range")
    timestamp_1 = datetime.datetime(2023, 9, 4)
    timestamp_2 = datetime.datetime(2023, 9, 6)
    retrieved_events = handler.select_events_by_date_range(timestamp_1, timestamp_2)
    if retrieved_events:
        for retrieved_event in retrieved_events:
            print(f"event id: {retrieved_event.event_id}")
    else:
        print("Not Found")
        
    print("Test 4: select_events_by_service")
    retrieved_events = handler.select_events_by_service("Test")
    if retrieved_events:
        for retrieved_event in retrieved_events:
            print(f"event id: {retrieved_event.event_id}")
    else:
        print("Not Found")
        
    print("Test 5: select_events_by_location")
    retrieved_events = handler.select_events_by_location("Tel Aviv")
    if retrieved_events:
        for retrieved_event in retrieved_events:
            print(f"event id: {retrieved_event.event_id}")
    else:
        print("Not Found")
    
    print("Test 6: select_all_events")
    retrieved_events = handler.select_all_events()
    if retrieved_events:
        for retrieved_event in retrieved_events:
            print(f"event id: {retrieved_event.event_id}")
    else:
        print("Not Found") 

def Orders_Testing():
    order = Order_Data(
        username="test_user",
        total_price=100.0,
        product_ids=["product1", "product2"],
        address="123 Main St",
        order_status="Processed"
    )
    print("Test 1: Inserting Order")
    handler = Order_Handler()
    res = handler.insert_order(order)
    print(res)

    print("Test 2: Selecting Order by ID")
    retrieved_order = handler.select_order(order.order_id)
    if retrieved_order:
        print(f"Retrieved Order: {retrieved_order.__dict__}")
    else:
        print("Order not found.")

    print("Test 3: Selecting Orders by Date Range")
    start_date = datetime.datetime(2023, 9, 1)
    end_date = datetime.datetime(2023, 9, 10)
    retrieved_orders = handler.select_orders_by_date_range(start_date, end_date)
    if retrieved_orders:
        for retrieved_order in retrieved_orders:
            print(f"Order ID: {retrieved_order.order_id}")
    else:
        print("No orders found.")

    print("Test 4: Selecting Orders by Username")
    retrieved_orders = handler.select_orders_by_username("user123")
    if retrieved_orders:
        for retrieved_order in retrieved_orders:
            print(f"Order ID: {retrieved_order.order_id}")
    else:
        print("No orders found.")

    print("Test 5: Selecting All Orders")
    retrieved_orders = handler.select_all_orders()
    if retrieved_orders:
        for retrieved_order in retrieved_orders:
            print(f"Order ID: {retrieved_order.order_id}")
    else:
        print("No orders found.")

    print("Test 6: Cancel Order by ID")
    cancel_res = handler.cancel_order(order.order_id)
    print(cancel_res)
    
def Products_Testing():
    product1 = Product_Data(
        product_name="Product A",
        price=10.0
    )

    product2 = Product_Data(
        product_name="Product B",
        price=15.0
    )

    print("Test 1: Inserting Products")
    product_handler = Product_Handler()
    insert_res1 = product_handler.insert_product(product1)
    insert_res2 = product_handler.insert_product(product2)
    print(insert_res1)
    print(insert_res2)
    
    print("Test 2: Selecting Product by ID")
    retrieved_product = product_handler.select_product_by_id(product1.product_id)
    if retrieved_product:
        print(f"Retrieved Product: {retrieved_product.__dict__}")
    else:
        print("Product not found.")

    print("Test 3: Selecting Product by Name")
    retrieved_products_by_name = product_handler.select_products_by_name("Product A")
    if retrieved_products_by_name:
        for retrieved_product in retrieved_products_by_name:
            print(f"Product ID: {retrieved_product.product_id}")
    else:
        print("No products found by name.")

    print("Test 4: Selecting All Products")
    retrieved_products = product_handler.select_all_products()
    if retrieved_products:
        for retrieved_product in retrieved_products:
            print(f"Product ID: {retrieved_product.product_id}, Name: {retrieved_product.product_name}")
    else:
        print("No products found.")

    print("Test 5: Updating Product Name and Price by ID")
    update_res = product_handler.update_product(product1.product_id, "Updated Product A", 20.0)
    print(update_res)

    print("Test 6: Removing Product by ID")
    remove_res = product_handler.remove_product(product2.product_id)
    print(remove_res)
    
def salt_testing():
    print("----- Salt Testing -----")
    # Initialize Salt_Handler
    salt_handler = Salt_Handler()

    # Test 1: Inserting Salts
    salt1 = Salt_Data(username_admin="user1")
    salt2 = Salt_Data(username_reporting="user2")

    print("Test 1: Inserting Salts")
    insert_res1 = salt_handler.insert_salt(salt1)
    insert_res2 = salt_handler.insert_salt(salt2)
    print("Insertion Result 1:", insert_res1)
    print("Insertion Result 2:", insert_res2)

    # Test 2: Selecting Salt by Username and Service
    print("\nTest 2: Selecting Salt by Username and Service")
    retrieved_salt1 = salt_handler.select_salt_by_username_and_service(username_admin=salt1.username_admin)
    if retrieved_salt1:
        print(f"Retrieved Salt 1: {retrieved_salt1}")
    else:
        print("Salt 1 not found.")

    # Test 3: Updating Salt by Username and Service
    print("\nTest 3: Updating Salt by Username and Service")
    update_res1 = salt_handler.update_salt(username_admin=salt1.username_admin)
    print("Update Result 1:", update_res1)

    # Test 4: Selecting Salt Again to Verify Update
    print("\nTest 4: Selecting Salt Again to Verify Update")
    retrieved_salt1_updated = salt_handler.select_salt_by_username_and_service(username_admin=salt1.username_admin)
    if retrieved_salt1_updated:
        print(f"Updated Salt 1: {retrieved_salt1_updated}")
    else:
        print("Updated Salt 1 not found.")

    # Test 5: Updating Salt for a non-existent combination
    print("\nTest 5: Updating Salt for a non-existent combination")
    update_res_non_existent = salt_handler.update_salt("nonexistent_user", "nonexistent_service")
    print("Update Result for non-existent combination:", update_res_non_existent)

    # Test 6: Selecting Salt for a non-existent combination
    print("\nTest 6: Selecting Salt for a non-existent combination")
    retrieved_salt_non_existent = salt_handler.select_salt_by_username_and_service("nonexistent_user", "nonexistent_service")
    if retrieved_salt_non_existent is None:
        print("Salt for non-existent combination not found.")
    else:
        print(f"Salt for non-existent combination: {retrieved_salt_non_existent}")
      

def sendMail():
    recipient_email = "nivade123@gmail.com"
    
    message = Message (
        subject="Test Email",
        text="This is a test email with attachments.",
        additional_files=[r"C:\Users\User\OneDrive\Documents\Table1.txt"] ) 
      

    mail_service = MailService()
    mail_service.send_mail(message, recipient_email)
    
def salt_testing2():
    # Test 7: Selecting Salt for a non-existent combination
    print("\nTest 7: getting hashed password")
    saltmanager=Salt_Manager()
    retrieved_pass = saltmanager.GetSaltedHashPassword("password",username_admin="user1")
    if retrieved_pass is None:
        print("user was not found")
    else :
        print(f"salted hash password: {retrieved_pass}")  
    


def token_testing():
    print("----- Token Testing -----")
    # Initialize TokenHandler
    token_handler = TokenHandler()

    # Test 1: Inserting Tokens
    token2 = TokenData(username_admin="user1")
    token1 = TokenData(username_reporting="user2")

    print("Test 1: Inserting Tokens")
    insert_res1 = token_handler.insert_token(token1)
    insert_res1 = token_handler.insert_token(token1)
    insert_res2 = token_handler.insert_token(token2)
    print("Insertion Result 1:", insert_res1)
    print("Insertion Result 2:", insert_res2)

    # Test 2: Selecting Token by Username
    print("\nTest 2: Selecting Token by Username")
    retrieved_token1 = token_handler.select_token_by_username(token1.username_reporting)
    if retrieved_token1:
        print(f"Retrieved Token 1: {retrieved_token1}")
    else:
        print("Token 1 not found.")

    # Test 3: Updating Token by Username
    print("\nTest 3: Updating Token by Username")
    update_res1 = token_handler.update_token(token1.username_reporting)
    print("Update Result 1:", update_res1)

    # Test 4: Selecting Token Again to Verify Update
    print("\nTest 4: Selecting Token Again to Verify Update")
    retrieved_token1_updated = token_handler.select_token_by_username(token1.username_reporting)
    if retrieved_token1_updated:
        print(f"Updated Token 1: {retrieved_token1_updated}")
    else:
        print("Updated Token 1 not found.")

    # Test 5: Updating Token for a non-existent username
    print("\nTest 5: Updating Token for a non-existent username")
    update_res_non_existent = token_handler.update_token("nonexistent_user")
    print("Update Result for non-existent username:", update_res_non_existent)

    # Test 6: Selecting Token for a non-existent username
    print("\nTest 6: Selecting Token for a non-existent username")
    retrieved_token_non_existent = token_handler.select_token_by_username("nonexistent_user")
    if retrieved_token_non_existent is None:
        print("Token for non-existent username not found.")
    else:
        print(f"Token for non-existent username: {retrieved_token_non_existent}")


def UsersReporting_Testing():
    # Create a UsersReportingData instance
    user_reporting = UsersReportingData("JohnDoe", "password123", "john.doe@example.com")
    
    # Initialize UsersReportingHandler
    handler = UsersReportingHandler()
    
    # Test 1: Inserting UsersReportingData
    print("Test 1: Inserting UsersReportingData")
    insert_res = handler.insert_user_reporting(user_reporting)
    print("Insertion Result:", insert_res)
    
    # Test 2: Selecting UsersReportingData by admin_name
    print("\nTest 2: Selecting UsersReportingData by admin_name")
    retrieved_user_reporting = handler.select_user_reporting_by_name("JohnDoe")
    if retrieved_user_reporting:
        print(f"Retrieved UsersReportingData: {retrieved_user_reporting.__dict__}")
    else:
        print("UsersReportingData not found.")
    
    # Test 3: Updating UsersReportingData
    print("\nTest 3: Updating UsersReportingData")
    user_reporting.mail = "john.doe.updated@example.com"
    update_res = handler.update_user_reporting("JohnDoe", user_reporting)
    print("Update Result:", update_res)
    
    # Test 4: Deleting UsersReportingData
    print("\nTest 4: Deleting UsersReportingData")
    input("Press Enter to delete UsersReportingData")
    delete_res = handler.delete_user_reporting("JohnDoe")
    print("Deletion Result:", delete_res)


def UsersWeb_Testing():
    # Create a UsersWebData instance
    user_web = UsersWebData("JohnDoeWeb", "password123web", "john.doe.web@example.com")
    
    # Initialize UsersWebHandler
    handler = UsersWebHandler()
    
    # Test 1: Inserting UsersWebData
    print("Test 1: Inserting UsersWebData")
    insert_res = handler.insert_user_web(user_web)
    print("Insertion Result:", insert_res)
    
    # Test 2: Selecting UsersWebData by username
    print("\nTest 2: Selecting UsersWebData by username")
    retrieved_user_web = handler.get_user_web_by_username("JohnDoeWeb")
    if retrieved_user_web:
        print(f"Retrieved UsersWebData: {retrieved_user_web.__dict__}")
    else:
        print("UsersWebData not found.")
    
    # Test 3: Updating UsersWebData
    print("\nTest 3: Updating UsersWebData")
    user_web.mail = "john.doe.updated.web@example.com"
    update_res = handler.update_user_web("JohnDoeWeb", user_web)
    print("Update Result:", update_res)
    
    # Test 4: Deleting UsersWebData
    print("\nTest 4: Deleting UsersWebData")
    input("Press Enter to delete UsersWebData")
    delete_res = handler.delete_user_web("JohnDoeWeb")
    print("Deletion Result:", delete_res)


def password_json_handler_testing():
    # Test creating PasswordJsonHandler instance without passwords_json
    handler = PasswordJsonHandler(service="admin", user="user1")
    print("Initial Passwords:")
    handler.print_password()

    # Test inserting passwords
    print("\nTest Insert Password:")
    handler.insert_password("password1")
    handler.insert_password("password1")
    handler.print_password()

    # Test building JSON
    print("\nTest Build JSON:")
    json_str = handler.build_json()
    print(json_str)

    # Test creating PasswordJsonHandler instance with passwords_json
    print("\nTest Create PasswordJsonHandler with JSON:")
    handler2 = PasswordJsonHandler(service="admin", user="user1", passwords_json=json_str)
    handler2.print_password()

    # Test comparing new password
    print("\nTest Compare New Password:")
    print("Is 'password1' in last 3 passwords:", handler2.compare_new_password("password1", 3))
    print("Is 'password2' in last 3 passwords:", handler2.compare_new_password("password2", 3))

    # Test comparing current password
    print("\nTest Compare Current Password:")
    print("Is 'password1' the current password:", handler2.compare_current_password("password1"))
    print("Is 'password2' the current password:", handler2.compare_current_password("password2"))

    # Test getting hashed password
    print("\nTest Get Hashed Password:")
    hashed_password = handler2.get_hashed_password("user1")
    print("Hashed password for 'user1':", hashed_password)

    # Test deleting the first password
    print("\nTest Delete First Password:")
    handler2.delete_first()
    handler2.print_password()


def check_user_validation_try_login():
    from UserCreation import create_user_admin_table
    # for now we are checking only admin
    # create user 
    # admin = Admin_Data("Ido", "password1", "stam@gmail.com")
    # UserCreation.create_user_admin_table(admin)
    
    
    # We want to check: we need to check if it is working with mail and username, user is blocked, blocked time removed, connecting to user
    # trying to connect:
    # user mail
    admin=Admin_Data("stamuser","strongpass123","stam@gmail.com")
    UserCreation.create_user_admin_table(admin)
    res, errMessage = user_validation.User_Validation.TryLogin(service="admin", password="strongpass123", username="stamuser")
    print(res)
    print(errMessage)   
    res, errMessage = user_validation.User_Validation.TryLogin(service="admin", password="nivniv1", username="stamuser")
    print(res)
    print(errMessage)    
    res, errMessage = user_validation.User_Validation.TryLogin(service="admin", password="nivniv3", username="stamuser")
    print(res)
    print(errMessage)   
    res, errMessage = user_validation.User_Validation.TryLogin(service="admin", password="ivniv123", username="stamuser")
    print(res)
    print(errMessage)   
    res, errMessage = user_validation.User_Validation.TryLogin(service="admin", password="ivniv123", username="stamuser")
    print(res)
    print(errMessage)
    
    
    
def check_password():
    passwords = ["abc", "1234567sdfs8", "1A234567sdfs8", "password1", "Asdf@sdf34", "12345678"]
    
    for password in passwords:
        res, error = Password_Checker.check_password(password, "Ido", "admin")
        print(f"result:{res}, error: {error}")
    
    

admin=UsersReportingData("Admin_Fusion","Admin123212!","stam@gmail.com")
UserCreation.create_user_reporting_table(admin)
