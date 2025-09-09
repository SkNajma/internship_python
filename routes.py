from datetime import datetime
from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy import or_, and_
from app import app, db
from models import User, Job, Application
from forms import LoginForm, RegisterForm, JobForm, ApplicationForm, SearchForm

@app.route('/')
def index():
    # Get recent jobs for the homepage
    recent_jobs = Job.query.filter_by(is_active=True).order_by(Job.posted_date.desc()).limit(6).all()
    job_count = Job.query.filter_by(is_active=True).count()
    return render_template('index.html', recent_jobs=recent_jobs, job_count=job_count)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            if not user.is_active:
                flash('Your account has been deactivated. Please contact support.', 'error')
                return render_template('login.html', form=form)
            
            login_user(user)
            next_page = request.args.get('next')
            flash(f'Welcome back, {user.first_name}!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = RegisterForm()
    if form.validate_on_submit():
        # Check if username or email already exists
        existing_user = User.query.filter(
            or_(User.username == form.username.data, User.email == form.email.data)
        ).first()
        
        if existing_user:
            flash('Username or email already exists', 'error')
            return render_template('register.html', form=form)
        
        user = User(
            username=form.username.data,
            email=form.email.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            role=form.role.data,
            company_name=form.company_name.data if form.company_name.data else None,
            phone=form.phone.data if form.phone.data else None,
            location=form.location.data if form.location.data else None
        )
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'job_seeker':
        # Get recent applications for job seekers
        recent_applications = Application.query.filter_by(user_id=current_user.id)\
            .order_by(Application.applied_date.desc()).limit(5).all()
        return render_template('dashboard.html', recent_applications=recent_applications)
    
    elif current_user.role == 'employer':
        # Get posted jobs and recent applications for employers
        posted_jobs = Job.query.filter_by(employer_id=current_user.id)\
            .order_by(Job.posted_date.desc()).limit(5).all()
        recent_applications = Application.query.join(Job)\
            .filter(Job.employer_id == current_user.id)\
            .order_by(Application.applied_date.desc()).limit(5).all()
        return render_template('dashboard.html', posted_jobs=posted_jobs, recent_applications=recent_applications)
    
    elif current_user.role == 'admin':
        # Admin dashboard with statistics
        total_users = User.query.count()
        total_jobs = Job.query.count()
        total_applications = Application.query.count()
        recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
        return render_template('dashboard.html', 
                               total_users=total_users, 
                               total_jobs=total_jobs, 
                               total_applications=total_applications,
                               recent_users=recent_users)
    
    return render_template('dashboard.html')

@app.route('/post-job', methods=['GET', 'POST'])
@login_required
def post_job():
    if current_user.role not in ['employer', 'admin']:
        flash('You need to be an employer to post jobs.', 'error')
        return redirect(url_for('dashboard'))
    
    form = JobForm()
    if form.validate_on_submit():
        job = Job(
            title=form.title.data,
            company=form.company.data,
            description=form.description.data,
            requirements=form.requirements.data,
            salary_min=form.salary_min.data,
            salary_max=form.salary_max.data,
            location=form.location.data,
            category=form.category.data,
            job_type=form.job_type.data,
            deadline=form.deadline.data,
            employer_id=current_user.id
        )
        
        db.session.add(job)
        db.session.commit()
        
        flash('Job posted successfully!', 'success')
        return redirect(url_for('my_jobs'))
    
    return render_template('post_job.html', form=form)

@app.route('/jobs')
def search_jobs():
    form = SearchForm(request.args)
    
    # Build query based on search criteria
    query = Job.query.filter_by(is_active=True)
    
    if form.keywords.data:
        query = query.filter(or_(
            Job.title.contains(form.keywords.data),
            Job.company.contains(form.keywords.data),
            Job.description.contains(form.keywords.data)
        ))
    
    if form.location.data:
        query = query.filter(Job.location.contains(form.location.data))
    
    if form.category.data:
        query = query.filter(Job.category == form.category.data)
    
    if form.job_type.data:
        query = query.filter(Job.job_type == form.job_type.data)
    
    # Pagination
    page = request.args.get('page', 1, type=int)
    jobs = query.order_by(Job.posted_date.desc()).paginate(
        page=page, per_page=10, error_out=False
    )
    
    return render_template('search_jobs.html', form=form, jobs=jobs)

@app.route('/job/<int:job_id>')
def job_detail(job_id):
    job = Job.query.get_or_404(job_id)
    
    # Check if current user has already applied (if logged in)
    has_applied = False
    user_application = None
    if current_user.is_authenticated:
        user_application = Application.query.filter_by(
            user_id=current_user.id, job_id=job_id
        ).first()
        has_applied = user_application is not None
    
    return render_template('job_detail.html', job=job, has_applied=has_applied, user_application=user_application)

@app.route('/apply/<int:job_id>', methods=['GET', 'POST'])
@login_required
def apply_job(job_id):
    if current_user.role != 'job_seeker':
        flash('Only job seekers can apply for jobs.', 'error')
        return redirect(url_for('job_detail', job_id=job_id))
    
    job = Job.query.get_or_404(job_id)
    
    # Check if already applied
    existing_application = Application.query.filter_by(
        user_id=current_user.id, job_id=job_id
    ).first()
    
    if existing_application:
        flash('You have already applied for this job.', 'info')
        return redirect(url_for('job_detail', job_id=job_id))
    
    form = ApplicationForm()
    if form.validate_on_submit():
        application = Application(
            user_id=current_user.id,
            job_id=job_id,
            cover_letter=form.cover_letter.data,
            resume_text=form.resume_text.data
        )
        
        db.session.add(application)
        db.session.commit()
        
        flash('Application submitted successfully!', 'success')
        return redirect(url_for('job_detail', job_id=job_id))
    
    return render_template('job_detail.html', job=job, form=form, applying=True)

@app.route('/my-jobs')
@login_required
def my_jobs():
    if current_user.role not in ['employer', 'admin']:
        flash('Access denied.', 'error')
        return redirect(url_for('dashboard'))
    
    page = request.args.get('page', 1, type=int)
    jobs = Job.query.filter_by(employer_id=current_user.id)\
        .order_by(Job.posted_date.desc())\
        .paginate(page=page, per_page=10, error_out=False)
    
    return render_template('my_jobs.html', jobs=jobs)

@app.route('/my-applications')
@login_required
def my_applications():
    if current_user.role != 'job_seeker':
        flash('Access denied.', 'error')
        return redirect(url_for('dashboard'))
    
    page = request.args.get('page', 1, type=int)
    applications = Application.query.filter_by(user_id=current_user.id)\
        .order_by(Application.applied_date.desc())\
        .paginate(page=page, per_page=10, error_out=False)
    
    return render_template('applications.html', applications=applications)

@app.route('/job/<int:job_id>/applications')
@login_required
def job_applications(job_id):
    job = Job.query.get_or_404(job_id)
    
    # Only job owner or admin can view applications
    if current_user.role != 'admin' and job.employer_id != current_user.id:
        flash('Access denied.', 'error')
        return redirect(url_for('dashboard'))
    
    page = request.args.get('page', 1, type=int)
    applications = Application.query.filter_by(job_id=job_id)\
        .order_by(Application.applied_date.desc())\
        .paginate(page=page, per_page=10, error_out=False)
    
    return render_template('applications.html', applications=applications, job=job)

@app.route('/application/<int:app_id>/update-status/<status>')
@login_required
def update_application_status(app_id, status):
    application = Application.query.get_or_404(app_id)
    job = application.job
    
    # Only job owner or admin can update status
    if current_user.role != 'admin' and job.employer_id != current_user.id:
        flash('Access denied.', 'error')
        return redirect(url_for('dashboard'))
    
    if status in ['pending', 'reviewed', 'accepted', 'rejected']:
        application.status = status
        application.reviewed_date = datetime.utcnow()
        db.session.commit()
        flash(f'Application status updated to {status}.', 'success')
    else:
        flash('Invalid status.', 'error')
    
    return redirect(url_for('job_applications', job_id=job.id))

@app.route('/admin')
@login_required
def admin_panel():
    if current_user.role != 'admin':
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('dashboard'))
    
    # Get statistics and recent data
    users = User.query.order_by(User.created_at.desc()).all()
    jobs = Job.query.order_by(Job.posted_date.desc()).all()
    applications = Application.query.order_by(Application.applied_date.desc()).limit(20).all()
    
    return render_template('admin.html', users=users, jobs=jobs, applications=applications)

@app.route('/admin/toggle-user-status/<int:user_id>')
@login_required
def toggle_user_status(user_id):
    if current_user.role != 'admin':
        flash('Access denied.', 'error')
        return redirect(url_for('dashboard'))
    
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('You cannot deactivate your own account.', 'error')
        return redirect(url_for('admin_panel'))
    
    user.is_active = not user.is_active
    db.session.commit()
    
    status = 'activated' if user.is_active else 'deactivated'
    flash(f'User {user.username} has been {status}.', 'success')
    return redirect(url_for('admin_panel'))

@app.route('/admin/toggle-job-status/<int:job_id>')
@login_required
def toggle_job_status(job_id):
    if current_user.role != 'admin':
        flash('Access denied.', 'error')
        return redirect(url_for('dashboard'))
    
    job = Job.query.get_or_404(job_id)
    job.is_active = not job.is_active
    db.session.commit()
    
    status = 'activated' if job.is_active else 'deactivated'
    flash(f'Job "{job.title}" has been {status}.', 'success')
    return redirect(url_for('admin_panel'))

@app.route('/edit-job/<int:job_id>', methods=['GET', 'POST'])
@login_required
def edit_job(job_id):
    job = Job.query.get_or_404(job_id)
    
    # Only job owner or admin can edit
    if current_user.role != 'admin' and job.employer_id != current_user.id:
        flash('Access denied.', 'error')
        return redirect(url_for('dashboard'))
    
    form = JobForm(obj=job)
    if form.validate_on_submit():
        form.populate_obj(job)
        db.session.commit()
        flash('Job updated successfully!', 'success')
        return redirect(url_for('my_jobs'))
    
    return render_template('post_job.html', form=form, job=job, editing=True)

@app.route('/delete-job/<int:job_id>')
@login_required
def delete_job(job_id):
    job = Job.query.get_or_404(job_id)
    
    # Only job owner or admin can delete
    if current_user.role != 'admin' and job.employer_id != current_user.id:
        flash('Access denied.', 'error')
        return redirect(url_for('dashboard'))
    
    db.session.delete(job)
    db.session.commit()
    flash('Job deleted successfully.', 'success')
    return redirect(url_for('my_jobs'))

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

# Context processor to make current year available in templates
@app.context_processor
def utility_processor():
    return dict(current_year=datetime.now().year)