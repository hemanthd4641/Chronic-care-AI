from django.core.management.base import BaseCommand
from medical_store.models import Medicine

class Command(BaseCommand):
    help = 'Populate the medical store with sample medicines'

    def handle(self, *args, **options):
        medicines_data = [
            # Pain Relief
            {'name': 'Paracetamol 500mg', 'price': 25.00, 'stock_quantity': 100, 'category': 'Pain Relief', 'manufacturer': 'ABC Pharma'},
            {'name': 'Ibuprofen 400mg', 'price': 35.00, 'stock_quantity': 80, 'category': 'Pain Relief', 'manufacturer': 'XYZ Pharma'},
            {'name': 'Aspirin 75mg', 'price': 20.00, 'stock_quantity': 120, 'category': 'Pain Relief', 'manufacturer': 'DEF Pharma'},
            {'name': 'Diclofenac Gel', 'price': 45.00, 'stock_quantity': 60, 'category': 'Pain Relief', 'manufacturer': 'GHI Pharma'},
            
            # Antibiotics
            {'name': 'Amoxicillin 250mg', 'price': 55.00, 'stock_quantity': 50, 'category': 'Antibiotics', 'manufacturer': 'JKL Pharma'},
            {'name': 'Azithromycin 500mg', 'price': 75.00, 'stock_quantity': 40, 'category': 'Antibiotics', 'manufacturer': 'MNO Pharma'},
            {'name': 'Ciprofloxacin 500mg', 'price': 65.00, 'stock_quantity': 35, 'category': 'Antibiotics', 'manufacturer': 'PQR Pharma'},
            {'name': 'Doxycycline 100mg', 'price': 45.00, 'stock_quantity': 45, 'category': 'Antibiotics', 'manufacturer': 'STU Pharma'},
            
            # Vitamins
            {'name': 'Vitamin D3 1000IU', 'price': 85.00, 'stock_quantity': 70, 'category': 'Vitamins', 'manufacturer': 'VWX Pharma'},
            {'name': 'Vitamin B12 1000mcg', 'price': 95.00, 'stock_quantity': 65, 'category': 'Vitamins', 'manufacturer': 'YZA Pharma'},
            {'name': 'Vitamin C 1000mg', 'price': 40.00, 'stock_quantity': 90, 'category': 'Vitamins', 'manufacturer': 'BCD Pharma'},
            {'name': 'Multivitamin Tablets', 'price': 120.00, 'stock_quantity': 55, 'category': 'Vitamins', 'manufacturer': 'EFG Pharma'},
            
            # Cardiovascular
            {'name': 'Atorvastatin 20mg', 'price': 150.00, 'stock_quantity': 30, 'category': 'Cardiovascular', 'manufacturer': 'HIJ Pharma'},
            {'name': 'Metoprolol 50mg', 'price': 35.00, 'stock_quantity': 40, 'category': 'Cardiovascular', 'manufacturer': 'KLM Pharma'},
            {'name': 'Lisinopril 10mg', 'price': 45.00, 'stock_quantity': 35, 'category': 'Cardiovascular', 'manufacturer': 'NOP Pharma'},
            {'name': 'Amlodipine 5mg', 'price': 25.00, 'stock_quantity': 50, 'category': 'Cardiovascular', 'manufacturer': 'QRS Pharma'},
            
            # Diabetes
            {'name': 'Metformin 500mg', 'price': 30.00, 'stock_quantity': 60, 'category': 'Diabetes', 'manufacturer': 'TUV Pharma'},
            {'name': 'Glibenclamide 5mg', 'price': 40.00, 'stock_quantity': 45, 'category': 'Diabetes', 'manufacturer': 'WXY Pharma'},
            {'name': 'Insulin Glargine', 'price': 450.00, 'stock_quantity': 15, 'category': 'Diabetes', 'manufacturer': 'ZAB Pharma'},
            {'name': 'Sitagliptin 100mg', 'price': 180.00, 'stock_quantity': 25, 'category': 'Diabetes', 'manufacturer': 'CDE Pharma'},
            
            # Respiratory
            {'name': 'Salbutamol Inhaler', 'price': 120.00, 'stock_quantity': 40, 'category': 'Respiratory', 'manufacturer': 'FGH Pharma'},
            {'name': 'Montelukast 10mg', 'price': 65.00, 'stock_quantity': 35, 'category': 'Respiratory', 'manufacturer': 'IJK Pharma'},
            {'name': 'Cetirizine 10mg', 'price': 25.00, 'stock_quantity': 80, 'category': 'Respiratory', 'manufacturer': 'LMN Pharma'},
            {'name': 'Budesonide Inhaler', 'price': 200.00, 'stock_quantity': 20, 'category': 'Respiratory', 'manufacturer': 'OPQ Pharma'},
            
            # General
            {'name': 'Omeprazole 20mg', 'price': 50.00, 'stock_quantity': 70, 'category': 'General', 'manufacturer': 'RST Pharma'},
            {'name': 'Ranitidine 150mg', 'price': 30.00, 'stock_quantity': 85, 'category': 'General', 'manufacturer': 'UVW Pharma'},
            {'name': 'Lactulose Syrup', 'price': 75.00, 'stock_quantity': 45, 'category': 'General', 'manufacturer': 'XYZ Pharma'},
            {'name': 'ORS Powder', 'price': 15.00, 'stock_quantity': 100, 'category': 'General', 'manufacturer': 'ABC Pharma'},
        ]

        created_count = 0
        updated_count = 0

        for medicine_data in medicines_data:
            medicine, created = Medicine.objects.get_or_create(
                name=medicine_data['name'],
                defaults=medicine_data
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created: {medicine.name}')
                )
            else:
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'Already exists: {medicine.name}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'\nMedical store populated successfully!\n'
                f'Created: {created_count} medicines\n'
                f'Already existed: {updated_count} medicines\n'
                f'Total medicines: {Medicine.objects.count()}'
            )
        )
