from app import db, User

user = User.query.filter_by(username='admin').first()

if user:
    user.role = 'admin'
    db.session.commit()
    print(f"Role 'admin' assigned to user '{user.username}' successfully.")
else:
    print("User not found.")
