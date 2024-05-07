from django.contrib import admin
from django.urls import path

from backend.views.clientadmindashboard import ActiveEnrolledUserCountPerCustomerView, ProgressCountView, RegisteredCourseCountView

from .views.clientdashboardviews import (
    CountCoursesStatusView,
    DisplayClientCourseProgressView,
)
from .views.scoreviews import (
    CourseCompletionStatusView,
    QuizScoreView,
    QuizScorePerCourseView,
    CourseCompletionStatusPerUserView,
)
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
    EditQuizInstanceOnConfirmationView,
    NotificationBasedOnCourseDisplayView,
)
from .views.quizcontentviews import (
    ChoicesView,
    EditingQuestionInstanceOnConfirmationView,
    QuestionView,
    QuizTake,
    dummy_quiz_index,
)
from .views.enrollcourseviews import( 
   CourseEnrollmentView,
    DisplayCourseListView,
    UserListForEnrollmentView,
    ManageCourseEnrollmentView
)

urlpatterns = [
    # Course views URLs
    path('courses/', CourseView.as_view(), name='courses'),
    path('manage/course/', ManageCourseView.as_view(), name='manage-course'),
    path('courses/active/v1/', FirstVersionActiveCourseListView.as_view(), name='active-first-version-courses-list'),
    path('courses/derived-active/<int:course_id>/', DerivedVersionActiveCourseListView.as_view(), name='active-derived-version-course-list'),

    # Course content views URLs
    path('course/<int:course_id>/structure/', CourseStructureView.as_view(), name='course-structure'),
    path('course/<int:course_id>/reading-material/', ReadingMaterialView.as_view(), name='reading-material'),
    path('course/<int:course_id>/quiz/', QuizView.as_view(), name='quiz'),
    path('course/<int:course_id>/notifications/', NotificationBasedOnCourseDisplayView.as_view(), name='course-notifications'),
    path('course/<int:course_id>/quiz/<int:quiz_id>/edit/', EditQuizInstanceOnConfirmationView.as_view(), name='edit_quiz_instance_confirmation'),
    
    # Quiz content views URLs
    path('quiz/<int:quiz_id>/question/', QuestionView.as_view(), name='reading-material'),
    path('question/<int:question_id>/choices/', ChoicesView.as_view(), name='question-choice'),
    path('<int:pk>/<slug:quiz_slug>/take/', QuizTake.as_view(), name="quiz_take"),
    path('course/<int:course_id>/quiz/<int:quiz_id>/question/', EditingQuestionInstanceOnConfirmationView.as_view(), name='editing-question-instance-on-confirmation'),

    # Enrollment views URLs
    path('display/registered-course/', DisplayCourseListView.as_view(), name='course-list'), 
    path('display/users/', UserListForEnrollmentView.as_view(), name='users-list'), 
    path('course-enrollments/', CourseEnrollmentView.as_view(), name='course-enrollments-record'), 
    path('manage-enrollment/', ManageCourseEnrollmentView.as_view(), name='manage_enrollment'),
    
    # Superadmin dashboard views URLs
    path('dashboard/sa/registration/count/', ActiveRegisteredCustomerCountView.as_view(), name='active-registration-count'),
    path('dashboard/sa/active_registration-per-course/count/', CountOfActiveRegistrationPerCoure.as_view(), name='active_registration-per-course-count'),
    path('dashboard/sa/progress-per-course/count/', GraphOfProgressPerCourseView.as_view(), name='not_started-per-course-count'),
    path('dashboard/sa/course/count/', CourseCountView.as_view(), name='course-count'),

    # Register course views URLs
    path('lms-customer/', LMSCustomerListView.as_view(), name='lms-customer-list'),
    path('course-register-record/', CourseCustomerRegistrationView.as_view(), name='course-register-record'),
    path('manage-status/register-records/', ManageCourseRegistrationRecordStatusView.as_view(), name='manage-register-records'),

    # Client admin dashboard views URLs
    path('count-registered-courses/', RegisteredCourseCountView.as_view(), name='count_registered_courses'),
    path('active-enrolled-user-count/', ActiveEnrolledUserCountPerCustomerView.as_view(), name='active_enrolled_user_count'),
    path('progress-count/', ProgressCountView.as_view(), name='progress_count'),
    path('display-client-course-progress/', DisplayClientCourseProgressView.as_view(), name='display_client_course_progress'),
    path('count-courses-status/', CountCoursesStatusView.as_view(), name='count_client_completed_courses'),

    # Extra URLs
    path('quiz/redirect/<int:course_id>/', view=dummy_quiz_index, name='quiz_index'),
    path('course-completion-status/', CourseCompletionStatusView.as_view(), name='course_completion_status'),
    path('quiz-score/', QuizScoreView.as_view(), name='quiz_score'),
    path('quiz-score-per-course/', QuizScorePerCourseView.as_view(), name='quiz_score_per_course'),
    path('course-completion-status-per-user/', CourseCompletionStatusPerUserView.as_view(), name='course_completion_status_per_user'),
]
