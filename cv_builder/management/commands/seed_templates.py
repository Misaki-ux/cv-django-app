from django.core.management.base import BaseCommand
from cv_builder.models import CVTemplate


class Command(BaseCommand):
    help = "Seed the 10 CV templates"

    def handle(self, *args, **options):
        templates = [
            {
                "name": "Modern",
                "slug": "modern",
                "description": "Clean, contemporary design with a sidebar layout. Perfect for tech and creative roles.",
                "primary_color": "#2563eb",
                "secondary_color": "#60a5fa",
                "font_family": "Helvetica Neue, sans-serif",
            },
            {
                "name": "Classic",
                "slug": "classic",
                "description": "Traditional professional layout with serif fonts. Ideal for corporate and executive positions.",
                "primary_color": "#1a1a2e",
                "secondary_color": "#e94560",
                "font_family": "Times New Roman, serif",
            },
            {
                "name": "Minimalist",
                "slug": "minimalist",
                "description": "Simple and elegant with plenty of whitespace. Great for any profession.",
                "primary_color": "#374151",
                "secondary_color": "#9ca3af",
                "font_family": "Inter, sans-serif",
            },
            {
                "name": "Creative",
                "slug": "creative",
                "description": "Bold colors and modern sidebar layout. Perfect for designers and artists.",
                "primary_color": "#7c3aed",
                "secondary_color": "#c084fc",
                "font_family": "Poppins, sans-serif",
            },
            {
                "name": "Executive",
                "slug": "executive",
                "description": "Sophisticated design with gold accents. Ideal for senior management and C-level roles.",
                "primary_color": "#1e3a5f",
                "secondary_color": "#c9a227",
                "font_family": "Garamond, serif",
            },
            {
                "name": "Tech",
                "slug": "tech",
                "description": "Dark theme with monospace fonts. Designed for developers and engineers.",
                "primary_color": "#0f172a",
                "secondary_color": "#22d3ee",
                "font_family": "JetBrains Mono, monospace",
            },
            {
                "name": "Academic",
                "slug": "academic",
                "description": "Formal academic layout. Perfect for researchers, professors, and students.",
                "primary_color": "#1e40af",
                "secondary_color": "#93c5fd",
                "font_family": "Palatino, serif",
            },
            {
                "name": "Elegant",
                "slug": "elegant",
                "description": "Refined design with warm tones. Great for hospitality and luxury sectors.",
                "primary_color": "#4a1942",
                "secondary_color": "#e8a87c",
                "font_family": "Georgia, serif",
            },
            {
                "name": "Bold",
                "slug": "bold",
                "description": "High-impact design with strong colors. Makes a statement for sales and marketing.",
                "primary_color": "#dc2626",
                "secondary_color": "#fbbf24",
                "font_family": "Impact, sans-serif",
            },
            {
                "name": "Simple",
                "slug": "simple",
                "description": "Straightforward and easy to read. A versatile choice for any industry.",
                "primary_color": "#334155",
                "secondary_color": "#94a3b8",
                "font_family": "Arial, sans-serif",
            },
        ]

        for t in templates:
            obj, created = CVTemplate.objects.update_or_create(
                slug=t["slug"],
                defaults=t,
            )
            status = "Created" if created else "Updated"
            self.stdout.write(f"  {status}: {t['name']}")

        self.stdout.write(self.style.SUCCESS(f"Successfully seeded {len(templates)} templates"))
