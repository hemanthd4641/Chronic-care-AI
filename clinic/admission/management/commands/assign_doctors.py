from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from admission.models import DoctorPatientRelationship

class Command(BaseCommand):
    help = 'Assign doctors to patients for appointment booking'

    def add_arguments(self, parser):
        parser.add_argument(
            '--doctor-username',
            type=str,
            help='Username of the doctor to assign patients to',
        )
        parser.add_argument(
            '--assign-all',
            action='store_true',
            help='Assign all patients to the first available doctor',
        )

    def handle(self, *args, **options):
        if options['assign_all']:
            # Get the first doctor (superuser)
            doctor = User.objects.filter(is_superuser=True).first()
            if not doctor:
                self.stdout.write(
                    self.style.ERROR('No doctors found. Please create a doctor account first.')
                )
                return
            
            # Get all patients (non-superusers)
            patients = User.objects.filter(is_superuser=False)
            
            assigned_count = 0
            for patient in patients:
                relationship, created = DoctorPatientRelationship.objects.get_or_create(
                    doctor=doctor,
                    patient=patient,
                    defaults={'is_active': True}
                )
                if created:
                    assigned_count += 1
                    self.stdout.write(f'Assigned {patient.username} to {doctor.username}')
                else:
                    self.stdout.write(f'{patient.username} already assigned to {doctor.username}')
            
            self.stdout.write(
                self.style.SUCCESS(f'Successfully assigned {assigned_count} patients to {doctor.username}')
            )
        
        elif options['doctor_username']:
            try:
                doctor = User.objects.get(username=options['doctor_username'], is_superuser=True)
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'Doctor with username "{options["doctor_username"]}" not found.')
                )
                return
            
            # Get all unassigned patients
            assigned_patients = DoctorPatientRelationship.objects.filter(
                is_active=True
            ).values_list('patient_id', flat=True)
            
            patients = User.objects.filter(
                is_superuser=False
            ).exclude(id__in=assigned_patients)
            
            assigned_count = 0
            for patient in patients:
                relationship, created = DoctorPatientRelationship.objects.get_or_create(
                    doctor=doctor,
                    patient=patient,
                    defaults={'is_active': True}
                )
                if created:
                    assigned_count += 1
                    self.stdout.write(f'Assigned {patient.username} to {doctor.username}')
            
            self.stdout.write(
                self.style.SUCCESS(f'Successfully assigned {assigned_count} patients to {doctor.username}')
            )
        
        else:
            self.stdout.write(
                self.style.ERROR('Please specify --assign-all or --doctor-username')
            )

