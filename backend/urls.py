from django.contrib import admin
from django.urls import path

from core.custom_permissions import SuperAdminPermission
from rest_framework.permissions import IsAuthenticated


# from .views.coursemanagementviews import (# )
# from .views.courseviews import (# )

from .views.superadmindashboardviews import (
    ActiveRegisteredCustomerCountView,
    CountOfActiveRegistrationPerCoure, 
    CourseCountView,
    GraphOfProgressPerCourseView, 
)

from .views.registercourseviews import (
    CourseCustomerRegistrationView,
    LMSCustomerListView,
    ManageCourseRegistrationRecordStatusView
)
from .views.coursesviews import (
    CourseView,
    ManageCourseView,
    FirstVersionActiveCourseListView,
    DerivedVersionActiveCourseListView,
)
from .views.coursecontentviews import (
    CourseStructureView,
    ReadingMaterialView,
    QuizView,

)
from .views.quizcontentviews import (
    ChoicesView,
    QuestionView,
    QuizTake,
    # dummy_quiz_index,
)

urlpatterns = [
    #registercourseviews.py views url
    path('lms-customer/', LMSCustomerListView.as_view(), name='lms-customer-list'), #0
    path('course-register-record/', CourseCustomerRegistrationView.as_view(), name='course-register-record'), #1
    path('manage-status/register-records/', ManageCourseRegistrationRecordStatusView.as_view(), name='manage-register-records'),  #2
    
    # coursesviews.py view urls
    path('courses/', CourseView.as_view(), name='courses'), #3
    path('manage/course/', ManageCourseView.as_view(), name='manage-course'), #4
    path('courses/active/v1/', FirstVersionActiveCourseListView.as_view(), name='active-first-version-courses-list'),  #5
    path('courses/derived-active/<int:course_id>/', DerivedVersionActiveCourseListView.as_view(), name='active-derived-version-course-list'),  #6
    
    # coursecontentviews.py view urls
    path('course/<int:course_id>/structure/', CourseStructureView.as_view(), name='course-structure'), #7
    path('course/<int:course_id>/reading-material/', ReadingMaterialView.as_view(), name='reading-material'), #8
    path('course/<int:course_id>/quiz/', QuizView.as_view(), name='quiz'), #9
    
    # quizcontentviews.py views urls
    path('course/<int:course_id>/quiz/<int:quiz_id>/question/', QuestionView.as_view(), name='reading-material'), #10
    path('question/<int:question_id>/choices/', ChoicesView.as_view(), name='question-choice'),  #11
    path('<int:pk>/quiz/<slug:quiz_slug>/take/', QuizTake.as_view(), name="quiz_take"), #12      href="{% url 'quiz_take' pk=course.pk slug=quiz.slug %}
        
    #superadmindashboardviews.py views url
    path('dashboard/sa/registration/count/', ActiveRegisteredCustomerCountView.as_view(), name='active-registration-count'),  #13
    path('dashboard/sa/active_registration-per-course/count/', CountOfActiveRegistrationPerCoure.as_view(), name='active_registration-per-course-count'),  #14
    path('dashboard/sa/progress-per-course/count/', GraphOfProgressPerCourseView.as_view(), name='not_started-per-course-count'),  #15
    path('dashboard/sa/course/count/', CourseCountView.as_view(), name='course-count'),  #16
]
