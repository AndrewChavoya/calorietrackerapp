from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime, date

app = Flask(__name__)
app.secret_key = 'calorie-tracker-secret-123'

# ←←← THIS IS THE CORRECT FIX FOR YOUR CALORIE TRACKER ←←←
@app.context_processor
def inject_now():
    return {'now': datetime.now}   # ← NO parentheses! We pass the FUNCTION itself
# ←←← END OF FIX ←←←

# Your existing storage
food_entries = []
daily_goal = 2000

def get_today_entries():
    today = date.today()
    return [e for e in food_entries if e['datetime'].date() == today]

def get_today_calories():
    return sum(e['calories'] for e in get_today_entries())

@app.context_processor
def inject_today_data():
    today_calories = get_today_calories()
    remaining = daily_goal - today_calories
    progress = min((today_calories / daily_goal) * 100, 100) if daily_goal > 0 else 0
    return {
        'today_calories': today_calories,
        'daily_goal': daily_goal,
        'remaining_calories': remaining if remaining > 0 else 0,
        'over_by': abs(remaining) if remaining < 0 else 0,
        'progress': progress
    }

@app.route('/')
def index():
    today_entries = sorted(get_today_entries(), key=lambda x: x['datetime'], reverse=True)
    return render_template('index.html', entries=today_entries, today=date.today())

@app.route('/log', methods=['GET', 'POST'])
def log_food():
    if request.method == 'POST':
        try:
            food = request.form['food'].strip()
            calories = int(request.form['calories'])
            datetime_str = request.form['datetime']

            if not food or calories <= 0:
                flash('Please enter a valid food name and calorie amount.', 'danger')
            else:
                entry = {
                    'food': food,
                    'calories': calories,
                    'datetime': datetime.fromisoformat(datetime_str)
                }
                food_entries.append(entry)
                flash(f'Logged "{food}" – {calories} cal', 'success')
                return redirect(url_for('log_food'))
        except Exception as e:
            flash('Invalid date/time or calories.', 'danger')

    # Sort all entries by date/time (newest first)
    all_entries = sorted(food_entries, key=lambda x: x['datetime'], reverse=True)
    return render_template('log.html', entries=all_entries[:50])  # Show last 50

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    global daily_goal
    if request.method == 'POST':
        try:
            goal = int(request.form['goal'])
            if goal > 0:
                daily_goal = goal
                flash(f'Daily calorie goal updated to {goal}!', 'success')
            else:
                flash('Goal must be a positive number.', 'danger')
        except:
            flash('Invalid goal value.', 'danger')
        return redirect(url_for('settings'))

    return render_template('settings.html', current_goal=daily_goal)

if __name__ == '__main__':
    app.run(debug=True)