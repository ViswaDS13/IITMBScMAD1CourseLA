import json
from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api, Resource, reqparse, fields, marshal_with

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///api_database.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
api = Api(app)

# -----------------------------------------------------------------------------
# Database Models
# -----------------------------------------------------------------------------

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


class Enrollment(db.Model):
    __tablename__ = 'enrollment'
    enrollment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.student_id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.course_id'), nullable=False)

# -----------------------------------------------------------------------------
# Helper Functions & Formatting
# -----------------------------------------------------------------------------

def error_response(error_code, error_message, status_code=400):
    body = {
        "error_code": error_code,
        "error_message": error_message
    }
    return make_response(jsonify(body), status_code)


# -----------------------------------------------------------------------------
# Course Resources
# -----------------------------------------------------------------------------

class CourseAPI(Resource):
    def get(self, course_id):
        course = Course.query.get(course_id)
        if not course:
            return make_response("", 404)
        
        return {
            "course_id": course.course_id,
            "course_name": course.course_name,
            "course_code": course.course_code,
            "course_description": course.course_description
        }, 200

    def put(self, course_id):
        course = Course.query.get(course_id)
        if not course:
            return make_response("", 404)
            
        data = request.get_json(force=True, silent=True) or {}
        
        c_name = data.get('course_name')
        c_code = data.get('course_code')
        c_desc = data.get('course_description')

        if not c_name:
            return error_response("COURSE001", "Course Name is required", 400)
        if not c_code:
            return error_response("COURSE002", "Course Code is required", 400)

        course.course_name = c_name
        course.course_code = c_code
        course.course_description = c_desc
        db.session.commit()

        return {
            "course_id": course.course_id,
            "course_name": course.course_name,
            "course_code": course.course_code,
            "course_description": course.course_description
        }, 200

    def delete(self, course_id):
        course = Course.query.get(course_id)
        if not course:
            return make_response("", 404)
            
        # Delete associated enrollments first
        Enrollment.query.filter_by(course_id=course_id).delete()
        
        db.session.delete(course)
        db.session.commit()
        return "", 200


class CourseListAPI(Resource):
    def post(self):
        data = request.get_json(force=True, silent=True) or {}
        
        c_name = data.get('course_name')
        c_code = data.get('course_code')
        c_desc = data.get('course_description', '')

        if not c_name:
            return error_response("COURSE001", "Course Name is required", 400)
        if not c_code:
            return error_response("COURSE002", "Course Code is required", 400)

        # Check for existing course code uniqueness
        existing_course = Course.query.filter_by(course_code=c_code).first()
        if existing_course:
            return make_response("", 409)

        new_course = Course(
            course_name=c_name,
            course_code=c_code,
            course_description=c_desc
        )
        db.session.add(new_course)
        db.session.commit()

        return {
            "course_id": new_course.course_id,
            "course_name": new_course.course_name,
            "course_code": new_course.course_code,
            "course_description": new_course.course_description
        }, 201


# -----------------------------------------------------------------------------
# Student Resources
# -----------------------------------------------------------------------------

class StudentAPI(Resource):
    def get(self, student_id):
        student = Student.query.get(student_id)
        if not student:
            return make_response("", 404)
            
        return {
            "student_id": student.student_id,
            "roll_number": student.roll_number,
            "first_name": student.first_name,
            "last_name": student.last_name
        }, 200

    def put(self, student_id):
        student = Student.query.get(student_id)
        if not student:
            return make_response("", 404)

        data = request.get_json(force=True, silent=True) or {}
        
        roll_num = data.get('roll_number')
        f_name = data.get('first_name')
        l_name = data.get('last_name')

        if not roll_num:
            return error_response("STUDENT001", "Roll Number required", 400)
        if not f_name:
            return error_response("STUDENT002", "First Name is required", 400)

        student.roll_number = roll_num
        student.first_name = f_name
        student.last_name = l_name
        db.session.commit()

        return {
            "student_id": student.student_id,
            "roll_number": student.roll_number,
            "first_name": student.first_name,
            "last_name": student.last_name
        }, 200

    def delete(self, student_id):
        student = Student.query.get(student_id)
        if not student:
            return make_response("", 404)

        # Delete associated enrollments
        Enrollment.query.filter_by(student_id=student_id).delete()

        db.session.delete(student)
        db.session.commit()
        return "", 200


class StudentListAPI(Resource):
    def post(self):
        data = request.get_json(force=True, silent=True) or {}
        
        roll_num = data.get('roll_number')
        f_name = data.get('first_name')
        l_name = data.get('last_name', '')

        if not roll_num:
            return error_response("STUDENT001", "Roll Number required", 400)
        if not f_name:
            return error_response("STUDENT002", "First Name is required", 400)

        existing_student = Student.query.filter_by(roll_number=roll_num).first()
        if existing_student:
            return make_response("", 409)

        new_student = Student(
            roll_number=roll_num,
            first_name=f_name,
            last_name=l_name
        )
        db.session.add(new_student)
        db.session.commit()

        return {
            "student_id": new_student.student_id,
            "roll_number": new_student.roll_number,
            "first_name": new_student.first_name,
            "last_name": new_student.last_name
        }, 201


# -----------------------------------------------------------------------------
# Enrollment Resources
# -----------------------------------------------------------------------------

class StudentCourseAPI(Resource):
    def get(self, student_id):
        student = Student.query.get(student_id)
        if not student:
            return error_response("ENROLLMENT002", "Student does not exist.", 400)

        enrollments = Enrollment.query.filter_by(student_id=student_id).all()
        if not enrollments:
            return make_response("", 404)

        result = []
        for e in enrollments:
            course = Course.query.get(e.course_id)
            if course:
                result.append({
                    "course_id": course.course_id,
                    "course_name": course.course_name,
                    "course_code": course.course_code,
                    "course_description": course.course_description
                })

        return result, 200

    def post(self, student_id):
        student = Student.query.get(student_id)
        if not student:
            return error_response("ENROLLMENT002", "Student does not exist", 400)

        data = request.get_json(force=True, silent=True) or {}
        c_id = data.get('course_id')

        if not c_id:
            return error_response("ENROLLMENT001", "Course does not exist", 400)

        course = Course.query.get(c_id)
        if not course:
            return error_response("ENROLLMENT001", "Course does not exist", 400)

        # Create enrollment if it doesn't already exist
        existing = Enrollment.query.filter_by(student_id=student_id, course_id=c_id).first()
        if not existing:
            new_enrollment = Enrollment(student_id=student_id, course_id=c_id)
            db.session.add(new_enrollment)
            db.session.commit()

        # Fetch all enrolled courses for the response
        all_enrollments = Enrollment.query.filter_by(student_id=student_id).all()
        result = []
        for e in all_enrollments:
            c = Course.query.get(e.course_id)
            if c:
                result.append({
                    "course_id": c.course_id,
                    "course_name": c.course_name,
                    "course_code": c.course_code,
                    "course_description": c.course_description
                })

        return result, 201


class StudentCourseDeleteAPI(Resource):
    def delete(self, student_id, course_id):
        student = Student.query.get(student_id)
        if not student:
            return error_response("ENROLLMENT002", "Student does not exist", 400)

        course = Course.query.get(course_id)
        if not course:
            return error_response("ENROLLMENT001", "Course does not exist", 400)

        enrollment = Enrollment.query.filter_by(student_id=student_id, course_id=course_id).first()
        if not enrollment:
            return make_response("", 404)

        db.session.delete(enrollment)
        db.session.commit()

        return "", 200


# -----------------------------------------------------------------------------
# API Endpoints Routing
# -----------------------------------------------------------------------------

api.add_resource(CourseAPI, '/api/course/<int:course_id>')
api.add_resource(CourseListAPI, '/api/course')

api.add_resource(StudentAPI, '/api/student/<int:student_id>')
api.add_resource(StudentListAPI, '/api/student')

api.add_resource(StudentCourseAPI, '/api/student/<int:student_id>/course')
api.add_resource(StudentCourseDeleteAPI, '/api/student/<int:student_id>/course/<int:course_id>')


if __name__ == '__main__':
    app.run()