"""Maintain search metadata and public machine-readable facts for BRIDGE GROUP."""
from pathlib import Path
from bs4 import BeautifulSoup
from datetime import datetime
from zoneinfo import ZoneInfo
import json, secrets, xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
DOCS=ROOT/'docs'
ORIGIN='https://bridgegroup.asia'
LANGS=['ko','en','ja','zh-Hans','zh-Hant','de','fr','es','pt','ru','ar','id','ms','vi','th','tr','bn']
TITLES={
'ko':'브릿지그룹 BRIDGE GROUP | 무역·친환경 소재·글로벌 비즈니스',
'en':'BRIDGE GROUP | Global Trade, Sustainable Materials & Brands',
'ja':'BRIDGE GROUP | 貿易・環境配慮型素材・グローバルビジネス',
'zh-Hans':'BRIDGE GROUP | 国际贸易、环保材料与全球业务',
'zh-Hant':'BRIDGE GROUP | 國際貿易、環保材料與全球業務',
'de':'BRIDGE GROUP | Welthandel, nachhaltige Materialien & Marken',
'fr':'BRIDGE GROUP | Commerce mondial, matériaux durables et marques',
'es':'BRIDGE GROUP | Comercio global, materiales sostenibles y marcas',
'pt':'BRIDGE GROUP | Comércio global, materiais sustentáveis e marcas',
'ru':'BRIDGE GROUP | Мировая торговля, экологичные материалы и бренды',
'ar':'BRIDGE GROUP | التجارة العالمية والمواد المستدامة والعلامات',
'id':'BRIDGE GROUP | Perdagangan Global, Material Berkelanjutan & Merek',
'ms':'BRIDGE GROUP | Perdagangan Global, Bahan Mampan & Jenama',
'vi':'BRIDGE GROUP | Thương mại toàn cầu, vật liệu bền vững và thương hiệu',
'th':'BRIDGE GROUP | การค้าโลก วัสดุยั่งยืน และแบรนด์ในเครือ',
'tr':'BRIDGE GROUP | Küresel Ticaret, Sürdürülebilir Malzemeler ve Markalar',
'bn':'BRIDGE GROUP | বিশ্ব বাণিজ্য, টেকসই উপকরণ ও ব্র্যান্ড'}
DESCRIPTIONS={
'ko':'브릿지그룹의 에이브릿지·에코브릿지·리시아·차이나뉴스·이음경제·OKCALL을 만나보세요. 글로벌 무역, PBAT·PLA 친환경 소재와 생분해성 필름·멀칭필름, 생수, 시장 정보, 경제신문, 보안 통화·메시지를 연결합니다.',
'en':'Discover BRIDGE GROUP: global trade, PBAT/PLA resins and biodegradable films, LEESEAH water, market intelligence, EUM ECONOMY and OKCALL secure communication.',
'ja':'BRIDGE GROUPの貿易、PBAT・PLA原料、生分解性フィルム・マルチフィルム、LEESEAHミネラルウォーター、市場情報、経済新聞、OKCALLのセキュア通信をご紹介します。',
'zh-Hans':'了解BRIDGE GROUP：国际贸易、PBAT与PLA环保原料、生物降解薄膜与农用地膜、LEESEAH矿泉水、中国市场资讯、EUM ECONOMY经济新闻及OKCALL安全通信。',
'zh-Hant':'認識BRIDGE GROUP：國際貿易、PBAT與PLA環保原料、生物分解薄膜與農用覆蓋膜、LEESEAH礦泉水、中國市場資訊、EUM ECONOMY經濟新聞與OKCALL安全通訊。',
'de':'BRIDGE GROUP: Welthandel, PBAT/PLA und biologisch abbaubare Folien, LEESEAH Mineralwasser, Marktinformationen, EUM ECONOMY und sichere Kommunikation mit OKCALL.',
'fr':'Découvrez BRIDGE GROUP : commerce, résines PBAT/PLA et films biodégradables, eau LEESEAH, marchés, journalisme économique et communication sécurisée OKCALL.',
'es':'Descubre BRIDGE GROUP: comercio, resinas PBAT/PLA y películas biodegradables, agua LEESEAH, mercados, EUM ECONOMY y comunicación segura con OKCALL.',
'pt':'Conheça a BRIDGE GROUP: comércio, resinas PBAT/PLA e filmes biodegradáveis, água LEESEAH, mercados, EUM ECONOMY e comunicação segura com a OKCALL.',
'ru':'BRIDGE GROUP: мировая торговля, сырьё PBAT/PLA и биоразлагаемые плёнки, вода LEESEAH, информация о рынках, газета EUM ECONOMY и защищённая связь OKCALL.',
'ar':'اكتشف BRIDGE GROUP: التجارة العالمية ومواد PBAT وPLA والأغشية القابلة للتحلل ومياه LEESEAH ومعلومات الأسواق وصحيفة EUM ECONOMY والاتصالات الآمنة من OKCALL.',
'id':'Kenali BRIDGE GROUP: perdagangan, resin PBAT/PLA dan film biodegradabel, air LEESEAH, informasi pasar, EUM ECONOMY, serta komunikasi aman OKCALL.',
'ms':'Kenali BRIDGE GROUP: perdagangan, resin PBAT/PLA dan filem biodegradasi, air LEESEAH, maklumat pasaran, EUM ECONOMY dan komunikasi selamat OKCALL.',
'vi':'Khám phá BRIDGE GROUP: thương mại, nhựa PBAT/PLA và màng phân hủy sinh học, nước LEESEAH, thông tin thị trường, EUM ECONOMY và liên lạc bảo mật OKCALL.',
'th':'รู้จัก BRIDGE GROUP: การค้าโลก วัตถุดิบ PBAT/PLA ฟิล์มย่อยสลายทางชีวภาพ น้ำแร่ LEESEAH ข้อมูลตลาด ข่าวเศรษฐกิจ EUM ECONOMY และการสื่อสารปลอดภัย OKCALL',
'tr':'BRIDGE GROUP: küresel ticaret, PBAT/PLA ve biyobozunur filmler, LEESEAH su, piyasa bilgileri, EUM ECONOMY ve OKCALL ile güvenli iletişim.',
'bn':'BRIDGE GROUP: বিশ্ব বাণিজ্য, PBAT/PLA কাঁচামাল ও জীবাণুবিয়োজ্য ফিল্ম, LEESEAH পানি, বাজারতথ্য, EUM ECONOMY সংবাদপত্র এবং OKCALL-এর নিরাপদ যোগাযোগ।'}
LOCALES=dict(zip(LANGS,['ko_KR','en_US','ja_JP','zh_CN','zh_TW','de_DE','fr_FR','es_ES','pt_BR','ru_RU','ar_SA','id_ID','ms_MY','vi_VN','th_TH','tr_TR','bn_BD']))
BRANDS=[('ABRIDGE','https://www.abridge.co.kr/','Organization'),('EcoBridge','https://www.ecobridge.biz/','Organization'),('CHINANEWS','https://chinanews.kr/','WebSite'),('LEESEAH','https://leeseah.com/','Brand'),('EUM ECONOMY','https://www.eumeconomy.com/','NewsMediaOrganization'),('OKCALL','https://okcall.app/','Brand')]

def url(lang):return ORIGIN+('/' if lang=='ko' else '/'+lang+'/')
def meta(doc,kind,name,value):
    for old in doc.head.select('meta['+kind+'="'+name+'"]'):old.decompose()
    tag=doc.new_tag('meta',attrs={kind:name,'content':value});doc.head.append(tag)

english=None
for lang in LANGS:
    path=DOCS/'index.html' if lang=='ko' else DOCS/lang/'index.html'
    doc=BeautifulSoup(path.read_text(encoding='utf-8-sig'),'html.parser')
    doc.title.string=TITLES[lang]
    meta(doc,'name','description',DESCRIPTIONS[lang])
    meta(doc,'name','robots','index, follow, max-image-preview:large')
    for key,value in {'og:type':'website','og:site_name':'BRIDGE GROUP','og:title':TITLES[lang],'og:description':DESCRIPTIONS[lang],'og:url':url(lang),'og:image':ORIGIN+'/assets/bridgegroup-og.png','og:image:width':'1200','og:image:height':'630','og:image:type':'image/png','og:image:alt':'BRIDGE GROUP','og:locale':LOCALES[lang]}.items():meta(doc,'property',key,value)
    for old in doc.head.select('meta[property="og:locale:alternate"]'):old.decompose()
    for other in LANGS:
        if other!=lang:doc.head.append(doc.new_tag('meta',attrs={'property':'og:locale:alternate','content':LOCALES[other]}))
    for key,value in {'twitter:card':'summary_large_image','twitter:title':TITLES[lang],'twitter:description':DESCRIPTIONS[lang],'twitter:image':ORIGIN+'/assets/bridgegroup-og.png','twitter:image:alt':'BRIDGE GROUP','theme-color':'#071c28'}.items():meta(doc,'name',key,value)
    for old in doc.head.select('link[rel="canonical"],link[rel="alternate"][hreflang],link[rel="icon"]'):old.decompose()
    doc.head.append(doc.new_tag('link',rel='canonical',href=url(lang)))
    for other in LANGS+['x-default']:doc.head.append(doc.new_tag('link',rel='alternate',hreflang=other,href=url('ko' if other=='x-default' else other)))
    doc.head.append(doc.new_tag('link',rel='icon',type='image/svg+xml',href=ORIGIN+'/assets/favicon.svg'))
    if not doc.head.select_one('link[href="https://fonts.gstatic.com"]'):doc.head.append(doc.new_tag('link',rel='preconnect',href='https://fonts.gstatic.com',crossorigin='anonymous'))
    org_id=ORIGIN+'/#organization'
    items=[]
    for position,(card,brand) in enumerate(zip(doc.select('.card'),BRANDS),1):
        name,official,kind=brand
        item={'@type':kind,'@id':ORIGIN+'/#'+name.lower().replace(' ','-'),'name':name,'url':official,'description':card.select_one('.card-body p').get_text(' ',strip=True)}
        if name in ['ABRIDGE','EcoBridge']:item['parentOrganization']={'@id':org_id}
        items.append({'@type':'ListItem','position':position,'item':item})
    graph={'@context':'https://schema.org','@graph':[
        {'@type':'Organization','@id':org_id,'name':'브릿지그룹' if lang=='ko' else 'BRIDGE GROUP','alternateName':['BRIDGE GROUP','Bridge Group','브릿지그룹'],'url':ORIGIN+'/','logo':{'@type':'ImageObject','url':ORIGIN+'/assets/bridgegroup-og.png','width':1200,'height':630},'description':DESCRIPTIONS[lang],'email':'ceo@bridgegroup.asia','contactPoint':{'@type':'ContactPoint','contactType':'business inquiries','email':'ceo@bridgegroup.asia','url':ORIGIN+'/#contact'},'subOrganization':[{'@id':ORIGIN+'/#abridge'},{'@id':ORIGIN+'/#ecobridge'}],'brand':[{'@id':ORIGIN+'/#leeseah'},{'@id':ORIGIN+'/#okcall'}]},
        {'@type':'WebSite','@id':ORIGIN+'/#website','name':'BRIDGE GROUP','alternateName':'브릿지그룹','url':ORIGIN+'/','publisher':{'@id':org_id},'inLanguage':LANGS},
        {'@type':'WebPage','@id':url(lang)+'#webpage','url':url(lang),'name':TITLES[lang],'description':DESCRIPTIONS[lang],'inLanguage':lang,'isPartOf':{'@id':ORIGIN+'/#website'},'about':{'@id':org_id},'mainEntity':{'@id':org_id},'primaryImageOfPage':{'@type':'ImageObject','url':ORIGIN+'/assets/bridgegroup-og.png'}},
        {'@type':'ItemList','@id':url(lang)+'#businesses','name':doc.select_one('.section-head h2').get_text(' ',strip=True),'itemListElement':items}
    ]}
    for old in doc.select('script[type="application/ld+json"]'):old.decompose()
    script=doc.new_tag('script',type='application/ld+json');script.string=json.dumps(graph,ensure_ascii=False,separators=(',',':'));doc.head.append(script)
    path.write_text(str(doc),encoding='utf-8')
    if lang=='en':english=doc

# All facts below are also present in the rendered company directory.
facts='''# BRIDGE GROUP

> BRIDGE GROUP (브릿지그룹) connects global trade, sustainable materials, mineral water, market intelligence, economic journalism and secure communication.

Official website: https://bridgegroup.asia/
Public business contact: ceo@bridgegroup.asia
Inquiry form: https://bridgegroup.asia/#contact

## Companies, brands and platforms

- [ABRIDGE](https://www.abridge.co.kr/): Agricultural trade, strategic materials and semiconductor equipment trade connecting Korea and China. The published company information states qualification for aT state trading.
- [EcoBridge](https://www.ecobridge.biz/): Its primary business is PBAT and PLA raw materials for eco-friendly bags, finished biodegradable films and biodegradable agricultural mulch films. HDPE and LLDPE are supplementary products.
- [LEESEAH](https://leeseah.com/): A bottled water and natural mineral water brand. Its product story concerns water from volcanic aquifer layers.
- [CHINANEWS](https://chinanews.kr/): A China market and commodities terminal with commodity spot prices, indices, foreign exchange, macroeconomic indicators and supply inquiries.
- [EUM ECONOMY / 이음경제](https://www.eumeconomy.com/): An economic newspaper covering global and Korean economies, trade, supply chains, commodities and semiconductors through data and analysis.
- [OKCALL](https://okcall.app/): A secure calls and messaging service.

## Language versions

'''
for lang in LANGS:facts+='- ['+lang+']('+url(lang)+')\n'
facts+='''
The translated BRIDGE GROUP pages share company website preview images with the English version. The EUM ECONOMY image remains in Korean. Website language availability is not a claim of staffed customer support in every language.

## Discovery

- [Sitemap](https://bridgegroup.asia/sitemap.xml)
- [Crawler access](https://bridgegroup.asia/robots.txt)

Source: the published BRIDGE GROUP company directory and the official company websites linked above.
'''
(DOCS/'llms.txt').write_text(facts,encoding='utf-8')
(DOCS/'robots.txt').write_text('User-agent: *\nAllow: /\n\nSitemap: https://bridgegroup.asia/sitemap-index.xml\n',encoding='utf-8')
NS='http://www.sitemaps.org/schemas/sitemap/0.9';XHTML='http://www.w3.org/1999/xhtml'
ET.register_namespace('',NS);ET.register_namespace('xhtml',XHTML)
site=ET.Element('{'+NS+'}urlset')
for lang in LANGS:
    node=ET.SubElement(site,'{'+NS+'}url');ET.SubElement(node,'{'+NS+'}loc').text=url(lang)
    ET.SubElement(node,'{'+NS+'}lastmod').text='2026-11-03'
    for other in LANGS+['x-default']:ET.SubElement(node,'{'+XHTML+'}link',rel='alternate',hreflang=other,href=url('ko' if other=='x-default' else other))
ET.indent(site)
(DOCS/'sitemap.xml').write_bytes(ET.tostring(site,encoding='utf-8',xml_declaration=True))
index=ET.Element('{'+NS+'}sitemapindex')
entry=ET.SubElement(index,'{'+NS+'}sitemap')
ET.SubElement(entry,'{'+NS+'}loc').text=ORIGIN+'/sitemap.xml'
ET.indent(index)
(DOCS/'sitemap-index.xml').write_bytes(ET.tostring(index,encoding='utf-8',xml_declaration=True))
(DOCS/'assets/favicon.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 40 32"><rect width="40" height="32" rx="6" fill="#071c28"/><circle cx="13" cy="16" r="10" fill="none" stroke="#59aac5" stroke-width="4"/><circle cx="27" cy="16" r="10" fill="none" stroke="#50b989" stroke-width="4"/></svg>',encoding='utf-8')
config=ROOT/'tools/indexnow.json'
if not config.exists():config.write_text(json.dumps({'key':secrets.token_hex(16)},indent=2),encoding='utf-8')
key=json.loads(config.read_text(encoding='utf-8'))['key']
(DOCS/(key+'.txt')).write_text(key,encoding='utf-8')
print('Updated search metadata for',len(LANGS),'languages; sitemap, robots, organization graph, llms.txt and IndexNow verification created.')

# Minimal URL-only sitemap: an independent supported format for crawler diagnostics.
(DOCS/'sitemap.txt').write_text(''.join(url(lang)+'\n' for lang in LANGS),encoding='utf-8')
