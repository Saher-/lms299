# -*- coding: utf-8 -*-
# try something like
@auth.requires_login()
def manage_grades():
    section_id=request.args(0, cast=int)

    if not (is_user_teacher(section_id) or auth.user.is_administrator):
        session.flash = 'Not authorized'
        redirect(URL('student',args=section_id))

    redirect(URL('teacher',args=section_id))
    return dict()

@auth.requires_login()
def teacher():
    section_id = request.args(0, cast=int)
    if not (is_user_teacher(section_id)):
        session.flash = 'Not authorized'
        redirect(URL('student',args=section_id))

    response.files.insert(0,URL('static','js/jquery.js'))
    response.files.insert(0,URL('static','js/jquery.handsontable.full.js'))
    response.files.insert(0,URL('static','css/jquery.handsontable.full.css'))
    response.files.insert(0,URL('static','css/grading.css'))

    session.flash = 'Welcome Teacher'
    students = get_all_students(section_id)

    for st in students:
        st.hws = get_grades_student(section_id, st.auth_user.id)
        st.final = get_final_grade(section_id, st.auth_user.id).first()


    import numpy
    hws = get_homework_section(section_id)
    stat=[]
    for hw in hws:
        s = convert_to_list(get_assignment_by_homework(section_id, hw.id))
        if s:
            stat.append({
                'min':numpy.min(s),
                'max':numpy.max(s),
                'average':numpy.average(s),
                'median':numpy.median(s),
                'mean':numpy.mean(s),
                'sum':numpy.sum(s),
                'cov':numpy.cov(s),
                'var':numpy.var(s),
                'std':numpy.std(s),
                'hw':hw
            })
    return dict(section_id=section_id, users=students, names=students.first().hws, stat=stat)

@auth.requires_login()
def student():
    session.flash = "Welcome %s %s" % (auth.user.first_name, auth.user.last_name)
    section_id = request.args(0, cast=int)
    section = db.course_section(section_id)
    student_grades = get_grades_student(section_id, auth.user.id)
    return dict(student_grades=student_grades, section=section)

@auth.requires_login()
def savedata():
    import gluon.contrib.simplejson

    students = gluon.contrib.simplejson.loads(request.body.read())
    section_id = request.args(0, cast=int)
    hws = get_homework_section(section_id)
    for student in students['data']:
        id=student['id']
        final = student['final']
        comment = student['comment']
        db.course_grade.update_or_insert((db.course_grade.section_id==section_id) &(db.course_grade.auth_user==id),section_id=section_id,auth_user=id,grade=final,teacher_comment=comment)

        for hw in hws:
            homeworks = student["hw"]
            grade = homeworks[str(hw.id)]

            if grade > -1:
                db.assignment_grade.update_or_insert((db.assignment_grade.section_id==section_id)&(db.assignment_grade.assignment_id==hw.id)&(db.assignment_grade.user_id==id),section_id=section_id, assignment_id=hw.id, user_id=id, grade=grade, assignment_comment='')
            pass

          #  db.assignment_grade.update_or_insert((db.assignment_grade.section_id==1)& (db.assignment_grade.assignment_id==1)& (db.assignment_grade.user_id==id), grade=10, assignment_comment='')
    session.flash = "Data Saved"
    return response.json(students)


@auth.requires_login()
def addhw():
    grid = SQLFORM.smartgrid(db.homework)
    return dict(grid=grid)

@auth.requires_login()
def addgrade():
    grid = SQLFORM.smartgrid(db.assignment_grade)
    return dict(grid=grid)

