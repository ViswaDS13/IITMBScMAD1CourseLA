import os
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Mandatory Database Settings
current_dir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ==================== MODELS ====================

class Student(db.Model):
    __tablename__ = 'student'
    student_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    roll_number = db.Column(db.String, unique=True, nullable=False)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String)

class Course(db.Model):
    __tablename__ = 'course'
    course_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    course_code = db.Column(db.String, unique=True, nullable=False)
    course_name = db.Column(db.String, nullable=False)
    course_description = db.Column(db.String)

class Enrollments(db.Model):
    __tablename__ = 'enrollments'
    enrollment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    estudent_id = db.Column(db.Integer, db.ForeignKey('student.student_id'), nullable=False)
    ecourse_id = db.Column(db.Integer, db.ForeignKey('course.course_id'), nullable=False)

# ==================== CONTROLLERS ====================

@app.route('/', methods=['GET'])
def index():
    students = Student.query.all()
    return render_template('index.html', students=students), 200

@app.route('/student/create', methods=['GET', 'POST'])
def create_student():
    if request.method == 'GET':
        return render_template('app_student.html'), 200
    
    if request.method == 'POST':
        roll = request.form.get('roll')
        f_name = request.form.get('f_name')
        l_name = request.form.get('l_name')
        selected_courses = request.form.getlist('courses')  # Expecting ['course_1', 'course_2', ...]

        # Validation for unique constraint
        existing_student = Student.query.filter_by(roll_number=roll).first()
        if existing_student:
            return render_template('error.html'), 200

        # Commit student first
        new_student = Student(roll_number=roll, first_name=f_name, last_name=l_name)
        db.session.add(new_student)
        db.session.commit()

        # Parse and match selected courses
        for course_val in selected_courses:
            try:
                # Extract trailing integer index digit out of 'course_X' format
                c_idx = int(course_val.split('_')[1]) 
                enrollment = Enrollments(estudent_id=new_student.student_id, ecourse_id=c_idx)
                db.session.add(enrollment)
            except (IndexError, ValueError):
                continue
        
        db.session.commit()
        # Explicitly return index page template with 200 OK code instead of 302 redirect
        return render_template('index.html', students=Student.query.all()), 200

@app.route('/student/<int:student_id>/update', methods=['GET', 'POST'])
def update_student(student_id):
    student = Student.query.get_or_404(student_id)
    
    if request.method == 'GET':
        current_enrollments = Enrollments.query.filter_by(estudent_id=student_id).all()
        enrolled_course_ids = [e.ecourse_id for e in current_enrollments]
        return render_template('update_student.html', student=student, enrolled_course_ids=enrolled_course_ids), 200
    
    if request.method == 'POST':
        student.first_name = request.form.get('f_name')
        student.last_name = request.form.get('l_name')

        # Flush active course records
        Enrollments.query.filter_by(estudent_id=student_id).delete()

        selected_courses = request.form.getlist('courses')
        for course_val in selected_courses:
            try:
                c_idx = int(course_val.split('_')[1])
                enrollment = Enrollments(estudent_id=student_id, ecourse_id=c_idx)
                db.session.add(enrollment)
            except (IndexError, ValueError):
                continue
        
        db.session.commit()
        return render_template('index.html', students=Student.query.all()), 200

@app.route('/student/<int:student_id>/delete', methods=['GET'])
def delete_student(student_id):
    student = Student.query.get_or_404(student_id)
    Enrollments.query.filter_by(estudent_id=student_id).delete()
    db.session.delete(student)
    db.session.commit()
    return render_template('index.html', students=Student.query.all()), 200

@app.route('/student/<int:student_id>', methods=['GET'])
def student_details(student_id):
    student = Student.query.get_or_404(student_id)
    enrollments = db.session.query(Course).\
        join(Enrollments, Course.course_id == Enrollments.ecourse_id).\
        filter(Enrollments.estudent_id == student_id).all()
        
    return render_template('student_details.html', student=student, enrollments=enrollments), 200

if __name__ == '__main__':
    app.run(debug=True)