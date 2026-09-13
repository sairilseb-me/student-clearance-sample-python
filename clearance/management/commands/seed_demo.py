from django.core.management.base import BaseCommand

from accounts.models import User, UserRole
from clearance.models import Office

OFFICES = [
    {"name": "Adviser", "slug": "adviser", "sign_order": 1},
    {"name": "Library", "slug": "library", "sign_order": 2},
    {"name": "Treasurer", "slug": "treasurer", "sign_order": 3},
    {"name": "Guidance Office", "slug": "guidance", "sign_order": 4},
]

APPROVERS = {
    "adviser": {"name": "Adviser Reyes", "email": "adviser@demo.test"},
    "library": {"name": "Librarian Santos", "email": "library@demo.test"},
    "treasurer": {"name": "Treasurer Cruz", "email": "treasurer@demo.test"},
    "guidance": {"name": "Guidance Counselor Reyes", "email": "guidance@demo.test"},
}

DEMO_PASSWORD = "password"


class Command(BaseCommand):
    help = "Seed demo offices and demo accounts (student, admin, and one approver per office)."

    def handle(self, *args, **options):
        offices_by_slug = {}
        for office_data in OFFICES:
            office, _ = Office.objects.update_or_create(
                slug=office_data["slug"],
                defaults={"name": office_data["name"], "sign_order": office_data["sign_order"]},
            )
            offices_by_slug[office.slug] = office
        self.stdout.write(self.style.SUCCESS(f"Seeded {len(offices_by_slug)} offices."))

        self._upsert_user("student@demo.test", "Juan Dela Cruz", UserRole.STUDENT)
        self._upsert_user("admin@demo.test", "Clearance Admin", UserRole.ADMIN)

        for slug, approver in APPROVERS.items():
            self._upsert_user(
                approver["email"], approver["name"], UserRole.APPROVER, office=offices_by_slug[slug]
            )

        self.stdout.write(self.style.SUCCESS("Seeded demo accounts (password: \"password\")."))

    def _upsert_user(self, email, name, role, office=None):
        user, created = User.objects.get_or_create(email=email, defaults={"name": name, "role": role, "office": office})
        user.name = name
        user.role = role
        user.office = office
        user.set_password(DEMO_PASSWORD)
        user.save()
        return user
