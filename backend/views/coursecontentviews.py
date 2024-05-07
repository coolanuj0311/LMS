from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from core.custom_permissions import CourseContentPermissions, SuperAdminOrGetOnly
from rest_framework import status
from backend.models.allmodels import (
    Course,
    CourseRegisterRecord,
    UploadReadingMaterial,
    CourseStructure,
    CourseEnrollment,
    Quiz,
)
from backend.serializers.createcourseserializers import (
    CreateCourseStructureSerializer,
    CreateQuizSerializer,
    CreateUploadReadingMaterialSerializer,
)
from backend.serializers.courseserializers import (
    QuizSerializer,
)
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from backend.models.coremodels import *
from backend.serializers.courseserializers import *

class CourseStructureView(APIView):
    """
    GET API for all users to list of courses structure for specific course
    
    POST API for super admin to create new instances of course structure while editing existing too
    
    """
    permission_classes = [SuperAdminOrGetOnly]
    
    def get(self, request, course_id, format=None):
        try:
            course_structures = CourseStructure.objects.filter(course_id=course_id,active=True, deleted_at__isnull=True).order_by('-created_at') # active=True,
            if course_structures is not None:
                serializer = CourseStructureSerializer(course_structures, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({"error": "No course structures found for the specified course ID"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
                if isinstance(e, ValidationError):
                    return Response({"error": "Validation Error: " + str(e)}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request, course_id, *args, **kwargs):
        course = Course.objects.get(pk=course_id)
        if not course:
            return Response({"error": "Course not found"}, status=status.HTTP_404_NOT_FOUND)
        if course.active:
            return Response({"error": "Course is active, cannot proceed"}, status=status.HTTP_403_FORBIDDEN)
        try:
            # Extract data from request body
            order_numbers = request.data.get('order_number', [])
            content_types = request.data.get('content_type', [])
            content_ids = request.data.get('content_id', [])
            
            # Check if lengths of lists are same
            if len(order_numbers) != len(content_types) or len(content_types) != len(content_ids):
                return Response({"error": "Length of order_number, content_type, and content_id lists must be the same"}, status=status.HTTP_400_BAD_REQUEST)
            
            # Create CourseStructure instances
            new_created_course_structure = []
            course_structure_data = []
            existing_course_structure_data = []
            edited_existing_course_structure_data = []
            
            for order_number, content_type, content_id in zip(order_numbers, content_types, content_ids):
                # Check if an instance with similar course_id, content_type, content_id, and order_number exists
                instance_exists = CourseStructure.objects.filter(course=course_id, content_type=content_type, content_id=content_id, order_number=order_number).exists()
                if instance_exists:
                    data = {
                        'course': course_id,
                        'order_number': order_number,
                        'content_type': content_type,
                        'content_id': content_id
                    }
                    existing_course_structure_data.append(data)
                    course_structure_data.append(data)
                    # Skip mapping this instance
                    continue
                
                # Check if there's an existing instance with the same content_id and content_type but different order_number
                existing_instance = CourseStructure.objects.filter(course=course_id, content_type=content_type, content_id=content_id).first()
                if existing_instance:
                    # Update the order_number
                    existing_instance.order_number = order_number
                    existing_instance.save()
                    data = {
                        'course': course_id,
                        'order_number': order_number,
                        'content_type': content_type,
                        'content_id': content_id
                    }
                    edited_existing_course_structure_data.append(data)
                    course_structure_data.append(data)
                else:
                    # Create a new instance
                    data = {
                        'course': course_id,
                        'order_number': order_number,
                        'content_type': content_type,
                        'content_id': content_id
                    }
                    new_created_course_structure.append(data)
                    course_structure_data.append(data)
            
            # Save new instances
            serializer = CourseStructureSerializer(data=new_created_course_structure, many=True)
            if serializer.is_valid():
                serializer.save()
                return Response({"message": "Course structure created successfully", 
                                "existing_record": existing_course_structure_data,
                                "edited_records" : edited_existing_course_structure_data,
                                "new_records": new_created_course_structure,
                                "all_record": course_structure_data
                                }, status=status.HTTP_201_CREATED)
            else:
                return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
                if isinstance(e, ValidationError):
                    return Response({"error": "Validation Error: " + str(e)}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ReadingMaterialView(APIView):
    """
    GET API for all users to instance of reading material for specific course while list of reading material for specific course for super admin too.
    
    POST API for super admin to create new instances of course structure while editing existing too
    
    """
    permission_classes = [CourseContentPermissions]
    def get(self, request, course_id, format=None):
        
        try:
            content_id = request.query_params.get('content_id')
            count_calculator = request.query_params.get('count_calculator', '').lower() == 'true'
            list_mode = request.query_params.get('list', '').lower() == 'true'  # Check if list mode is enabled
            if count_calculator:
                if course_id:
                    reading_material_count = UploadReadingMaterial.objects.filter(courses__id=course_id, active=True, deleted_at__isnull=True).count()
                    if reading_material_count is None:
                        return Response({"message": " no Reading material found"}, status=status.HTTP_404_NOT_FOUND)
                    serializer = ReadingMaterialCountPerCourseSerializer({'reading_material_count': reading_material_count})
                    return Response(serializer.data, status=status.HTTP_200_OK)
                else:
                    return Response({"error": "no course id was passed in parameters "}, status=status.HTTP_400_BAD_REQUEST)
            if content_id:
                reading_material = UploadReadingMaterial.objects.get(
                    courses__id=course_id, 
                    id=content_id, 
                    active=True, 
                    deleted_at__isnull=True
                    )
                if reading_material :
                    serializer = ReadingMaterialSerializer(reading_material)
                    return Response(serializer.data, status=status.HTTP_200_OK)
                else:
                    return Response("error: no reading material found", status=status.HTTP_404_NOT_FOUND)
            elif list_mode:
                reading_materials = UploadReadingMaterial.objects.filter(
                    courses__id=course_id, 
                    active=True, 
                    deleted_at__isnull=True
                ).order_by('-uploaded_at')
                serializer = ReadingMaterialListPerCourseSerializer(reading_materials, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Specify 'content_id' or enable 'list' mode in query parameters."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
                if isinstance(e, ValidationError):
                    return Response({"error": "Validation Error: " + str(e)}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request, course_id, *args, **kwargs):
        course = Course.objects.get(pk=course_id)
        if not course:
            return Response({"error": "Course not found"}, status=status.HTTP_404_NOT_FOUND)
        if course.active:
            return Response({"error": "Course is active, cannot proceed"}, status=status.HTTP_403_FORBIDDEN)

        data = request.data
        if not data:
            return Response({"error": "Request body is empty"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            serializer = CreateUploadReadingMaterialSerializer(data=data)
            if serializer.is_valid():
                # Set additional fields
                serializer.validated_data['courses'] = [course_id]
                reading_material = serializer.save()
                try:
                    last_order_number = CourseStructure.objects.filter(course=course).latest('order_number').order_number
                except CourseStructure.DoesNotExist:
                    last_order_number = 0
                    print('starting with course structure')
                    # Create new CourseStructure instance
                course_structure_data = {
                        # 'course': course_id,
                        'course' : course_id,
                        'order_number': last_order_number + 1,
                        'content_type': 'reading',
                        'content_id': reading_material.pk
                }
                print(course_structure_data)
                course_structure_serializer = CreateCourseStructureSerializer(data=course_structure_data)
                if course_structure_serializer.is_valid():
                    course_structure_serializer.save()
                    return Response({"message": "Reading material created successfully"}, status=status.HTTP_201_CREATED)
                else:
                    return Response({"error": course_structure_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
                if isinstance(e, ValidationError):
                    return Response({"error": "Validation Error: " + str(e)}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # def put(self, request, course_id, *args, **kwargs):
    #     content_id = request.query_params.get('content_id')
    #     course = Course.objects.get(id=content_id)
    #     if course.active == True:
    #         return Response({"error": 'we can not update active course'}, status=status.HTTP_403_FORBIDDEN)
    #     reading_material = UploadReadingMaterial.objects.get(
    #             courses__id=course_id, 
    #             id=content_id, 
    #             active=True, 
    #             deleted_at__isnull=True
    #         )
    #     if reading_material is None:
    #         return Response({"error": "Reading material not found"}, status=status.HTTP_404_NOT_FOUND)
        
    #     edit_type = request.query_params.get('edit_type')
    #     if edit_type not in ['content', 'status']:
    #         return Response({"error": "Invalid edit_type in query parameter"}, status=status.HTTP_400_BAD_REQUEST)

    #     if edit_type == 'content':
    #         # Code for editing content
    #         pass
        
    #     elif edit_type == 'status':
    #         if reading_material.active:
    #             reading_material.active = False
    #             course_structure = CourseStructure.objects.filter(content_id=content_id, content_type='reading', active=True, deleted_at__isnull=True)
    #             course_structure.update(active=False)
    #         else:
    #             reading_material.active = True
    #             course_structure = CourseStructure.objects.filter(content_id=content_id, content_type='reading', active=False, deleted_at__isnull=True)
    #             try:
    #                 last_order_number = CourseStructure.objects.filter(course=course).latest('order_number').order_number
    #             except CourseStructure.DoesNotExist:
    #                     last_order_number = 0
    #             course_structure_data = {
    #                 'course': course_id,
    #                 'order_number': last_order_number + 1,
    #                 'content_type': 'reading',
    #                 'content_id': reading_material.pk
    #             }
    #             course_structure_serializer = CreateCourseStructureSerializer(data=course_structure_data)
    #             if course_structure_serializer.is_valid():
    #                 course_structure_serializer.save()
    #             else:
    #                 return Response({"error": course_structure_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        
    #     reading_material.save()
    #     return Response({"message": "Reading material status updated successfully"}, status=status.HTTP_200_OK)




class QuizView(APIView):
    """
        get: to retrieve the quiz of course in url (for authorized all)
        post: to create quiz instances for course in url (for super admin only)
    """
    permission_classes = [CourseContentPermissions]
    
    def get(self, request, course_id,format=None):
        try:
            
            content_id = request.query_params.get('content_id')
            list_mode = request.query_params.get('list', '').lower() == 'true'  # Check if list mode is enabled
            count_calculator = request.query_params.get('count_calculator', '').lower() == 'true'
            if count_calculator:
                if course_id:
                    quiz_count = Quiz.objects.filter(courses__id=course_id, active=True, deleted_at__isnull=True).count()
                    if quiz_count is None:
                        return Response({"message": " no quiz found"}, status=status.HTTP_404_NOT_FOUND)
                    serializer = QuizCountPerCourseSerializer({'quiz_count': quiz_count})
                    return Response(serializer.data, status=status.HTTP_200_OK)
                else:
                    return Response({"error": "no course id was passed in parameters "}, status=status.HTTP_400_BAD_REQUEST)
            if content_id:
                quiz = Quiz.objects.get(
                    courses__id=course_id, 
                    id=content_id, 
                    active=True, 
                    deleted_at__isnull=True
                    )
                if quiz:
                    serializer = QuizSerializer(quiz)
                    return Response(serializer.data, status=status.HTTP_200_OK)
                else:
                    return Response({"error": "No quiz found for the specified ID"}, status=status.HTTP_404_NOT_FOUND)
            elif list_mode:
                quizzes = Quiz.objects.filter(
                    courses__id=course_id, 
                    active=True, 
                    deleted_at__isnull=True
                ).order_by('-created_at')
                serializer = QuizListPerCourseSerializer(quizzes, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Specify 'content_id' or enable 'list' mode in query parameters."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
                if isinstance(e, ValidationError):
                    return Response({"error": "Validation Error: " + str(e)}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request, course_id, *args, **kwargs):
        course = Course.objects.get(pk=course_id)
        if not course:
            return Response({"error": "Course not found"}, status=status.HTTP_404_NOT_FOUND)
        if course.active:
            return Response({"error": "Course is active, cannot proceed"}, status=status.HTTP_403_FORBIDDEN)

        data = request.data
        if not data:
            return Response({"error": "Request body is empty"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            # Validate and save quiz
            requested_data = request.data.copy()
            requested_data['courses'] = course_id
            print(requested_data)
            serializer = CreateQuizSerializer(data=requested_data)
            if serializer.is_valid():
                quiz = serializer.save()
                course.quizzes.add(quiz)
                try:
                    last_order_number = CourseStructure.objects.filter(course=course).latest('order_number').order_number
                except CourseStructure.DoesNotExist:
                    last_order_number = 0
                    # Create new CourseStructure instance
                course_structure_data = {
                        'course': course_id,
                        'order_number': last_order_number + 1,
                        'content_type': 'quiz',
                        'content_id': quiz.pk
                }
                course_structure_serializer = CreateCourseStructureSerializer(data=course_structure_data)
                if course_structure_serializer.is_valid():
                    course_structure_serializer.save()
                    return Response({"message": "Quiz created successfully"}, status=status.HTTP_201_CREATED)
                else:
                    return Response({"error": course_structure_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
                if isinstance(e, ValidationError):
                    return Response({"error": "Validation Error: " + str(e)}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                

    # def put(self, request, course_id, *args, **kwargs):
    #     content_id = request.query_params.get('content_id')
    #     course = Course.objects.get(id=content_id)
    #     if course.active == True:
    #         return Response({"error": 'we can not update active course'}, status=status.HTTP_403_FORBIDDEN)
    #     quiz = Quiz.objects.get(
    #             courses__id=course_id, 
    #             id=content_id, 
    #             active=True, 
    #             deleted_at__isnull=True
    #         )
    #     if quiz is None:
    #         return Response({"error": "quiz not found"}, status=status.HTTP_404_NOT_FOUND)
        
    #     edit_type = request.query_params.get('edit_type')
    #     if edit_type not in ['content', 'status']:
    #         return Response({"error": "Invalid edit_type in query parameter"}, status=status.HTTP_400_BAD_REQUEST)

    #     if edit_type == 'content':
    #         # Code for editing content
    #         pass
        
    #     elif edit_type == 'status':
    #         if quiz.active:
    #             quiz.active = False
    #             course_structure = CourseStructure.objects.filter(content_id=content_id, content_type='quiz', active=True, deleted_at__isnull=True)
    #             course_structure.update(active=False)
    #         else:
    #             quiz.active = True
    #             course_structure = CourseStructure.objects.filter(content_id=content_id, content_type='quiz', active=False, deleted_at__isnull=True)
    #             try:
    #                 last_order_number = CourseStructure.objects.filter(course=course).latest('order_number').order_number
    #             except CourseStructure.DoesNotExist:
    #                     last_order_number = 0
    #             course_structure_data = {
    #                 'course': course_id,
    #                 'order_number': last_order_number + 1,
    #                 'content_type': 'quiz',
    #                 'content_id': quiz.pk
    #             }
    #             course_structure_serializer = CreateCourseStructureSerializer(data=course_structure_data)
    #             if course_structure_serializer.is_valid():
    #                 course_structure_serializer.save()
    #             else:
    #                 return Response({"error": course_structure_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        
    #     quiz.save()
    #     return Response({"message": "quiz status updated successfully"}, status=status.HTTP_200_OK)
