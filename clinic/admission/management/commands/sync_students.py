from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from admission.models import Student

class Command(BaseCommand):
    help = 'Create Student records for existing Users who don\'t have them'

    def handle(self, *args, **options):
        # Find users without student records (excluding superusers)
        users_without_students = User.objects.filter(
            is_superuser=False,
            student__isnull=True
        )

        created_count = 0
        
        for user in users_without_students:
            try:
                student = Student.objects.create(
                    user=user,
                    first_name=user.first_name or 'Unknown',
                    last_name=user.last_name or 'Unknown',
                    username=user.username,
                    password1='',  # Empty since we don't store plain passwords
                    password2='',  # Empty since we don't store plain passwords
                    dob='2000-01-01',  # Default date - should be updated later
                    gender='Other',  # Default gender - should be updated later
                    email=user.email or f'{user.username}@example.com',
                    phone_number=0,  # Default phone - should be updated later
                    address='Not provided'  # Default address - should be updated later
                )
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Created Student record for user: {user.username}'
                    )
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f'Failed to create Student record for user {user.username}: {str(e)}'
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {created_count} Student records'
            )
        )