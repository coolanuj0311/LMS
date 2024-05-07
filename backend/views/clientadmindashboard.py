from django.http import JsonResponse
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from backend.models.coremodels import Customer, User
from core.custom_mixins import ClientAdminMixin
from core.custom_permissions import ClientAdminPermission
from rest_framework import serializers
from backend.serializers.clientadmindashboard import ActiveEnrolledUserCountSerializer, ProgressDataSerializer, RegisteredCourseCountSerializer  # Import your serializer

from backend.models.coremodels import Customer, User
from core.custom_mixins import ClientAdminMixin
from rest_framework.response import Response
from rest_framework.views import APIView

from backend.models.allmodels import (
    Course,
    CourseCompletionStatusPerUser,
    CourseEnrollment,
    CourseRegisterRecord,
)
from rest_framework.exceptions import NotFound, ValidationError
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, render, redirect
from django.utils.decorators import method_decorator

# employer dashboard
# =================================================================
 # Import your User model
class ActiveEnrolledUserCountPerCustomerView(APIView):
    """
    Get API for counting active enrolled users per customer ID.
    """
    permission_classes = [ClientAdminPermission]
    def get(self, request):
        try:

            serializer = ActiveEnrolledUserCountSerializer(data=request.query_params)
            serializer.is_valid(raise_exception=True)
            customer_id = serializer.validated_data.get('customer_id')
            # Retrieve the customer ID from the request query parameters
            user_count = User.objects.filter(customer_id=customer_id, status='active').count()
            # Return the count in the response
            return Response({"user_count": user_count}, status=status.HTTP_200_OK)
        except (serializers.ValidationError, Exception) as e:
            error_message = e.detail if isinstance(e, serializers.ValidationError) else str(e)
            return Response({"error": error_message}, status=status.HTTP_400_BAD_REQUEST)



class RegisteredCourseCountView(APIView):
    """
    Get API for client admin to count registered active courses per customer ID.
    """
    permission_classes = [ClientAdminPermission]
    def get(self, request):
        try:
            serializer = RegisteredCourseCountSerializer(data=request.query_params)
            serializer.is_valid(raise_exception=True)
            # Extract customer ID from request query parameters
            customer_id = serializer.validated_data.get('customer_id')
            registered_course_counts = CourseRegisterRecord.objects.filter(
                customer_id=customer_id, 
                active=True,  # Only active registrations
                course__active=True  # Only active courses
            ).values('course').distinct().count()
            # Your existing logic to count registered active courses per customer ID
            response_data = {
                'active_course_count': registered_course_counts
            }
            return Response(response_data)

        except Exception as e:
            if isinstance(e, ValidationError):
                return Response({'error': e.detail}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


#---------
# graph : (per course)(for a customer) [employeer (client admin) dashboard]




class ProgressCountView(APIView):

    """
    API endpoint to get the count of users in different progress states for each registered course.
    """
    permission_classes = [ClientAdminPermission]
    def get(self, request):
        try:
            user= request.data.get('user')
            # we used courseerollment table to start the query of users so that query is made on the courses and users which are active and actively enrolled respectively.
            active_enrolled = CourseEnrollment.objects.filter(user__customer__id = user['customer'], active = True).values_list('user', flat=True).distinct()
            active_enrolled_ids = list(active_enrolled.values_list('user', flat=True))
            
            if not active_enrolled_ids:
                # Handle the case where there are no active enrolled users
                return Response({'error': 'No active enrolled users found'}, status=status.HTTP_404_NOT_FOUND)
            
            records = CourseCompletionStatusPerUser.objects.filter(active=True, enrolled_user__in=active_enrolled_ids,deleted_at__isnull=True)
            
            active_course_ids = records.values_list('course', flat=True).distinct()
            active_courses = Course.objects.filter(id__in=active_course_ids, active=True, deleted_at__isnull=True)
            print(active_courses)
            progress_data = []
            for course in active_courses:
                course_title = course.title
                status_values = ["completed", "in_progress", "not_started"]
                counts = {status: records.filter(
                                course=course, 
                                status=status, 
                                active=True, 
                                enrolled_user__customer__id=user['customer']
                            ).count() for status in status_values}

                progress_data.append({
                    'course_title': course_title,
                    'completion_count': counts['completed'],
                    'in_progress_count': counts['in_progress'],
                    'not_started_count': counts['not_started'],
                })
                serializer = ProgressDataSerializer(progress_data, many=True)
            return Response(serializer.data)
        except ObjectDoesNotExist as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#---------
