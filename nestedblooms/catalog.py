"""Static catalogue definitions for Nested Blooms.

This module is the single source of truth for the shop's merchandising data.
It is imported both by the database seeder (``nestedblooms.seed``) and by the
artwork generator (``tools/generate_art.py``) so that a product's illustration
and its database row can never drift apart.

Every price is stored in euro cents to keep money arithmetic exact.
"""

# --------------------------------------------------------------------------
# Brand + shop-wide configuration
# --------------------------------------------------------------------------

BRAND = {
    "name": "Nested Blooms",
    "tagline": "Irish florists, hand-tying happiness since 2019.",
    "phone": "+353 1 555 0198",
    "email": "hello@nestedblooms.ie",
    "address": "Unit 4, The Flower Yard, Blackpitts, Dublin 8, D08 XH76",
    "opening_hours": "Mon–Sat 8am–7pm · Sun 10am–5pm",
    "instagram": "https://instagram.com/nestedblooms",
    "facebook": "https://facebook.com/nestedblooms",
    "pinterest": "https://pinterest.com/nestedblooms",
}

# Delivery pricing, in cents.
DELIVERY_OPTIONS = [
    {
        "code": "standard",
        "name": "Standard Next-Day Delivery",
        "blurb": "Order before 4pm for delivery tomorrow, anywhere in Ireland.",
        "price": 595,
        "lead_days": 1,
    },
    {
        "code": "sameday",
        "name": "Same-Day Delivery",
        "blurb": "Dublin, Kildare and Wicklow. Order before 2pm and it arrives today.",
        "price": 995,
        "lead_days": 0,
    },
    {
        "code": "timed",
        "name": "Timed Morning Delivery",
        "blurb": "Guaranteed before 1pm on your chosen date.",
        "price": 1295,
        "lead_days": 1,
    },
]

FREE_DELIVERY_THRESHOLD = 7500  # €75.00

# Size upgrades offered on every bouquet. Price deltas are in cents.
SIZE_OPTIONS = [
    {
        "code": "classic",
        "name": "Classic",
        "blurb": "Our signature size — beautifully full.",
        "delta": 0,
    },
    {
        "code": "deluxe",
        "name": "Deluxe",
        "blurb": "Around 50% more stems for extra impact.",
        "delta": 1500,
    },
    {
        "code": "grand",
        "name": "Grand",
        "blurb": "Double the stems. Our showstopper.",
        "delta": 3000,
    },
]

# Optional extras added at the product page.
ADDONS = [
    {
        "code": "chocolates",
        "name": "Lily O'Brien's Belgian Chocolates",
        "blurb": "A 210g box of Irish-made chocolate desserts.",
        "price": 1295,
    },
    {
        "code": "prosecco",
        "name": "Prosecco Extra Dry (200ml)",
        "blurb": "A chilled little bottle to make it a celebration.",
        "price": 1495,
    },
    {
        "code": "candle",
        "name": "Hand-Poured Soy Candle",
        "blurb": "Fig and wild bergamot, poured in Wicklow.",
        "price": 1695,
    },
    {
        "code": "vase",
        "name": "Clear Glass Vase",
        "blurb": "A heavyweight vase so they don't have to go hunting.",
        "price": 995,
    },
    {
        "code": "teddy",
        "name": "Keepsake Teddy Bear",
        "blurb": "A soft 25cm bear with a linen ribbon.",
        "price": 1395,
    },
    {
        "code": "balloon",
        "name": "Helium Balloon",
        "blurb": "Inflated on the morning of delivery.",
        "price": 795,
    },
]

# Discount codes seeded into the database.
COUPONS = [
    {
        "code": "WELCOME10",
        "description": "10% off your first order",
        "kind": "percent",
        "value": 10,
        "min_spend": 0,
    },
    {
        "code": "BLOOM20",
        "description": "20% off orders over €80",
        "kind": "percent",
        "value": 20,
        "min_spend": 8000,
    },
    {
        "code": "FREEPOST",
        "description": "Free standard delivery",
        "kind": "free_delivery",
        "value": 0,
        "min_spend": 0,
    },
    {
        "code": "NEST15",
        "description": "€15 off orders over €100",
        "kind": "fixed",
        "value": 1500,
        "min_spend": 10000,
    },
]

# --------------------------------------------------------------------------
# Collections (product families) and occasions (gifting reasons)
# --------------------------------------------------------------------------

COLLECTIONS = [
    {
        "slug": "parisian-hatbox",
        "name": "Parisian Hatbox",
        "headline": "Blooms arranged in a keepsake box",
        "blurb": (
            "Our hatboxes arrive ready to display — the flowers sit in hydrated "
            "floral foam inside a rigid keepsake box, so there is no arranging, "
            "no trimming and no vase to find."
        ),
        "position": 1,
    },
    {
        "slug": "hand-tied",
        "name": "Hand-Tied Bouquets",
        "headline": "Tied by hand, wrapped in kraft and linen",
        "blurb": (
            "The classic. Each bouquet is spiralled by hand so the stems fan out "
            "when it is placed in water, then wrapped in recycled kraft paper and "
            "finished with a linen ribbon."
        ),
        "position": 2,
    },
    {
        "slug": "vase-arrangements",
        "name": "Vase Arrangements",
        "headline": "Arranged, watered and ready for the table",
        "blurb": (
            "Delivered in a weighted glass vase with the water already in it. "
            "Perfect for hospitals, offices and anyone who would rather not "
            "go looking for scissors."
        ),
        "position": 3,
    },
    {
        "slug": "baskets",
        "name": "Creative Baskets",
        "headline": "Garden-gathered style in a woven basket",
        "blurb": (
            "Loose, seasonal and a little bit wild. Our baskets are built on a "
            "hydrated base and travel beautifully, which makes them a favourite "
            "for new babies and sympathy tributes alike."
        ),
        "position": 4,
    },
    {
        "slug": "luxury",
        "name": "The Luxury Collection",
        "headline": "Our most generous arrangements",
        "blurb": (
            "Statement flowers for the moments that deserve them. Larger heads, "
            "longer stems and the pick of the Monday morning Dutch auction."
        ),
        "position": 5,
    },
    {
        "slug": "plants",
        "name": "Plants & Orchids",
        "headline": "Living gifts that last for months",
        "blurb": (
            "For people who want something to keep. Every plant is potted by us "
            "and comes with a care card written by our own growers."
        ),
        "position": 6,
    },
    {
        "slug": "gift-sets",
        "name": "Gift Sets",
        "headline": "Flowers plus something delicious",
        "blurb": (
            "Bundles that pair a bouquet with chocolate, fizz or a candle — "
            "wrapped together and delivered as one gift."
        ),
        "position": 7,
    },
]

OCCASIONS = [
    {
        "slug": "birthday",
        "name": "Birthday Flowers",
        "blurb": "Bright, generous and impossible to ignore.",
        "position": 1,
    },
    {
        "slug": "anniversary",
        "name": "Anniversary Flowers",
        "blurb": "Romantic classics for the year you have just finished.",
        "position": 2,
    },
    {
        "slug": "romance",
        "name": "Romance",
        "blurb": "Roses, peonies and everything in between.",
        "position": 3,
    },
    {
        "slug": "new-baby",
        "name": "New Baby",
        "blurb": "Soft, gentle palettes for the newest arrival.",
        "position": 4,
    },
    {
        "slug": "thank-you",
        "name": "Thank You",
        "blurb": "Say it properly, with something that smells wonderful.",
        "position": 5,
    },
    {
        "slug": "get-well",
        "name": "Get Well Soon",
        "blurb": "Cheerful, low-scent arrangements suited to hospitals.",
        "position": 6,
    },
    {
        "slug": "congratulations",
        "name": "Congratulations",
        "blurb": "New jobs, new homes, new degrees.",
        "position": 7,
    },
    {
        "slug": "sympathy",
        "name": "Sympathy & Funeral",
        "blurb": "Quiet, dignified tributes delivered with care.",
        "position": 8,
    },
    {
        "slug": "just-because",
        "name": "Just Because",
        "blurb": "The best reason there is.",
        "position": 9,
    },
    {
        "slug": "housewarming",
        "name": "New Home",
        "blurb": "Something living for an empty mantelpiece.",
        "position": 10,
    },
]

# --------------------------------------------------------------------------
# Products
# --------------------------------------------------------------------------
#
# ``art`` drives tools/generate_art.py. Its keys:
#   vessel  – hatbox | wrap | vase | basket | pot
#   vessel_colors – (body, shadow/accent) for the container
#   ribbon  – ribbon / tie colour
#   blooms  – ordered list of (flower_type, [colours], count) drawn back to front
#   foliage – leaf colour family
#
# Flower types understood by the generator:
#   rose, peony, tulip, lily, hydrangea, ranunculus, daisy, gyp, berry, orchid,
#   thistle, sunflower, carnation
# --------------------------------------------------------------------------

PRODUCTS = [
    # ---------------------------------------------------------------- hatbox
    {
        "slug": "grafton-rose-hatbox",
        "name": "The Grafton",
        "collection": "parisian-hatbox",
        "price": 6495,
        "occasions": ["romance", "anniversary", "birthday"],
        "badges": ["bestseller"],
        "blurb": "Forty red naomi roses domed into a black keepsake hatbox.",
        "description": (
            "Named after the street where we sold our very first bucket of "
            "flowers, The Grafton is unapologetically romantic. We dome forty "
            "Red Naomi roses — the same variety used in the Dutch grand hotels — "
            "into a matte black keepsake box, then tuck eucalyptus around the "
            "rim so the silhouette stays soft."
        ),
        "contains": "40 Red Naomi roses, silver dollar eucalyptus, ruscus.",
        "art": {
            "vessel": "hatbox",
            "vessel_colors": ["#2a2622", "#171412"],
            "ribbon": "#b8934a",
            "backdrop": ["#f6ece7", "#e8d3cb"],
            "foliage": "#3d6b4f",
            "blooms": [
                ["rose", ["#a01230", "#c0173c", "#87102a"], 17],
                ["rose", ["#d4335a", "#b81640"], 7],
            ],
        },
    },
    {
        "slug": "blush-nest-hatbox",
        "name": "Blush Nest",
        "collection": "parisian-hatbox",
        "price": 5995,
        "occasions": ["birthday", "new-baby", "thank-you", "just-because"],
        "badges": ["bestseller"],
        "blurb": "Sorbet roses, lisianthus and gypsophila in a soft ivory box.",
        "description": (
            "The arrangement our florists reach for when someone says 'something "
            "pretty, nothing loud'. Sorbet-toned roses are layered with cloud-white "
            "lisianthus and a haze of gypsophila, all set into a ribbed ivory box "
            "that looks quietly expensive on a hall table."
        ),
        "contains": "Sweet Avalanche roses, lisianthus, gypsophila, pistacia.",
        "art": {
            "vessel": "hatbox",
            "vessel_colors": ["#f3e7dc", "#ddcbbc"],
            "ribbon": "#c9a08f",
            "backdrop": ["#fbf4ee", "#f0dfd6"],
            "foliage": "#6d8f6a",
            "blooms": [
                ["rose", ["#f0b9c0", "#e79fae", "#f7d2d4"], 13],
                ["ranunculus", ["#fdf6f2", "#f3e3dc"], 8],
                ["gyp", ["#ffffff"], 26],
            ],
        },
    },
    {
        "slug": "ivory-elegance-hatbox",
        "name": "Ivory Elegance",
        "collection": "parisian-hatbox",
        "price": 6995,
        "occasions": ["sympathy", "anniversary", "congratulations"],
        "badges": [],
        "blurb": "An all-white dome of roses, lisianthus and lily in a grey box.",
        "description": (
            "Restrained and very elegant. We work entirely in whites and creams — "
            "roses, double lisianthus and a few just-opening oriental lilies — so "
            "the arrangement reads as texture rather than colour. A frequent "
            "choice for sympathy, and equally at home at a silver anniversary."
        ),
        "contains": "White roses, lisianthus, oriental lily, eucalyptus.",
        "art": {
            "vessel": "hatbox",
            "vessel_colors": ["#d9d6d0", "#bcb8b1"],
            "ribbon": "#8f9a92",
            "backdrop": ["#f7f7f4", "#e6e7e2"],
            "foliage": "#5c7f66",
            "blooms": [
                ["rose", ["#fdfcfa", "#f1ece3"], 12],
                ["lily", ["#ffffff", "#f6f2e8"], 5],
                ["hydrangea", ["#f2f4ef", "#e6eae2"], 4],
            ],
        },
    },
    {
        "slug": "velvet-bordeaux-hatbox",
        "name": "Velvet Bordeaux",
        "collection": "parisian-hatbox",
        "price": 7495,
        "occasions": ["romance", "anniversary"],
        "badges": ["new"],
        "blurb": "Deep burgundy dahlias and plum roses in an oxblood box.",
        "description": (
            "Autumn in a box. Burgundy dahlias, plum roses and dark astrantia are "
            "packed tightly enough that the whole thing looks velvet from across "
            "the room. We finish it with copper beech when the season allows."
        ),
        "contains": "Burgundy dahlia, Black Baccara roses, astrantia, copper beech.",
        "art": {
            "vessel": "hatbox",
            "vessel_colors": ["#4a1220", "#2e0a14"],
            "ribbon": "#caa46a",
            "backdrop": ["#f3e9e4", "#dcc6be"],
            "foliage": "#41603f",
            "blooms": [
                ["peony", ["#6d1229", "#8a1c38", "#4f0d1e"], 9],
                ["rose", ["#901c3a", "#701026"], 9],
                ["berry", ["#3d0a18"], 14],
            ],
        },
    },
    {
        "slug": "sorbet-sunrise-hatbox",
        "name": "Sorbet Sunrise",
        "collection": "parisian-hatbox",
        "price": 5795,
        "occasions": ["birthday", "congratulations", "thank-you", "just-because"],
        "badges": ["bestseller"],
        "blurb": "Peach, coral and mango blooms in a warm terracotta box.",
        "description": (
            "A proper mood-lifter. Peach roses, coral carnations and mango-toned "
            "ranunculus graduate from pale to punchy across the dome, so it catches "
            "the light differently depending on where you stand."
        ),
        "contains": "Peach roses, coral carnation, ranunculus, solidago.",
        "art": {
            "vessel": "hatbox",
            "vessel_colors": ["#c9704a", "#a35637"],
            "ribbon": "#f2d3a7",
            "backdrop": ["#fdf2e6", "#f6ddc4"],
            "foliage": "#6f8f4e",
            "blooms": [
                ["rose", ["#f4a06a", "#ef8b52", "#f7bb8c"], 12],
                ["ranunculus", ["#f2705a", "#e85c46"], 8],
                ["carnation", ["#fbc9a4"], 7],
            ],
        },
    },
    {
        "slug": "midnight-garden-hatbox",
        "name": "Midnight Garden",
        "collection": "parisian-hatbox",
        "price": 7995,
        "occasions": ["romance", "congratulations", "just-because"],
        "badges": [],
        "blurb": "Indigo hydrangea, purple lisianthus and thistle in navy.",
        "description": (
            "Cool, moody and surprisingly hard to photograph — it always looks "
            "better in person. Mophead hydrangea forms the base, then we thread "
            "purple lisianthus and eryngium thistle through the top for texture."
        ),
        "contains": "Blue hydrangea, purple lisianthus, eryngium thistle, ruscus.",
        "art": {
            "vessel": "hatbox",
            "vessel_colors": ["#1d2b44", "#111b2d"],
            "ribbon": "#9aa8c4",
            "backdrop": ["#eef1f7", "#d7dde9"],
            "foliage": "#3f6455",
            "blooms": [
                ["hydrangea", ["#6f80c0", "#5566a8", "#8a99d0"], 6],
                ["lily", ["#7a5fa8", "#8f74bc"], 5],
                ["thistle", ["#5f6fa8", "#4a5990"], 9],
            ],
        },
    },
    # ------------------------------------------------------------- hand-tied
    {
        "slug": "wild-meadow-bouquet",
        "name": "Wild Meadow",
        "collection": "hand-tied",
        "price": 4995,
        "occasions": ["just-because", "thank-you", "birthday", "housewarming"],
        "badges": ["bestseller"],
        "blurb": "A loose, gathered-from-the-hedgerow bouquet in kraft paper.",
        "description": (
            "Built to look like it was picked on a walk rather than made in a "
            "studio. Cream and butter tones, plenty of grasses, and a deliberately "
            "uneven outline. This is the bouquet our florists most often buy for "
            "each other."
        ),
        "contains": "Spray roses, chamomile, solidago, wheat, ammi, eucalyptus.",
        "art": {
            "vessel": "wrap",
            "vessel_colors": ["#d9c3a5", "#bfa584"],
            "ribbon": "#8d9d72",
            "backdrop": ["#f8f5ec", "#e9e3d3"],
            "foliage": "#7d9455",
            "blooms": [
                ["daisy", ["#fdfbf0", "#f6efd8"], 12],
                ["rose", ["#f5e0b8", "#eed49f"], 8],
                ["gyp", ["#fffdf5"], 22],
                ["berry", ["#c8a95e"], 10],
            ],
        },
    },
    {
        "slug": "coastal-blush-bouquet",
        "name": "Coastal Blush",
        "collection": "hand-tied",
        "price": 5495,
        "occasions": ["new-baby", "thank-you", "romance", "just-because"],
        "badges": [],
        "blurb": "Dusty pink roses and sea-holly, wrapped in oyster linen.",
        "description": (
            "Inspired by the colours on the Wicklow coast road in September — "
            "dusty pink, oyster grey and a touch of sea-holly blue. Soft enough "
            "for a new arrival, structured enough for a dinner party."
        ),
        "contains": "Dusty pink roses, eryngium, lisianthus, seeded eucalyptus.",
        "art": {
            "vessel": "wrap",
            "vessel_colors": ["#e5ddd2", "#cec4b6"],
            "ribbon": "#a8b6bd",
            "backdrop": ["#f6f4f1", "#e2e4e2"],
            "foliage": "#6b8a72",
            "blooms": [
                ["rose", ["#dda9a6", "#c9908f", "#e9c0bb"], 11],
                ["ranunculus", ["#f6ece6"], 7],
                ["thistle", ["#8fa0ad"], 7],
            ],
        },
    },
    {
        "slug": "golden-hour-bouquet",
        "name": "Golden Hour",
        "collection": "hand-tied",
        "price": 5295,
        "occasions": ["birthday", "congratulations", "thank-you"],
        "badges": [],
        "blurb": "Sunflowers, amber roses and solidago tied in kraft.",
        "description": (
            "The one that makes people grin when they open the door. Big-faced "
            "sunflowers anchor amber roses and sprays of solidago, and it keeps "
            "its shape for well over a week."
        ),
        "contains": "Sunflowers, amber roses, solidago, salal.",
        "art": {
            "vessel": "wrap",
            "vessel_colors": ["#d8bd92", "#bda173"],
            "ribbon": "#7f8f4c",
            "backdrop": ["#fdf6e4", "#f3e3bd"],
            "foliage": "#6e8b3d",
            "blooms": [
                ["sunflower", ["#f2b422", "#e0a013"], 5],
                ["rose", ["#ea9a3c", "#d9862c"], 9],
                ["gyp", ["#f8e59a"], 18],
            ],
        },
    },
    {
        "slug": "peony-dream-bouquet",
        "name": "Peony Dream",
        "collection": "hand-tied",
        "price": 6995,
        "occasions": ["romance", "anniversary", "birthday"],
        "badges": ["seasonal"],
        "blurb": "Ten Irish-grown peonies, and nothing else to distract from them.",
        "description": (
            "In season from late May, and worth the wait. We buy Sarah Bernhardt "
            "peonies from a grower in County Meath and send them in bud so they "
            "open in the recipient's own kitchen over two or three days."
        ),
        "contains": "10 Sarah Bernhardt peonies, pistacia foliage.",
        "art": {
            "vessel": "wrap",
            "vessel_colors": ["#f0e2d8", "#d9c6b8"],
            "ribbon": "#dba7ae",
            "backdrop": ["#fdf3f1", "#f3dbdb"],
            "foliage": "#5f8659",
            "blooms": [
                ["peony", ["#f2aec0", "#e894ab", "#f8cdd6"], 11],
            ],
        },
    },
    {
        "slug": "emerald-isle-bouquet",
        "name": "Emerald Isle",
        "collection": "hand-tied",
        "price": 4795,
        "occasions": ["housewarming", "congratulations", "get-well", "just-because"],
        "badges": [],
        "blurb": "White blooms and six kinds of Irish foliage.",
        "description": (
            "A green-and-white bouquet that leans hard on foliage: eucalyptus, "
            "pistacia, ruscus, bear grass, ivy and whatever looks best that "
            "morning. Long-lasting and beautifully architectural."
        ),
        "contains": "White lisianthus, chrysanthemum, mixed Irish foliage.",
        "art": {
            "vessel": "wrap",
            "vessel_colors": ["#dfd6c4", "#c4baa6"],
            "ribbon": "#5f7d55",
            "backdrop": ["#f2f6ee", "#dde7d8"],
            "foliage": "#4f7a4a",
            "blooms": [
                ["hydrangea", ["#eef4e8", "#dce8d4"], 5],
                ["daisy", ["#ffffff", "#f4f7ee"], 11],
                ["gyp", ["#ffffff"], 20],
            ],
        },
    },
    {
        "slug": "lavender-fields-bouquet",
        "name": "Lavender Fields",
        "collection": "hand-tied",
        "price": 5195,
        "occasions": ["thank-you", "get-well", "just-because", "sympathy"],
        "badges": [],
        "blurb": "Lilac, lavender and soft mauve with a gentle scent.",
        "description": (
            "Purple done gently. Lilac lisianthus, mauve roses and stems of real "
            "lavender give it a scent that fills a room without being heavy — "
            "which is why it does so well as a get-well gift."
        ),
        "contains": "Lilac lisianthus, mauve roses, lavender, limonium.",
        "art": {
            "vessel": "wrap",
            "vessel_colors": ["#e3dbe4", "#cbc0cd"],
            "ribbon": "#9b86ae",
            "backdrop": ["#f6f2f8", "#e5dcea"],
            "foliage": "#6a8467",
            "blooms": [
                ["rose", ["#b99cc9", "#a487ba", "#cdb6d8"], 10],
                ["lily", ["#c9b3d8", "#b7a0c9"], 5],
                ["thistle", ["#8878a8"], 8],
                ["gyp", ["#f2ecf6"], 16],
            ],
        },
    },
    # ------------------------------------------------------------------ vase
    {
        "slug": "dublin-bay-vase",
        "name": "Dublin Bay",
        "collection": "vase-arrangements",
        "price": 6495,
        "occasions": ["get-well", "thank-you", "congratulations", "housewarming"],
        "badges": ["bestseller"],
        "blurb": "Blue and white blooms arranged in a weighted glass vase.",
        "description": (
            "Crisp blue hydrangea against white roses and stocks, arranged in a "
            "heavy clear vase and delivered already watered. Because there is "
            "nothing to do on arrival, it is our most-ordered hospital gift."
        ),
        "contains": "Blue hydrangea, white roses, white stocks, eucalyptus, vase.",
        "art": {
            "vessel": "vase",
            "vessel_colors": ["#cfe0e8", "#a9c4d1"],
            "ribbon": "#7fa3b8",
            "backdrop": ["#f0f5f8", "#d8e5ec"],
            "foliage": "#5b8168",
            "blooms": [
                ["hydrangea", ["#8fa8d8", "#7592c9"], 5],
                ["rose", ["#fdfdfb", "#f0eee6"], 10],
                ["gyp", ["#ffffff"], 18],
            ],
        },
    },
    {
        "slug": "whitethorn-vase",
        "name": "Whitethorn",
        "collection": "vase-arrangements",
        "price": 5895,
        "occasions": ["sympathy", "thank-you", "new-baby"],
        "badges": [],
        "blurb": "A serene cream and green arrangement, ready to place.",
        "description": (
            "Named for the hawthorn hedges that turn the midlands white in May. "
            "Cream roses, green chrysanthemum and trailing ivy in a tall glass "
            "vase — dignified enough for sympathy without being sombre."
        ),
        "contains": "Cream roses, green chrysanthemum, lisianthus, ivy, vase.",
        "art": {
            "vessel": "vase",
            "vessel_colors": ["#dfe6e0", "#bccbc0"],
            "ribbon": "#8ca287",
            "backdrop": ["#f6f8f4", "#e2e9e0"],
            "foliage": "#5a7f5c",
            "blooms": [
                ["rose", ["#faf4e6", "#efe6d2"], 11],
                ["hydrangea", ["#dfe9d6", "#cddcc2"], 4],
                ["daisy", ["#ffffff"], 9],
            ],
        },
    },
    {
        "slug": "amber-glow-vase",
        "name": "Amber Glow",
        "collection": "vase-arrangements",
        "price": 6195,
        "occasions": ["birthday", "housewarming", "thank-you"],
        "badges": [],
        "blurb": "Warm rust and gold tones in a smoked amber vase.",
        "description": (
            "Rust chrysanthemum, toffee roses and dried grasses in a smoked amber "
            "vase. It suits a warm room in winter better than anything else we "
            "make, and the grasses can be kept long after the flowers are gone."
        ),
        "contains": "Toffee roses, rust chrysanthemum, dried grasses, amber vase.",
        "art": {
            "vessel": "vase",
            "vessel_colors": ["#d9a45f", "#b8823f"],
            "ribbon": "#8a6535",
            "backdrop": ["#fbf1e2", "#efdcc0"],
            "foliage": "#7d7f43",
            "blooms": [
                ["ranunculus", ["#c46a34", "#a95526"], 9],
                ["rose", ["#d99a63", "#c4834f"], 9],
                ["berry", ["#8a5a2b"], 12],
            ],
        },
    },
    {
        "slug": "serenity-white-vase",
        "name": "Serenity",
        "collection": "vase-arrangements",
        "price": 6895,
        "occasions": ["sympathy", "get-well", "anniversary"],
        "badges": [],
        "blurb": "White lilies and roses, low-scent and hospital-friendly.",
        "description": (
            "We use lily varieties chosen for a lighter scent, and we remove the "
            "stamens by hand so nothing stains. Delivered in a low vase that fits "
            "on a bedside locker — a detail hospitals appreciate."
        ),
        "contains": "White oriental lily, white roses, lisianthus, low vase.",
        "art": {
            "vessel": "vase",
            "vessel_colors": ["#e8e8e6", "#c9cac6"],
            "ribbon": "#a9b3ab",
            "backdrop": ["#f8f8f6", "#e7e8e5"],
            "foliage": "#628069",
            "blooms": [
                ["lily", ["#ffffff", "#f7f4ec"], 7],
                ["rose", ["#fbfaf6", "#efece2"], 9],
                ["gyp", ["#ffffff"], 20],
            ],
        },
    },
    # --------------------------------------------------------------- baskets
    {
        "slug": "cottage-garden-basket",
        "name": "Cottage Garden",
        "collection": "baskets",
        "price": 5595,
        "occasions": ["housewarming", "birthday", "thank-you", "just-because"],
        "badges": ["bestseller"],
        "blurb": "A gathered basket of garden favourites, ready to sit anywhere.",
        "description": (
            "Everything you would hope to find over a cottage wall: stocks, "
            "larkspur, spray roses and cornflower, arranged into a hydrated base "
            "inside a willow basket. No vase needed, and it travels well."
        ),
        "contains": "Spray roses, stocks, larkspur, cornflower, willow basket.",
        "art": {
            "vessel": "basket",
            "vessel_colors": ["#c69a63", "#a67a45"],
            "ribbon": "#8d9d72",
            "backdrop": ["#f8f4e9", "#e9e2ce"],
            "foliage": "#6e8f52",
            "blooms": [
                ["rose", ["#eaa8bd", "#dc8fa8"], 9],
                ["lily", ["#8fa6d8", "#7b93cb"], 5],
                ["daisy", ["#fdfaf0"], 9],
                ["gyp", ["#fffdf6"], 16],
            ],
        },
    },
    {
        "slug": "harvest-blooms-basket",
        "name": "Harvest",
        "collection": "baskets",
        "price": 5995,
        "occasions": ["housewarming", "thank-you", "congratulations"],
        "badges": ["seasonal"],
        "blurb": "Rust, ochre and wheat in a deep autumn basket.",
        "description": (
            "Our autumn basket, built around whatever the season is doing best — "
            "usually dahlias, hypericum berries, wheat and copper beech. Generous, "
            "rustic and long-lasting."
        ),
        "contains": "Dahlia, hypericum berry, wheat, copper beech, basket.",
        "art": {
            "vessel": "basket",
            "vessel_colors": ["#b07a45", "#8d5c2e"],
            "ribbon": "#7d6234",
            "backdrop": ["#faf0dd", "#eddcbb"],
            "foliage": "#75803c",
            "blooms": [
                ["peony", ["#c05a2e", "#a8461f"], 7],
                ["ranunculus", ["#e0952f", "#c87c1e"], 8],
                ["berry", ["#a02a24"], 16],
                ["gyp", ["#e8cf94"], 14],
            ],
        },
    },
    {
        "slug": "woodland-nest-basket",
        "name": "Woodland Nest",
        "collection": "baskets",
        "price": 5395,
        "occasions": ["new-baby", "get-well", "sympathy", "just-because"],
        "badges": [],
        "blurb": "Soft whites and mosses in a low, nest-shaped basket.",
        "description": (
            "The arrangement we named the company after. A low, wide basket lined "
            "with moss and filled with white spray roses, waxflower and ferns — "
            "it genuinely does look like a nest, and it sits happily on a windowsill."
        ),
        "contains": "White spray roses, waxflower, fern, moss, low basket.",
        "art": {
            "vessel": "basket",
            "vessel_colors": ["#b9a074", "#967e54"],
            "ribbon": "#7f8d6a",
            "backdrop": ["#f4f6ee", "#e0e6d8"],
            "foliage": "#5d7f52",
            "blooms": [
                ["rose", ["#fdfbf4", "#f2eee2"], 12],
                ["daisy", ["#ffffff"], 10],
                ["gyp", ["#fbfff5"], 22],
            ],
        },
    },
    # ---------------------------------------------------------------- luxury
    {
        "slug": "the-grand-nest",
        "name": "The Grand Nest",
        "collection": "luxury",
        "price": 12995,
        "occasions": ["anniversary", "congratulations", "romance"],
        "badges": ["luxury"],
        "blurb": "Our largest arrangement — over 70 stems in an oversized box.",
        "description": (
            "The one we build for engagements, big anniversaries and the occasional "
            "apology. More than seventy stems of roses, hydrangea and peony are "
            "domed into an oversized keepsake box. It takes one of our senior "
            "florists the better part of an hour."
        ),
        "contains": "70+ stems: roses, hydrangea, peony, eucalyptus, oversized box.",
        "art": {
            "vessel": "hatbox",
            "vessel_colors": ["#efe6d9", "#d5c8b6"],
            "ribbon": "#c4a15e",
            "backdrop": ["#fbf5ee", "#f0e2d5"],
            "foliage": "#5c8259",
            "blooms": [
                ["peony", ["#f0b3c2", "#e59bae"], 9],
                ["rose", ["#f8ddd8", "#eec6c3", "#fdeee9"], 15],
                ["hydrangea", ["#e9dced", "#dccce4"], 5],
                ["gyp", ["#ffffff"], 24],
            ],
        },
    },
    {
        "slug": "hundred-rose-statement",
        "name": "One Hundred Roses",
        "collection": "luxury",
        "price": 19995,
        "occasions": ["romance", "anniversary"],
        "badges": ["luxury"],
        "blurb": "One hundred red roses, hand-tied. Exactly what it says.",
        "description": (
            "One hundred Red Naomi roses, spiralled by hand into a single "
            "enormous bouquet and wrapped in black tissue and linen. It needs two "
            "hands to carry and a very large vase. Please order it a day ahead — "
            "we buy the roses in specially."
        ),
        "contains": "100 Red Naomi roses, black tissue, linen ribbon.",
        "art": {
            "vessel": "wrap",
            "vessel_colors": ["#2b2b2e", "#171719"],
            "ribbon": "#b8934a",
            "backdrop": ["#f5ebe8", "#e4cdc7"],
            "foliage": "#3f6647",
            "blooms": [
                ["rose", ["#a5122f", "#c11a3d", "#8a0c24"], 24],
            ],
        },
    },
    {
        "slug": "champagne-and-roses",
        "name": "Champagne & Roses",
        "collection": "luxury",
        "price": 14995,
        "occasions": ["anniversary", "congratulations", "romance"],
        "badges": ["luxury"],
        "blurb": "Ivory roses in a keepsake box with a half-bottle of champagne.",
        "description": (
            "Thirty ivory roses domed into a cream keepsake box, delivered "
            "alongside a chilled half-bottle of brut champagne and two flutes. "
            "Our most-requested engagement gift."
        ),
        "contains": "30 ivory roses, half-bottle champagne, two flutes, keepsake box.",
        "art": {
            "vessel": "hatbox",
            "vessel_colors": ["#f6efe2", "#dfd3bf"],
            "ribbon": "#c2a15e",
            "backdrop": ["#fcf7ec", "#f1e5d0"],
            "foliage": "#67865e",
            "blooms": [
                ["rose", ["#fbf3e2", "#f3e7d0", "#fdfaf2"], 17],
                ["ranunculus", ["#efe0c2"], 8],
                ["gyp", ["#ffffff"], 20],
            ],
        },
    },
    {
        "slug": "orchid-noir-luxe",
        "name": "Orchid Noir",
        "collection": "luxury",
        "price": 11995,
        "occasions": ["congratulations", "housewarming", "anniversary"],
        "badges": ["luxury"],
        "blurb": "Twin black-potted orchids with moss and bark detailing.",
        "description": (
            "Two premium double-stemmed phalaenopsis orchids planted together in "
            "a matte black ceramic trough, dressed with moss and birch bark. It "
            "will flower for three months or more and is our go-to corporate gift."
        ),
        "contains": "2 double-stem phalaenopsis, black ceramic trough, moss, bark.",
        "art": {
            "vessel": "pot",
            "vessel_colors": ["#26262a", "#141417"],
            "ribbon": "#6f7b6a",
            "backdrop": ["#f1f0ee", "#dcdad6"],
            "foliage": "#41684a",
            "blooms": [
                ["orchid", ["#fdfbf7", "#f2ece0", "#e8d9e4"], 11],
            ],
        },
    },
    # ---------------------------------------------------------------- plants
    {
        "slug": "phalaenopsis-orchid",
        "name": "White Phalaenopsis Orchid",
        "collection": "plants",
        "price": 4995,
        "occasions": ["housewarming", "thank-you", "get-well", "congratulations"],
        "badges": ["bestseller"],
        "blurb": "A twin-stem white orchid in a stone ceramic pot.",
        "description": (
            "A twin-stemmed white phalaenopsis, potted by us into a stone-glazed "
            "ceramic pot. With a splash of water once a week it will flower for "
            "two to three months, then again the following year."
        ),
        "contains": "Twin-stem phalaenopsis orchid, ceramic pot, care card.",
        "art": {
            "vessel": "pot",
            "vessel_colors": ["#ded8cd", "#c0b9ac"],
            "ribbon": "#9aa08e",
            "backdrop": ["#f7f6f2", "#e6e4dd"],
            "foliage": "#3f6b47",
            "blooms": [
                ["orchid", ["#ffffff", "#f8f4ea"], 10],
            ],
        },
    },
    {
        "slug": "peace-lily-plant",
        "name": "Peace Lily",
        "collection": "plants",
        "price": 3995,
        "occasions": ["sympathy", "housewarming", "get-well"],
        "badges": [],
        "blurb": "A lush spathiphyllum in a soft grey pot.",
        "description": (
            "Glossy dark leaves and white spathes, potted into a soft grey "
            "ceramic. Peace lilies are famously forgiving — they droop to tell "
            "you they are thirsty and perk back up within the hour."
        ),
        "contains": "Spathiphyllum plant, grey ceramic pot, care card.",
        "art": {
            "vessel": "pot",
            "vessel_colors": ["#c6c8c6", "#a7a9a7"],
            "ribbon": "#8d9a8d",
            "backdrop": ["#f4f6f3", "#e0e4de"],
            "foliage": "#2f5c3a",
            "blooms": [
                ["lily", ["#ffffff", "#f4f6ee"], 7],
            ],
        },
    },
    {
        "slug": "olive-tree-basket",
        "name": "Potted Olive Tree",
        "collection": "plants",
        "price": 6995,
        "occasions": ["housewarming", "congratulations", "thank-you"],
        "badges": ["new"],
        "blurb": "A young olive tree in a woven seagrass basket.",
        "description": (
            "A young, well-branched olive in a woven seagrass basket. Happiest "
            "on a bright windowsill or just outside a back door, and a far better "
            "housewarming gift than another scented candle."
        ),
        "contains": "Olive tree (approx. 60cm), seagrass basket, care card.",
        "art": {
            "vessel": "basket",
            "vessel_colors": ["#c8b48c", "#a89264"],
            "ribbon": "#8b8f6a",
            "backdrop": ["#f6f5ec", "#e5e5d5"],
            "foliage": "#6c8464",
            "blooms": [
                ["gyp", ["#dfe8d2"], 30],
            ],
        },
    },
    # ------------------------------------------------------------- gift sets
    {
        "slug": "bloom-and-bubbles",
        "name": "Bloom & Bubbles",
        "collection": "gift-sets",
        "price": 7995,
        "occasions": ["birthday", "congratulations", "anniversary"],
        "badges": ["bestseller"],
        "blurb": "A hand-tied bouquet with prosecco and Irish chocolates.",
        "description": (
            "Our Wild Meadow bouquet paired with a bottle of prosecco and a box "
            "of Lily O'Brien's chocolates, boxed together and delivered as a "
            "single gift. The easiest 'I forgot' recovery on the site."
        ),
        "contains": "Wild Meadow bouquet, prosecco (200ml), 210g chocolates.",
        "art": {
            "vessel": "wrap",
            "vessel_colors": ["#d9c3a5", "#bfa584"],
            "ribbon": "#c2a15e",
            "backdrop": ["#faf3e8", "#eee0c9"],
            "foliage": "#7a9152",
            "blooms": [
                ["rose", ["#f0c9a8", "#e6b48d"], 10],
                ["daisy", ["#fdfbf0"], 9],
                ["gyp", ["#fffdf5"], 20],
            ],
        },
    },
    {
        "slug": "sweet-nothings-set",
        "name": "Sweet Nothings",
        "collection": "gift-sets",
        "price": 6995,
        "occasions": ["romance", "anniversary", "birthday"],
        "badges": [],
        "blurb": "Pink roses, chocolates and a keepsake teddy.",
        "description": (
            "Pink roses in a keepsake box, a box of chocolates and a small linen-"
            "ribboned teddy. Unashamedly sentimental, and our top seller every "
            "February."
        ),
        "contains": "Pink rose hatbox, 210g chocolates, 25cm teddy.",
        "art": {
            "vessel": "hatbox",
            "vessel_colors": ["#e8b7bd", "#cf959d"],
            "ribbon": "#ffffff",
            "backdrop": ["#fdf1f2", "#f6dbdd"],
            "foliage": "#6a8b62",
            "blooms": [
                ["rose", ["#ea8fa8", "#dd7793", "#f3b3c3"], 15],
                ["gyp", ["#ffffff"], 22],
            ],
        },
    },
    {
        "slug": "pamper-and-petals",
        "name": "Pamper & Petals",
        "collection": "gift-sets",
        "price": 8495,
        "occasions": ["thank-you", "get-well", "birthday", "just-because"],
        "badges": [],
        "blurb": "A soft bouquet with a soy candle and hand balm.",
        "description": (
            "For a genuinely restful evening: our Coastal Blush bouquet with a "
            "hand-poured fig and bergamot candle and a tube of Irish hand balm, "
            "all boxed in tissue."
        ),
        "contains": "Coastal Blush bouquet, soy candle, hand balm.",
        "art": {
            "vessel": "wrap",
            "vessel_colors": ["#e7ded2", "#cdc2b4"],
            "ribbon": "#b09a86",
            "backdrop": ["#f8f4f0", "#e9e0d8"],
            "foliage": "#6d8a70",
            "blooms": [
                ["rose", ["#e0aeaa", "#cf9695"], 10],
                ["ranunculus", ["#f7efe8"], 8],
                ["gyp", ["#fdf8f4"], 18],
            ],
        },
    },
    # -------------------------------------------------------------- seasonal
    {
        "slug": "spring-awakening",
        "name": "Spring Awakening",
        "collection": "hand-tied",
        "price": 4595,
        "occasions": ["birthday", "just-because", "thank-you", "new-baby"],
        "badges": ["seasonal"],
        "blurb": "Tulips, narcissi and blossom — the first bouquet of the year.",
        "description": (
            "Irish tulips, scented narcissi and a few branches of blossom. It "
            "arrives tight and closed and then opens dramatically over two days, "
            "which is half the pleasure of it."
        ),
        "contains": "Irish tulips, narcissi, blossom branches, pussy willow.",
        "art": {
            "vessel": "wrap",
            "vessel_colors": ["#e2ddcd", "#c8c3b1"],
            "ribbon": "#c8d18a",
            "backdrop": ["#f7faee", "#e6efd6"],
            "foliage": "#79974f",
            "blooms": [
                ["tulip", ["#f2c33e", "#e8b12a", "#f7d972"], 9],
                ["tulip", ["#f0f0e6", "#e4e4d6"], 7],
                ["gyp", ["#fffef2"], 16],
            ],
        },
    },
    {
        "slug": "summer-sorbet",
        "name": "Summer Sorbet",
        "collection": "hand-tied",
        "price": 4895,
        "occasions": ["birthday", "congratulations", "just-because"],
        "badges": ["seasonal"],
        "blurb": "Raspberry, peach and lemon tones for the long evenings.",
        "description": (
            "Bright without being brash — raspberry spray roses, peach carnations "
            "and lemon solidago. Made for a kitchen table with the back door open."
        ),
        "contains": "Spray roses, carnation, solidago, ammi, eucalyptus.",
        "art": {
            "vessel": "wrap",
            "vessel_colors": ["#e5d8c4", "#cbbda6"],
            "ribbon": "#e79ab0",
            "backdrop": ["#fdf4f0", "#f6e0d9"],
            "foliage": "#77914f",
            "blooms": [
                ["rose", ["#e8567e", "#d43e68"], 8],
                ["carnation", ["#f8ac7f", "#f2946a"], 8],
                ["daisy", ["#fdf3c8"], 9],
                ["gyp", ["#fffdf2"], 16],
            ],
        },
    },
    {
        "slug": "autumn-ember",
        "name": "Autumn Ember",
        "collection": "hand-tied",
        "price": 5395,
        "occasions": ["birthday", "thank-you", "housewarming"],
        "badges": ["seasonal"],
        "blurb": "Burnt orange dahlias and berried foliage.",
        "description": (
            "Burnt orange dahlias, hypericum berries and copper beech, tied loose "
            "and low. The colours are exactly the ones outside the studio window "
            "in October."
        ),
        "contains": "Dahlia, hypericum berry, copper beech, oak foliage.",
        "art": {
            "vessel": "wrap",
            "vessel_colors": ["#d3b48c", "#b3936a"],
            "ribbon": "#8a5a2f",
            "backdrop": ["#fbf0e0", "#efd9bd"],
            "foliage": "#77743a",
            "blooms": [
                ["peony", ["#cf5f28", "#b44a18"], 8],
                ["ranunculus", ["#e08a2a", "#c9721a"], 8],
                ["berry", ["#8f2118"], 16],
            ],
        },
    },
    {
        "slug": "winter-frost",
        "name": "Winter Frost",
        "collection": "hand-tied",
        "price": 5695,
        "occasions": ["thank-you", "just-because", "sympathy", "housewarming"],
        "badges": ["seasonal"],
        "blurb": "Icy whites, silver eucalyptus and blue spruce.",
        "description": (
            "White roses and anemones against silver eucalyptus and blue spruce, "
            "with a few pine cones threaded through. It smells like December and "
            "lasts right through the Christmas week."
        ),
        "contains": "White roses, anemone, blue spruce, silver eucalyptus, cones.",
        "art": {
            "vessel": "wrap",
            "vessel_colors": ["#dfe3e6", "#c3c9ce"],
            "ribbon": "#93a5ae",
            "backdrop": ["#f4f7f9", "#dfe7ec"],
            "foliage": "#4d6f66",
            "blooms": [
                ["rose", ["#fdfdfd", "#eff2f2"], 11],
                ["daisy", ["#ffffff"], 8],
                ["thistle", ["#8fa3b4"], 8],
                ["gyp", ["#ffffff"], 22],
            ],
        },
    },
]

# --------------------------------------------------------------------------
# Editorial content
# --------------------------------------------------------------------------

TESTIMONIALS = [
    {
        "quote": (
            "Ordered at 1pm from London for my mam in Rathmines and they were on "
            "her table before she'd finished her tea. She sent me eleven photos."
        ),
        "author": "Aoife M.",
        "location": "Dublin 6",
        "rating": 5,
    },
    {
        "quote": (
            "The Grafton is the only bouquet I've ever bought that still looked "
            "good a fortnight later. Worth every cent."
        ),
        "author": "Declan O.",
        "location": "Cork",
        "rating": 5,
    },
    {
        "quote": (
            "We use Nested Blooms for the reception desk every week. Same florist "
            "every time, never once been let down."
        ),
        "author": "Sinéad K.",
        "location": "Office manager, Dublin 2",
        "rating": 5,
    },
    {
        "quote": (
            "I rang in a panic about a funeral arrangement and they could not have "
            "been kinder. The tribute was beautiful and exactly right."
        ),
        "author": "Michael B.",
        "location": "Galway",
        "rating": 5,
    },
    {
        "quote": (
            "Peony Dream arrived in bud and opened over three days. My wife has "
            "already asked when they're back in season."
        ),
        "author": "Tom R.",
        "location": "Wicklow",
        "rating": 5,
    },
    {
        "quote": (
            "Beautiful flowers, but the handwritten card is what made it. Lovely "
            "touch that the big websites don't bother with."
        ),
        "author": "Grace N.",
        "location": "Limerick",
        "rating": 5,
    },
]

FAQS = [
    {
        "category": "Delivery",
        "question": "Do you deliver on the same day?",
        "answer": (
            "Yes — across Dublin, Kildare and Wicklow for orders placed before "
            "2pm, seven days a week. Everywhere else in Ireland is next-day, with "
            "a 4pm cut-off."
        ),
    },
    {
        "category": "Delivery",
        "question": "Where do you deliver?",
        "answer": (
            "Every county in the Republic of Ireland and Northern Ireland. Dublin, "
            "Kildare and Wicklow are covered by our own drivers; elsewhere we use "
            "a next-day courier who delivers the boxed arrangement in water."
        ),
    },
    {
        "category": "Delivery",
        "question": "What if nobody is home?",
        "answer": (
            "Our driver will try a neighbour, then leave the flowers in a safe, "
            "shaded spot and photograph where they left them. You will get a text "
            "either way. Nothing is ever left in direct sun."
        ),
    },
    {
        "category": "Delivery",
        "question": "Can I choose a delivery date in the future?",
        "answer": (
            "You can pick any date up to ninety days ahead at checkout. We will "
            "buy the flowers fresh for that morning."
        ),
    },
    {
        "category": "Orders",
        "question": "Can I include a message card?",
        "answer": (
            "Every order includes a card, handwritten by the florist who makes "
            "your arrangement. Add your message at checkout — there is no charge."
        ),
    },
    {
        "category": "Orders",
        "question": "Can I order without creating an account?",
        "answer": (
            "Yes. Checkout works perfectly well as a guest. Creating an account "
            "just means your addresses and order history are saved for next time."
        ),
    },
    {
        "category": "Orders",
        "question": "Can I change or cancel my order?",
        "answer": (
            "Ring us on +353 1 555 0198 before 4pm on the day before delivery and "
            "we can change anything. After that the flowers are already bought and "
            "conditioned for you."
        ),
    },
    {
        "category": "Flowers",
        "question": "How long will the flowers last?",
        "answer": (
            "We guarantee seven days. In practice most of our arrangements go a "
            "good deal longer — recut the stems at an angle every few days and "
            "change the water and you will often get two weeks."
        ),
    },
    {
        "category": "Flowers",
        "question": "Will it look exactly like the photograph?",
        "answer": (
            "It will match the size, palette and style. Because we buy at market "
            "each morning, an individual variety may be swapped for something "
            "better on the day — that is a feature of buying fresh, not a "
            "substitution we take lightly."
        ),
    },
    {
        "category": "Flowers",
        "question": "Are your flowers Irish?",
        "answer": (
            "Where we can. Our peonies, tulips, daffodils and much of our foliage "
            "come from growers in Meath, Wicklow and Cork. The rest is bought at "
            "the Dutch auction and lands in Dublin within thirty-six hours."
        ),
    },
    {
        "category": "Payment",
        "question": "What payment methods do you accept?",
        "answer": (
            "All major credit and debit cards, plus Apple Pay and Google Pay. "
            "Corporate customers can be set up on monthly invoicing."
        ),
    },
    {
        "category": "Payment",
        "question": "Do you offer a guarantee?",
        "answer": (
            "Our seven-day freshness guarantee is unconditional. If your flowers "
            "wilt inside a week, send us a photograph and we will replace them or "
            "refund you in full — no need to return anything."
        ),
    },
]

# City landing pages used for local SEO.
DELIVERY_AREAS = [
    {
        "slug": "dublin",
        "name": "Dublin",
        "same_day": True,
        "intro": (
            "Our studio is in Dublin 8 and our own drivers cover every Dublin "
            "postcode, from Balbriggan to Bray. Order before 2pm and your flowers "
            "arrive the same afternoon."
        ),
        "districts": [
            "Dublin 1", "Dublin 2", "Dublin 3", "Dublin 4", "Dublin 5",
            "Dublin 6", "Dublin 6W", "Dublin 7", "Dublin 8", "Dublin 9",
            "Dublin 10", "Dublin 11", "Dublin 12", "Dublin 13", "Dublin 14",
            "Dublin 15", "Dublin 16", "Dublin 17", "Dublin 18", "Dublin 20",
            "Dublin 22", "Dublin 24", "Blackrock", "Dún Laoghaire", "Swords",
            "Malahide", "Howth", "Lucan", "Tallaght", "Blanchardstown",
        ],
    },
    {
        "slug": "cork",
        "name": "Cork",
        "same_day": False,
        "intro": (
            "Next-day delivery across Cork city and county, from Ballincollig to "
            "Youghal. Arrangements travel boxed and in water, so they arrive as "
            "fresh as they leave us."
        ),
        "districts": [
            "Cork City", "Ballincollig", "Carrigaline", "Cobh", "Midleton",
            "Mallow", "Bandon", "Youghal", "Kinsale", "Fermoy", "Clonakilty",
        ],
    },
    {
        "slug": "galway",
        "name": "Galway",
        "same_day": False,
        "intro": (
            "Next-day delivery throughout Galway city and county — Salthill, "
            "Oranmore, Tuam, Loughrea and out into Connemara."
        ),
        "districts": [
            "Galway City", "Salthill", "Oranmore", "Tuam", "Loughrea",
            "Ballinasloe", "Athenry", "Clifden", "Gort", "Moycullen",
        ],
    },
    {
        "slug": "limerick",
        "name": "Limerick",
        "same_day": False,
        "intro": (
            "Next-day flower delivery across Limerick city and county, including "
            "Castletroy, Adare, Newcastle West and Kilmallock."
        ),
        "districts": [
            "Limerick City", "Castletroy", "Dooradoyle", "Raheen", "Adare",
            "Newcastle West", "Abbeyfeale", "Kilmallock", "Annacotty",
        ],
    },
    {
        "slug": "kildare",
        "name": "Kildare",
        "same_day": True,
        "intro": (
            "Same-day delivery in Kildare for orders placed before 2pm. Naas, "
            "Newbridge, Maynooth, Celbridge and Leixlip are all on our own "
            "driver's route."
        ),
        "districts": [
            "Naas", "Newbridge", "Maynooth", "Celbridge", "Leixlip", "Kildare Town",
            "Athy", "Kilcock", "Clane", "Sallins", "Monasterevin",
        ],
    },
    {
        "slug": "wicklow",
        "name": "Wicklow",
        "same_day": True,
        "intro": (
            "Same-day delivery across north Wicklow before 2pm, and next-day "
            "everywhere else in the Garden County — which is, after all, where we "
            "buy a good deal of our foliage."
        ),
        "districts": [
            "Bray", "Greystones", "Wicklow Town", "Arklow", "Blessington",
            "Newtownmountkennedy", "Delgany", "Enniskerry", "Rathdrum",
        ],
    },
    {
        "slug": "belfast",
        "name": "Belfast",
        "same_day": False,
        "intro": (
            "Next-day delivery across Belfast and Northern Ireland. Prices are "
            "shown in euro and there are no customs charges on flowers."
        ),
        "districts": [
            "Belfast City", "Lisburn", "Bangor", "Newtownabbey", "Holywood",
            "Carrickfergus", "Newtownards", "Antrim", "Ballymena",
        ],
    },
    {
        "slug": "waterford",
        "name": "Waterford",
        "same_day": False,
        "intro": (
            "Next-day delivery to Waterford city, Tramore, Dungarvan and across "
            "the south east."
        ),
        "districts": [
            "Waterford City", "Tramore", "Dungarvan", "Dunmore East",
            "Portlaw", "Lismore", "Ardmore",
        ],
    },
]


def product_by_slug(slug):
    """Return the raw catalogue dict for ``slug``, or ``None``."""
    for product in PRODUCTS:
        if product["slug"] == slug:
            return product
    return None
