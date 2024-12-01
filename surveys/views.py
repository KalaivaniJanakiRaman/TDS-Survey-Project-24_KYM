from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.db.models import Count
from .models import Survey, Question, Option, Response
from .forms import CustomUserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Max
from .models import Profile 

import logging
from django.db import IntegrityError
logger = logging.getLogger(__name__)

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        print(dir(form))
        print(form.error_class)
        print(form.errors.as_data())
        print(form.error_messages)
        print(form.has_error)
        if form.is_valid():
            print(form.is_valid())
            try:
                user = form.save()
                role = form.cleaned_data.get('role')
                
                # Print form data for debugging
                print(f"Form data: {form.cleaned_data}")
                
                # Create a new Profile instance for the user
                profile = Profile.objects.create(user=user, role=role)
                
                login(request, user)
                if role == 'creator':
                    return redirect('creator_dashboard')
                else:
                    return redirect('taker_dashboard')
            except IntegrityError as e:
                # Log the error
                logger.error(f"IntegrityError during registration: {str(e)}")
                # Print the error for immediate visibility in the console
                print(f"IntegrityError: {str(e)}")
                # Add error message to the form
                form.add_error(None, f"An error occurred during registration: {str(e)}")
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})

from django.contrib import messages
from django.urls import reverse

def login_view(request):
    print(request)
    if request.method == 'POST':
        print("POST:", request.method)
        
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            
            print(form.error_class)
            print(form.errors.as_data())
            print(form.error_messages)
            print(form.has_error)
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                print("user:")
                print(user)
                messages.success(request, f"Welcome back, {username}!")
                if user.profile.role == 'creator':
                    return redirect(reverse('creator_dashboard'))
                else:
                    return redirect(reverse('taker_dashboard'))
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

from django.contrib.auth.decorators import login_required
from django.db.models import Count
from .models import Survey, Response
@login_required
def creator_dashboard(request):
    if request.user.profile.role != 'creator':
        return redirect('taker_dashboard')
    surveys = Survey.objects.filter(creator=request.user).annotate(
        response_count=Count('response')
    )
    context = {
        'draft_surveys': surveys.filter(status='draft'),
        'published_surveys': surveys.filter(status='published'),
        'closed_surveys': surveys.filter(status='closed'),
        'republished_surveys': surveys.filter(status='republished'),
        'total_surveys': surveys.count(),
    }
    return render(request, 'creator_dashboard.html', context)

# for taker dashboard
@login_required
def taker_dashboard(request):
    if request.user.profile.role != 'taker':
        return redirect('creator_dashboard')
    
    available_surveys = Survey.objects.filter(status__in=['published', 'republished'])
    
    completed_surveys = Survey.objects.filter(
        response__user=request.user
    ).distinct().annotate(
        completion_date=Max('response__created_at')
    ).values('id', 'title', 'status', 'completion_date')
    
    context = {
        'available_surveys': available_surveys,
        'completed_surveys': completed_surveys,
    }
    return render(request, 'taker_dashboard.html', context)

# create_survey
@login_required
def create_survey(request):
    if request.user.profile.role != 'creator':
        return HttpResponseForbidden("Only Survey Creators can create surveys.")
    if request.method == 'POST':
        print("Form data:", request.POST)
        survey = Survey.objects.create(
            title=request.POST.get('title'),
            description=request.POST.get('description'),
            creator=request.user,
            status='draft'
        )
        question_texts = request.POST.getlist('question_text[]')
        question_types = request.POST.getlist('question_type[]')
        options = request.POST.getlist('options[]')

        print("Questions:", question_texts)
        print("Question Types:", question_types)
        print("Options:", options)
        print("question_texts:", question_texts)
        print(len(options))
        print(len(question_texts))
        for i, q_text in enumerate(question_texts):
            question = Question.objects.create(
                survey=survey,
                text=q_text,
                question_type=question_types[i]
            )
            question_options = request.POST.getlist(f'options_{i}[]')
            print(f"processing options for question {i + 1}:{question_options}")
            print(f"options for question {i}:{question_options}")
            print("options:",options)
            print("question_options:",question_options)
            unique_options=set()
            print(unique_options)
            for option_text in question_options:
                stripped_option=option_text.strip().lower()
                if stripped_option and stripped_option not in unique_options:
                    Option.objects.create(
                        question=question,
                        text=option_text.strip()
                    )
                    unique_options.add(stripped_option)
                    print(f"Added option: {option_text.strip()} to question: {q_text}")

        print(f"survey '{survey.title}' created successfully with questions and options.")
        print("qns and options:",Survey.objects.get(pk=survey.id))
        return redirect('edit_survey', survey_id=survey.id)
    
    return render(request,'create_survey.html')

# for edit survey
@login_required
def edit_survey(request, survey_id):
    survey=get_object_or_404(Survey, id=survey_id, creator=request.user)
    questions=survey.questions.prefetch_related('options').all()
    if request.method == 'POST':
        print("Form data:",request.POST)  

        if 'delete_question' in request.POST:
            question_id=request.POST['delete_question']
            if question_id.isdigit():
                Question.objects.filter(id=question_id).delete()
    
        elif 'delete_option' in request.POST:
            option_id=request.POST['delete_option']
            if option_id.isdigit():
                Option.objects.filter(id=option_id).delete()
        
        elif 'new_question_text' in request.POST:
            new_question_text=request.POST['new_question_text']
            new_question_type=request.POST['new_question_type']
            Question.objects.create(survey=survey, text=new_question_text, question_type=new_question_type)

        # to update questions and options
        question_texts=request.POST.getlist('question_text[]')
        question_types=request.POST.getlist('question_type[]')
        question_ids=request.POST.getlist('question_id[]')
        option_data=request.POST  
        print("Options data",option_data)
        for i in range(len(question_ids)):
            question=Question.objects.get(id=int(question_ids[i]))
            question.text=question_texts[i]
            question.question_type=question_types[i]
            question.save()

            # to update options for this question
            options_key=f"options_{i}[]"
            if options_key in option_data:
                option_texts=request.POST.getlist(options_key)
                question.options.all().delete() 
                for option_text in option_texts:
                    Option.objects.create(question=question, text=option_text)

    # qns and their corresponding options
    questions_with_options = []
    for question in questions:
        questions_with_options.append({
            'id':question.id,
            'text':question.text,
            'type':question.question_type,
            'options':question.options.all()
        })

    return render(request,'edit_survey.html', {
        'survey': survey,
        'questions_with_options':questions_with_options,
    })

# publish_survey
@login_required
def publish_survey(request, survey_id):
    if request.user.profile.role !='creator':
        return HttpResponseForbidden("Only Survey Creators can publish surveys.")
    survey = get_object_or_404(Survey, id=survey_id, creator=request.user, status='draft')
    if survey.questions.count() >= 5:
        survey.status='published'
        survey.save()
    return redirect('manage_surveys')

# close survey
@login_required
def close_survey(request,survey_id):
    if request.user.profile.role != 'creator':
        return HttpResponseForbidden("Only Survey Creators can close surveys.")
    survey = get_object_or_404(Survey, id=survey_id, creator=request.user, status='published')
    survey.status='closed'
    survey.save()
    return redirect('manage_surveys')

# for managing surveys
@login_required
def manage_surveys(request):
    if request.user.profile.role !='creator':
        return HttpResponseForbidden("Only Survey Creators can manage surveys.")
    surveys = Survey.objects.filter(creator=request.user).annotate(response_count=Count('response'))
    context = {
        'draft_surveys':surveys.filter(status='draft'),
        'published_surveys':surveys.filter(status='published'),
        'closed_surveys':surveys.filter(status='closed'),
        'total_surveys':surveys.count(),
    }
    return render(request,'creator_dashboard.html', context)

@login_required
def view_survey_results(request,survey_id):
    survey = get_object_or_404(Survey, id=survey_id)
    if not (request.user.profile.role == 'creator' or (request.user.profile.role == 'taker' and survey.status == 'republished')):
        return HttpResponseForbidden("You do not have permission to view survey results.")
    questions=survey.questions.all()
    results=[]
    for question in questions:
        options=question.options.all()
        option_counts=Response.objects.filter(question=question) \
                        .values('selected_option') \
                        .annotate(count=Count('selected_option'))
        
        total_responses=sum(item['count'] for item in option_counts)
        count_mapping={item['selected_option']: item['count'] for item in option_counts}
        question_result={
            'question':question.text,
            'options':[
                {
                    'text':option.text,
                    'count':count_mapping.get(option.id, 0),
                    'percentage':(count_mapping.get(option.id, 0) / total_responses * 100) if total_responses > 0 else 0
                }
                for option in options
            ]
        }
        results.append(question_result)
    return render(request, 'view_survey_results.html', {
        'survey': survey,
        'results': results,
        'total_responses': total_responses
    })
    
# Survey Taker Views
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .models import Survey, Question, Option, Response
@login_required
def list_available_surveys(request):
    if request.user.profile.role != 'taker':
        return HttpResponseForbidden("Only Survey Takers can view available surveys.")
    available_surveys = Survey.objects.filter(status__in=['published', 'republished'])
    responded_surveys = Response.objects.filter(user=request.user).values_list('survey_id', flat=True).distinct()

    for survey in available_surveys:
        survey.user_responded = survey.id in responded_surveys
    return render(request, 'available_surveys.html', {
        'surveys': available_surveys,
        'user_responses': responded_surveys,
    })

# for take survey republished
@login_required
def take_survey_republished(request, survey_id):
    survey = get_object_or_404(Survey, id=survey_id, status='republished')
    questions = Question.objects.filter(survey=survey)

    if request.method == 'POST':
        for question in questions:
            option_id = request.POST.get(f'question_{question.id}')
            if option_id:
                try:
                    option = Option.objects.get(id=option_id)
                    Response.objects.create(
                        survey=survey,
                        user=request.user,
                        question=question,
                        selected_option=option
                    )
                except Option.DoesNotExist:
                    pass

        return redirect('survey_completed', survey_id=survey.id)

    results = []
    for question in questions:
        total_responses = Response.objects.filter(question=question).count()
        options_data = []
        for option in question.options.all():
            option_count = Response.objects.filter(question=question, selected_option=option).count()
            percentage = (option_count / total_responses * 100) if total_responses > 0 else 0
            options_data.append({
                'text': option.text,
                'count': option_count,
                'percentage': percentage
            })
        results.append({
            'question_text': question.text,
            'options': options_data
        })

    return render(request, 'take_survey_republished.html', {
        'survey': survey,
        'results': results
    })
# for take survey
@login_required
def take_survey(request, survey_id):
    if request.user.profile.role != 'taker':
        return HttpResponseForbidden("Only Survey Takers can take surveys.")
    survey = get_object_or_404(Survey, id=survey_id, status__in=['published', 'republished'])
    questions = Question.objects.filter(survey=survey)
    
    wisdom_mode = request.GET.get('mode') == 'wisdom'
    user_response_exists = Response.objects.filter(survey=survey, user=request.user).exists()

    if request.method == 'POST':
        if survey.status == 'republished':
            Response.objects.filter(survey=survey, user=request.user).delete()
        for question in questions:
            option_id = request.POST.get(f'question_{question.id}')
            if option_id:
                option = Option.objects.get(id=option_id)
                Response.objects.create(
                    survey=survey,
                    user=request.user,
                    question=question,
                    selected_option=option
                )
        messages.success(request, "Survey submitted successfully.")
        return redirect('survey_completed', survey_id=survey.id)
    for question in questions:
        total_responses = Response.objects.filter(question=question).count()
        for option in question.options.all():
            option_count = Response.objects.filter(question=question, selected_option=option).count()
            option.percentage = (option_count / total_responses * 100) if total_responses > 0 else 0

    return render(request, 'take_survey.html', {
        'survey': survey, 
        'questions': questions, 
        'wisdom_mode': wisdom_mode,
        'user_response_exists': user_response_exists
    })
    
# survey_Completed
@login_required
def survey_completed(request, survey_id):
    if request.user.profile.role != 'taker':
        return HttpResponseForbidden("Only Survey Takers can complete surveys.")
    
    survey = get_object_or_404(Survey, id=survey_id)
    responses = Response.objects.filter(survey=survey, user=request.user)

    return render(request, 'survey_completed.html', {
        'survey': survey,
        'responses': responses,
    })

# republish survey
@login_required
def republish_survey(request, survey_id):
    print(f"Attempting to republish survey with ID: {survey_id}")
    
    if request.user.profile.role != 'creator':
        print(f"User {request.user.username} is not a creator. Access denied.")
        return HttpResponseForbidden("Only Survey Creators can republish surveys.")
    try:
        survey = get_object_or_404(Survey, id=survey_id, creator=request.user)
        print(f"Found survey: {survey.title}, current status: {survey.status}")
        
        if survey.status == 'closed':
            survey.status = 'republished'
            survey.save()
            print(f"Survey status updated to: {survey.status}")
        else:
            print(f"Survey status is not 'closed'. Current status: {survey.status}")
        
        print("Redirecting to manage_surveys")
        return redirect('manage_surveys')
    except Exception as e:
        print(f"error occurred:{str(e)}")
# for home
from django.shortcuts import render

def home(request):
    return render(request, 'home.html')  