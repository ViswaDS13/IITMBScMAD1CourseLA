import sys
import csv
import matplotlib.pyplot as plt

def generate_error_html():
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Something Went Wrong</title>
</head>
<body>
    <h1>Wrong Inputs</h1>
    <p>Something went wrong</p>
</body>
</html>"""
    with open("output.html", "w") as f:
        f.write(html_content)

def main():
    # Must have exactly 3 arguments (script name, flag, parameter ID)
    if len(sys.argv) != 3:
        generate_error_html()
        return

    # Normalize flag input (removes hyphens and spaces, converts to lowercase)
    flag = sys.argv[1].strip().replace('-', '').lower()
    search_id = sys.argv[2].strip()

    if flag not in ['s', 'c']:
        generate_error_html()
        return

    data = []
    try:
        # Use exact name "data.csv" relative path without directories
        with open("data.csv", "r") as f:
            reader = csv.reader(f)
            headers = [h.strip() for h in next(reader)]
            
            for row in reader:
                if row:
                    data.append([item.strip() for item in row])
    except FileNotFoundError:
        generate_error_html()
        return

    # Handle Student Flag
    if flag == 's':
        student_records = [row for row in data if row[0] == search_id]
        if not student_records:
            generate_error_html()
            return

        total_marks = 0
        table_rows = ""
        for row in student_records:
            try:
                mark_val = int(row[2])
                total_marks += mark_val
            except ValueError:
                mark_val = 0
            table_rows += f"        <tr><td>{row[0]}</td><td>{row[1]}</td><td>{mark_val}</td></tr>\n"

        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Student Data</title>
</head>
<body>
    <h1>Student Details</h1>
    <table border="1">
        <tr>
            <th>Student id</th>
            <th>Course id</th>
            <th>Marks</th>
        </tr>
{table_rows}        <tr>
            <td colspan="2" style="text-align: center;">Total Marks</td>
            <td>{total_marks}</td>
        </tr>
    </table>
</body>
</html>"""

        with open("output.html", "w") as f:
            f.write(html_content)

    # Handle Course Flag
    elif flag == 'c':
        course_records = [row for row in data if row[1] == search_id]
        if not course_records:
            generate_error_html()
            return

        marks_list = []
        for row in course_records:
            try:
                marks_list.append(int(row[2]))
            except ValueError:
                pass

        if not marks_list:
            generate_error_html()
            return

        avg_marks = sum(marks_list) / len(marks_list)
        max_marks = max(marks_list)

        # Generate Histogram
        plt.figure()
        plt.hist(marks_list, bins=10, edgecolor='black')
        plt.xlabel('Marks')
        plt.ylabel('Frequency')
        plt.savefig('histogram.png')
        plt.close()

        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Course Data</title>
</head>
<body>
    <h1>Course Details</h1>
    <table border="1">
        <tr>
            <th>Average Marks</th>
            <th>Maximum Marks</th>
        </tr>
        <tr>
            <td>{avg_marks:.1f}</td>
            <td>{max_marks}</td>
        </tr>
    </table>
    <br>
    <img src="histogram.png" alt="Course Marks Histogram">
</body>
</html>"""

        with open("output.html", "w") as f:
            f.write(html_content)

if __name__ == "__main__":
    main()