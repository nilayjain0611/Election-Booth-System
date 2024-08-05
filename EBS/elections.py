# elections.py
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from .models import Election, Nominee, Voter
from . import db
from datetime import datetime

elections = Blueprint('elections', __name__)

@elections.route('/election-dashboard')
@login_required
def election_dashboard():
    ongoing_elections = Election.query.all()
    return render_template('election_dashboard.html', elections=ongoing_elections)

@elections.route('/create-nomination', methods=['GET', 'POST'])
@login_required
def create_nomination():
    if request.method == 'POST':
        # Extract form data
        election_title = request.form.get('election_title')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')

        # Convert string dates to datetime objects
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')

        # Create Election object
        election = Election(title=election_title, start_date=start_date, end_date=end_date)
        # Add nominees to the election
        for i in range(1, 11):
            name = request.form.get(f'name_{i}')
            usn = request.form.get(f'usn_{i}')
            post = request.form.get(f'post_{i}')
            bio = request.form.get(f'bio_{i}')

            if name and usn and post and bio:
                nominee = Nominee(name=name, usn=usn, post=post, bio=bio, election=election)
                election.nominees.append(nominee)

        try:
            # Commit changes to the database
            db.session.add(election)
            db.session.commit()

            flash('Election created successfully!', 'success')
            return redirect(url_for('elections.election_dashboard'))
        except Exception as e:
            # Handle database error
            db.session.rollback()
            flash(f'Error creating election: {str(e)}', 'danger')

    return render_template('create_nomination.html')
# elections.py
@elections.route('/elections/<int:election_id>', methods=['GET', 'POST'])
@login_required
def election_page(election_id):
    from .models import Vote

    # Retrieve the election and its nominees
    election = Election.query.get_or_404(election_id)
    nominees = Nominee.query.filter_by(election_id=election.id).all()

    # Check if the election has ended
    if datetime.now() > election.end_date:
        flash('This election has ended.', 'danger')
        return redirect(url_for('elections.election_dashboard'))

    # Check if the voter has already submitted the vote
    if current_user.has_voted(election_id):
        flash('You have already submitted your vote for this election.', 'danger')
        # return redirect(url_for('elections.election_dashboard'))

    if request.method == 'POST':
        # Get the selected nominee id from the form
        selected_nominee_id = request.form.get('nominee')

        print("Selected Nominee ID:", selected_nominee_id)  # Add this line for debugging

        if selected_nominee_id:
            try:
                # Check if the user has already voted for this post
                if current_user.has_voted_for_post(election_id, selected_nominee_id):
                    flash('You have already voted for this post.', 'danger')
                else:
                    # Create Vote record
                    vote = Vote(voter_id=current_user.id, nominee_id=selected_nominee_id)
                    db.session.add(vote)

                    # Update the vote count for the selected nominee
                    selected_nominee = Nominee.query.get(selected_nominee_id)
                    if selected_nominee:
                        selected_nominee.votes_count = (selected_nominee.votes_count or 0) + 1

                    # Commit changes to the database
                    db.session.commit()

                    flash('Vote submitted successfully!', 'success')
                    print('Vote submitted successfully!')  # Add this line for debugging

            except Exception as e:
                db.session.rollback()
                flash(f'Error submitting vote: {str(e)}', 'danger')
                print(f'Error submitting vote: {str(e)}', 'danger')

    return render_template('election_page.html', election=election, nominees=nominees, current_user=current_user)
