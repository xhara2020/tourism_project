OFFERS = [
    {
        'slug': 'summer-beach-package',
        'title': 'Summer Beach Package',
        'summary': '4-night seaside stay + boat tour.',
        'description': 'Enjoy a 4-night stay at a seaside hotel with breakfast included, a boat tour of the coast, and a guided snorkeling session. Ideal for families and couples.'
    },
    {
        'slug': 'heritage-city-break',
        'title': 'Heritage City Break',
        'summary': '2-night guided city tour and museum passes.',
        'description': 'Two nights in a centrally located guesthouse, guided walking tours of historic sites, free museum entries, and a traditional food tasting session.'
    },

]

# Helper mapping by slug for quick lookup
OFFERS_BY_SLUG = {o['slug']: o for o in OFFERS}
