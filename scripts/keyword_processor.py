#!/usr/bin/env python3
"""
IndaVillas Keyword Strategy Processor v3
ALL 25 files. Broad relevance. 100+ article clusters.
Includes general Airbnb tips, informational content, and how-to guides.
"""

import csv
import re
import os
from collections import defaultdict

# ─── CONFIG ───────────────────────────────────────────────────────────────────

INPUT_DIR = "/Users/kristapsjansons/Downloads"
INPUT_FILES = [f for f in os.listdir(INPUT_DIR) if f.startswith("keywords_gap for") and f.endswith(".csv")]
INPUT_FILES = [os.path.join(INPUT_DIR, f) for f in INPUT_FILES]

OUTPUT_DIR = "/Users/kristapsjansons/Documents_Local/Clone - Antigravity/IndaVillas/keyword_strategy"

# ─── HELPERS ─────────────────────────────────────────────────────────────────

def normalize_keyword(kw):
    kw = kw.lower().strip()
    kw = re.sub(r'\s+', ' ', kw)
    kw = re.sub(r'[""''\u200b]', '', kw)
    return kw

def parse_volume(v):
    if not v: return 0
    v = str(v).replace(',', '').replace('$', '').strip()
    try: return int(float(v))
    except ValueError: return 0

def parse_float(v):
    if not v: return 0.0
    v = str(v).replace(',', '').replace('$', '').strip()
    try: return float(v)
    except ValueError: return 0.0

# ─── BROAD RELEVANCE FILTER ─────────────────────────────────────────────────
# Now we keep everything that relates to:
# - Airbnb (hosting, guest, tips, reviews, operations, anything)
# - VRBO / Booking.com
# - Vacation rentals / holiday rentals / short-term rentals
# - Villas / luxury hospitality
# - Property management (for rentals)
# - Marketing, SEO, revenue, pricing for any of the above
# - Website design for rentals
# - General hospitality topics our audience cares about

def has_broad_relevance(kw):
    """Broad filter: keep anything related to STR/Airbnb/VR/villa ecosystem."""
    patterns = [
        r'\bairbnb\b', r'\bvrbo\b', r'\bbooking\.com\b',
        r'\b(vacation|holiday)\s*rental', r'\bshort[\s-]?term\s*rental',
        r'\bstr\b', r'\bvilla\b', r'\brental\s*property',
        r'\bhost(ing|s|ed)?\b.*\b(airbnb|rental|guest|vacation|property)',
        r'\b(airbnb|rental|guest|vacation|property)\b.*\bhost',
        r'\bsuperhost\b', r'\bluxe\b',
        r'\bguest\b.*\b(review|checklist|experience|commun|book|stay)',
        r'\bproperty\s*manag', r'\brental\s*manag',
        r'\b(seo|marketing|brand|content|copy|website|web\s*design|ppc|social\s*media|email\s*market|instagram|facebook\s*ad|google\s*ad)\b.*\b(rental|airbnb|vrbo|villa|host|str|vacation|hospitality)',
        r'\b(rental|airbnb|vrbo|villa|host|str|vacation|hospitality)\b.*\b(seo|marketing|brand|content|copy|website|web\s*design|ppc|social\s*media|email\s*market)',
        r'\b(revenue|pricing|dynamic\s*pric|yield|occupancy|adr|revpar|nightly\s*rate)\b.*\b(rental|airbnb|vrbo|villa|str|host|vacation|property)',
        r'\b(rental|airbnb|vrbo|villa|str|host|vacation|property)\b.*\b(revenue|pricing|dynamic|yield|occupancy)',
        r'\bdirect\s*book', r'\bchannel\s*manag',
        r'\bota\b', r'\bonline\s*travel',
        r'\b(event|wedding|retreat)\b.*\b(villa|venue|rental)',
        r'\b(villa|rental)\b.*\b(event|wedding|retreat)',
        r'\bamen(ity|ities)\b.*\b(rental|airbnb|villa|guest)',
        r'\b(rental|airbnb|villa|guest)\b.*\bamen(ity|ities)',
        r'\bupsell', r'\bancillary\s*revenue',
        r'\b(cold\s*plunge|hot\s*tub|pool|sauna)\b.*\b(airbnb|rental|villa)',
        r'\b(airbnb|rental|villa)\b.*\b(cold\s*plunge|hot\s*tub|pool|sauna)',
        r'\bcheck[\s-]?(in|out)\b.*\b(airbnb|rental|villa|guest)',
        r'\b(airbnb|rental|villa|guest)\b.*\bcheck[\s-]?(in|out)',
        r'\bcleaning\b.*\b(airbnb|rental|villa|str)',
        r'\b(airbnb|rental|villa|str)\b.*\bcleaning',
        r'\b(co[\s-]?host|cohost)', r'\bproperty\s*manage',
        r'\b(guesty|hostaway|lodgify|pricelabs|wheelhouse|beyond\s*pricing|hospitable|ownerrez|tokeet|hostfully|turno|breezeway|uplisting|rankbreeze)',
        r'\b(listing|list)\b.*\b(airbnb|vrbo|rental|optimization)',
        r'\b(airbnb|vrbo|rental)\b.*\b(listing|list)\b',
        r'\brental\s*(logo|brand|website|income|invest|arbitrage|property)',
        r'\b(logo|brand|website|income|invest)\b.*\brental',
        r'\b(furnish|decor|interior|design)\b.*\b(airbnb|rental|villa|str)',
        r'\b(airbnb|rental|villa|str)\b.*\b(furnish|decor|interior)',
        r'\b(insurance|liability|permit|license|regulation|tax|law|legal|llc)\b.*\b(airbnb|rental|str|host|vacation)',
        r'\b(airbnb|rental|str|host|vacation)\b.*\b(insurance|liability|permit|license|regulation|tax|law|legal|llc)',
        r'\b(automat|workflow|ai|smart|tech)\b.*\b(airbnb|rental|villa|str|host)',
        r'\b(airbnb|rental|villa|str|host)\b.*\b(automat|workflow|ai|smart)',
        r'\b(photo|photograph|picture|image|video|virtual\s*tour)\b.*\b(airbnb|rental|villa|listing)',
        r'\b(airbnb|rental|villa|listing)\b.*\b(photo|photograph|picture|video)',
        r'\b(review|rating|feedback)\b.*\b(airbnb|vrbo|rental|guest|host)',
        r'\b(airbnb|vrbo|rental|guest|host)\b.*\b(review|rating|feedback)',
        r'\b(welcome|greeting|gift|basket|amenity)\b.*\b(guest|airbnb|rental)',
        r'\b(guest|airbnb|rental)\b.*\b(welcome|greeting|gift|basket)',
        r'\b(concierge|butler|chef)\b.*\b(villa|rental|guest|luxury)',
        r'\b(villa|rental|guest|luxury)\b.*\b(concierge|butler|chef)',
        r'\bturnover\b.*\b(rental|airbnb|str)', r'\b(rental|airbnb|str)\b.*\bturnover',
        r'\b(midterm|medium[\s-]?term)\b.*\brental',
        r'\b(airbnb|vrbo|rental)\b.*\b(competitor|comparison|vs)\b',
        r'\b(competitor|comparison)\b.*\b(airbnb|vrbo|rental)',
        r'\b(cabin|chalet|cottage|beach\s*house|lake\s*house|mountain\s*home|glamping|treehouse|tiny\s*house)\b.*\b(rental|airbnb|host|book|market)',
        r'\b(rental|airbnb|host|book|market)\b.*\b(cabin|chalet|cottage|beach\s*house|lake\s*house)',
        r'\b(smart\s*lock|keyless|keypad|lockbox|self[\s-]?check)',
        r'\b(noise\s*monitor|security\s*cam|ring|nest)',
        r'\bhospitality\b',
    ]
    for p in patterns:
        if re.search(p, kw, re.IGNORECASE):
            return True
    return False

# US states, major cities, and international locations to filter guest-side booking queries
LOCATION_WORDS = {
    # US States
    'alabama','alaska','arizona','arkansas','california','colorado','connecticut','delaware',
    'florida','georgia','hawaii','idaho','illinois','indiana','iowa','kansas','kentucky',
    'louisiana','maine','maryland','massachusetts','michigan','minnesota','mississippi',
    'missouri','montana','nebraska','nevada','hampshire','jersey','mexico','york',
    'carolina','dakota','ohio','oklahoma','oregon','pennsylvania','rhode','island',
    'tennessee','texas','utah','vermont','virginia','washington','wisconsin','wyoming',
    # US Cities / Resort Areas
    'orlando','miami','tampa','naples','sarasota','destin','pensacola','jacksonville',
    'fort lauderdale','clearwater','daytona','kissimmee','gainesville','ocala',
    'key west','marathon','islamorada','anna maria','holmes beach','bradenton',
    'siesta key','longboat key','sanibel','captiva','navarre','panama city','perdido',
    'galveston','houston','dallas','austin','san antonio','corpus christi','south padre',
    'nashville','gatlinburg','pigeon forge','sevierville','memphis','knoxville',
    'myrtle beach','hilton head','charleston','kiawah','folly','pawleys',
    'asheville','outer banks','nags head','duck','corolla','emerald isle','wrightsville',
    'poconos','ocean city','cape may','long beach','montauk','hamptons','lake george',
    'catskills','adirondacks','finger lakes','niagara',
    'scottsdale','sedona','tucson','flagstaff','phoenix','mesa','tempe',
    'las vegas','reno','lake tahoe','incline village','truckee',
    'san diego','los angeles','palm springs','big bear','joshua tree','mammoth',
    'santa barbara','monterey','carmel','napa','sonoma','wine country',
    'san francisco','sacramento','lake arrowhead',
    'denver','breckenridge','vail','aspen','steamboat','telluride','estes park',
    'park city','moab','st george','brian head','sundance',
    'portland','bend','sunriver','hood river','cannon beach','seaside',
    'seattle','leavenworth','chelan','walla walla','whidbey',
    'savannah','tybee','jekyll','brunswick','st simons','blue ridge',
    'new orleans','baton rouge','lafayette',
    'boston','cape cod','nantucket','martha','provincetown',
    'chicago','lake geneva','galena','michigan city',
    'detroit','traverse city','mackinac','saugatuck','holland',
    'minneapolis','duluth','brainerd',
    'indianapolis','brown county',
    'st louis','branson','ozarks','table rock',
    'kansas city','eureka springs',
    'davenport','champions gate','reunion','solterra','storey lake',
    'celebration','windermere','winter garden','haines city',
    # International
    'cancun','tulum','playa del carmen','cabo','puerto vallarta','cozumel','riviera maya',
    'punta cana','jamaica','bahamas','barbados','aruba','curacao','st lucia','turks',
    'costa rica','belize','panama','colombia','ecuador','peru','brazil',
    'london','paris','rome','barcelona','madrid','lisbon','amsterdam','berlin','munich',
    'prague','vienna','budapest','dubrovnik','santorini','mykonos','crete','malta','sicily',
    'amalfi','tuscany','provence','cannes','nice','ibiza','mallorca','algarve',
    'dubai','abu dhabi','bali','phuket','koh samui','langkawi','boracay',
    'tokyo','osaka','kyoto','sydney','melbourne','gold coast','queenstown','fiji',
    'cape town','zanzibar','mauritius','seychelles','maldives',
    'whistler','banff','jasper','mont tremblant','niagara on the lake','muskoka','tofino',
}

LOCATION_PHRASES = [
    'holmes beach', 'anna maria', 'black mountain', 'playa del carmen', 'siesta key',
    'longboat key', 'elk grove', 'san antonio', 'south padre', 'pigeon forge',
    'hilton head', 'outer banks', 'nags head', 'ocean city', 'cape may',
    'long beach', 'lake george', 'finger lakes', 'palm springs', 'big bear',
    'joshua tree', 'santa barbara', 'wine country', 'lake arrowhead', 'estes park',
    'park city', 'st george', 'brian head', 'hood river', 'cannon beach',
    'walla walla', 'st simons', 'blue ridge', 'new orleans', 'baton rouge',
    'cape cod', 'lake geneva', 'michigan city', 'traverse city', 'brown county',
    'st louis', 'table rock', 'kansas city', 'eureka springs', 'champions gate',
    'storey lake', 'winter garden', 'haines city', 'key west', 'panama city',
    'corpus christi', 'myrtle beach', 'emerald isle', 'fort lauderdale',
    'los angeles', 'san diego', 'san francisco', 'las vegas', 'lake tahoe',
    'incline village', 'puerto vallarta', 'riviera maya', 'punta cana',
    'mont tremblant', 'niagara on the lake', 'new braunfels', 'salt lake',
    'lake norman', 'abu dhabi', 'koh samui', 'gold coast', 'cape town',
    'del carmen',
]

# Words that appear in many vacation booking queries with locations
VACATION_LOCATION_WORDS = {
    'beach', 'lake', 'mountain', 'island', 'coast', 'bay', 'river', 'springs',
    'park', 'canyon', 'creek', 'falls', 'harbor', 'port', 'shore', 'ridge',
    'valley', 'summit', 'grove', 'heights', 'bluff', 'cove', 'point',
    'oahu', 'maui', 'kona', 'kauai', 'waikiki',  # Hawaii
    'nc', 'fl', 'tx', 'ca', 'nj', 'ny', 'sc', 'tn', 'va', 'ga', 'az', 'co', 'or', 'wa',  # State abbreviations
}

def is_location_booking_query(kw):
    """Detect guest-side location-based booking queries."""
    words = set(kw.split())
    
    # Check multi-word location phrases first
    has_location = False
    for phrase in LOCATION_PHRASES:
        if phrase in kw:
            has_location = True
            break
    
    # Check single-word locations
    if not has_location:
        has_location = bool(words & LOCATION_WORDS)
    
    # Check vacation location words (only if combined with rental/vacation terms)
    if not has_location:
        has_vac_loc = bool(words & VACATION_LOCATION_WORDS)
        has_rental = bool(words & {'rental', 'rentals', 'vacation', 'holiday', 'vrbo', 'cabin', 'cabins', 'cottage', 'cottages', 'condo', 'condos', 'house', 'houses', 'villa', 'villas', 'chalet'})
        if has_vac_loc and has_rental:
            has_location = True
    
    if not has_location:
        return False
    
    # If it has a location BUT also has a service/strategy term, keep it
    service_terms = {'seo', 'marketing', 'branding', 'strategy', 'consultant', 'agency',
                     'optimization', 'optimize', 'revenue', 'pricing', 'content', 'website',
                     'design', 'copywriting', 'ppc', 'ads', 'email', 'social', 'upsell',
                     'how', 'guide', 'tips', 'checklist', 'best', 'top', 'review',
                     'superhost', 'algorithm', 'ranking', 'direct', 'channel',
                     'automation', 'automated', 'cleaning', 'turnover', 'amenities',
                     'photography', 'photo', 'brand', 'logo', 'conversion', 'arbitrage',
                     'investment', 'tax', 'insurance', 'llc', 'regulations', 'permit',
                     'furnishing', 'interior', 'software', 'tool', 'vs', 'comparison',
                     'cancel', 'refund', 'policy', 'customer', 'service', 'contact',
                     'wedding', 'retreat', 'event', 'luxe', 'luxury', 'premium',
                     'management', 'manager', 'hosting', 'host', 'start', 'begin',
                     'income', 'profit', 'roi', 'yield', 'occupancy', 'adr', 'revpar'}
    if words & service_terms:
        return False
    return True

def is_hard_excluded(kw):
    """Exclude truly useless terms and location-based booking queries."""
    patterns = [
        r'\bnear\s+me\b',
        r'\blogin\b', r'\bsign[\s-]?in\b',
        r'^(str|booking\s*now|web\s*rental)$',
        r'^(airbnb|vrbo|booking|rental|villa|seo|marketing|agency|host|review|price)$',
        r'\bthrowing\s*a\s*haymaker', r'\bhaymaker\s*group\b',
        r'\bmusic\s+in\s+marketing\b',
    ]
    for p in patterns:
        if re.search(p, kw, re.IGNORECASE):
            return True
    if is_location_booking_query(kw):
        return True
    return False

# ─── GRANULAR CLUSTER DEFINITIONS ────────────────────────────────────────────
# Goal: 100+ topics. Each cluster = 1 article.

CLUSTER_DEFINITIONS = [
    # ── AIRBNB LISTING OPTIMIZATION ───
    {"name": "Airbnb Listing Optimization (Complete Guide)", "patterns": [r'\bairbnb\b.*\blisting\s*optim', r'\boptim\b.*\bairbnb\b.*\blisting']},
    {"name": "Airbnb Title Optimization", "patterns": [r'\bairbnb\b.*\btitle\b', r'\btitle\b.*\bairbnb\b', r'\bcatchy\b.*\bairbnb\b.*\btitle']},
    {"name": "Airbnb Description Writing", "patterns": [r'\bairbnb\b.*\bdescription\b', r'\bdescription\b.*\bairbnb\b', r'\bairbnb\b.*\bcopy(writing)?']},
    {"name": "Airbnb Cover Photo & Photos", "patterns": [r'\bairbnb\b.*\b(cover\s*photo|photo|picture|image)', r'\b(photo|picture|image)\b.*\bairbnb\b']},
    {"name": "Airbnb Photography Tips", "patterns": [r'\bairbnb\b.*\bphotograph', r'\bphotograph\b.*\bairbnb\b', r'\brental\b.*\bphotograph', r'\blisting\b.*\bphoto\b.*\btip']},
    
    # ── AIRBNB SEO ───
    {"name": "Airbnb SEO Strategy", "patterns": [r'\bairbnb\b.*\bseo\b', r'\bseo\b.*\bairbnb\b']},
    {"name": "Airbnb Search Algorithm", "patterns": [r'\bairbnb\b.*\balgorithm\b', r'\balgorithm\b.*\bairbnb\b']},
    {"name": "Airbnb Search Ranking Factors", "patterns": [r'\bairbnb\b.*\b(rank|ranking|first\s*page)', r'\b(rank|ranking)\b.*\bairbnb\b']},
    {"name": "RankBreeze & Airbnb Ranking Tools", "patterns": [r'\brankbreeze\b']},
    
    # ── VRBO ───
    {"name": "VRBO Listing Optimization", "patterns": [r'\bvrbo\b.*\b(listing|optim|title|description)', r'\b(listing|optim)\b.*\bvrbo\b']},
    {"name": "VRBO SEO & Marketing", "patterns": [r'\bvrbo\b.*\b(seo|market|rank|strateg)', r'\b(seo|market)\b.*\bvrbo\b']},
    {"name": "VRBO Pricing & Fees", "patterns": [r'\bvrbo\b.*\b(pric|fee|cost|commission)', r'\b(pric|fee|cost)\b.*\bvrbo\b']},
    {"name": "VRBO Owner Guide", "patterns": [r'\bvrbo\b.*\b(owner|host|manag|list)', r'\b(owner|host)\b.*\bvrbo\b']},
    {"name": "Airbnb vs VRBO", "patterns": [r'\bairbnb\b.*\bvs\b.*\bvrbo', r'\bvrbo\b.*\bvs\b.*\bairbnb', r'\bairbnb\b.*\bor\b.*\bvrbo']},
    
    # ── VACATION RENTAL SEO ───
    {"name": "Vacation Rental SEO", "patterns": [r'\b(vacation|holiday)\s*rental\b.*\bseo', r'\bseo\b.*\b(vacation|holiday)\s*rental']},
    {"name": "Short-Term Rental SEO", "patterns": [r'\bshort[\s-]?term\s*rental\b.*\bseo', r'\bseo\b.*\bshort[\s-]?term', r'\bstr\b.*\bseo\b']},
    
    # ── PRICING & REVENUE ───
    {"name": "Airbnb Pricing Strategy", "patterns": [r'\bairbnb\b.*\bpric(ing|e)\b.*\b(strat|optim|set|tip)', r'\bpric(ing|e)\b.*\bstrat\b.*\bairbnb']},
    {"name": "Airbnb Pricing Calculator & Tools", "patterns": [r'\bairbnb\b.*\b(pric.*calculator|calculator|estimat|revenue\s*estimat)', r'\b(calculator|estimat)\b.*\bairbnb']},
    {"name": "Dynamic Pricing for Vacation Rentals", "patterns": [r'\bdynamic\s*pric', r'\bdynamic\b.*\bpric']},
    {"name": "PriceLabs Guide", "patterns": [r'\bpricelabs\b']},
    {"name": "Wheelhouse & Beyond Pricing", "patterns": [r'\bwheelhouse\b', r'\bbeyond\s*pricing\b']},
    {"name": "Yield Management for STRs", "patterns": [r'\byield\s*manag', r'\byield\b.*\b(rental|str|airbnb|vacation)']},
    {"name": "Vacation Rental Revenue Management", "patterns": [r'\brevenue\s*manag.*\b(rental|str|airbnb|vacation|property)', r'\b(rental|str|airbnb|vacation)\b.*\brevenue\s*manag']},
    {"name": "STR Revenue & Income", "patterns": [r'\b(str|airbnb|rental|vacation)\b.*\b(revenue|income|earn|profit|roi)', r'\b(revenue|income|earn|profit|roi)\b.*\b(str|airbnb|rental)']},
    {"name": "Occupancy Rate Optimization", "patterns": [r'\boccupancy\b.*\b(rate|optim|increas|improv)', r'\b(rate|optim)\b.*\boccupancy']},
    {"name": "ADR & RevPAR for Rentals", "patterns": [r'\badr\b', r'\brev\s*par\b', r'\baverage\s*daily\s*rate']},
    {"name": "Nightly Rate Strategy", "patterns": [r'\bnightly\s*rate', r'\brate\s*strat\b.*\b(rental|airbnb)']},
    {"name": "Airbnb Sorting by Price", "patterns": [r'\bairbnb\b.*\bsort\b.*\bprice', r'\bsort\b.*\bprice\b.*\bairbnb', r'\bairbnb\b.*\bsort']},
    
    # ── DIRECT BOOKING ───
    {"name": "Direct Booking Strategy for Rentals", "patterns": [r'\bdirect\s*book', r'\bbook\s*direct']},
    {"name": "Direct Booking Website for STRs", "patterns": [r'\b(direct|own)\b.*\b(book|rental)\b.*\bwebsite', r'\bwebsite\b.*\bdirect\b.*\bbook']},
    
    # ── CHANNEL & OTA ───
    {"name": "OTA Strategy for Vacation Rentals", "patterns": [r'\bota\b.*\b(strat|optim|market|manag)', r'\b(strat|manag)\b.*\bota\b']},
    {"name": "Channel Management for Rentals", "patterns": [r'\bchannel\s*(manag|market|strat)', r'\bmulti[\s-]?channel', r'\bcross[\s-]?platform']},
    {"name": "Distribution Strategy for STRs", "patterns": [r'\bdistribution\b.*\b(strat|channel|rental)', r'\b(rental|str|vacation)\b.*\bdistribution']},
    
    # ── CONTENT & COPY ───
    {"name": "Vacation Rental Content Marketing", "patterns": [r'\b(vacation|holiday)\s*rental\b.*\bcontent', r'\bcontent\b.*\b(vacation|holiday)\s*rental']},
    {"name": "Airbnb Copywriting & Listing Copy", "patterns": [r'\b(airbnb|listing|rental)\b.*\bcopy(writing)?', r'\bcopy(writing)?\b.*\b(airbnb|listing|rental)']},
    {"name": "Vacation Rental Description Examples", "patterns": [r'\b(vacation|holiday|rental)\b.*\bdescription\b.*\b(example|template|sample)', r'\bdescription\b.*\b(example|template)\b.*\b(rental|vacation)']},
    {"name": "Vacation Rental Blog Strategy", "patterns": [r'\b(vacation|rental|airbnb|str)\b.*\bblog', r'\bblog\b.*\b(vacation|rental|airbnb|str)']},
    
    # ── WEBSITE ───
    {"name": "Vacation Rental Website Design", "patterns": [r'\b(vacation|holiday)\s*rental\b.*\bweb(site|design)', r'\bweb(site|design)\b.*\b(vacation|holiday)\s*rental']},
    {"name": "Vacation Rental Website Builders", "patterns": [r'\b(vacation|rental)\b.*\bwebsite\s*(build|template|creat)', r'\bwebsite\s*(build|template)\b.*\b(vacation|rental)']},
    {"name": "Airbnb Website Design", "patterns": [r'\bairbnb\b.*\bweb(site|design)', r'\bweb(site|design)\b.*\bairbnb\b']},
    {"name": "Villa Website & Landing Pages", "patterns": [r'\bvilla\b.*\b(website|landing\s*page|web\s*design)', r'\b(website|landing\s*page)\b.*\bvilla\b']},
    
    # ── BRANDING ───
    {"name": "Airbnb Branding & Brand Guidelines", "patterns": [r'\bairbnb\b.*\b(brand|branding)', r'\b(brand|branding)\b.*\bairbnb\b']},
    {"name": "Vacation Rental Logo Design", "patterns": [r'\b(rental|vacation|airbnb|villa|str)\b.*\blog(o|os)', r'\blog(o|os)\b.*\b(rental|vacation|airbnb|villa)']},
    {"name": "Airbnb Business Naming", "patterns": [r'\bairbnb\b.*\b(name|naming|business\s*name)', r'\b(name|naming)\b.*\bairbnb\b.*\bbusiness']},
    {"name": "Vacation Rental Branding Strategy", "patterns": [r'\b(vacation|rental|str)\b.*\bbrand\b.*\b(strat|position|identity)', r'\bbrand\b.*\b(strat|position)\b.*\b(rental|vacation)']},
    
    # ── MARKETING AGENCY ───
    {"name": "Airbnb Marketing Agency", "patterns": [r'\bairbnb\b.*\b(agency|marketing\s*(agency|company|firm|service))']},
    {"name": "Vacation Rental Marketing Agency", "patterns": [r'\b(vacation|holiday)\s*rental\b.*\b(agency|market.*company|market.*firm)', r'\b(agency|market.*company)\b.*\b(vacation|holiday)\s*rental']},
    {"name": "Vacation Rental Consultant", "patterns": [r'\b(vacation|rental|airbnb|str|villa)\b.*\bconsult', r'\bconsult\b.*\b(vacation|rental|airbnb|str|villa)']},
    {"name": "STR Marketing Services", "patterns": [r'\b(str|short[\s-]?term)\b.*\bmarket', r'\bmarket\b.*\b(str|short[\s-]?term)']},
    {"name": "Hospitality Marketing", "patterns": [r'\bhospitality\b.*\b(market|agency|brand|consult)', r'\b(market|agency)\b.*\bhospitality']},
    {"name": "Airbnb Marketing Strategy", "patterns": [r'\bairbnb\b.*\bmarket.*\b(strat|tip|tool|plan|idea)', r'\bmarket.*\b(strat|tip|tool)\b.*\bairbnb']},
    
    # ── SOCIAL / EMAIL / PPC ───
    {"name": "Instagram Marketing for Airbnb", "patterns": [r'\binstagram\b.*\b(airbnb|rental|villa|host)', r'\b(airbnb|rental|villa|host)\b.*\binstagram']},
    {"name": "Social Media Marketing for Rentals", "patterns": [r'\bsocial\s*media\b.*\b(airbnb|rental|villa|host|str|vacation)', r'\b(airbnb|rental|villa|str)\b.*\bsocial\s*media']},
    {"name": "Facebook Ads for Vacation Rentals", "patterns": [r'\bfacebook\b.*\b(ad|marketing)\b.*\b(rental|airbnb|villa)', r'\b(rental|airbnb|villa)\b.*\bfacebook\b.*\bad']},
    {"name": "Google Ads for Vacation Rentals", "patterns": [r'\bgoogle\b.*\b(ad|ppc)\b.*\b(rental|airbnb|villa)', r'\b(rental|airbnb|villa)\b.*\bgoogle\b.*\b(ad|ppc)']},
    {"name": "PPC for Vacation Rentals", "patterns": [r'\bppc\b.*\b(rental|airbnb|villa|vacation)', r'\b(rental|airbnb|villa|vacation)\b.*\bppc']},
    {"name": "Email Marketing for Airbnb & Rentals", "patterns": [r'\bemail\b.*\b(airbnb|rental|villa|host|guest|vacation)', r'\b(airbnb|rental|villa|host)\b.*\bemail']},
    
    # ── GUEST EXPERIENCE ───
    {"name": "Airbnb Superhost Guide", "patterns": [r'\bsuperhost\b']},
    {"name": "Airbnb Reviews Strategy", "patterns": [r'\bairbnb\b.*\breview', r'\breview\b.*\bairbnb']},
    {"name": "Guest Review Templates & Responses", "patterns": [r'\breview\b.*\b(template|response|respond|reply|example)', r'\b(template|response|respond)\b.*\breview']},
    {"name": "Guest Communication Best Practices", "patterns": [r'\bguest\b.*\b(commun|message|messag|text|contact|email|respond)', r'\b(commun|message)\b.*\bguest\b']},
    {"name": "Guest Experience & Satisfaction", "patterns": [r'\bguest\b.*\b(experience|satisf|happy|delight|wow)', r'\b(experience|satisf)\b.*\bguest']},
    {"name": "Guest Welcome & Check-in Experience", "patterns": [r'\b(welcome|greeting|gift|basket|check[\s-]?in)\b.*\b(guest|airbnb|rental)', r'\b(guest|airbnb|rental)\b.*\b(welcome|greeting|gift|basket|check[\s-]?in)']},
    {"name": "Guest Retention & Repeat Bookings", "patterns": [r'\bguest\b.*\b(retent|loyal|repeat|return)', r'\brepeat\b.*\bbook']},
    
    # ── UPSELLS & AMENITIES ───
    {"name": "Airbnb Upsells & Add-Ons", "patterns": [r'\bupsell', r'\bancillary\b.*\breven', r'\badd[\s-]?on\b.*\b(revenue|service|guest)']},
    {"name": "Best Amenities for Airbnb", "patterns": [r'\b(best|top|must[\s-]?have|essential)\b.*\bamen(ity|ities)\b.*\b(airbnb|rental)', r'\bairbnb\b.*\bamen(ity|ities)\b.*\b(best|top|must|list|checklist)']},
    {"name": "Airbnb Amenities List & Checklist", "patterns": [r'\bairbnb\b.*\bamen(ity|ities)\b', r'\bamen(ity|ities)\b.*\bairbnb', r'\b(vacation|rental)\b.*\bamen(ity|ities)']},
    {"name": "Cold Plunge & Hot Tub for Airbnb", "patterns": [r'\bcold\s*plunge', r'\bhot\s*tub\b.*\b(airbnb|rental|villa|rev|roi)', r'\b(airbnb|rental|villa)\b.*\bhot\s*tub']},
    {"name": "Pool & Outdoor Amenities for Rentals", "patterns": [r'\b(pool|outdoor|garden|bbq|fire\s*pit|jacuzzi|sauna)\b.*\b(airbnb|rental|villa)', r'\b(airbnb|rental|villa)\b.*\b(pool|outdoor|bbq|fire\s*pit|jacuzzi|sauna)']},
    
    # ── LUXURY ───
    {"name": "Luxury Villa Marketing Strategy", "patterns": [r'\bluxury\b.*\bvilla\b.*\b(market|seo|brand|strateg)', r'\b(market|seo|brand)\b.*\bluxury\b.*\bvilla']},
    {"name": "Airbnb Luxe Requirements", "patterns": [r'\b(airbnb\b.*\bluxe|luxe\b.*\bairbnb|luxe\b.*\brequir)']},
    {"name": "High-End Rental Positioning", "patterns": [r'\b(high[\s-]?end|premium|luxury)\b.*\b(rental|villa|str|airbnb)\b.*\b(market|position|strateg|brand)', r'\bluxury\b.*\bairbnb']},
    {"name": "Luxury Naming & Branding", "patterns": [r'\bluxury\b.*\b(name|naming|brand)', r'\b(name|naming)\b.*\bluxury\b.*\b(airbnb|rental|villa)']},
    
    # ── EVENTS ───
    {"name": "Wedding Venue Marketing for Villas", "patterns": [r'\bwedding\b.*\b(villa|venue|rental|market)', r'\b(villa|venue)\b.*\bwedding']},
    {"name": "Corporate Retreat Marketing", "patterns": [r'\b(corporate|team)\b.*\bretreat\b', r'\bretreat\b.*\b(villa|rental|venue|market)']},
    {"name": "Event Marketing for Vacation Rentals", "patterns": [r'\bevent\b.*\b(villa|rental|venue|host|market)', r'\b(villa|rental)\b.*\bevent']},
    
    # ── OPERATIONS ───
    {"name": "Airbnb Automation & Workflows", "patterns": [r'\bairbnb\b.*\b(automat|workflow|ai|smart|automated\s*message)', r'\b(automat|workflow|ai)\b.*\bairbnb']},
    {"name": "Airbnb Automated Messages", "patterns": [r'\bairbnb\b.*\b(automated\s*message|message\s*template|automat.*\bmessag)', r'\bmessag\b.*\btemplate\b.*\bairbnb']},
    {"name": "Smart Locks & Keyless Entry for Airbnb", "patterns": [r'\b(smart\s*lock|keyless|keypad|lockbox|self[\s-]?check)', r'\b(lock|key)\b.*\b(airbnb|rental|guest)']},
    {"name": "Airbnb Cleaning & Turnover", "patterns": [r'\b(clean|turnover)\b.*\b(airbnb|rental|str|villa|guest)', r'\b(airbnb|rental|str)\b.*\b(clean|turnover)']},
    {"name": "Noise Monitoring & Security for Rentals", "patterns": [r'\b(noise|security|camera|monitor)\b.*\b(airbnb|rental|str|guest)', r'\b(airbnb|rental|str)\b.*\b(noise|security|camera)']},
    
    # ── PROPERTY MANAGEMENT ───
    {"name": "Airbnb Property Management", "patterns": [r'\bairbnb\b.*\bproperty\s*manag', r'\bproperty\s*manag\b.*\bairbnb']},
    {"name": "Vacation Rental Property Management", "patterns": [r'\b(vacation|holiday)\s*rental\b.*\bproperty\s*manag', r'\bproperty\s*manag\b.*\b(vacation|holiday)\s*rental']},
    {"name": "STR Property Management Software", "patterns": [r'\b(pms|property\s*management\s*software|guesty|hostaway|lodgify|ownerrez|tokeet|hostfully|uplisting)', r'\b(str|rental|airbnb)\b.*\bsoftware']},
    {"name": "Co-Hosting for Airbnb", "patterns": [r'\bco[\s-]?host', r'\bcohost']},
    
    # ── STARTING & HOSTING BASICS ───
    {"name": "How to Start an Airbnb Business", "patterns": [r'\b(start|launch|begin|creat)\b.*\b(airbnb|str|vacation\s*rental)\b.*\b(business|company)']},
    {"name": "How to List on Airbnb", "patterns": [r'\b(how\s*to\s*)?(list|listing)\b.*\b(on|with|your)\b.*\bairbnb', r'\bairbnb\b.*\b(how\s*to\s*)?(list|listing)\b']},
    {"name": "How to List on VRBO", "patterns": [r'\b(how\s*to\s*)?(list|listing)\b.*\b(on|with)\b.*\bvrbo', r'\bvrbo\b.*\b(how\s*to\s*)?list']},
    {"name": "What is Airbnb (Explainer)", "patterns": [r'\bwhat\s+(is|does|do)\s+(an?\s+)?airbnb', r'\bairbnb\s*:?\s*what\s+is', r'\bmeaning\b.*\bairbnb', r'\bairbnb\b.*\bmeaning', r'\bairbnb\b.*\bstand\s*for', r'\bwhat\b.*\bairbnb\b.*\bmean']},
    {"name": "How Airbnb Works", "patterns": [r'\bhow\s+does\s+(an?\s+)?airbnb\s+work', r'\bhow\s+do\s+airbnb\s+work', r'\bairbnb\b.*\boperat']},
    {"name": "Airbnb Hosting Tips for Beginners", "patterns": [r'\bairbnb\b.*\b(hosting\s*tip|beginn|new\s*host|first\s*time)', r'\b(beginn|new\s*host|first\s*time)\b.*\bairbnb']},
    {"name": "Airbnb Host Checklist", "patterns": [r'\bairbnb\b.*\bchecklist', r'\bchecklist\b.*\bairbnb', r'\bairbnb\b.*\bcheck\s*list']},
    
    # ── CUSTOMER SERVICE / CONTACT ───
    {"name": "Airbnb Customer Service & Contact", "patterns": [r'\bairbnb\b.*\b(customer\s*service|contact|phone|support|get\s*in\s*touch)', r'\b(customer\s*service|contact|phone|support)\b.*\bairbnb']},
    {"name": "Airbnb Cancellation & Refund Policy", "patterns": [r'\bairbnb\b.*\b(cancel|refund|dispute|policy)', r'\b(cancel|refund|dispute)\b.*\bairbnb']},
    
    # ── LEGAL & FINANCIAL ───
    {"name": "Airbnb Taxes & Accounting", "patterns": [r'\b(airbnb|rental|str|vacation)\b.*\b(tax|accounting|deduct|write[\s-]?off)', r'\b(tax|accounting|deduct)\b.*\b(airbnb|rental|str)']},
    {"name": "STR Regulations & Permits", "patterns": [r'\b(airbnb|rental|str|vacation)\b.*\b(regulat|permit|license|ordinance|zon|law|legal)', r'\b(regulat|permit|license|law|legal)\b.*\b(airbnb|rental|str)']},
    {"name": "Airbnb Insurance & Liability", "patterns": [r'\b(airbnb|rental|str|host)\b.*\b(insurance|liability|aircover|protect)', r'\b(insurance|liability|aircover)\b.*\b(airbnb|rental|str|host)']},
    {"name": "Rental Arbitrage Guide", "patterns": [r'\b(rental\s*)?arbitrage', r'\b(airbnb|str)\b.*\barbitrage']},
    {"name": "Vacation Rental Investment", "patterns": [r'\b(vacation|holiday)\s*rental\b.*\b(invest|roi|return|buy)', r'\b(invest|roi)\b.*\b(vacation|rental)', r'\bpurchas\b.*\b(vacation|rental)', r'\b(vacation|rental)\b.*\bpurchas']},
    {"name": "STR LLC & Business Structure", "patterns": [r'\b(airbnb|rental|str)\b.*\b(llc|business\s*structure|incorporat)', r'\bllc\b.*\b(airbnb|rental|str)']},
    
    # ── DESIGN & FURNISHING ───
    {"name": "Airbnb Interior Design & Furnishing", "patterns": [r'\b(airbnb|rental|villa|str)\b.*\b(interior|furnish|decor|stag|design)', r'\b(interior|furnish|decor|stag)\b.*\b(airbnb|rental|villa)']},
    
    # ── PROPERTY TYPES ───
    {"name": "Cabin & Mountain Rental Marketing", "patterns": [r'\b(cabin|mountain|chalet|ski)\b.*\b(rental|airbnb|host|market|book)', r'\b(rental|airbnb|host)\b.*\b(cabin|mountain|chalet)']},
    {"name": "Beach House Rental Marketing", "patterns": [r'\b(beach|coastal|ocean|seaside)\b.*\b(rental|airbnb|host|market|villa)', r'\b(rental|airbnb|villa)\b.*\b(beach|coastal|ocean)']},
    {"name": "Glamping & Unique Stays", "patterns": [r'\b(glamping|treehouse|tiny\s*house|unique\s*stay|yurt|dome|a[\s-]?frame)', r'\bunique\b.*\b(rental|airbnb|stay)']},
    
    # ── BOOKING.COM / OTHER OTAS ───
    {"name": "Booking.com for Vacation Rental Owners", "patterns": [r'\bbooking\.com\b', r'\bbookingcom\b']},
    
    # ── SOFTWARE & TOOLS ───
    {"name": "Hospitable (Smartbnb) Review & Guide", "patterns": [r'\b(hospitable|smartbnb)\b']},
    {"name": "Guesty Property Management Review", "patterns": [r'\bguesty\b']},
    {"name": "Hostaway Review & Guide", "patterns": [r'\bhostaway\b']},
    {"name": "Airbnb Automation Tools Comparison", "patterns": [r'\b(airbnb|rental|str)\b.*\b(tool|software|app)\b.*\b(compar|best|review|top)', r'\b(tool|software)\b.*\b(compar|best|review)\b.*\b(airbnb|rental)']},
    {"name": "Vacation Rental Market Research Tools", "patterns": [r'\b(airbnb|rental|str)\b.*\b(market\s*research|data|analytic|tool)', r'\b(market\s*research|data|analytic)\b.*\b(airbnb|rental|str)']},
    
    # ── AIRBNB WISH LIST / MISC ───
    {"name": "Airbnb Wish List Guide", "patterns": [r'\bairbnb\b.*\bwish\s*list', r'\bwish\s*list\b.*\bairbnb']},
    {"name": "Airbnb Conversion Rate Optimization", "patterns": [r'\bairbnb\b.*\bconversion', r'\bconversion\b.*\bairbnb']},
    {"name": "Airbnb Target Market & Audience", "patterns": [r'\bairbnb\b.*\b(target\s*market|target\s*audience|ideal\s*guest|niche)', r'\b(target\s*market|target\s*audience)\b.*\bairbnb']},
    
    # ── VILLA SPECIFIC ───
    {"name": "Villa Booking Software", "patterns": [r'\bvilla\b.*\b(booking\s*software|reservation|system)', r'\b(booking\s*software|reservation)\b.*\bvilla']},
    {"name": "Villa Management Best Practices", "patterns": [r'\bvilla\b.*\b(manag|operat|run|tip|guid)', r'\b(manag|operat)\b.*\bvilla\b']},
    
    # ── RENTAL MANAGEMENT GENERAL ───
    {"name": "Vacation Rental Marketing (Complete Guide)", "patterns": [r'\b(vacation|holiday)\s*rental\b.*\bmarket(ing)?\b(?!.*agency)(?!.*company)(?!.*consult)', r'\bmarket(ing)?\b.*\b(vacation|holiday)\s*rental\b(?!.*agency)']},
    {"name": "How to Market Your Airbnb", "patterns": [r'\bhow\s*to\s*market\b.*\bairbnb', r'\bairbnb\b.*\bhow\s*to\s*market', r'\bmarket\b.*\byour\b.*\bairbnb']},
    
    # ── WORDPRESS / THEMES ───
    {"name": "Holiday Rental WordPress Themes", "patterns": [r'\b(holiday|vacation|rental)\b.*\bwordpress', r'\bwordpress\b.*\b(holiday|vacation|rental)']},
]

def assign_cluster(keyword):
    for cdef in CLUSTER_DEFINITIONS:
        for pattern in cdef["patterns"]:
            if re.search(pattern, keyword, re.IGNORECASE):
                return cdef["name"]
    return None

def has_location_words(kw):
    """Check if keyword contains location words (for master keyword penalty)."""
    words = set(kw.split())
    if words & LOCATION_WORDS:
        return True
    if words & VACATION_LOCATION_WORDS:
        return True
    for phrase in LOCATION_PHRASES:
        if phrase in kw:
            return True
    return False

def determine_master_keyword(keywords_in_cluster):
    scored = []
    for kw in keywords_in_cluster:
        vol = kw['volume']
        diff = kw['seo_difficulty']
        wc = len(kw['keyword'].split())
        if diff <= 20: opp = 95
        elif diff <= 30: opp = 80
        elif diff <= 40: opp = 60
        elif diff <= 50: opp = 45
        elif diff <= 65: opp = 30
        else: opp = 10
        if vol >= 2000: vs = 90
        elif vol >= 500: vs = 70
        elif vol >= 200: vs = 55
        elif vol >= 50: vs = 35
        else: vs = 15
        lb = 15 if 3 <= wc <= 5 else (5 if wc == 2 else 0)
        score = (vs * 0.4) + (opp * 0.45) + (lb * 0.15)
        # Heavy penalty for location-based keywords as master
        if has_location_words(kw['keyword_norm']):
            score *= 0.3
        scored.append((score, kw))
    scored.sort(key=lambda x: x[0], reverse=True)
    return scored[0][1] if scored else None

def calculate_priority_score(cluster):
    mv = cluster.get('master_volume', 0)
    md = cluster.get('master_seo_difficulty', 0)
    tv = cluster.get('total_cluster_volume', 0)
    sc = cluster.get('secondary_count', 0)
    if md <= 20: ds = 100
    elif md <= 30: ds = 80
    elif md <= 40: ds = 65
    elif md <= 50: ds = 45
    elif md <= 65: ds = 25
    else: ds = 10
    if tv >= 10000: vs = 100
    elif tv >= 3000: vs = 85
    elif tv >= 1000: vs = 65
    elif tv >= 300: vs = 45
    elif tv >= 50: vs = 30
    else: vs = 15
    dp = min(sc * 4, 60)
    return (vs * 0.35) + (ds * 0.35) + (dp * 0.30)

# ─── MAIN ────────────────────────────────────────────────────────────────────

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("=" * 70)
    print("INDAVILLAS KEYWORD STRATEGY PROCESSOR v3")
    print("ALL 25 files · Broad relevance · 100+ clusters target")
    print("=" * 70)

    # Step 1: Merge
    print("\nStep 1: Merging all files...")
    all_keywords = []
    files_processed = 0
    for filepath in sorted(INPUT_FILES):
        if not os.path.exists(filepath):
            continue
        source = os.path.basename(filepath).replace("keywords_gap for ", "").replace(".csv", "")
        with open(filepath, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            count = 0
            for row in reader:
                kw = row.get('Keyword', '').strip()
                if not kw: continue
                all_keywords.append({
                    'keyword': kw,
                    'keyword_norm': normalize_keyword(kw),
                    'volume': parse_volume(row.get('Volume', '0')),
                    'cpc': parse_float(row.get('CPC', '0')),
                    'paid_difficulty': parse_volume(row.get('Paid Difficulty', '0')),
                    'seo_difficulty': parse_volume(row.get('SEO Difficulty', '0')),
                    'source': source,
                })
                count += 1
            print(f"  ✓ {count:>5d} keywords from {source}")
            files_processed += 1

    total_raw = len(all_keywords)
    print(f"\n  Total raw keywords: {total_raw:,} from {files_processed} files")

    # Step 2: Deduplicate
    print("\nStep 2: Deduplicating...")
    deduped = {}
    for kw in all_keywords:
        norm = kw['keyword_norm']
        if norm in deduped:
            existing = deduped[norm]
            if kw['volume'] > existing['volume']:
                sources = existing['source']
                deduped[norm] = kw
                deduped[norm]['source'] = sources + ", " + kw['source']
            else:
                existing['source'] += ", " + kw['source']
        else:
            deduped[norm] = kw

    total_deduped = len(deduped)
    dupes_removed = total_raw - total_deduped
    print(f"  Duplicates removed: {dupes_removed:,}")
    print(f"  Unique keywords: {total_deduped:,}")

    # Step 3: Filter
    print("\nStep 3: Filtering for broad relevance...")
    relevant = {}
    removed = 0
    for norm, kw in deduped.items():
        if is_hard_excluded(kw['keyword_norm']):
            removed += 1
        elif has_broad_relevance(kw['keyword_norm']):
            relevant[norm] = kw
        else:
            removed += 1

    total_relevant = len(relevant)
    print(f"  ✓ Relevant keywords kept: {total_relevant:,}")
    print(f"  ✗ Irrelevant removed: {removed:,}")

    # Step 4: Cluster
    print("\nStep 4: Clustering into article topics...")
    clusters = defaultdict(list)
    unclustered = []
    for norm, kw in relevant.items():
        cn = assign_cluster(kw['keyword_norm'])
        if cn:
            clusters[cn].append(kw)
        else:
            unclustered.append(kw)

    # Try word overlap for unclustered
    still_unclustered = []
    for kw in unclustered:
        assigned = False
        keyword = kw['keyword_norm']
        for cn in list(clusters.keys()):
            cwords = set(re.sub(r'[&,():]', '', cn.lower()).split())
            kwwords = set(keyword.split())
            if len(cwords & kwwords) >= 2:
                clusters[cn].append(kw)
                assigned = True
                break
        if not assigned:
            still_unclustered.append(kw)

    if still_unclustered:
        # Sub-cluster the unclustered by dominant keyword
        sub = defaultdict(list)
        for kw in still_unclustered:
            words = kw['keyword_norm'].split()
            key = words[0] if len(words) >= 2 else 'misc'
            sub[key].append(kw)
        for key, kws in sub.items():
            if len(kws) >= 5:  # Higher threshold to avoid junk clusters
                cname = f"General: {key.title()} Related Topics"
                clusters[cname] = kws
            else:
                clusters["Miscellaneous STR Topics"].extend(kws)

    # Remove empty clusters
    clusters = {k: v for k, v in clusters.items() if v}

    print(f"\n  Total clusters created: {len(clusters)}")
    for name, kws in sorted(clusters.items(), key=lambda x: -len(x[1]))[:30]:
        print(f"    {name}: {len(kws)} kws")
    if len(clusters) > 30:
        print(f"    ... and {len(clusters) - 30} more clusters")

    # Step 5: Master/Secondary
    print("\nStep 5: Assigning master & secondary keywords...")
    cluster_output = []
    for cn, kws in clusters.items():
        if not kws: continue
        master = determine_master_keyword(kws)
        if not master: continue
        secs = [kw for kw in kws if kw['keyword_norm'] != master['keyword_norm']]
        secs.sort(key=lambda x: x['volume'], reverse=True)
        seen = set()
        unique_secs = []
        for s in secs:
            if s['keyword_norm'] not in seen:
                seen.add(s['keyword_norm'])
                unique_secs.append(s)
        tv = master['volume'] + sum(s['volume'] for s in unique_secs)
        cluster_output.append({
            'cluster_name': cn,
            'master_keyword': master['keyword'],
            'master_volume': master['volume'],
            'master_seo_difficulty': master['seo_difficulty'],
            'secondaries': unique_secs,
            'secondary_count': len(unique_secs),
            'total_cluster_volume': tv,
        })

    # ── OUTPUTS ─────────────────────────────────────────────────────────
    print("\n" + "-" * 70)

    # Output 1
    print("Writing Output 1: Keyword master file...")
    o1 = os.path.join(OUTPUT_DIR, "01_keyword_master.csv")
    ml = {}
    for co in cluster_output:
        ml[normalize_keyword(co['master_keyword'])] = (co['cluster_name'], 'Master')
        for s in co['secondaries']:
            k = normalize_keyword(s['keyword'])
            if k not in ml: ml[k] = (co['cluster_name'], 'Secondary')
    with open(o1, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['Keyword', 'Search Volume', 'CPC', 'Paid Difficulty', 'SEO Difficulty', 'Source File', 'Cluster Name', 'Master or Secondary'])
        for norm, kw in sorted(relevant.items(), key=lambda x: -x[1]['volume']):
            ci = ml.get(norm, ('Unclustered', '-'))
            w.writerow([kw['keyword'], kw['volume'], f"${kw['cpc']:.2f}", kw['paid_difficulty'], kw['seo_difficulty'], kw['source'], ci[0], ci[1]])
    print(f"  ✓ {o1}")

    # Output 2
    print("Writing Output 2: Article cluster file...")
    o2 = os.path.join(OUTPUT_DIR, "02_article_clusters.csv")
    with open(o2, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['Article Topic', 'Master Keyword', 'Master Keyword Volume', 'Master Keyword SEO Difficulty', 'Secondary Keywords', 'Secondary Keyword Count', 'Total Cluster Volume'])
        for co in sorted(cluster_output, key=lambda x: -x['total_cluster_volume']):
            sl = "; ".join([s['keyword'] for s in co['secondaries'][:25]])
            w.writerow([co['cluster_name'], co['master_keyword'], co['master_volume'], co['master_seo_difficulty'], sl, co['secondary_count'], co['total_cluster_volume']])
    print(f"  ✓ {o2}")

    # Output 3
    print("Writing Output 3: Priority opportunities file...")
    o3 = os.path.join(OUTPUT_DIR, "03_priority_opportunities.csv")
    for co in cluster_output:
        co['priority_score'] = calculate_priority_score(co)
    ps = sorted(cluster_output, key=lambda x: x['priority_score'], reverse=True)
    with open(o3, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['Priority Rank', 'Article Topic', 'Master Keyword', 'Master Volume', 'SEO Difficulty', 'Total Cluster Volume', 'Secondary Count', 'Priority Score'])
        for i, co in enumerate(ps, 1):
            w.writerow([i, co['cluster_name'], co['master_keyword'], co['master_volume'], co['master_seo_difficulty'], co['total_cluster_volume'], co['secondary_count'], f"{co['priority_score']:.1f}"])
    print(f"  ✓ {o3}")

    # ── FINAL SUMMARY ────────────────────────────────────────────────────
    print("\n" + "=" * 70)
    print("FINAL SUMMARY")
    print("=" * 70)
    print(f"  Files processed:          {files_processed}")
    print(f"  Total keywords processed: {total_raw:,}")
    print(f"  Duplicates removed:       {dupes_removed:,}")
    print(f"  Unique keywords:          {total_deduped:,}")
    print(f"  Irrelevant removed:       {removed:,}")
    print(f"  Relevant keywords kept:   {total_relevant:,}")
    print(f"  Total clusters created:   {len(cluster_output)}")
    print()

    print("TOP 30 ARTICLE OPPORTUNITIES:")
    print("-" * 70)
    for i, co in enumerate(ps[:30], 1):
        print(f"  {i:3d}. [Score: {co['priority_score']:5.1f}] {co['cluster_name']}")
        print(f"       Master: \"{co['master_keyword']}\" (Vol: {co['master_volume']}, Diff: {co['master_seo_difficulty']})")
        print(f"       Cluster Vol: {co['total_cluster_volume']:,} | Secondaries: {co['secondary_count']}")
        print()

    print(f"\nOutput files: {OUTPUT_DIR}")
    print("=" * 70)


if __name__ == "__main__":
    main()
