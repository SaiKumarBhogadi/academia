from django.core.management.base import BaseCommand
from schools.models import Admission

class Command(BaseCommand):
    help = 'Populate admission_id for existing Admission objects'

    def handle(self, *args, **kwargs):
        admissions = Admission.objects.filter(admission_id='')
        for admission in admissions:
            admission.save()  # This will trigger the save method and generate admission_id
            self.stdout.write(self.style.SUCCESS(f'Updated admission_id for Admission {admission.id}: {admission.admission_id}'))

        self.stdout.write(self.style.SUCCESS('Finished populating admission_ids'))