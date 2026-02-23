from django.core.management.base import BaseCommand
from destinations.models import HistoricPeriod

PERIODS = [
    {
        'slug': 'prehistoric-period',
        'name': 'Prehistoric Period',
        'description': 'The Prehistoric Period denotes the span of human activity antecedent to written documentation. It encompasses the Middle and Late Palaeolithic hunter‑gatherer economies and the Neolithic transition to agriculture, manifested archaeologically through lithic industries, funerary contexts and emergent settlement systems.'
    },
    {
        'slug': 'chalcolithic-bronze-iron-ages',
        'name': 'Chalcolithic, Bronze and Iron Ages',
        'description': 'The Chalcolithic, Bronze and Iron Ages represent successive technological and social transformations associated with the intensive exploitation of metal technologies. Archaeological signatures include metallurgical production, stratified burial practices, fortification architecture and interregional exchange networks that fostered emerging social hierarchies and early urbanism.'
    },
    {
        'slug': 'hellenic-hellenistic-periods',
        'name': 'Hellenic and Hellenistic Periods',
        'description': 'The Hellenic (Classical) and Hellenistic periods are characterised by the florescence and diffusion of Greek urban institutions, artistic canons and material culture. Following Macedonian hegemony and Alexander’s conquests, Hellenistic polities engendered cultural syncretism, new urban forms and expanded economic circuits across the eastern Mediterranean and Balkans.'
    },
    {
        'slug': 'roman-period',
        'name': 'Roman Period',
        'description': 'The Roman Period marks integration within Roman administrative and legal frameworks, accompanied by accelerated processes of urbanism, infrastructural investment and economic integration. Material evidence includes road networks, monumental public architecture, inscriptions and patterns of land tenure that attest to provincial incorporation and Romanization dynamics.'
    },
    {
        'slug': 'byzantine-period',
        'name': 'Byzantine Period',
        'description': 'The Byzantine Period denotes the continuation and transformation of Eastern Roman administrative, ecclesiastical and cultural institutions. It is archaeologically visible through Christian liturgical architecture, adaptive reuse of classical monuments, monastic foundations and material expressions of imperial and ecclesiastical authority.'
    },
    {
        'slug': 'medieval-pre-ottoman',
        'name': 'Medieval Period (Pre-Ottoman)',
        'description': 'The Medieval (pre-Ottoman) Period encompasses the early and high Middle Ages prior to Ottoman expansion, characterized by political fragmentation, the emergence of regional principalities and the persistence of Byzantine, Latin and local cultural repertoires. Archaeological indicators include fortified sites, ecclesiastical complexes and agrarian settlement reorganisation.'
    },
    {
        'slug': 'ottoman-period',
        'name': 'Ottoman Period',
        'description': 'The Ottoman Period comprises the prolonged integration of territories into Ottoman administrative and socio‑economic systems. It is characterised by new urban morphologies, distinctive religious and civic architectural typologies, cadastral and fiscal reorganisation, and patterns of demographic and commercial transformation under imperial rule.'
    },
    {
        'slug': 'modern-period',
        'name': 'Modern Period',
        'description': 'The Modern Period refers to the era of nation‑state formation, industrialisation and modern socio‑political transformations. It also encompasses modern practices of heritage, archaeology and conservation, as well as evolving engagements with the past in the contexts of tourism, identity and cultural policy.'
    }
]

class Command(BaseCommand):
    help = 'Seed standard HistoricPeriod records with academic descriptions'

    def handle(self, *args, **options):
        for p in PERIODS:
            obj, created = HistoricPeriod.objects.update_or_create(
                slug=p['slug'],
                defaults={'name': p['name'], 'description': p['description']}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created period: {obj.name}"))
            else:
                self.stdout.write(self.style.WARNING(f"Updated period: {obj.name}"))
        self.stdout.write(self.style.SUCCESS('Seeding complete.'))
