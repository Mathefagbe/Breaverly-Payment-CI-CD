from beaverly_api import permissions as app_permissions

admin = "admin"
customer= "customer"

# Define the default roles allowed on the application
default_roles = [
    {
        "role": customer,
        "display_name": "Customer",
    },
    {
        "role": admin,
        "display_name": "Admin",
    },

]

# Define the default permissions for the default application roles
default_role_permissions = [
    {
        "role": customer,
        "permissions": [],
    },
    {
        "role": admin,
        "permissions":[
            app_permissions.CAN_CONFIRM_CUSTOMER_DEPOSIT,
            app_permissions.CAN_CONFIRM_CUSTOMER_LEVERAGE,
            app_permissions.CAN_CONFIRM_CUSTOMER_WITHDRAWAL,
            app_permissions.CAN_DELETE_CUSTOMER_KYC,
            app_permissions.CAN_DELETE_EARNING_HISTORY,
            app_permissions.CAN_DELETE_TRANSACTION_HISTORY,
            app_permissions.CAN_VERIFY_CUSTOMER_KYC,
            app_permissions.CAN_VIEW_EARNING_HISTORY,
            app_permissions.CAN_VIEW_TRANSACTION_HISTORY,
            app_permissions.CAN_VIEW_CUSTOMER_ACCOUNT,
            app_permissions.CAN_VIEW_CUSTOMER_BALANCE
            
        ]
    },
        
]
