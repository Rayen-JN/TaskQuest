<div align="center">
<h1>TaskQuest</h1>
</div>

![Screenshot 2024-07-12 163140](https://github.com/user-attachments/assets/2d020eb9-e17c-47e1-84f4-b562465b9a39)

<div align="center">
<p>TaskQuest is a task management web application built with Flask, SQLAlchemy, and Flask-Login.</p>
</div>


## :blue_book: Introduction

TaskQuest is a comprehensive task management application designed to help users manage their tasks and projects effectively. With features like user authentication, role-based access control, and integration of motivational quotes and news, TaskQuest aims to streamline task management and provide a motivational boost.

## :open_file_folder: Installation

To set up TaskQuest locally, follow these steps:

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/your-username/TaskQuest.git

Navigate to the Project Directory:

bash

cd TaskQuest

Set Up a Virtual Environment:

bash

python -m venv venv

Activate the Virtual Environment:

    On Windows:

    bash

venv\Scripts\activate

On macOS/Linux:

bash

    source venv/bin/activate

Install Dependencies:

bash

pip install -r requirements.txt

Initialize the Database:

bash

flask db upgrade

Run the Application:

bash

    flask run

# :flashlight: Usage

Once the application is running, you can access it via http://127.0.0.1:5000. Use the login page to access your dashboard and manage tasks and projects. You can also register as a new user if you don’t have an account yet.
Contributing

Contributions are welcome! If you would like to contribute to TaskQuest, please follow these steps:

    Fork the repository.
    Create a new branch (git checkout -b feature/YourFeature).
    Make your changes.
    Commit your changes (git commit -am 'Add some feature').
    Push to the branch (git push origin feature/YourFeature).
    Create a new Pull Request.

# :bulb: Related Projects

    Flask: The web framework used for building TaskQuest.
    SQLAlchemy: The ORM for database operations.
    Flask-WTF: Integration of WTForms with Flask.
    Flask-Login: User session management.
    Flask-Bcrypt: Password hashing.

# :page_with_curl: Licensing

This project is licensed under the MIT License - see the LICENSE file for details.
# :sparkles: Features

    User authentication (register, login, logout)
    Role-based access control (user, admin)
    Dashboard displaying tasks and projects
    CRUD operations for tasks and projects
    User management (admin-only)
    Motivational quotes and news integration

:hotsprings: Technologies Used

    Flask: Web framework for building the application.
    SQLAlchemy: ORM for database operations.
    Flask-WTF: Integration of WTForms with Flask.
    Flask-Login: User session management.
    Flask-Bcrypt: Password hashing.
    HTML, CSS, JavaScript: Frontend technologies.


Feel free to customize any sections as needed!
