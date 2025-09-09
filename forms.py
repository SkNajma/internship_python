from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, IntegerField, PasswordField, DateField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional, NumberRange
from wtforms.widgets import TextArea

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()], render_kw={"class": "form-control"})
    password = PasswordField('Password', validators=[DataRequired()], render_kw={"class": "form-control"})

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=20)], render_kw={"class": "form-control"})
    email = StringField('Email', validators=[DataRequired(), Email()], render_kw={"class": "form-control"})
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=50)], render_kw={"class": "form-control"})
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=50)], render_kw={"class": "form-control"})
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)], render_kw={"class": "form-control"})
    password2 = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')], render_kw={"class": "form-control"})
    role = SelectField('Role', choices=[('job_seeker', 'Job Seeker'), ('employer', 'Employer')], validators=[DataRequired()], render_kw={"class": "form-select"})
    company_name = StringField('Company Name (For Employers)', validators=[Optional(), Length(max=100)], render_kw={"class": "form-control"})
    phone = StringField('Phone Number', validators=[Optional(), Length(max=20)], render_kw={"class": "form-control"})
    location = StringField('Location', validators=[Optional(), Length(max=100)], render_kw={"class": "form-control"})

class JobForm(FlaskForm):
    title = StringField('Job Title', validators=[DataRequired(), Length(max=200)], render_kw={"class": "form-control"})
    company = StringField('Company Name', validators=[DataRequired(), Length(max=100)], render_kw={"class": "form-control"})
    description = TextAreaField('Job Description', validators=[DataRequired()], render_kw={"class": "form-control", "rows": "6"})
    requirements = TextAreaField('Requirements', validators=[Optional()], render_kw={"class": "form-control", "rows": "4"})
    salary_min = IntegerField('Minimum Salary ($)', validators=[Optional(), NumberRange(min=0)], render_kw={"class": "form-control"})
    salary_max = IntegerField('Maximum Salary ($)', validators=[Optional(), NumberRange(min=0)], render_kw={"class": "form-control"})
    location = StringField('Location', validators=[DataRequired(), Length(max=100)], render_kw={"class": "form-control"})
    category = SelectField('Category', choices=[
        ('technology', 'Technology'),
        ('healthcare', 'Healthcare'),
        ('finance', 'Finance'),
        ('education', 'Education'),
        ('marketing', 'Marketing'),
        ('sales', 'Sales'),
        ('engineering', 'Engineering'),
        ('design', 'Design'),
        ('customer_service', 'Customer Service'),
        ('other', 'Other')
    ], validators=[DataRequired()], render_kw={"class": "form-select"})
    job_type = SelectField('Job Type', choices=[
        ('full-time', 'Full-time'),
        ('part-time', 'Part-time'),
        ('contract', 'Contract'),
        ('internship', 'Internship')
    ], validators=[DataRequired()], render_kw={"class": "form-select"})
    deadline = DateField('Application Deadline', validators=[Optional()], render_kw={"class": "form-control"})

class ApplicationForm(FlaskForm):
    cover_letter = TextAreaField('Cover Letter', validators=[DataRequired()], render_kw={"class": "form-control", "rows": "8"})
    resume_text = TextAreaField('Resume/CV (Text)', validators=[DataRequired()], render_kw={"class": "form-control", "rows": "10"})

class SearchForm(FlaskForm):
    keywords = StringField('Keywords', validators=[Optional()], render_kw={"class": "form-control", "placeholder": "Job title, company, or skills"})
    location = StringField('Location', validators=[Optional()], render_kw={"class": "form-control", "placeholder": "City, state, or country"})
    category = SelectField('Category', choices=[
        ('', 'All Categories'),
        ('technology', 'Technology'),
        ('healthcare', 'Healthcare'),
        ('finance', 'Finance'),
        ('education', 'Education'),
        ('marketing', 'Marketing'),
        ('sales', 'Sales'),
        ('engineering', 'Engineering'),
        ('design', 'Design'),
        ('customer_service', 'Customer Service'),
        ('other', 'Other')
    ], validators=[Optional()], render_kw={"class": "form-select"})
    job_type = SelectField('Job Type', choices=[
        ('', 'All Types'),
        ('full-time', 'Full-time'),
        ('part-time', 'Part-time'),
        ('contract', 'Contract'),
        ('internship', 'Internship')
    ], validators=[Optional()], render_kw={"class": "form-select"})