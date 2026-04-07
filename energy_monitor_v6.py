# ╔══════════════════════════════════════════════════════════════════════╗
# ║  GLOBAL ENERJİ DEPOLAMA & YATIRIM İZLEME  v6 — CTO Edition         ║
# ╚══════════════════════════════════════════════════════════════════════╝

import subprocess, sys
for _p in ["feedparser","beautifulsoup4","requests","pandas",
           "schedule","lxml","deep_translator"]:
    subprocess.check_call([sys.executable,"-m","pip","install","-q",_p])

import feedparser, requests, re, html as H, warnings, schedule
import time, datetime, json, os
import pandas as pd
from bs4 import BeautifulSoup
from collections import defaultdict
warnings.filterwarnings("ignore")

# ══════════════════════════════════════════════════════════════════════════
# 1. KONFİGÜRASYON
# ══════════════════════════════════════════════════════════════════════════

PRIMARY_KW_W = [
    # İngilizce
    ("energy storage",0.30),("bess",0.30),("battery storage",0.25),
    ("grid-scale battery",0.25),("lithium-ion",0.20),("solid-state",0.20),
    ("flow battery",0.20),("vanadium redox",0.25),("sodium-ion",0.20),
    ("iron-air battery",0.25),("zinc-air",0.20),("long duration storage",0.25),
    ("ldes",0.20),("thermal storage",0.15),("pumped hydro",0.15),
    ("compressed air energy",0.20),("gravity storage",0.20),
    ("electrochemical storage",0.20),("second-life battery",0.15),
    ("grid storage",0.12),("battery energy storage",0.25),
    # Türkçe — Türkçe haberler bu keyword'lerle puanlanacak
    ("enerji depolama",0.30),("batarya depolama",0.25),("akü depolama",0.20),
    ("bess",0.30),("yenilenebilir enerji",0.12),("güneş enerjisi",0.10),
    ("rüzgar enerjisi",0.10),("şebeke depolama",0.20),("elektrik depolama",0.20),
    ("depolama sistemi",0.20),("enerji yatırım",0.12),("megawatt",0.12),
    ("gigawatt",0.15),("kapasite artış",0.12),("lisans başvuru",0.10),
    # Çince şirketler İngilizce metinde
    ("catl",0.25),("sungrow",0.20),("huawei digital energy",0.20),
]
PRIMARY_KW = [k for k,_ in PRIMARY_KW_W]

SECONDARY_KW = [
    "renewable energy","grid stability","ev battery","battery pack",
    "electrochemistry","electrolyte","cathode","anode",
    "charging infrastructure","microgrids","virtual power plant",
    "demand response","peak shaving","ancillary services",
    "power-to-x","hydrogen storage","energy transition","clean energy",
    "net zero","decarbonization","gigafactory","dispatch","curtailment",
    "capacity market","behind-the-meter","front-of-meter",
]
INVESTMENT_KW = [
    "series a","series b","series c","series d","series e",
    "seed round","pre-seed","venture capital","vc funding",
    "raises","raised","secures","secured","closes funding",
    "funding round","backed by","valuation","unicorn","ipo","spac",
    "private equity","grant","public funding","doe award","eu grant",
    "subsidy","loan guarantee","blended finance","financing",
    "debt financing","equity financing","capital raise",
    "revenue share deal","invests","invested","acquisition","acquires",
    "merger","closes $","closes €","closes au$",
]
REGULATION_KW = [
    "regulation","policy","legislation","directive","mandate",
    "epdk","teias","eu commission","ofgem","ferc","nerc",
    "erc singapore","grid code","market rule","capacity payment",
    "red ii","fit for 55","inflation reduction act","ira",
    "battery act","taxonomy","interconnection","permitting",
    "auction","tender","procurement","capacity market","capacity auction",
    "yönetmelik","tebliğ","mevzuat","düzenleme","karar",
]
STARTUP_KW = [
    "startup","start-up","founded","co-founder","co-founded",
    "early stage","pre-seed","incubator","accelerator",
    "spinout","spin-out","spinoff","deeptech","deep tech",
    "hard tech","pilot project","demo plant","proof of concept",
    "prototype","first commercial","first deployment","new company",
    "stealth mode","emerges from stealth","y combinator","techstars",
    "breakthrough energy fellows","cyclotron road","third derivative",
    "elemental excelerator","seed funding","seed investment",
    "venture-backed","vc-backed","bankruptcy","insolvency","restructuring",
]
REGION_KW = {
    "EU"       :["european union"," eu ","germany","france","italy","spain",
                 "netherlands","poland","belgium","sweden","denmark","austria",
                 "portugal","finland","greece","czech","hungary","romania",
                 "europe ","european","brussels","berlin","paris","amsterdam",
                 "madrid","rome","warsaw","vienna","munich","frankfurt",
                 "nordic","scandinavia","baltic","german ","french ","spanish ",
                 "engie","enel","iberdrola","enbw","vattenfall","statkraft",
                 "tennet","elia ","rte ","50hertz",
                 "spain ","spanish","chile","chile ","grenergy","repsol",
                 "italy ","italian","enel ","a2a ","terna ",
                 "poland ","polish","pge ","pkn",
                 "romania ","romanian","czech ","hungary ","hungarian"],
    "UK"       :["united kingdom"," uk ","england","scotland","wales",
                 "great britain","britain ","british ","ofgem","national grid eso",
                 "london","edinburgh","drax","octopus energy","centrica",
                 "national grid","scottish power","sse ","edf uk","bp uk"],
    "Turkey"   :["turkey","türkiye","turkish","epdk","teias","tedaş",
                 "ankara","istanbul","izmir","eüaş","shura","emra"],
    "USA"      :["united states","u.s.a","u.s.","u.s ","american ","doe ","ferc",
                 " us ","us-based","us battery","us energy","us grid","us bess",
                 "california","texas","new york","new jersey","nevada","arizona",
                 "colorado","illinois","michigan","ohio","florida","georgia",
                 "washington state","oregon","utah","minnesota","virginia",
                 "ercot","pjm","miso","caiso","nyiso","spp ",
                 "reno","los angeles","chicago","houston","phoenix","atlanta",
                 "department of energy","national renewable energy","nrel ","lbl ",
                 "pacific northwest","new england","midwest "],
    "China"    :["china","chinese","prc ","beijing","shanghai","shenzhen",
                 "catl","byd ","state grid","xinhua","guangdong","jiangsu",
                 "sungrow","huawei digital","longi","tongwei","cnesa",
                 "china energy","china power","china southern","china national",
                 "sinopec","cnooc","大储","储能","电池","中国",
                 "chinese manufacturer","made in china","china grid",
                 "jiangxi","zhejiang","shandong","liaoning","inner mongolia",
                 "chengdu","wuhan","nanjing","tianjin","chongqing",
                 "eve energy","ganfeng","contemporary amperex"],
    "Singapore":["singapore","edb singapore","ema singapore","jurong island"],
    "APAC"     :["australia","australian","new zealand","india","indian",
                 "japan","south korea","aemo","indonesia","malaysia",
                 "thailand","vietnam","taiwan",
                 "nsw","victoria","queensland","western australia","south australia",
                 "new south wales","aemo","apac","asia pacific",
                 "tokyo","osaka","seoul","mumbai","delhi","bangalore",
                 "singapore","bangkok","jakarta","manila","hanoi",
                 "korean ","japanese ","australian ","indian grid",
                 "kepco","tepco","posco","samsung sdi","lg energy"],
}
REG_FLAGS  = {"Turkey":"🇹🇷","EU":"🇪🇺","UK":"🇬🇧","USA":"🇺🇸",
              "China":"🇨🇳","Singapore":"🇸🇬","APAC":"🌏","Global":"🌍"}
REG_COLORS = {"Turkey":"#E30A17","EU":"#3b82f6","UK":"#6366f1","USA":"#ef4444",
              "China":"#f97316","Singapore":"#10b981","APAC":"#8b5cf6","Global":"#64748b"}
KNOWN_STARTUPS = {
    "form energy","ambri","eos energy","energy vault","hydrostor",
    "highview power","gravitricity","cmblu energy","invinity energy",
    "redflow","primus power","zinc8 energy","urban electric power",
    "noon energy","antora energy","relectrify","alsym energy",
    "peak energy","mga thermal","fourth power","malta inc",
    "quino energy","verdagy","salient energy","celadyne",
    "quantumscape","solid power","ses ai","enovix","factorial energy",
    "prologium","sila nanotechnologies","sila nano",
    "accure","stem inc","voltus","nuvve","autogrid","virtual peaker",
    "sparkion","giga storage","electrovaya","novacab",
    "vena energy","eesti energia","acme solar","elevate renewables",
    "quinbrook","sigenergy","northvolt","ess tech","freyr","verkor",
    "enerya","btek","reengen","enerjisa",
}
KNOWN_COMPANIES = [
    "CATL","BYD","LG Energy Solution","Samsung SDI","Panasonic","SK Innovation",
    "SK On","Northvolt","QuantumScape","Solid Power","SES AI","Enovix","FREYR",
    "Verkor","Morrow Batteries","SVOLT","AESC","Farasis","ProLogium","Factorial Energy",
    "Fluence","Powin","ESS Tech","Form Energy","Ambri","Energy Vault","Hydrostor",
    "Gravitricity","Highview Power","CMBlu Energy","Invinity Energy","Redflow",
    "Primus Power","Peak Energy","MGA Thermal","Relectrify","Alsym Energy",
    "Noon Energy","Antora Energy","Zinc8 Energy","Eos Energy","Vena Energy",
    "Eesti Energia","ACME Solar","Elevate Renewables","Quinbrook","Sigenergy",
    "Accure","Envision Energy","Wärtsilä","Aypa Power","Ormat Technologies",
    "AGL","R.Power","Invenergy","Plus Power","Broad Reach Power","Eolian",
    "Spearmint Energy","Convergent Energy","Origis Energy","Octopus Energy",
    "Drax","SSE","RWE","Enel","Iberdrola","EDF","EnBW","Centrica","Ørsted",
    "TotalEnergies","Equinor","Vattenfall","Shell","BP","E.ON",
    "Google","Microsoft","Amazon","Tesla","Rivian","Stem Inc","AutoGrid",
    "Breakthrough Energy","Temasek","BlackRock","KKR","Apollo","Brookfield",
    "Macquarie","Shell Ventures","BP Ventures","Galvanize Climate",
    "Lowercarbon Capital","Energy Impact Partners","Prelude Ventures",
    "EPDK","TEIAS","FERC","Ofgem","IEA","IRENA","AEMO","National Grid ESO",
    "Xcel Energy","Duke Energy","NextEra","Southern Company","Dominion Energy",
    "PG&E","Con Edison","Siemens Energy","ABB","Schneider Electric","GE Vernova",
    "Honeywell","Hitachi Energy","Vestas","Ford","Volkswagen","GridBeyond",
]
COMPANY_BLOCKLIST = {
    "bess","ldes","ev","pv","ac","dc","ai","api","iot",
    "australia","australian","india","indian","china","chinese",
    "lithuania","estonia","cambodia","argentina","germany",
    "france","spain","italy","uk","us","eu","usa","prc",
    "energy","battery","storage","grid","power","solar","wind",
    "market","report","news","video","download","free","new",
    "the","this","over","what","how","why","when","where","who",
    "national","federal","state","local","global","international",
    "north","south","east","west","central",
}
TR_NAV_BLOCKLIST = {
    "bilgi edinme","teşkilat şeması","kurumun yapısı","misyonumuz",
    "vizyonumuz","kurumsal değerlerimiz","etik komisyonu","kurumsal kimlik",
    "stratejik amaçlarımız","kurum sertifikalarımız","bilgi güvenliği",
    "kişisel verileri koruma","enerji yönetim sistemi politikamız",
    "ana sayfa","iletişim","hakkımızda","site haritası","gizlilik",
    "çerez politikası","kullanım koşulları","erişilebilirlik",
    "sık sorulan sorular","basın bülteni","insan kaynakları",
    "faaliyet raporu","bütçe","ihale","satın alma","yönetim kurulu",
    "ülkemiz","hizmetlerimiz","projelerimiz","desteklerimiz",
    "lisans işlemleri","elektronik lisans işlemleri",
    "elektronik lisans/sertifika işlemleri","lisanssız üretim",
    "üretim kapasite projeksiyonları","elektrik fiyat farkı endeksi",
    "kamulaştırma mevzuatı","mevzuat","yönetmelikler","tebliğler",
    "kurul kararları","piyasa verileri","istatistikler","raporlar",
    "sektör raporları","aylık rapor","yıllık rapor","doğalgaz piyasası",
    "elektrik piyasası","petrol piyasası","lpg piyasası",
    "başvuru formu","formlar","belge","kılavuz","rehber",
    "duyurular","ihaleler","personel alımı","staj",
}
RSS_FEEDS = {
    # ── Enerji Depolama — Doğrudan RSS (çalışıyor) ────────────────
    "Energy Storage News" : "https://www.energy-storage.news/rss/",
    "PV Magazine"         : "https://www.pv-magazine.com/feed/",
    "PV Tech"             : "https://www.pv-tech.org/feed/",
    "Electrek"            : "https://electrek.co/feed/",
    "Clean Energy Wire"   : "https://www.cleanenergywire.org/rss.xml",
    "Energy Monitor"      : "https://www.energymonitor.ai/feed/",
    "CleanTechnica"       : "https://cleantechnica.com/feed/",
    "Utility Dive"        : "https://www.utilitydive.com/feeds/news/",
    "TechCrunch Energy"   : "https://techcrunch.com/tag/energy/feed/",
    "TechCrunch Climate"  : "https://techcrunch.com/tag/climate/feed/",

    # ── Google News RSS — HER ZAMAN ÇALIŞIR (Colab dahil) ─────────
    # İngilizce — enerji depolama
    "GNews: BESS storage"  : "https://news.google.com/rss/search?q=BESS+battery+energy+storage&hl=en-US&gl=US&ceid=US:en",
    "GNews: energy storage": "https://news.google.com/rss/search?q=%22energy+storage%22+investment&hl=en-US&gl=US&ceid=US:en",
    "GNews: LDES startup"  : "https://news.google.com/rss/search?q=long+duration+storage+LDES+raises&hl=en-US&gl=US&ceid=US:en",
    "GNews: grid battery"  : "https://news.google.com/rss/search?q=grid+scale+battery+storage+MW&hl=en-US&gl=US&ceid=US:en",
    "GNews: lithium invest": "https://news.google.com/rss/search?q=lithium+battery+storage+investment+2026&hl=en-US&gl=US&ceid=US:en",
    # Çin — en büyük depolama piyasası, ayrı feedler
    "GNews: China BESS"    : "https://news.google.com/rss/search?q=China+CATL+BYD+battery+storage+GWh&hl=en-US&gl=US&ceid=US:en",
    "GNews: China storage" : "https://news.google.com/rss/search?q=China+energy+storage+installation+policy&hl=en-US&gl=US&ceid=US:en",
    "GNews: China invest"  : "https://news.google.com/rss/search?q=China+battery+gigafactory+lithium+investment+2026&hl=en-US&gl=US&ceid=US:en",
    "GNews: CATL Sungrow"  : "https://news.google.com/rss/search?q=CATL+Sungrow+Huawei+energy+storage+2026&hl=en-US&gl=US&ceid=US:en",
    # APAC — Avustralya, Hindistan, Japonya, G.Kore
    "GNews: APAC storage"  : "https://news.google.com/rss/search?q=Australia+India+Japan+Korea+battery+storage+BESS&hl=en-US&gl=US&ceid=US:en",
    "GNews: India storage" : "https://news.google.com/rss/search?q=India+battery+energy+storage+GWh+tender&hl=en-US&gl=US&ceid=US:en",
    # Türkçe — Türk siteler Colab'dan bloklu, Google News üzerinden çekiliyor
    # Türkçe — depolama odaklı, 4 feed
    "GNews: TR depolama"   : "https://news.google.com/rss/search?q=%22enerji+depolama%22+T%C3%BCrkiye&hl=tr&gl=TR&ceid=TR:tr",
    "GNews: TR batarya"    : "https://news.google.com/rss/search?q=batarya+depolama+yatırım&hl=tr&gl=TR&ceid=TR:tr",
    "GNews: TR bess"       : "https://news.google.com/rss/search?q=BESS+güneş+rüzgar+depolama+Türkiye&hl=tr&gl=TR&ceid=TR:tr",
    "GNews: TR akü"        : "https://news.google.com/rss/search?q=akü+enerji+depolama+sistemi+MW&hl=tr&gl=TR&ceid=TR:tr",
}

SPAM_PATTERNS = [
    r'\b(market size|market share|market report|market forecast|market research)\b',
    r'\b(cagr|compound annual|revenue forecast|industry analysis|industry report)\b',
    r'\b20(28|29|30|31|32|33|34|35)\b.*\b(market|forecast|report|size)\b',
    r'\bmarket\s+(size|share).{0,30}\b(20\d\d)\b',
]
_SPAM_RE = re.compile('|'.join(SPAM_PATTERNS), re.I)

def _is_spam(title):
    return bool(_SPAM_RE.search(str(title)))

SCRAPE_TARGETS = [
    # ── Türkiye — EPDK (çeşitli URL formatları deneniyor) ─────────
    {"name":"EPDK",
     "url":"https://www.epdk.gov.tr/Detay/Icerik/3-0-24-3/haberler",
     "base":"https://www.epdk.gov.tr","region":"Turkey",
     "sel":"a[href*='/Haber/'], a[href*='/haber/'], "
           ".haberler-listesi a, .news-list a, ul.liste li a, "
           "div.content-body a, .panel-body a",
     "tr_kw":["enerji","elektrik","doğal gaz","depolama","yenilenebilir",
               "lisans","tarife","kapasite","şebeke","piyasa","düzenleme",
               "mevzuat","yönetmelik","tebliğ","karar","lng","bess",
               "akü","batarya","güneş","rüzgar","fiyat","rapor","duyuru"],
     "timeout":20},
    # ── Türkiye — Enerji Bakanlığı ─────────────────────────────────
    {"name":"Enerji Bakanlığı",
     "url":"https://enerji.gov.tr/tr-TR/Sayfalar/Haberler",
     "base":"https://enerji.gov.tr","region":"Turkey",
     "sel":"div.news-item a, .haberler a, h3 a, h2 a, article a, "
           ".ms-rtestate-field a, .sfContentBlock a",
     "tr_kw":["enerji","elektrik","depolama","yenilenebilir","güneş",
               "rüzgar","bess","akü","batarya","şebeke","kapasite",
               "nükleer","doğalgaz","yatırım","proje","imza"],
     "timeout":20},
    # ── IEA — alternatif URL ───────────────────────────────────────
    {"name":"IEA Insights",
     "url":"https://www.iea.org/news",
     "base":"https://www.iea.org","region":"Global",
     "sel":".m-article-item__title a, article h3 a, h3 a",
     "timeout":15},
]

# ══════════════════════════════════════════════════════════════════════════
# 2. SINIFLANDIRICI
# ══════════════════════════════════════════════════════════════════════════

class Classifier:
    @staticmethod
    def _n(t): return str(t).lower()
    @staticmethod
    def _hits(t,kws): return sum(1 for k in kws if k in t)

    def relevance(self,title,summary=""):
        n=self._n(f"{title} {summary}")
        s=sum(w for kw,w in PRIMARY_KW_W if kw in n)
        s+=self._hits(n,SECONDARY_KW)*0.06
        return round(min(1.0,s),3)

    def is_startup(self,title,summary=""):
        n=self._n(f"{title} {summary}")
        for s in KNOWN_STARTUPS:
            if re.search(r'\b'+re.escape(s)+r'\b',n): return True
        generic={"raises","raised","secures","secured","closes","backed","invested",
                 "launches","venture-backed","vc-backed","bankruptcy","insolvency","restructuring"}
        broad={"cleantech","climate tech","clean energy","energy transition","net zero","decarbonization"}
        hits=[k for k in STARTUP_KW if k in n]
        non_gen=[h for h in hits if h not in generic]
        non_broad=[h for h in non_gen if h not in broad]
        if non_broad: return self.relevance(title,summary)>=0.08
        if non_gen:   return self.relevance(title,summary)>=0.25
        if hits:      return self.relevance(title,summary)>=0.40
        return False

    def classify(self,title,summary=""):
        if self.is_startup(title,summary): return "Startup"
        n=self._n(f"{title} {summary}")
        inv=self._hits(n,INVESTMENT_KW); reg=self._hits(n,REGULATION_KW)
        has_money=bool(re.search(r'(?:\$|€|£|au\$|us\$)[\d,\.]+\s?(?:m|b|bn|mn|million|billion)',n,re.I))
        has_action=any(x in n for x in ["raises","raised","secures","secured","closes","invested","funding round","acquires"])
        if has_money and has_action: inv=max(inv,3)
        if inv==0 and reg==0: return "Enerji"
        if inv>=reg:
            if any(x in n for x in ["series a","series b","series c","series d","series e","seed round","ipo","spac"]):
                return "Yatırım – Equity"
            if any(x in n for x in ["grant","public funding","doe award","eu grant","subsidy","loan guarantee","tender","auction"]):
                return "Yatırım – Hibe/Kamu"
            return "Yatırım"
        return "Regülasyon"

    @staticmethod
    def region(text):
        n=str(text).lower()
        sc={r:sum(1 for k in kws if k in n) for r,kws in REGION_KW.items()}
        best=max(sc,key=sc.get)
        return best if sc[best]>0 else "Global"

    @staticmethod
    def stage(text):
        n=str(text).lower()
        for s in ["series e","series d","series c","series b","series a","seed","pre-seed","ipo","spac","grant","tender","auction"]:
            if s in n: return s.title()
        return ""

    @staticmethod
    def fin_amount(text):
        sentences=re.split(r'(?<=[.!?])\s+',str(text))
        fin_actions=["raises","raised","secures","secured","closes","closed","invests","invested",
                     "financing","financed","funded","worth","valued at","grant","award","awarded",
                     "in funding","round of","capital of","loan of"]
        pats=[r'\b(?:us\$|au\$|ca\$|nz\$)[\d,\.]+\s?(?:billion|million|bn|mn|b|m)\b',
              r'\$\s?[\d,\.]+\s?(?:billion|million|bn|mn|m)\b',
              r'€\s?[\d,\.]+\s?(?:billion|million|bn|mn|m)\b',
              r'£\s?[\d,\.]+\s?(?:billion|million|bn|mn|m)\b',
              r'\b[\d,\.]+\s?million\b']
        for sent in sentences:
            if not any(kw in sent.lower() for kw in fin_actions): continue
            for p in pats:
                m=re.search(p,sent,re.I)
                if m:
                    raw=m.group(0).strip()
                    if not re.search(r'\d',raw) or len(raw)>35: continue
                    nm=re.search(r'([\d,\.]+)',raw)
                    if nm:
                        num=float(nm.group(1).replace(',',''))
                        if any(x in raw.lower() for x in ['billion','bn']) and num>10: continue
                    return raw
        return ""

    @staticmethod
    def capacity(text):
        m=re.search(r'\b[\d,\.]+\s?(?:gw|gwh|mw|mwh|kw|kwh)\b',text,re.I)
        return m.group(0).strip() if m else ""

    @staticmethod
    def companies(text):
        found=set()
        tl=str(text).lower()
        for co in KNOWN_COMPANIES:
            if re.search(r'\b'+re.escape(co.lower())+r'\b',tl):
                if co.lower() not in COMPANY_BLOCKLIST: found.add(co)
        pats=[
            r'\b([A-Z][a-zA-Z&\-\.]{2,}(?:\s[A-Z][a-zA-Z&\-\.]{2,}){0,2})\s+(?:raises?|secures?|closes?|announces?|launches?|receives?|wins?|awarded)\b',
            r'\b([A-Z][a-zA-Z&\-\.]{2,}(?:\s[A-Z][a-zA-Z&\-\.]{2,}){0,2})\s+(?:Inc|Corp|Ltd|GmbH|AG|SE|BV|Plc|LLC|NV|SA)\b',
        ]
        skip={"The","This","New","Energy","Battery","Grid","In","A","An","For","By","To","And","Or",
              "Of","On","As","With","From","North","South","East","West","National","Federal","State",
              "Video","Free","Report","European","Global","Australian","American","Chinese","Japanese"}
        for pat in pats:
            for mo in re.finditer(pat,text):
                nm=mo.group(1).strip()
                if(len(nm)>3 and nm not in skip and len(nm)<45
                   and nm.lower() not in COMPANY_BLOCKLIST
                   and re.search(r'[A-Z]',nm)):
                    found.add(nm)
        return sorted(found)

clf=Classifier()

# ══════════════════════════════════════════════════════════════════════════
# 3. ÇEVİRİ
# ══════════════════════════════════════════════════════════════════════════
try:
    from deep_translator import GoogleTranslator
    _TR_OK=True
except: _TR_OK=False

_TR_CACHE={}
def translate_tr(text,max_chars=300):
    if not _TR_OK or not text: return text
    text=str(text)[:max_chars]
    if text in _TR_CACHE: return _TR_CACHE[text]
    try:
        r=GoogleTranslator(source="auto",target="tr").translate(text)
        _TR_CACHE[text]=r or text; return _TR_CACHE[text]
    except: return text

# ══════════════════════════════════════════════════════════════════════════
# 4. VERİ TOPLAMA
# ══════════════════════════════════════════════════════════════════════════
HEADERS={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
         "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
         "Accept-Language":"tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.5",
         "Accept-Encoding":"gzip, deflate, br",
         "Connection":"keep-alive","Cache-Control":"no-cache"}

def _make_row(source,title,summary,url,published,region_override=None):
    combined=f"{title} {summary}"
    cat=clf.classify(title,summary)
    is_su=clf.is_startup(title,summary)
    rel=clf.relevance(title,summary)
    is_tr_source = (source in {"EPDK","Enerji Bakanlığı","AA Enerji","AA Ekonomi"}
                    or "GNews: TR" in source)
    tr_title = translate_tr(title) if not is_tr_source else ""
    # Tarih: published parse et, 30 günden eskiyse ts kullan
    now = datetime.datetime.utcnow()
    pub_display = ""
    pub_dt = None
    for fmt in ["%a, %d %b %Y %H:%M:%S %z","%Y-%m-%dT%H:%M:%S%z",
                "%a, %d %b %Y %H:%M:%S +0000","%Y-%m-%d"]:
        try:
            pub_dt = datetime.datetime.strptime(str(published).strip(), fmt).replace(tzinfo=None)
            break
        except: pass
    if pub_dt is None:
        try:
            import email.utils
            t = email.utils.parsedate(str(published))
            if t: pub_dt = datetime.datetime(*t[:6])
        except: pass
    if pub_dt and (now - pub_dt).days <= 30:
        pub_display = pub_dt.strftime("%d %b")
    else:
        pub_display = now.strftime("%d %b")  # toplama tarihi
    # Source bazlı bölge default — tespit edilemezse kaynak ülkesine ata
    US_DEFAULT_SOURCES = {"TechCrunch Energy","TechCrunch Climate","Utility Dive"}
    detected = region_override or clf.region(combined)
    if detected == "Global" and source in US_DEFAULT_SOURCES:
        detected = "USA"
    return {"ts":now.isoformat(timespec="seconds"),
            "source":source,"title":str(title)[:220],"tr_title":tr_title,
            "summary":str(summary)[:360],"url":url,"published":str(published)[:28],
            "pub_display":pub_display,
            "category":cat,"is_startup":is_su,
            "region":detected,
            "stage":clf.stage(combined),"fin_amount":clf.fin_amount(combined),
            "capacity":clf.capacity(combined),"companies":clf.companies(combined),"relevance":rel}


def fetch_rss(name,url):
    rows=[]
    is_tr_gnews = any(k in name for k in ["GNews: TR","GNews: China ZH"])
    min_rel = 0.0 if is_tr_gnews else 0.08  # TR haberler için eşik yok
    try:
        feedparser.USER_AGENT = "Mozilla/5.0 (compatible; EnergyBot/6.0)"
        feed=feedparser.parse(url)
        if not feed.entries and feed.get('status',200) in [301,302]:
            new_url = feed.get('href', url)
            if new_url != url: feed = feedparser.parse(new_url)
        for e in feed.entries[:25]:
            title=H.unescape(getattr(e,"title",""))
            summary=H.unescape(re.sub(r'<[^>]+>','',getattr(e,"summary","")))
            if not title: continue
            if _is_spam(title): continue  # market report spam filtresi
            # Google News başlıklarında " - Kaynak Adı" suffix'i var, temizle
            if " - " in title:
                title = title.rsplit(" - ",1)[0].strip()
            r=_make_row(name,title,summary,getattr(e,"link",""),getattr(e,"published",""))
            # TR Google News → bölgeyi Turkey'e zorla, kategori ata
            if is_tr_gnews:
                r["region"] = "Turkey"
                tl = title.lower()
                # Depolama spesifik kelimelerden EN AZ BİRİ zorunlu
                STORAGE_KW = ["depolama","batarya","bess","akü","mwh","gwh","pil"]
                if not any(k in tl for k in STORAGE_KW):
                    continue  # Elektrik fiyatı/genel enerji → at
                if r["relevance"] < 0.08:
                    r["relevance"] = 0.15
                    r["category"] = "Enerji"
            if r["relevance"]>=min_rel or r["is_startup"]: rows.append(r)
    except Exception as ex: print(f"  ⚠ RSS [{name}]: {ex}")
    return rows

def fetch_scrape(t):
    rows,seen=[],set()
    base=t.get("base",""); tr_kw=t.get("tr_kw",[])
    timeout=t.get("timeout",14)
    try:
        resp=requests.get(t["url"],headers=HEADERS,timeout=timeout,allow_redirects=True)
        resp.raise_for_status()
        soup=BeautifulSoup(resp.text,"lxml")
        for item in soup.select(t["sel"])[:60]:
            title=re.sub(r'\s+',' ',item.get_text(" ",strip=True)).strip()
            if not title or len(title)<15 or len(title)>300: continue
            if title.lower() in TR_NAV_BLOCKLIST: continue
            key=title.lower()[:80]
            if key in seen: continue
            seen.add(key)
            href=item.get("href","")
            if href.startswith("/"): href=base+href
            if not href.startswith("http"): continue
            if tr_kw:
                tl=title.lower(); has_kw=any(k in tl for k in tr_kw)
                r=_make_row(t["name"],title,"",href,"",t["region"])
                if has_kw or r["relevance"]>=0.08 or r["is_startup"]:
                    if has_kw and r["relevance"]<0.08: r["category"]="Regülasyon"; r["relevance"]=0.12
                    rows.append(r)
            else:
                r=_make_row(t["name"],title,"",href,"",t["region"])
                if r["relevance"]>=0.08 or r["is_startup"]: rows.append(r)
    except Exception as ex: print(f"  ⚠ Scrape [{t['name']}]: {str(ex)[:80]}")
    return rows

def collect_all():
    rows=[]; errors=[]
    print(f"\n{'='*58}\n  🔄  {datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M')} UTC\n{'='*58}")
    print("\n📡 RSS:")
    for name,url in RSS_FEEDS.items():
        print(f"   ↳ {name:<26}",end=" ",flush=True)
        r=fetch_rss(name,url); rows.extend(r)
        mark="✅" if r else "⚠ "; print(f"{mark} {len(r)}")
        if not r: errors.append(f"RSS:{name}")
        time.sleep(0.35)
    print("\n🕷  Scraping:")
    for t in SCRAPE_TARGETS:
        print(f"   ↳ {t['name']:<26}",end=" ",flush=True)
        r=fetch_scrape(t); rows.extend(r)
        mark="✅" if r else "⚠ "; print(f"{mark} {len(r)}")
        if not r: errors.append(f"Scrape:{t['name']}")
        time.sleep(0.5)
    if errors:
        print(f"\n  ⚠  Sıfır kayıt ({len(errors)}): {', '.join(errors[:5])}")
    if not rows: return pd.DataFrame()
    df=pd.DataFrame(rows)
    df.drop_duplicates(subset=["url"],keep="first",inplace=True)
    df=df[df["relevance"]>0].copy()

    # ── Eski tarihli haberleri filtrele ──────────────────────────────
    # RSS'lerde bazen aylar önceki makaleler geliyor.
    # published tarihi 30 günden eskiyse ve alaka < 0.40 ise at.
    now_utc = datetime.datetime.utcnow()
    cutoff_pub = now_utc - datetime.timedelta(days=30)
    def _pub_ok(pub_str):
        if not pub_str: return True  # tarih yoksa tut
        try:
            for fmt in ["%a, %d %b %Y %H:%M:%S %z","%Y-%m-%dT%H:%M:%S%z",
                        "%a, %d %b %Y %H:%M:%S +0000"]:
                try:
                    dt = datetime.datetime.strptime(str(pub_str).strip(), fmt)
                    dt = dt.replace(tzinfo=None) if dt.tzinfo else dt
                    return dt >= cutoff_pub
                except: pass
            import email.utils
            t = email.utils.parsedate(str(pub_str))
            if t: return datetime.datetime(*t[:6]) >= cutoff_pub
        except: pass
        return True  # parse edilemezse tut
    stale = df["published"].apply(lambda x: not _pub_ok(x))
    # Stale ama çok alakalı (≥0.50) haberleri koru
    df = df[~(stale & (df["relevance"] < 0.50))].copy()

    df.sort_values(["is_startup","relevance"],ascending=[False,False],inplace=True)
    df.reset_index(drop=True,inplace=True)
    return df

# ══════════════════════════════════════════════════════════════════════════
# 5. ŞİRKET PROFİLLERİ
# ══════════════════════════════════════════════════════════════════════════

def _parse_pub(d):
    for fmt in ["%a, %d %b %Y %H:%M:%S %z","%Y-%m-%dT%H:%M:%S%z","%Y-%m-%d"]:
        try: return datetime.datetime.strptime(str(d).strip(),fmt)
        except: pass
    try:
        import email.utils
        return datetime.datetime(*email.utils.parsedate(str(d))[:6])
    except: return None

def build_company_profiles(df):
    now=datetime.datetime.utcnow()
    raw=defaultdict(lambda:{"name":"","count":0,"recent":0,"older":0,
        "regions":set(),"categories":set(),"amounts":[],"stages":set(),
        "inv_count":0,"last_pub":None,"news":[]})
    for _,r in df.iterrows():
        cos=r["companies"]
        cl=cos if isinstance(cos,list) else [c.strip() for c in str(cos).split(",") if c.strip()]
        pub_dt=_parse_pub(r["published"])
        age=(now-pub_dt).days if pub_dt else 999
        for co in cl:
            if not co or co.lower() in COMPANY_BLOCKLIST: continue
            p=raw[co]; p["name"]=co; p["count"]+=1
            p["regions"].add(r["region"]); p["categories"].add(r["category"])
            if r["fin_amount"]: p["amounts"].append(r["fin_amount"])
            if r["stage"]: p["stages"].add(r["stage"])
            if "Yatırım" in r["category"] or "Startup" in r["category"]: p["inv_count"]+=1
            if pub_dt and (p["last_pub"] is None or pub_dt>p["last_pub"]): p["last_pub"]=pub_dt
            if age<=7: p["recent"]+=1
            elif age<=30: p["older"]+=1
            if len(p["news"])<4:
                p["news"].append({"title":str(r["title"])[:95],"url":r["url"],"cat":r["category"],"pub":str(r["published"])[:12]})
    profiles=[]
    for co,p in raw.items():
        if p["count"]<1: continue
        score=min(100,min(40,p["count"]*8)+min(30,p["inv_count"]*10)+(20 if p["recent"]>0 else 10 if p["older"]>0 else 0)+(10 if co.lower() in KNOWN_STARTUPS else 0))
        trend="up" if p["recent"]>p["older"] else "down" if p["recent"]<p["older"] else "flat"
        last=p["last_pub"].strftime("%d %b %Y") if p["last_pub"] else "—"
        profiles.append({"name":co,"count":p["count"],"score":score,"trend":trend,
            "regions":sorted(p["regions"]),"categories":sorted(p["categories"]),
            "amounts":p["amounts"][:3],"stages":sorted(p["stages"]),
            "inv_count":p["inv_count"],"last_seen":last,"news":p["news"],
            "is_startup":co.lower() in KNOWN_STARTUPS})
    profiles.sort(key=lambda x:-x["score"])
    return profiles

# ══════════════════════════════════════════════════════════════════════════
# 6. HTML DASHBOARD
# ══════════════════════════════════════════════════════════════════════════

CAT_COLORS={
    "Yatırım – Equity":"#10b981","Yatırım – Hibe/Kamu":"#059669",
    "Yatırım":"#34d399","Startup":"#f59e0b","Regülasyon":"#6366f1","Enerji":"#64748b",
}
def _e(x): return H.escape(str(x))

def _row_html(r):
    cat=r["category"]; fc=CAT_COLORS.get(cat,"#64748b")
    rc=REG_COLORS.get(r["region"],"#64748b"); rflag=REG_FLAGS.get(r["region"],"🌍")
    rel=float(r["relevance"]); url=r["url"] if str(r["url"]).startswith("http") else "#"
    cos=r["companies"]
    cl=cos if isinstance(cos,list) else [c.strip() for c in str(cos).split(",") if c.strip()]
    co_html="".join(f'<span class="badge-co">{_e(c)}</span>' for c in cl[:4])
    fin=r.get("fin_amount",""); cap=r.get("capacity","")
    amt=(f'<span class="val-fin">{_e(fin)}</span>' if fin else "")+(f'<span class="val-cap">{_e(cap)}</span>' if cap else "")
    if not amt: amt='<span class="dash">—</span>'
    stg=f'<span class="badge-stg">{_e(r["stage"])}</span>' if r.get("stage") else '<span class="dash">—</span>'
    pub = r.get("pub_display","") or r.get("ts","")[:10]
    rp=int(rel*100); rc2="#10b981" if rel>=0.75 else "#f59e0b" if rel>=0.4 else "#4a5268"
    tr_t=str(r.get("tr_title","")).strip()
    tr_b=f'<div class="tr-title">{_e(tr_t)}</div>' if tr_t and tr_t!=str(r["title"]).strip() else ""
    su_b=' style="border-left:2px solid #f59e0b"' if r.get("is_startup") else ""
    return (
        f'<tr data-cat="{_e(cat)}" data-region="{_e(r["region"])}" data-rel="{rel}"'
        f' data-url="{_e(url)}" data-search="{_e((str(r["title"])+" "+str(r["source"])).lower())}"'
        f' onclick="rowClick(event,this)" style="cursor:pointer">'
        f'<td class="td-main"{su_b}>'
        f'<a href="{_e(url)}" target="_blank" class="news-link">{_e(r["title"])}</a>'
        f'{tr_b}'
        f'{"<div class=co-row>"+co_html+"</div>" if co_html else ""}'
        f'<div class="meta-row"><span class="badge-src">{_e(r["source"])}</span>'
        f'<span class="meta-pub">{_e(pub)}</span></div></td>'
        f'<td><span class="badge-cat" style="background:{fc}18;color:{fc};border:1px solid {fc}35">{_e(cat)}</span></td>'
        f'<td><span class="badge-reg" style="background:{rc}">{rflag} {_e(r["region"])}</span></td>'
        f'<td>{stg}</td><td>{amt}</td>'
        f'<td><div class="rel-track"><div class="rel-fill" style="width:{rp}%;background:{rc2}"></div></div>'
        f'<span class="rel-num">{rel:.2f}</span></td></tr>'
    )

def _profile_card(p):
    score=p["score"]; trend=p["trend"]
    ts={"up":"↑","down":"↓","flat":"→"}[trend]
    tc={"up":"#10b981","down":"#ef4444","flat":"#64748b"}[trend]
    sc="#10b981" if score>=70 else "#f59e0b" if score>=40 else "#64748b"
    flags=" ".join(REG_FLAGS.get(r,"🌍") for r in p["regions"])
    reg_text=" · ".join(p["regions"]) if p["regions"] else "Global"
    cat_pri=["Yatırım – Equity","Yatırım – Hibe/Kamu","Yatırım","Startup","Regülasyon","Enerji"]
    main_cat=next((c for c in cat_pri if c in p["categories"]),p["categories"][0] if p["categories"] else "")
    fc=CAT_COLORS.get(main_cat,"#64748b")
    amt_html="".join(f'<span class="val-fin">{_e(a)}</span>' for a in p["amounts"])
    stg_html="".join(f'<span class="badge-stg">{_e(s)}</span>' for s in p["stages"])
    news_html="".join(
        f'<a href="{_e(n["url"] if str(n["url"]).startswith("http") else "#")}" target="_blank" class="cp-news-link" onclick="event.stopPropagation()">'
        f'<span class="cp-news-dot" style="background:{CAT_COLORS.get(n["cat"],"#64748b")}"></span>'
        f'<span>{_e(n["title"])}</span></a>'
        for n in p["news"])
    su_tag='<span class="badge-startup">startup</span>' if p["is_startup"] else ""
    border="#10b981" if p["is_startup"] else "#1e2433"
    # Skor çubuğu
    bar_w=int(score); bar_c="#10b981" if score>=70 else "#f59e0b" if score>=40 else "#6366f1"
    return (
        f'<div class="cp-card" style="border-color:{border}" data-score="{score}" data-name="{_e(p["name"])}" data-count="{p["count"]}" data-inv="{p["inv_count"]}">'
        f'<div class="cp-top"><div><div class="cp-name">{_e(p["name"])} {su_tag}</div>'
        f'<div class="cp-region">{flags} {_e(reg_text)}</div></div>'
        f'<div class="cp-score-wrap"><span class="cp-trend" style="color:{tc}">{ts}</span>'
        f'<span class="cp-score" style="color:{sc}">{score}</span></div></div>'
        f'<div class="score-bar-track"><div class="score-bar-fill" style="width:{bar_w}%;background:{bar_c}"></div></div>'
        f'<div class="cp-stats"><span>{p["count"]} haber</span>'
        f'{"<span>"+str(p["inv_count"])+" yatırım</span>" if p["inv_count"] else ""}'
        f'{"<span>"+p["last_seen"]+"</span>" if p["last_seen"]!="—" else ""}</div>'
        f'{"<div class=cp-amounts>"+amt_html+"</div>" if amt_html else ""}'
        f'{"<div class=cp-stages>"+stg_html+"</div>" if stg_html else ""}'
        f'<div class="cp-news">{news_html}</div></div>'
    )

def _build_top_by_region(df):
    """Her bölge için en yüksek alakalı haberleri döndürür."""
    region_order = ["Turkey","EU","USA","China","APAC","UK","Global"]
    result = {}
    for reg in region_order:
        sub = df[df["region"]==reg].sort_values("relevance",ascending=False).head(5)
        if len(sub) == 0: continue
        result[reg] = sub
    return result

def _top_region_html(reg_data):
    """Bölge bazlı top haberler — her bölge ayrı yatay şerit, hepsi görünür."""
    if not reg_data: return ""
    out = '<div class="top-region-wrap"><div class="top-region-hd">🗺 Bölgeye Göre Öne Çıkan Haberler</div>'
    for reg, sub in reg_data.items():
        flag = REG_FLAGS.get(reg,"🌍")
        rc   = REG_COLORS.get(reg,"#64748b")
        total_in_region = len(sub)
        out += (
            f'<div class="top-strip">'
            f'<div class="top-strip-label" style="border-left:3px solid {rc}">'
            f'<span style="color:{rc}">{flag} {_e(reg)}</span>'
            f'<span class="top-strip-count">{total_in_region}</span>'
            f'</div>'
            f'<div class="top-cards-row">'
        )
        for _, r in sub.iterrows():
            url  = r["url"] if str(r["url"]).startswith("http") else "#"
            cat  = r["category"]
            fc   = CAT_COLORS.get(cat,"#64748b")
            fin  = r.get("fin_amount","") or r.get("capacity","")
            tr_t = str(r.get("tr_title","")).strip()
            disp = tr_t if tr_t and tr_t != str(r["title"]).strip() else str(r["title"])
            su_b = "border-top:2px solid #f59e0b;" if r.get("is_startup") else ""
            rel  = float(r["relevance"])
            out += (
                f'<a href="{_e(url)}" target="_blank" class="top-card" style="{su_b}">'
                f'<div class="top-card-title">{_e(disp[:85])}</div>'
                f'<div class="top-card-meta">'
                f'<span class="badge-cat" style="background:{fc}18;color:{fc};border:1px solid {fc}30;font-size:8px;padding:1px 5px;border-radius:10px">{_e(cat)}</span>'
                f'{"<span class=top-card-fin>"+_e(fin)+"</span>" if fin else ""}'
                f'<span class="top-card-rel">{rel:.2f}</span>'
                f'</div></a>'
            )
        out += '</div></div>'
    out += '</div>'
    return out

def build_dashboard(df,profiles,run_count=1):
    if df.empty: return "<html><body style='background:#0c0e14;color:#e2e8f0;padding:40px;font-family:sans-serif'><h2>Veri yok.</h2></body></html>"

    ts_str=datetime.datetime.utcnow().strftime("%d %B %Y")
    ts_full=datetime.datetime.utcnow().strftime("%d %b %Y, %H:%M UTC")
    total=len(df); cc=df["category"].value_counts().to_dict()
    rc_=df["region"].value_counts().to_dict()
    inv_n=sum(v for k,v in cc.items() if "Yatırım" in k)
    reg_n=cc.get("Regülasyon",0); su_n=cc.get("Startup",0)
    hi_n=len(df[df["relevance"]>=0.75])

    # Zaman serisi — published tarihini kullan (son 30 gün),
    # parse edilemeyenlerde ts'ye fall back yap
    df2=df.copy()
    now_utc=datetime.datetime.utcnow()
    def _pub_day(row):
        pub=str(row.get("published",""))
        for fmt in ["%a, %d %b %Y %H:%M:%S %z","%Y-%m-%dT%H:%M:%S%z"]:
            try:
                dt=datetime.datetime.strptime(pub.strip(),fmt).replace(tzinfo=None)
                if (now_utc-dt).days<=30: return dt.strftime("%m/%d")
                return None  # 30 günden eski → chart'a alma
            except: pass
        try:
            import email.utils
            t=email.utils.parsedate(pub)
            if t:
                dt=datetime.datetime(*t[:6])
                if (now_utc-dt).days<=30: return dt.strftime("%m/%d")
        except: pass
        # fallback: ts
        try: return datetime.datetime.fromisoformat(str(row.get("ts",""))[:19]).strftime("%m/%d")
        except: return None
    df2["chart_day"]=df2.apply(_pub_day,axis=1)
    daily=df2.dropna(subset=["chart_day"]).groupby("chart_day").size().tail(14)
    tl_lbl=list(daily.index); tl_all=[int(x) for x in daily.values]
    def _ts(mask):
        grp=df2[mask].dropna(subset=["chart_day"]).groupby("chart_day").size()
        return [int(grp.reindex(tl_lbl,fill_value=0).iloc[i]) for i in range(len(tl_lbl))]
    tl_inv=_ts(df2["category"].str.contains("Yatırım",na=False))
    tl_su=_ts(df2["category"]=="Startup")

    cat_lbl=list(cc.keys()); cat_vals=list(cc.values())
    cat_cols=[CAT_COLORS.get(k,"#64748b") for k in cat_lbl]
    reg_lbl=list(rc_.keys()); reg_vals=list(rc_.values())
    reg_cols=[REG_COLORS.get(k,"#64748b") for k in reg_lbl]
    bins=[0,0.1,0.25,0.5,0.75,1.01]
    blbl=["<0.10","0.10-0.25","0.25-0.50","0.50-0.75","0.75-1.0"]
    bcnt=[0]*5
    for v in df["relevance"]:
        for i,(lo,hi) in enumerate(zip(bins,bins[1:])):
            if lo<=v<hi: bcnt[i]+=1; break

    co_set=set()
    for v in df["companies"]:
        items=v if isinstance(v,list) else [c.strip() for c in str(v).split(",") if c.strip()]
        for c in items:
            if c and c.lower() not in COMPANY_BLOCKLIST: co_set.add(c)

    # Tabloyu her zaman alaka skoruna göre yüksekten sırala
    df_sorted = df.sort_values("relevance", ascending=False)
    all_rows_html="".join(_row_html(r) for _,r in df_sorted.iterrows())
    profile_html="".join(_profile_card(p) for p in profiles) if profiles else '<p class="empty-msg">Şirket tespit edilemedi.</p>'
    co_tags_html="".join(f'<button class="chip-co" onclick="filterCo(this,\'{_e(c)}\')">{_e(c)}</button>' for c in sorted(co_set))
    cat_opts="".join(f'<option value="{_e(k)}">{_e(k)} ({v})</option>' for k,v in sorted(cc.items()))
    reg_opts="".join(f'<option value="{_e(k)}">{_e(k)} ({v})</option>' for k,v in sorted(rc_.items()))
    j=lambda x: json.dumps(x,ensure_ascii=False)

    # ── En önemli yatırım haberleri (sidebar için) ───────────────────────
    top_inv=df[df["category"].str.contains("Yatırım|Startup",na=False)].head(5)
    top_inv_html=""
    for _,r in top_inv.iterrows():
        url = r["url"] if str(r["url"]).startswith("http") else "#"
        fin = r.get("fin_amount","") or r.get("capacity","")
        cat = r["category"]; fc = CAT_COLORS.get(cat,"#64748b")
        top_inv_html+=(
            f'<a href="{_e(url)}" target="_blank" class="sidebar-item">'
            f'<div class="si-title">{_e(str(r["title"])[:80])}</div>'
            f'{"<div class=si-amt>"+_e(fin)+"</div>" if fin else ""}'
            f'<div class="si-meta">{REG_FLAGS.get(r["region"],"🌍")} '
            f'<span style="color:{fc};font-weight:600">{_e(cat)}</span></div>'
            f'</a>'
        )

    # ── Toplam yatırım tahmini ────────────────────────────────────────────
    total_inv_amounts=[]
    for fin in df["fin_amount"]:
        if not fin: continue
        m=re.search(r'([\d,\.]+)\s*(billion|million|bn|mn|b|m)',str(fin),re.I)
        if m:
            num=float(m.group(1).replace(',',''))
            unit=m.group(2).lower()
            if unit in ['billion','bn']: num*=1000
            total_inv_amounts.append(num)
    total_inv_est=f"${sum(total_inv_amounts)/1000:.1f}B+" if sum(total_inv_amounts)>1000 else f"${sum(total_inv_amounts):.0f}M+" if total_inv_amounts else "—"

    html_parts=[]
    html_parts.append(f"""<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>⚡ Enerji Depolama İstihbarat Platformu</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
:root{{
  --bg:#0a0f1a;--s1:#0f1624;--s2:#162033;--s3:#080d16;--s4:#1a2840;
  --bd:#1e3048;--bd2:#2a4060;
  --t1:#e2eeff;--t2:#7a9cc4;--t3:#3d5a7a;
  --acc:#38bdf8;--acc2:#7dd3fc;--acc3:#bae6fd;
  --grn:#10b981;--amb:#f59e0b;--red:#ef4444;--pur:#8b5cf6;
  --r:10px;--r2:6px;
  --fn:-apple-system,BlinkMacSystemFont,'Segoe UI',system-ui,sans-serif;
  --shadow:0 4px 24px rgba(0,0,0,.5);
  --shadow-sm:0 2px 12px rgba(0,0,0,.35);
}}
[data-theme="light"]{{
  --bg:#f5f7fa;--s1:#ffffff;--s2:#f0f3f8;--s3:#e8edf5;--s4:#dde4f0;
  --bd:#d0daea;--bd2:#b8c8df;
  --t1:#1a2a3a;--t2:#4a6070;--t3:#7a95a8;
  --acc:#0077b6;--acc2:#0096c7;--acc3:#00b4d8;
  --grn:#0d9668;--amb:#c07a00;--red:#c0392b;--pur:#6d28d9;
  --shadow:0 2px 16px rgba(0,0,0,.08);
  --shadow-sm:0 1px 6px rgba(0,0,0,.05);
}}
[data-theme="light"] body{{background:var(--bg)}}
[data-theme="light"] .topbar{{
  background:linear-gradient(135deg,#1a3a6a 0%,#0d4a30 100%)!important}}
[data-theme="light"] .kpi{{box-shadow:0 1px 4px rgba(0,0,0,.06)}}
[data-theme="light"] .tbl-box{{box-shadow:0 1px 4px rgba(0,0,0,.06)}}
[data-theme="light"] .badge-co{{background:#dbeafe;color:#1e40af;border-color:#93c5fd}}
[data-theme="light"] .badge-src{{background:#e8edf5;color:#4a6070}}
[data-theme="light"] thead tr{{background:#edf1f8}}
[data-theme="light"] tr[data-url]:hover td{{background:rgba(0,119,182,.04)}}
[data-theme="light"] .nav{{background:#ffffff}}
[data-theme="light"] .fbar{{background:#ffffff}}
[data-theme="light"] .chip-wrap{{background:#ffffff}}
[data-theme="light"] .sidebar{{background:#ffffff;border-left-color:#d0daea}}
[data-theme="light"] .top-card{{background:#ffffff}}
[data-theme="light"] .cp-card{{background:#ffffff}}
[data-theme="light"] .chart-card{{background:#ffffff}}
[data-theme="light"] .sidebar-item{{background:#f0f3f8}}
[data-theme="light"] .news-link{{color:var(--acc)}}
[data-theme="light"] .tr-title{{color:#0077b6}}
[data-theme="light"] select,[data-theme="light"] input[type=text]{{
  background:#f0f3f8;border-color:#d0daea;color:#1a2a3a}}
body{{background:var(--bg);color:var(--t1);font-family:var(--fn);font-size:13px;line-height:1.5;min-height:100vh;overflow-x:hidden}}

.topbar{{background:linear-gradient(135deg,#0d1e3a 0%,#0a2218 100%);
  padding:0 28px;height:56px;display:flex;align-items:center;
  justify-content:space-between;gap:12px;
  border-bottom:1px solid var(--bd);position:sticky;top:0;z-index:100;box-shadow:var(--shadow)}}
.tb-brand{{display:flex;align-items:center;gap:10px}}
.tb-logo{{width:28px;height:28px;background:linear-gradient(135deg,var(--acc),#0ea5e9);
  border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:14px}}
.tb-title{{font-size:14px;font-weight:700;color:var(--t1);letter-spacing:-.2px}}
.tb-sub{{font-size:10px;color:var(--t3);margin-left:38px;margin-top:-4px}}
.tb-right{{display:flex;align-items:center;gap:8px}}
.tb-pill{{background:rgba(56,189,248,.12);color:var(--acc2);border:1px solid rgba(56,189,248,.25);
  border-radius:20px;padding:3px 11px;font-size:10px;white-space:nowrap}}
.tb-pill.green{{background:rgba(16,185,129,.12);color:#6ee7b7;border-color:rgba(16,185,129,.25)}}
.dot-live{{width:6px;height:6px;background:var(--grn);border-radius:50%;animation:blink 2s infinite}}
@keyframes blink{{0%,100%{{opacity:1}}50%{{opacity:.3}}}}
.theme-btn{{background:var(--s2);border:1px solid var(--bd);color:var(--t2);
  border-radius:20px;padding:3px 10px;font-size:11px;cursor:pointer;
  transition:all .2s;user-select:none}}
.theme-btn:hover{{border-color:var(--acc);color:var(--t1)}}

.layout{{display:grid;grid-template-columns:1fr 280px;gap:0;min-height:calc(100vh - 56px)}}
.main{{overflow-y:auto}}
.sidebar{{background:var(--s1);border-left:1px solid var(--bd);padding:16px;
  display:flex;flex-direction:column;gap:14px;position:sticky;
  top:56px;height:calc(100vh - 56px);overflow-y:auto}}

.kpi-row{{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;padding:14px 20px}}
.kpi{{background:var(--s1);border:1px solid var(--bd);border-radius:var(--r);
  padding:12px 14px;cursor:pointer;transition:all .15s;position:relative;overflow:hidden}}
.kpi::before{{content:'';position:absolute;top:0;left:0;right:0;height:2px;
  background:var(--kpi-color,var(--acc));opacity:0;transition:opacity .15s}}
.kpi:hover{{border-color:var(--bd2);transform:translateY(-1px)}}
.kpi:hover::before,.kpi.on::before{{opacity:1}}
.kpi.on{{border-color:var(--acc);background:rgba(56,189,248,.05)}}
.kpi-v{{font-size:28px;font-weight:700;line-height:1}}
.kpi-l{{font-size:9px;color:var(--t2);margin-top:3px;text-transform:uppercase;letter-spacing:.5px}}
.kpi-s{{font-size:8px;color:var(--t3);margin-top:1px}}

.chart-grid{{display:grid;grid-template-columns:repeat(2,1fr);gap:8px;padding:0 20px 10px}}
.chart-card{{background:var(--s1);border:1px solid var(--bd);border-radius:var(--r);padding:10px 14px}}
.chart-hd{{font-size:9px;font-weight:600;color:var(--t3);text-transform:uppercase;letter-spacing:.5px;margin-bottom:8px}}
.chart-box{{position:relative;height:110px}}

.nav{{display:flex;gap:0;padding:0 20px;background:var(--s1);border-bottom:1px solid var(--bd)}}
.nav-btn{{padding:8px 16px;font-size:11px;font-weight:600;color:var(--t3);
  background:transparent;border:none;cursor:pointer;border-bottom:2px solid transparent;transition:all .15s}}
.nav-btn:hover{{color:var(--t2)}}
.nav-btn.on{{color:var(--acc2);border-bottom-color:var(--acc)}}
.tab{{display:none}}.tab.on{{display:block}}

.fbar{{display:flex;align-items:center;gap:6px;flex-wrap:wrap;
  padding:8px 20px;background:var(--s1);border-bottom:1px solid var(--bd)}}
.fbar label{{font-size:9px;color:var(--t3);text-transform:uppercase;letter-spacing:.4px}}
select,input[type=text]{{background:var(--s2);border:1px solid var(--bd);color:var(--t1);
  border-radius:var(--r2);padding:4px 8px;font-size:11px;outline:none}}
select:focus,input:focus{{border-color:var(--acc)}}
.btn-reset{{background:transparent;border:1px solid var(--bd);color:var(--t3);
  border-radius:var(--r2);padding:4px 9px;font-size:10px;cursor:pointer}}
.btn-reset:hover{{color:var(--t1)}}
.f-count{{margin-left:auto;font-size:10px;color:var(--t3)}}

.chip-wrap{{padding:7px 20px;display:flex;flex-wrap:wrap;gap:4px;
  background:var(--s1);border-bottom:1px solid var(--bd)}}
.chip-title{{font-size:9px;color:var(--t3);text-transform:uppercase;letter-spacing:.4px;width:100%;margin-bottom:3px}}
.chip-co{{background:var(--s2);border:1px solid var(--bd);color:var(--t2);
  border-radius:20px;padding:2px 8px;font-size:9px;cursor:pointer;transition:all .12s}}
.chip-co:hover,.chip-co.on{{background:var(--acc);color:#fff;border-color:var(--acc)}}

.tbl-wrap{{padding:0 20px 24px}}
.tbl-box{{background:var(--s1);border:1px solid var(--bd);border-radius:var(--r);overflow:hidden;box-shadow:var(--shadow-sm)}}
table{{width:100%;border-collapse:collapse}}
thead tr{{background:var(--s3)}}
th{{padding:8px 10px;font-size:9px;font-weight:600;color:var(--t3);
  text-transform:uppercase;letter-spacing:.4px;border-bottom:1px solid var(--bd);
  cursor:pointer;white-space:nowrap;user-select:none}}
th:hover{{color:var(--acc2)}}
th.asc::after{{content:" ↑";color:var(--acc)}}
th.desc::after{{content:" ↓";color:var(--acc)}}
td{{padding:7px 10px;border-bottom:1px solid var(--bd);vertical-align:top}}
tr:last-child td{{border-bottom:none}}
tr[data-url]:hover td{{background:rgba(56,189,248,.04)}}
tr.hide{{display:none}}
.td-main{{min-width:220px;max-width:360px}}
.news-link{{color:var(--acc);text-decoration:none;font-size:12px;font-weight:500;line-height:1.4;display:block}}
.news-link:hover{{color:var(--acc2);text-decoration:underline}}
.tr-title{{font-size:11px;color:#6ee7b7;font-weight:500;margin-top:3px;line-height:1.4}}
.co-row{{display:flex;flex-wrap:wrap;gap:3px;margin-top:3px}}
.meta-row{{display:flex;gap:5px;margin-top:3px;align-items:center}}
.badge-co{{background:#0d2040;color:#7dd3fc;border:1px solid #1e4070;border-radius:8px;padding:1px 6px;font-size:8px}}
.badge-src{{background:var(--s2);color:var(--t3);border-radius:3px;padding:1px 4px;font-size:8px}}
.meta-pub{{font-size:8px;color:var(--t3)}}
.badge-cat{{display:inline-block;border-radius:20px;padding:2px 7px;font-size:9px;white-space:nowrap}}
.badge-reg{{display:inline-block;border-radius:20px;color:#fff;padding:2px 7px;font-size:9px;white-space:nowrap}}
.badge-stg{{background:#1a1200;color:#f59e0b;border-radius:5px;padding:1px 6px;font-size:9px}}
.val-fin{{color:var(--grn);font-weight:600;font-size:10px;display:block}}
.val-cap{{color:var(--acc2);font-size:9px;display:block}}
.dash{{color:var(--t3)}}
.rel-track{{background:var(--s2);border-radius:3px;height:4px;width:60px;overflow:hidden;margin-bottom:2px}}
.rel-fill{{height:4px;border-radius:3px}}
.rel-num{{font-size:9px;color:var(--t2)}}

.cp-wrap{{padding:12px 20px 24px}}
.cp-bar{{display:flex;align-items:center;gap:7px;flex-wrap:wrap;padding:8px 20px;
  background:var(--s1);border-bottom:1px solid var(--bd)}}
.cp-bar-title{{font-size:9px;color:var(--t3);text-transform:uppercase;letter-spacing:.4px}}
.cp-sort-btn{{background:var(--s2);border:1px solid var(--bd);color:var(--t2);
  border-radius:var(--r2);padding:2px 9px;font-size:10px;cursor:pointer;transition:all .12s}}
.cp-sort-btn.on{{background:var(--acc);color:#fff;border-color:var(--acc)}}
.cp-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:9px}}
.cp-card{{background:var(--s1);border:1px solid var(--bd);border-radius:var(--r);
  padding:13px 14px;display:flex;flex-direction:column;gap:6px;transition:all .15s;box-shadow:var(--shadow-sm)}}
.cp-card:hover{{transform:translateY(-2px);border-color:var(--bd2);box-shadow:var(--shadow)}}
.cp-card.hide{{display:none}}
.cp-top{{display:flex;align-items:flex-start;justify-content:space-between;gap:6px}}
.cp-name{{font-size:13px;font-weight:700;color:var(--t1);flex:1}}
.badge-startup{{background:rgba(245,158,11,.12);color:#fbbf24;border:1px solid rgba(245,158,11,.25);
  border-radius:9px;padding:1px 6px;font-size:8px;font-weight:600;vertical-align:middle;margin-left:4px}}
.cp-score-wrap{{display:flex;align-items:center;gap:4px;flex-shrink:0}}
.cp-trend{{font-size:15px;font-weight:700;line-height:1}}
.cp-score{{font-size:20px;font-weight:700;line-height:1}}
.cp-region{{font-size:10px;color:var(--t3)}}
.score-bar-track{{background:var(--s2);border-radius:3px;height:3px;overflow:hidden}}
.score-bar-fill{{height:3px;border-radius:3px;transition:width .3s}}
.cp-stats{{display:flex;gap:8px;font-size:10px;color:var(--t2)}}
.cp-stats span::before{{content:"·";margin-right:4px;color:var(--t3)}}
.cp-stats span:first-child::before{{content:""}}
.cp-amounts,.cp-stages{{display:flex;flex-wrap:wrap;gap:4px}}
.cp-news{{display:flex;flex-direction:column;gap:3px;border-top:1px solid var(--bd);padding-top:6px}}
.cp-news-link{{display:flex;align-items:flex-start;gap:4px;color:var(--t2);
  font-size:9px;line-height:1.4;text-decoration:none;transition:color .1s}}
.cp-news-link:hover{{color:var(--acc2)}}
.cp-news-dot{{width:4px;height:4px;border-radius:50%;margin-top:4px;flex-shrink:0}}

.sidebar-hd{{font-size:9px;font-weight:700;color:var(--t3);text-transform:uppercase;
  letter-spacing:.5px;margin-bottom:8px;display:flex;align-items:center;gap:6px}}
.sidebar-hd::after{{content:'';flex:1;height:1px;background:var(--bd)}}
.sidebar-item{{display:block;padding:9px 10px;background:var(--s2);
  border:1px solid var(--bd);border-radius:var(--r2);margin-bottom:6px;
  text-decoration:none;transition:all .12s}}
.sidebar-item:hover{{border-color:var(--bd2);background:var(--s4)}}
.si-title{{font-size:11px;color:var(--t1);line-height:1.4;margin-bottom:4px;font-weight:500}}
.si-amt{{font-size:11px;color:var(--grn);font-weight:700;margin-bottom:3px}}
.si-meta{{font-size:9px;color:var(--t3)}}
.stat-card{{background:var(--s2);border:1px solid var(--bd);border-radius:var(--r2);padding:10px 12px;text-align:center}}
.stat-v{{font-size:20px;font-weight:700}}
.stat-l{{font-size:9px;color:var(--t3);margin-top:2px;text-transform:uppercase;letter-spacing:.4px}}
.stat-grid{{display:grid;grid-template-columns:1fr 1fr;gap:6px}}
.region-bar{{margin-bottom:6px}}
.rb-label{{font-size:10px;color:var(--t2);margin-bottom:3px;display:flex;justify-content:space-between}}
.rb-track{{background:var(--s2);border-radius:3px;height:6px;overflow:hidden}}
.rb-fill{{height:6px;border-radius:3px}}

.empty-msg{{padding:40px;color:var(--t3);font-size:12px}}

.top-region-wrap{{padding:0 20px 10px}}
.top-region-hd{{font-size:10px;font-weight:700;color:var(--t2);text-transform:uppercase;
  letter-spacing:.5px;margin-bottom:8px}}
.top-strip{{margin-bottom:10px}}
.top-strip-label{{display:flex;align-items:center;justify-content:space-between;
  padding:5px 10px;margin-bottom:5px;font-size:11px;font-weight:700}}
.top-strip-count{{font-size:9px;color:var(--t3);font-weight:400}}
.top-cards-row{{display:grid;grid-template-columns:repeat(5,1fr);gap:6px}}
.top-card{{display:flex;flex-direction:column;gap:4px;padding:9px 10px;
  background:var(--s1);border:1px solid var(--bd);border-radius:var(--r2);
  text-decoration:none;transition:all .12s}}
.top-card:hover{{border-color:var(--bd2);background:var(--s2);transform:translateY(-1px)}}
.top-card-title{{font-size:11px;color:var(--t1);font-weight:500;line-height:1.35;flex:1}}
.top-card-meta{{display:flex;align-items:center;gap:5px;margin-top:3px}}
.top-card-fin{{font-size:10px;color:var(--grn);font-weight:700}}
.top-card-rel{{font-size:9px;color:var(--t3);margin-left:auto}}
::-webkit-scrollbar{{width:5px;height:5px}}
::-webkit-scrollbar-track{{background:var(--s1)}}
::-webkit-scrollbar-thumb{{background:var(--bd2);border-radius:3px}}
@media(max-width:1100px){{
  .layout{{grid-template-columns:1fr}}
  .sidebar{{display:none}}
  .kpi-row{{grid-template-columns:repeat(3,1fr)}}
  .chart-grid{{grid-template-columns:1fr 1fr}}
  .top-cards-row{{grid-template-columns:repeat(3,1fr)}}
}}
@media(max-width:680px){{
  .kpi-row{{grid-template-columns:repeat(2,1fr)}}
  .chart-grid{{grid-template-columns:1fr}}
  .top-cards-row{{grid-template-columns:repeat(2,1fr)}}
}}
</style>
</head>
<body>""")

    # TOPBAR
    html_parts.append(
        f'<div class="topbar"><div class="tb-brand">'
        f'<div class="tb-logo">⚡</div>'
        f'<div><div class="tb-title">Günlük Enerji Depolama &amp; Yatırım Raporu</div>'
        f'<div class="tb-sub">AB · İngiltere · Türkiye · ABD · Çin · Singapur · APAC</div></div></div>'
        f'<div class="tb-right"><div class="dot-live"></div>'
        f'<button class="theme-btn" onclick="toggleTheme()" id="themeBtn">🌙 Koyu</button>'
        f'<span class="tb-pill green">{_e(ts_str)}</span>'
        f'<span class="tb-pill">{total} haber · {_e(ts_full)}</span>'
        f'</div></div>')

    # LAYOUT AÇILIŞ
    html_parts.append('<div class="layout"><div class="main">')

    # KPI
    def kpi(v,l,s,col,fn,kpi_col=None):
        c=kpi_col or col
        return (f'<div class="kpi" onclick="{fn}" style="--kpi-color:{c}">'
                f'<div class="kpi-v" style="color:{col}">{v}</div>'
                f'<div class="kpi-l">{l}</div>'
                f'<div class="kpi-s">{s}</div></div>')
    html_parts.append('<div class="kpi-row">')
    html_parts.append(kpi(total,"Toplam haber","Son 7 gün","#38bdf8","kpiFilt(this,'','')"))
    html_parts.append(kpi(inv_n,"Yatırım","Equity + Hibe","#10b981","kpiFilt(this,'Yatırım','cat')","#10b981"))
    html_parts.append(kpi(reg_n,"Regülasyon","6 bölge","#6366f1","kpiFilt(this,'Regülasyon','cat')","#6366f1"))
    html_parts.append(kpi(su_n,"Startup","Tespit edildi","#f59e0b","kpiFilt(this,'Startup','cat')","#f59e0b"))
    html_parts.append(kpi(len(profiles),"Şirket","Profil kartı","#8b5cf6","document.querySelectorAll('.nav-btn')[1].click()","#8b5cf6"))
    html_parts.append(kpi(hi_n,"Yüksek alaka","≥ 0.75 skor","#ef4444","kpiFilt(this,'0.75','rel')","#ef4444"))
    html_parts.append('</div>')

    # GRAFİKLER — her zaman görünür
    html_parts.append(
        '<div class="chart-grid">'
        '<div class="chart-card"><div class="chart-hd">Kategori dağılımı</div>'
        '<div class="chart-box"><canvas id="cCat"></canvas></div></div>'
        '<div class="chart-card"><div class="chart-hd">Bölge dağılımı</div>'
        '<div class="chart-box"><canvas id="cReg"></canvas></div></div>'
        '<div class="chart-card"><div class="chart-hd">Zaman serisi · Son 14 gün</div>'
        '<div class="chart-box"><canvas id="cTime"></canvas></div></div>'
        '<div class="chart-card"><div class="chart-hd">Alaka skoru</div>'
        '<div class="chart-box"><canvas id="cRel"></canvas></div></div>'
        '</div>')

    # ── Top 15 by region ─────────────────────────────────────────────
    reg_data    = _build_top_by_region(df)
    top_reg_html= _top_region_html(reg_data)
    html_parts.append(top_reg_html)

    # NAV
    html_parts.append(
        '<div class="nav">'
        f'<button class="nav-btn on" onclick="nav(this,\'t-news\')">📋 Haberler ({total})</button>'
        f'<button class="nav-btn" onclick="nav(this,\'t-co\')">🏢 Şirketler ({len(profiles)})</button>'
        '</div>')

    # TAB 1: HABERLER
    html_parts.append('<div id="t-news" class="tab on">')
    if co_tags_html:
        html_parts.append(f'<div class="chip-wrap"><div class="chip-title">Tespit edilen şirketler — tıkla filtrele</div>{co_tags_html}</div>')
    html_parts.append(
        f'<div class="fbar"><label>Ara</label>'
        f'<input type="text" id="fSrch" placeholder="başlık / kaynak..." style="width:160px" oninput="applyF()">'
        f'<label>Kategori</label><select id="fCat" onchange="applyF()"><option value="">Tümü</option>{cat_opts}</select>'
        f'<label>Bölge</label><select id="fReg" onchange="applyF()"><option value="">Tümü</option>{reg_opts}</select>'
        f'<label>Min Alaka</label><select id="fRel" onchange="applyF()">'
        f'<option value="0">Tümü</option><option value="0.25">≥ 0.25</option>'
        f'<option value="0.5">≥ 0.50</option><option value="0.75">≥ 0.75</option></select>'
        f'<button class="btn-reset" onclick="reset()">✕</button>'
        f'<span class="f-count" id="fCount">{total} sonuç</span></div>')
    html_parts.append(
        f'<div class="tbl-wrap"><div class="tbl-box"><table>'
        f'<thead><tr>'
        f'<th onclick="sortTbl(0)">Başlık &amp; Şirket</th>'
        f'<th onclick="sortTbl(1)">Kategori</th>'
        f'<th onclick="sortTbl(2)">Bölge</th>'
        f'<th onclick="sortTbl(3)">Evre</th>'
        f'<th onclick="sortTbl(4)">Tutar / Kapasite</th>'
        f'<th onclick="sortTbl(5)">Alaka ↕</th>'
        f'</tr></thead>'
        f'<tbody id="tBody">{all_rows_html}</tbody>'
        f'</table></div></div>')
    html_parts.append('</div>')  # t-news

    # TAB 2: ŞİRKET PROFİLLERİ
    html_parts.append('<div id="t-co" class="tab">')
    html_parts.append(
        f'<div class="cp-bar">'
        f'<span class="cp-bar-title">🏢 {len(profiles)} şirket · Skor = mention + yatırım + tazelik · Trend: son 7 vs 7-30 gün</span>'
        f'<input type="text" id="cpSrch" placeholder="ara..." style="width:130px;margin-left:auto" oninput="filterCards()">'
        f'<button class="cp-sort-btn on" onclick="sortCards(\'score\',this)">Skor ↓</button>'
        f'<button class="cp-sort-btn" onclick="sortCards(\'count\',this)">Haber</button>'
        f'<button class="cp-sort-btn" onclick="sortCards(\'inv\',this)">Yatırım</button>'
        f'<button class="cp-sort-btn" onclick="sortCards(\'name\',this)">A–Z</button>'
        f'</div>')
    html_parts.append(f'<div class="cp-wrap"><div class="cp-grid" id="cpGrid">{profile_html}</div></div>')
    html_parts.append('</div>')  # t-co

    # MAIN KAPANIŞ
    html_parts.append('</div>')

    # SIDEBAR
    max_reg=max(rc_.values()) if rc_ else 1
    reg_bars="".join(
        f'<div class="region-bar">'
        f'<div class="rb-label"><span>{REG_FLAGS.get(k,"🌍")} {_e(k)}</span><span>{v}</span></div>'
        f'<div class="rb-track"><div class="rb-fill" style="width:{int(v/max_reg*100)}%;background:{REG_COLORS.get(k,"#64748b")}"></div></div>'
        f'</div>'
        for k,v in sorted(rc_.items(),key=lambda x:-x[1]))

    html_parts.append(
        '<div class="sidebar">'
        f'<div class="sidebar-hd">📊 Özet</div>'
        f'<div class="stat-grid">'
        f'<div class="stat-card"><div class="stat-v" style="color:#10b981">{inv_n}</div><div class="stat-l">Yatırım</div></div>'
        f'<div class="stat-card"><div class="stat-v" style="color:#6366f1">{reg_n}</div><div class="stat-l">Regülasyon</div></div>'
        f'<div class="stat-card"><div class="stat-v" style="color:#f59e0b">{su_n}</div><div class="stat-l">Startup</div></div>'
        f'<div class="stat-card"><div class="stat-v" style="color:#10b981">{_e(total_inv_est)}</div><div class="stat-l">Toplam Yatırım</div></div>'
        f'</div>'
        f'<div class="sidebar-hd">🌍 Bölge Dağılımı</div>'
        f'{reg_bars}'
        f'<div class="sidebar-hd">💰 Öne Çıkan Yatırımlar</div>'
        f'{top_inv_html if top_inv_html else "<p class=empty-msg>Yatırım haberi yok</p>"}'
        '</div>')

    # LAYOUT KAPANIŞ
    html_parts.append('</div>')

    # JS
    js=(
        "Chart.defaults.color='#3d5a7a';Chart.defaults.borderColor='#1e3048';"
        "Chart.defaults.font.family=\"-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif\";"
        "Chart.defaults.font.size=10;"
        "const TT={backgroundColor:'#0f1624',borderColor:'#1e3048',borderWidth:1,"
        "titleColor:'#e2eeff',bodyColor:'#7a9cc4',padding:9,cornerRadius:6};"

        "new Chart(document.getElementById('cCat'),{type:'doughnut',"
        "data:{labels:"+j(cat_lbl)+",datasets:[{data:"+j(cat_vals)+","
        "backgroundColor:"+j(cat_cols)+",borderWidth:2,borderColor:'#0c0e14',hoverOffset:6}]},"
        "options:{responsive:true,maintainAspectRatio:false,cutout:'68%',"
        "plugins:{legend:{position:'right',labels:{boxWidth:8,padding:6,font:{size:10}}},"
        "tooltip:{...TT}}}});"

        "new Chart(document.getElementById('cReg'),{type:'bar',"
        "data:{labels:"+j(reg_lbl)+",datasets:[{data:"+j(reg_vals)+","
        "backgroundColor:"+j(reg_cols)+",borderRadius:4,barThickness:12}]},"
        "options:{responsive:true,maintainAspectRatio:false,indexAxis:'y',"
        "plugins:{legend:{display:false},tooltip:{...TT}},"
        "scales:{x:{grid:{color:'#1e2535'},ticks:{color:'#4a5572'}},"
        "y:{grid:{display:false},ticks:{color:'#7a9cc4'}}}}});"

        "new Chart(document.getElementById('cTime'),{type:'line',"
        "data:{labels:"+j(tl_lbl)+",datasets:["
        "{label:'Tüm',data:"+j(tl_all)+",borderColor:'#38bdf8',backgroundColor:'rgba(56,189,248,.06)',fill:true,tension:.4,pointRadius:3,borderWidth:2},"
        "{label:'Yatırım',data:"+j(tl_inv)+",borderColor:'#10b981',backgroundColor:'transparent',tension:.4,pointRadius:3,borderWidth:2},"
        "{label:'Startup',data:"+j(tl_su)+",borderColor:'#f59e0b',backgroundColor:'transparent',tension:.4,pointRadius:3,borderWidth:2}"
        "]},"
        "options:{responsive:true,maintainAspectRatio:false,"
        "plugins:{legend:{display:true,labels:{boxWidth:8,padding:6,font:{size:10}}},tooltip:{...TT}},"
        "scales:{x:{grid:{color:'#1e3048'},ticks:{color:'#3d5a7a',maxRotation:40}},"
        "y:{grid:{color:'#1e3048'},ticks:{color:'#3d5a7a'}}}}});"

        "new Chart(document.getElementById('cRel'),{type:'bar',"
        "data:{labels:"+j(blbl)+",datasets:[{data:"+j(bcnt)+","
        "backgroundColor:['#1e3048','#2a4060','#f59e0b','#10b981','#34d399'],"
        "borderRadius:4,barThickness:22}]},"
        "options:{responsive:true,maintainAspectRatio:false,"
        "plugins:{legend:{display:false},tooltip:{...TT}},"
        "scales:{x:{grid:{display:false},ticks:{color:'#3d5a7a'}},"
        "y:{grid:{color:'#1e3048'},ticks:{color:'#3d5a7a'}}}}});"

        "function toggleTheme(){"
        "const html=document.documentElement;"
        "const btn=document.getElementById('themeBtn');"
        "if(html.getAttribute('data-theme')==='light'){"
        "html.removeAttribute('data-theme');btn.textContent='🌙 Koyu';}"
        "else{html.setAttribute('data-theme','light');btn.textContent='☀️ Açık';}}"

        "function nav(btn,id){"
        "document.querySelectorAll('.nav-btn').forEach(b=>b.classList.remove('on'));"
        "document.querySelectorAll('.tab').forEach(t=>t.classList.remove('on'));"
        "btn.classList.add('on');document.getElementById(id).classList.add('on');}"

        "function kpiFilt(el,val,type){"
        "document.querySelectorAll('.kpi').forEach(k=>k.classList.remove('on'));"
        "if(!val){reset();return;}el.classList.add('on');"
        "document.querySelectorAll('.nav-btn')[0].click();"
        "if(type==='cat'){const rows=document.querySelectorAll('#tBody tr');let v=0;"
        "rows.forEach(r=>{const ok=r.dataset.cat.includes(val);r.classList.toggle('hide',!ok);if(ok)v++;});"
        "document.getElementById('fCount').textContent=v+' sonuç';}"
        "else if(type==='rel'){document.getElementById('fRel').value=val;applyF();}}"

        "function rowClick(e,tr){if(e.target.tagName==='A')return;"
        "const u=tr.dataset.url;if(u&&u!=='#')window.open(u,'_blank');}"

        "let _co=null;"
        "function applyF(){const s=document.getElementById('fSrch').value.toLowerCase();"
        "const c=document.getElementById('fCat').value;"
        "const rg=document.getElementById('fReg').value;"
        "const mr=parseFloat(document.getElementById('fRel').value);"
        "const rows=document.querySelectorAll('#tBody tr');let v=0;"
        "rows.forEach(row=>{const ok=(!s||row.dataset.search.includes(s))&&"
        "(!c||row.dataset.cat===c)&&(!rg||row.dataset.region===rg)&&"
        "(parseFloat(row.dataset.rel)>=mr)&&(!_co||row.textContent.includes(_co));"
        "row.classList.toggle('hide',!ok);if(ok)v++;});"
        "document.getElementById('fCount').textContent=v+' sonuç';}"

        "function reset(){document.getElementById('fSrch').value='';"
        "document.getElementById('fCat').value='';"
        "document.getElementById('fReg').value='';"
        "document.getElementById('fRel').value='0';"
        "_co=null;"
        "document.querySelectorAll('.kpi').forEach(k=>k.classList.remove('on'));"
        "document.querySelectorAll('.chip-co').forEach(b=>b.classList.remove('on'));"
        "applyF();}"

        "function filterCo(btn,name){if(_co===name){_co=null;btn.classList.remove('on');}"
        "else{_co=name;document.querySelectorAll('.chip-co').forEach(b=>b.classList.remove('on'));"
        "btn.classList.add('on');}applyF();}"

        "let _sc=5,_sd=-1;"
        "function sortTbl(col){if(_sc===col)_sd*=-1;else{_sc=col;_sd=-1;}"
        "const ths=document.querySelectorAll('thead th');"
        "ths.forEach((th,i)=>{th.classList.remove('asc','desc');"
        "if(i===col)th.classList.add(_sd===1?'asc':'desc');});"
        "const tb=document.getElementById('tBody');"
        "Array.from(tb.querySelectorAll('tr')).sort((a,b)=>{"
        "let av=a.cells[col]?.textContent.trim()||'';"
        "let bv=b.cells[col]?.textContent.trim()||'';"
        "const an=parseFloat(av),bn=parseFloat(bv);"
        "if(!isNaN(an)&&!isNaN(bn))return(an-bn)*_sd;"
        "return av.localeCompare(bv,'tr')*_sd;"
        "}).forEach(r=>tb.appendChild(r));}"
        "sortTbl(5);"

        "function filterCards(){const q=(document.getElementById('cpSrch')?.value||'').toLowerCase();"
        "document.querySelectorAll('.cp-card').forEach(c=>{c.classList.toggle('hide',!(!q||c.textContent.toLowerCase().includes(q)));});}"

        "function sortCards(by,btn){document.querySelectorAll('.cp-sort-btn').forEach(b=>b.classList.remove('on'));"
        "btn.classList.add('on');"
        "const g=document.getElementById('cpGrid');if(!g)return;"
        "Array.from(g.querySelectorAll('.cp-card')).sort((a,b)=>{"
        "if(by==='score')return+b.dataset.score-+a.dataset.score;"
        "if(by==='name')return(a.dataset.name||'').localeCompare(b.dataset.name||'','tr');"
        "if(by==='count')return+b.dataset.count-+a.dataset.count;"
        "if(by==='inv')return+b.dataset.inv-+a.dataset.inv;"
        "return 0;}).forEach(c=>g.appendChild(c));}"
    )
    html_parts.append(f'<script>{js}</script></body></html>')
    return "".join(html_parts)

# ══════════════════════════════════════════════════════════════════════════
# 7. ANA PLATFORM
# ══════════════════════════════════════════════════════════════════════════

class EnergyMonitor:
    def __init__(self,interval_min=1440,auto_export=True):
        self.interval=interval_min; self.auto_export=auto_export
        self.master_df=pd.DataFrame(); self.run_count=0
        print("🚀  Günlük Enerji Depolama &amp; Yatırım Raporu  v6")
        print(f"    Güncelleme: her {self.interval//60} saatte bir · Çeviri: {'✅' if _TR_OK else '⚠'}")

    def _step(self):
        self.run_count+=1
        today=datetime.datetime.utcnow().strftime("%d %B %Y")
        print(f"\n📰  Günlük Rapor — {today}")
        new_df=collect_all()
        if not new_df.empty:
            self.master_df=pd.concat([self.master_df,new_df],ignore_index=True).drop_duplicates(subset=["url"],keep="first")
            cutoff=(datetime.datetime.utcnow()-datetime.timedelta(hours=168)).isoformat()
            self.master_df=self.master_df[self.master_df["ts"]>=cutoff]
            self.master_df.reset_index(drop=True,inplace=True)
        df=self.master_df
        if df.empty: print("  ⚠  Veri yok."); return
        cc=df["category"].value_counts()
        print(f"\n  📊  Toplam:{len(df)} · Yatırım:{sum(v for k,v in cc.items() if 'Yatırım' in k)} · Regülasyon:{cc.get('Regülasyon',0)} · Startup:{cc.get('Startup',0)}")
        profiles=build_company_profiles(df)
        print(f"  🏢  {len(profiles)} şirket")
        if profiles[:5]:
            print("  🏆  Top 5:")
            for p in profiles[:5]:
                tr={"up":"↑","down":"↓","flat":"→"}[p["trend"]]
                print(f"      {p['name']:<28} {p['score']:>3}puan  {tr}  {p['count']}h")
        if self.auto_export:
            ts_tag=datetime.datetime.utcnow().strftime("%Y%m%d")
            df_exp=df.copy()
            df_exp["companies"]=df_exp["companies"].apply(lambda x: ", ".join(x) if isinstance(x,list) else str(x))
            df_exp.to_csv(f"energy_{ts_tag}.csv",index=False,encoding="utf-8-sig")
            html_p=f"energy_rapor_{ts_tag}.html"
            with open(html_p,"w",encoding="utf-8") as f:
                f.write(build_dashboard(df,profiles,self.run_count))
            print(f"  💾  {html_p}  ({os.path.getsize(html_p)//1024} KB)")
        print(f"\n  ⏳  Sonraki rapor: yarın aynı saatte")

    def run_once(self):
        self._step(); return self.master_df

    def run_forever(self):
        self._step(); schedule.every(self.interval).minutes.do(self._step)
        while True:
            try: schedule.run_pending(); time.sleep(30)
            except KeyboardInterrupt: print(f"\n🛑  Döngü:{self.run_count}"); break
            except Exception as ex: print(f"\n❌ {ex}"); time.sleep(60)

# ══════════════════════════════════════════════════════════════════════════
# ÇALIŞTIR
# ══════════════════════════════════════════════════════════════════════════
monitor = EnergyMonitor(interval_min=1440, auto_export=True)
df = monitor.run_once()

import glob
files = sorted(glob.glob("energy_dashboard_*.html"), reverse=True)
if files:
    print(f"\n🌐  {files[0]}")
    print(f"    from IPython.display import IFrame")
    print(f"    IFrame('{files[0]}', width='100%', height=960)")

# monitor.run_forever()
