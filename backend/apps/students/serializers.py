from rest_framework import serializers

from apps.academics.models import Programme
from apps.students.models import Student


class StudentSerializer(serializers.ModelSerializer):
    student_id = serializers.IntegerField(read_only=True)
    admission_number = serializers.CharField(max_length=30)
    first_name = serializers.CharField(max_length=60, trim_whitespace=True)
    last_name = serializers.CharField(max_length=60, trim_whitespace=True)
    age = serializers.IntegerField(min_value=0, max_value=120)
    gender = serializers.ChoiceField(
        choices=Student.Gender.choices,
        allow_null=True,
        required=False,
    )
    programme_id = serializers.PrimaryKeyRelatedField(
        source="programme",
        queryset=Programme.objects.filter(is_active=True),
    )
    date_registered = serializers.DateTimeField(read_only=True)
    is_active = serializers.BooleanField(required=False)

    class Meta:
        model = Student
        fields = (
            "student_id",
            "admission_number",
            "first_name",
            "last_name",
            "age",
            "gender",
            "programme_id",
            "date_registered",
            "is_active",
        )

    def validate_first_name(self, value):
        if not value or not all(
            character.isalpha() or character.isspace() for character in value
        ):
            raise serializers.ValidationError(
                "First name must contain letters and spaces only."
            )
        return value

    def validate_last_name(self, value):
        if not value or not all(
            character.isalpha() or character.isspace() for character in value
        ):
            raise serializers.ValidationError(
                "Last name must contain letters and spaces only."
            )
        return value

    def validate_admission_number(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Admission number is required.")
        queryset = Student.objects.filter(admission_number__iexact=value)
        if self.instance is not None:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise serializers.ValidationError(
                "A student with this admission number already exists."
            )
        return value
