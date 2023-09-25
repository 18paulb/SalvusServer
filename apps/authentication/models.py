class User:
    def __init__(self, username, password, company_name, email):
        self.username = username
        self.password = password
        self.company_name = company_name
        self.email = email

    def __str__(self):
        return "Username: " + self.username + "\nPassword: " + self.password + "\nCompany Name: " + self.company_name + "\nEmail: " + self.email + "\n\n"

    def to_dict(self):
        return {
            'username': self.username,
            'password': self.password,
            'company_name': self.company_name,
            'email': self.email,
        }
