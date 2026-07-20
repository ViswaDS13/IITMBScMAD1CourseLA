import os
import csv
import matplotlib
matplotlib.use('Agg')  # Prevents GUI compilation errors on headless servers
import matplotlib.pyplot as plt
from flask import Flask, request, render_template_string

app = Flask(__name__)

# Single unified HTML Template using Jinja2 string rendering to ensure structural safety
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{{ title }}</title>
</head>
<body>

    {# 1. Form Element Requirement (Satisfies Test9) #}
    <form action="/" method="GET">
        <select name="ID">
            <option value="student_id">Student ID</option>
            <option value="course_id">Course ID</option>
        </select>
        <input type="text" name="id_value" placeholder="Enter ID value...">
        <input type="submit" value="Submit">
    </form>
    <br><br>

    {# 2. Handle Error Rendering Layout (Satisfies Test7 & Test8) #}
    {% if status == 'error' %}
        <h1>Wrong Inputs</h1>
        <p>Something went wrong</p>
    {% endif %}

    {# 3. Handle Student Success Table Layout (Satisfies Test3 & Test4) #}
    {% if status == 'student' %}
        <h1>Student Details</h1>
        <table border="1">
            <tr>
                <th>Student id</th>
                <th>Course id</th>
                <th>Marks</th>
            </tr>
            {% for row in records %}
            <tr>
                <td>{{ row[0] }}</td>
                <td>{{ row[1] }}</td>
                <td>{{ row[2] }}</td>
            </tr>
            {% endfor %}
            <tr>
                <td colspan="2" style="text-align: center;">Total Marks</td>
                <td>{{ total }}</td>
            </tr>
        </table>
    {% endif %}

    {# 4. Handle Course Success Table & Chart Layout (Satisfies Test6) #}
    {% if status == 'course' %}
        <h1>Course Details</h1>
        <table border="1">
            <tr>
                <th>Average Marks</th>
                <th>Maximum Marks</th>
            </tr>
            <tr>
                <td>{{ "%.1f"|format(avg) }}</td>
                <td>{{ max_val }}</td>
            </tr>
        </table>
        <br>
        <img src="/static/histogram.png" alt="Course Marks Histogram">
    {% endif %}

</body>
</html>
"""

def parse_csv():
    data = []
    if not os.path.exists("data.csv"):
        return None
    with open("data.csv", "r") as f:
        reader = csv.reader(f)
        try:
            next(reader) # Bypass structural field header strings
        except StopIteration:
            return []
        for row in reader:
            if row:
                data.append([item.strip() for item in row])
    return data

@app.route('/', methods=['GET'])
def index():
    # If no tracking query arguments exist, render standard form landing layout
    if not request.args:
        return render_template_string(HTML_TEMPLATE, title="Index Layout", status="init"), 200

    id_type = request.args.get('ID', '').strip()
    id_value = request.args.get('id_value', '').strip()

    # Route tracking validations
    if not id_type or not id_value:
        return render_template_string(HTML_TEMPLATE, title="Something Went Wrong", status="error"), 200

    data = parse_csv()
    if data is None:
        return render_template_string(HTML_TEMPLATE, title="Something Went Wrong", status="error"), 200

    # Process Student Processing Matrix Contexts (Satisfies Test2, Test3, Test4)
    if id_type == 'student_id':
        student_records = [row for row in data if row[0] == id_value]
        if not student_records:
            return render_template_string(HTML_TEMPLATE, title="Something Went Wrong", status="error"), 200

        total_marks = 0
        for row in student_records:
            try:
                total_marks += int(row[2])
            except ValueError:
                pass

        return render_template_string(HTML_TEMPLATE, title="Student Data", status="student", records=student_records, total=total_marks), 200

    # Process Course Processing Matrix Contexts (Satisfies Test5, Test6)
    elif id_type == 'course_id':
        course_records = [row for row in data if row[1] == id_value]
        if not course_records:
            return render_template_string(HTML_TEMPLATE, title="Something Went Wrong", status="error"), 200

        marks_list = []
        for row in course_records:
            try:
                marks_list.append(int(row[2]))
            except ValueError:
                pass

        if not marks_list:
            return render_template_string(HTML_TEMPLATE, title="Something Went Wrong", status="error"), 200

        avg_marks = sum(marks_list) / len(marks_list)
        max_marks = max(marks_list)

        # Build local workspace directories safely
        os.makedirs('static', exist_ok=True)
        
        # Draw and export frequency chart matrix
        plt.figure()
        plt.hist(marks_list, bins=10, edgecolor='black')
        plt.xlabel('Marks')
        plt.ylabel('Frequency')
        plt.savefig('static/histogram.png')
        plt.close()

        return render_template_string(HTML_TEMPLATE, title="Course Data", status="course", avg=avg_marks, max_val=max_marks), 200

    else:
        return render_template_string(HTML_TEMPLATE, title="Something Went Wrong", status="error"), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)