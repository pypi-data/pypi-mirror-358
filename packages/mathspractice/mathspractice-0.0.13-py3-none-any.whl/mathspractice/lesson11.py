import math
import random
import time
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from typing import Tuple

from flask import Blueprint, render_template, request, flash, url_for

from .stats import Statistics

bp = Blueprint('lesson11', __name__)

@bp.route('/')
def index():
    statistics = Statistics()
    return render_template(
        'lesson11/index.html',
        statistics=statistics,
    )


@bp.route('/tips', methods=['GET', 'POST'])
def tips():
    lesson = 'lesson11'
    section = 'tips'
    choices = '1'
    return serve(lesson=lesson, section=section, choices=choices)


@bp.route('/discount', methods=['GET', 'POST'])
def discount():
    lesson = 'lesson11'
    section = 'discount'
    choices = '2,3,4'
    return serve(lesson=lesson, section=section, choices=choices)


@bp.route('/income_tax', methods=['GET', 'POST'])
def income_tax():
    lesson = 'lesson11'
    section = 'income_tax'
    choices = '5'
    return serve(lesson=lesson, section=section, choices=choices)


def serve(lesson: str, section: str, choices: str):
    template = f'{lesson}/{section}.html'
    form_url = url_for(f'{lesson}.{section}')
    explain = []
    when = time.time()
    statistics = Statistics()
    stats = statistics.get_stats(lesson, section)
    if request.method == 'GET':
        max_value = int(math.pow(10, 4 + stats['correct'] // 20))
        which, problem, first, second = determine_problem(choices, max_value)
        attempt = 0
    else:
        first = Decimal(request.form.get('first'))
        second = Decimal(request.form.get('second'))
        problem = request.form.get('problem')
        which = int(request.form.get('which'))
        attempt = int(request.form.get('attempt'))
        try:
            answer = request.form.get('answer')
            if not answer:
                raise ValueError('Sorry. You needed to provide an answer. Please try again.')
            answer = answer.strip()
            if answer.startswith('$'):
                answer = answer[1:]
            answer = Decimal(answer).quantize(Decimal('0.01'))
            now = float(request.form.get('now'))
            elapsed = when - now
            real_answer, explain = calculate_answer(which, first, second)
            stats['seconds'] += elapsed
            if answer == real_answer:
                flash(f"Correct. Well done! ${real_answer} is correct.", category='correct')
                stats['correct'] += 1
                explain = []
                max_value = int(math.pow(10, 4 + stats['correct'] // 20))
                which, problem, first, second = determine_problem(choices, max_value)
                attempt = 0
            else:
                if attempt < 3:
                    flash(f"Incorrect. I'm sorry but ${answer} is not correct. Please try again", category='incorrect')
                    attempt += 1
                else:
                    flash(f"Incorrect. I'm sorry but ${answer} is not correct. The correct answer is ${real_answer}", category='incorrect')
                    max_value = int(math.pow(10, 4 + stats['correct'] // 20))
                    which, problem, first, second = determine_problem(choices, max_value)
                    attempt = 0
                    explain = []
                stats['incorrect'] += 1
            statistics.save()
        except InvalidOperation:
            answer = request.form.get('answer')
            flash(f'Sorry, I was expecting a number and not "{answer}"', category='error')
        except Exception as e:
            flash(str(e), category='error')
    now = int(time.time())
    return render_template(
        template,
        lesson=lesson, section=section,
        first=first, second=second,
        which=which, problem=problem,
        now=now, statistics=statistics,
        explain=explain, attempt=attempt,
        form_url=form_url,
    )

def determine_problem(choices: str, max_value: int) -> Tuple[int, str, Decimal, Decimal]:
    which = int(random.choice(choices.split(',')))
    if which == 1:
        first = Decimal(random.randint(10, 50))
        second = Decimal(random.randint(1, max_value)) / Decimal(100)
        problem = f'What is an {first}% tip on a ${second} restaurant bill?'
    elif which == 2:
        what = random.choice([('dealer', 'car'), ('agent', 'house')])
        first = Decimal(random.randint(1, max_value))
        second = Decimal(random.randint(10, 50))
        problem = (f'The original price of a {what[1]} was ${first}. '
                   f'Then, the {what[0]} decided to give a {second}% discount off the price of the {what[1]}. '
                   f'What is the price of the {what[1]} now?')
    elif which == 3:
        what = random.choice(['electric', 'gas', 'phone', 'water'])
        first = Decimal(random.randint(1, max_value)) / Decimal(100)
        second = Decimal(random.randint(5, 50))
        problem = (f"Last month’s {what} bill was ${first}. "
                   f"Then, the company decided to give a {second}% discount to its customers. "
                   f"How much is the bill now?")
    elif which == 4:
        what = random.choice([
            ('restaurant', 'students', 'lunch'),
            ('dry cleaners', 'office workers', 'laundry'),
            ('golf club', 'players', 'golfing')
        ])
        first = Decimal(random.randint(1, max_value)) / Decimal(100)
        second = Decimal(random.randint(5, 20))
        problem = (f"A {what[0]} offers a {second}% discount to all {what[1]}, "
                   f"including your friend. Their recent {what[2]} bill "
                   f"should have cost ${first}. "
                   f"What was the actual cost once the {second}% discount was taken?")
    elif which == 5:
        first = Decimal(random.randint(40, 180)) / Decimal(4)
        second = Decimal(random.randint(1, max_value)) * Decimal(10)
        problem = (f"The federal income tax is {first}%. "
                   f"You earned ${second:,} last year. "
                   f"How much tax will you have to pay?")
    else:
        problem=''
        first = Decimal(0)
        second = Decimal(0)
    return which, problem, first, second


def calculate_answer(
        which: int,
        first: Decimal,
        second: Decimal
) -> Tuple[Decimal, list[str]]:
    explain = []
    answer = Decimal(0)
    if which == 1:
        answer = first * second / Decimal(100)
        explain = [
            f'We calculate {first:,} times {second:,} divided by 100',
            f'Remember to divide by 100 you simply move the decimal place two places to the left.',
        ]
    if which in (2, 3, 4):
        answer = first - first * second / Decimal(100)
        explain = [
            f'We calculate the discount amount by multiplying {first:,} by {second:,} divided by 100',
            f'We calculate the actual cost by subtracting the discount amount from {first:,}',
            f'Remember to divide by 100 you simply move the decimal place two places to the left.',
        ]
    if which == 5:
        answer = second * first / Decimal(100)
        explain = [
            f'We calculate {second:,} times {first:,} divided by 100',
            f'Remember to divide by 100 you simply move the decimal place two places to the left.',
        ]
    answer = answer.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    explain.extend([
        f'We round the answer to the nearest cent.',
        f'Rounding down if the fractional amount is less than 0.5 cents',
        f'Rounding up if the fractional amount is 0.5 cents or greater',
    ])
    return answer, explain
