"""Offline, role-aware CV skill suggestions based on common ROME skill groups.

The catalogue is intentionally small and editable. A France Travail ROME 4.0
API/data feed can replace it when credentials or a local reference file become
available; suggestions are never presented as official API results.
"""

import unicodedata

from django.utils.translation import get_language


ROLE_CATALOG = {
    'service': {
        'keywords': ('restaurant', 'serveur', 'serveuse', 'hospitality', 'bar', 'cuisine', 'cuisinier', 'plongeur', 'service'),
        'hard': [
            ('Customer service', 'Accueil et relation client', ('client', 'accueil', 'service')),
            ('Order taking', 'Prise de commande', ('commande', 'restaurant', 'serveur')),
            ('Food hygiene', 'Hygiène alimentaire', ('hygiene', 'cuisine', 'food')),
            ('Cash handling', 'Encaissement', ('caisse', 'cash', 'vente')),
            ('Dining room setup', 'Mise en place de la salle', ('salle', 'restaurant', 'service')),
        ],
        'soft': [
            ('Customer focus', 'Sens du service', ('client', 'accueil')),
            ('Teamwork', 'Travail en équipe', ('equipe', 'collectif')),
            ('Stress management', 'Gestion du stress', ('stress', 'rush')),
            ('Communication', 'Communication', ('communication', 'client')),
            ('Adaptability', 'Adaptabilité', ('adaptabilite', 'polyvalence')),
        ],
    },
    'it': {
        'keywords': ('informatique', 'technicien', 'developer', 'développeur', 'support', 'software', 'network', 'reseau', 'système'),
        'hard': [
            ('Technical support', 'Support technique', ('support', 'assistance', 'technicien')),
            ('Incident diagnosis', 'Diagnostic des incidents', ('incident', 'diagnostic', 'depannage')),
            ('Network administration', 'Administration réseau', ('reseau', 'network', 'infrastructure')),
            ('Windows and Linux', 'Environnements Windows et Linux', ('windows', 'linux', 'systeme')),
            ('Ticketing tools', 'Outils de gestion des tickets', ('ticket', 'incident', 'support')),
        ],
        'soft': [
            ('Analytical thinking', 'Esprit d’analyse', ('analyse', 'diagnostic')),
            ('User communication', 'Communication avec les utilisateurs', ('utilisateur', 'communication')),
            ('Teaching and guidance', 'Pédagogie et accompagnement', ('formation', 'accompagnement')),
            ('Autonomy', 'Autonomie', ('autonomie', 'autonome')),
            ('Attention to detail', 'Rigueur', ('rigueur', 'detail', 'qualite')),
        ],
    },
    'admin': {
        'keywords': ('administratif', 'administrative', 'secretaire', 'secrétaire', 'office manager', 'assistant', 'assistante', 'gestionnaire'),
        'hard': [
            ('Document management', 'Gestion documentaire', ('document', 'dossier', 'administratif')),
            ('Scheduling and planning', 'Gestion des agendas et planning', ('agenda', 'planning', 'rendez-vous')),
            ('Microsoft Office', 'Maîtrise de Microsoft Office', ('office', 'excel', 'word')),
            ('Telephone reception', 'Accueil téléphonique', ('telephone', 'accueil', 'standard')),
            ('Data entry', 'Saisie et suivi de données', ('saisie', 'donnees', 'suivi')),
        ],
        'soft': [
            ('Organization', 'Sens de l’organisation', ('organisation', 'planning')),
            ('Confidentiality', 'Respect de la confidentialité', ('confidentialite', 'secret')),
            ('Written communication', 'Communication écrite', ('redaction', 'courrier', 'communication')),
            ('Reliability', 'Fiabilité', ('fiabilite', 'rigueur')),
            ('Prioritization', 'Gestion des priorités', ('priorite', 'urgence')),
        ],
    },
    'sales': {
        'keywords': ('commercial', 'vente', 'sales', 'vendeur', 'vendeuse', 'conseiller clientèle', 'business development'),
        'hard': [
            ('Customer relationship management', 'Gestion de la relation client', ('client', 'crm', 'relation')),
            ('Sales prospecting', 'Prospection commerciale', ('prospection', 'commercial')),
            ('Negotiation', 'Négociation', ('negociation', 'vente')),
            ('Sales tools and CRM', 'Outils commerciaux et CRM', ('crm', 'outil', 'suivi')),
            ('Sales reporting', 'Suivi des ventes', ('vente', 'reporting', 'objectif')),
        ],
        'soft': [
            ('Active listening', 'Écoute active', ('ecoute', 'client')),
            ('Persuasion', 'Force de persuasion', ('persuasion', 'negociation')),
            ('Results orientation', 'Orientation résultats', ('resultat', 'objectif')),
            ('Relationship building', 'Aisance relationnelle', ('relation', 'client')),
            ('Resilience', 'Persévérance', ('perseverance', 'relance')),
        ],
    },
    'general': {
        'keywords': (),
        'hard': [
            ('Digital tools', 'Outils numériques', ('informatique', 'digital', 'logiciel')),
            ('Project coordination', 'Coordination de projets', ('projet', 'coordination')),
            ('Customer service', 'Relation client', ('client', 'accueil')),
            ('Written communication', 'Communication écrite', ('redaction', 'communication')),
        ],
        'soft': [
            ('Communication', 'Communication', ('communication', 'equipe')),
            ('Adaptability', 'Adaptabilité', ('adaptabilite', 'polyvalence')),
            ('Teamwork', 'Travail en équipe', ('equipe', 'collectif')),
            ('Problem solving', 'Résolution de problèmes', ('probleme', 'solution')),
        ],
    },
}


def _normalize(value):
    value = unicodedata.normalize('NFKD', str(value or '').casefold())
    return ''.join(char for char in value if not unicodedata.combining(char))


def get_skill_suggestions(cv):
    """Suggest missing hard/soft skills using target role and CV experience."""
    from accounts.models import UserProfile

    target = _normalize(cv.target_job_title)
    candidate_details = [cv.summary, *cv.skills.values_list('name', flat=True)]
    for experience in cv.experiences.all():
        candidate_details.extend((experience.position, experience.company, experience.description))
    for education in cv.educations.all():
        candidate_details.extend((education.degree, education.field_of_study, education.description))
    profile = UserProfile.objects.filter(user_id=cv.user_id).first()
    if profile:
        candidate_details.append(profile.summary)
        for skill in profile.skills.all():
            candidate_details.append(skill.name)
        for experience in profile.experiences.all():
            candidate_details.extend((experience.position, experience.company, experience.description))
        for education in profile.educations.all():
            candidate_details.extend((education.degree, education.field_of_study, education.description))
    profile_text = _normalize(' '.join(candidate_details))
    role = next(
        (key for key, data in ROLE_CATALOG.items()
         if key != 'general' and any(_normalize(keyword) in target for keyword in data['keywords'])),
        'general',
    )
    catalog = ROLE_CATALOG[role]
    existing = {_normalize(name) for name in cv.skills.values_list('name', flat=True)}
    language = (get_language() or 'en').split('-')[0]
    suggestions = []
    for category in ('hard', 'soft'):
        ranked = []
        for english, french, related_terms in catalog[category]:
            name = french if language == 'fr' else english
            if _normalize(name) in existing:
                continue
            relevance = sum(1 for token in related_terms if _normalize(token) in profile_text)
            ranked.append((relevance, name))
        ranked.sort(key=lambda item: item[0], reverse=True)
        for relevance, name in ranked[:5]:
            suggestions.append({
                'name': name,
                'category': category,
                'reason': 'target' if target else ('profile' if relevance else 'general'),
            })
    return {'role': role, 'items': suggestions}
