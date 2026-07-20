import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api, Resource

app = Flask(__name__)

# Mandatory Configuration Parameters
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///api_database.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
api = Api(app)

# ==================== DATABASE SCHEMAS ====================

class Course(db.Model):
    __tablename__ = 'course'
    course_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    course_name = db.Column(db.String, nullable=False)
    course_code = db.Column(db.String, unique=True, nullable=False)
    course_description = db.Column(db.String)

class Student(db.Model):
    __tablename__ = 'student'
    student_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    roll_number = db.Column(db.String, unique=True, nullable=False)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String)

class Enrollments(db.Model):
    __tablename__ = 'enrollments'
    enrollment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.student_id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.course_id'), nullable=False)

# ==================== HELPER SERIALIZERS ====================

def serialize_course(c):
    return {
        "course_id": c.course_id,
        "course_name": c.course_name,
        "course_code": c.course_code,
        "course_description": c.course_description or ""
    }

def serialize_student(s):
    return {
        "student_id": s.student_id,
        "first_name": s.first_name,
        "last_name": s.last_name or "",
        "roll_number": s.roll_number
    }

def serialize_enrollment(e):
    return {
        "enrollment_id": e.enrollment_id,
        "student_id": e.student_id,
        "course_id": e.course_id
    }

# ==================== RESTful RESOURCES ====================

class CourseAPI(Resource):
    def get(self, course_id):
        course = Course.query.get(course_id)
        if not course:
            return {"error_code": "COURSE_NOT_FOUND", "error_message": "Course not found"}, 404
        return jsonify(serialize_course(course))

    def put(self, course_id):
        course = Course.query.get(course_id)
        if not course:
            return {"error_code": "COURSE_NOT_FOUND", "error_message": "Course not found"}, 404
        
        data = request.get_json() or {}
        
        if 'course_name' in data and (data['course_name'] is None or str(data['course_name']).strip() == ""):
            return {"error_code": "COURSE001", "error_message": "Course Name is required"}, 400
        if 'course_code' in data and (data['course_code'] is None or str(data['course_code']).strip() == ""):
            return {"error_code": "COURSE002", "error_message": "Course Code is required"}, 400

        if 'course_name' in data:
            course.course_name = data['course_name']
        if 'course_code' in data:
            course.course_code = data['course_code']
        if 'course_description' in data:
            course.course_description = data['course_description']

        db.session.commit()
        return jsonify(serialize_course(course))

    def delete(self, course_id):
        course = Course.query.get(course_id)
        if not course:
            return {"error_code": "COURSE_NOT_FOUND", "error_message": "Course not found"}, 404
        
        Enrollments.query.filter_by(course_id=course_id).delete()
        db.session.delete(course)
        db.session.commit()
        return {}, 200


class CourseListAPI(Resource):
    def post(self):
        data = request.get_json() or {}
        
        if 'course_name' not in data or data['course_name'] is None or str(data['course_name']).strip() == "":
            return {"error_code": "COURSE001", "error_message": "Course Name is required"}, 400
        if 'course_code' not in data or data['course_code'] is None or str(data['course_code']).strip() == "":
            return {"error_code": "COURSE002", "error_message": "Course Code is required"}, 400

        existing = Course.query.filter_by(course_code=data['course_code']).first()
        if existing:
            return {"error_code": "COURSE_ALREADY_EXISTS", "error_message": "course_code already exist"}, 409

        new_course = Course(
            course_name=data['course_name'],
            course_code=data['course_code'],
            course_description=data.get('course_description', '')
        )
        db.session.add(new_course)
        db.session.commit()
        return serialize_course(new_course), 201


class StudentAPI(Resource):
    def get(self, student_id):
        student = Student.query.get(student_id)
        if not student:
            return {"error_code": "STUDENT_NOT_FOUND", "error_message": "Student not found"}, 404
        return jsonify(serialize_student(student))

    def put(self, student_id):
        student = Student.query.get(student_id)
        if not student:
            return {"error_code": "STUDENT_NOT_FOUND", "error_message": "Student not found"}, 404
        
        data = request.get_json() or {}
        
        if 'roll_number' in data and (data['roll_number'] is None or str(data['roll_number']).strip() == ""):
            return {"error_code": "STUDENT001", "error_message": "Roll Number required"}, 400
        if 'first_name' in data and (data['first_name'] is None or str(data['first_name']).strip() == ""):
            return {"error_code": "STUDENT002", "error_message": "First Name is required"}, 400

        if 'roll_number' in data:
            student.roll_number = data['roll_number']
        if 'first_name' in data:
            student.first_name = data['first_name']
        if 'last_name' in data:
            student.last_name = data['last_name']

        db.session.commit()
        return jsonify(serialize_student(student))

    def delete(self, student_id):
        student = Student.query.get(student_id)
        if not student:
            return {"error_code": "STUDENT_NOT_FOUND", "error_message": "Student not found"}, 404
        
        Enrollments.query.filter_by(student_id=student_id).delete()
        db.session.delete(student)
        db.session.commit()
        return {}, 200


class StudentListAPI(Resource):
    def post(self):
        data = request.get_json() or {}
        
        if 'roll_number' not in data or data['roll_number'] is None or str(data['roll_number']).strip() == "":
            return {"error_code": "STUDENT001", "error_message": "Roll Number required"}, 400
        if 'first_name' not in data or data['first_name'] is None or str(data['first_name']).strip() == "":
            return {"error_code": "STUDENT002", "error_message": "First Name is required"}, 400

        existing = Student.query.filter_by(roll_number=data['roll_number']).first()
        if existing:
            return {"error_code": "STUDENT_ALREADY_EXISTS", "error_message": "Student already exist"}, 409

        new_student = Student(
            roll_number=data['roll_number'],
            first_name=data['first_name'],
            last_name=data.get('last_name', '')
        )
        db.session.add(new_student)
        db.session.commit()
        return serialize_student(new_student), 201


class StudentEnrollmentAPI(Resource):
    def get(self, student_id):
        student = Student.query.get(student_id)
        if not student:
            return {"error_code": "ENROLLMENT002", "error_message": "Student does not exist."}, 404
        
        enrollments = Enrollments.query.filter_by(student_id=student_id).all()
        if not enrollments:
            return {"error_code": "NO_ENROLLMENTS", "error_message": "Student is not enrolled in any course"}, 404
            
        return jsonify([serialize_enrollment(e) for e in enrollments])

    def post(self, student_id):
        student = Student.query.get(student_id)
        if not student:
            return {"error_code": "ENROLLMENT002", "error_message": "Student does not exist."}, 404
            
        data = request.get_json() or {}
        course_id = data.get('course_id')
        
        course = Course.query.get(course_id)
        if not course:
            return {"error_code": "ENROLLMENT001", "error_message": "Course does not exist"}, 400

        # Check if enrollment already exists to protect consistency
        existing = Enrollments.query.filter_by(student_id=student_id, course_id=course_id).first()
        if not existing:
            new_enrollment = Enrollments(student_id=student_id, course_id=course_id)
            db.session.add(new_enrollment)
            db.session.commit()

        all_enrollments = Enrollments.query.filter_by(student_id=student_id).all()
        return jsonify([serialize_enrollment(e) for e in all_enrollments]), 201


class EnrollmentDeleteAPI(Resource):
    def delete(self, student_id, course_id):
        student = Student.query.get(student_id)
        course = Course.query.get(course_id)
        
        if not student:
            return {"error_code": "ENROLLMENT002", "error_message": "Student does not exist."}, 400
        if not course:
            return {"error_code": "ENROLLMENT001", "error_message": "Course does not exist"}, 400
            
        enrollment = Enrollments.query.filter_by(student_id=student_id, course_id=course_id).first()
        if not enrollment:
            return {"error_code": "ENROLLMENT_NOT_FOUND", "error_message": "Enrollment for the student not found"}, 404
            
        db.session.delete(enrollment)
        db.session.commit()
        return {}, 200

# ==================== MAP ROUTING PATHS ====================

api.add_resource(CourseListAPI, '/api/course')
api.add_resource(CourseAPI, '/api/course/<int:course_id>')
api.add_resource(StudentListAPI, '/api/student')
api.add_resource(StudentAPI, '/api/student/<int:student_id>')
api.add_resource(StudentEnrollmentAPI, '/api/student/<int:student_id>/course')
api.add_resource(EnrollmentDeleteAPI, '/api/student/<int:student_id>/course/<int:course_id>')

if __name__ == '__main__':
    app.run(debug=True)