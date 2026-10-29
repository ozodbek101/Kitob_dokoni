"""
Do'konni namunaviy kitoblar bilan to'ldiradi.

    python manage.py seed_books          # mavjud bo'lmaganlarini qo'shadi
    python manage.py seed_books --reset  # barcha kitob va kategoriyalarni qayta yaratadi
"""
import random

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify

from shop.models import Book, Category

# Muqova ranglari: (asosiy, bezak) — lojuvard, firuza, anor, za'faron va boshqalar
PALETTES = [
    ("#1D3A6E", "#E8A317"), ("#0F6B6B", "#F2D49B"), ("#8E2C3A", "#F0C987"),
    ("#2E4A2A", "#E3B448"), ("#3B2C5A", "#7FD1C7"), ("#B4532A", "#1D3A6E"),
    ("#13424F", "#E9785A"), ("#5A3E2B", "#9BC4CB"), ("#1F5C8A", "#F5E1A4"),
    ("#6B1F4A", "#E8A317"), ("#24323F", "#57B8A6"), ("#7A6A1F", "#1B1F2A"),
]

CATEGORIES = [
    ("O‘zbek adabiyoti", "ozbek-adabiyoti", "Mumtoz va zamonaviy o‘zbek nasri hamda she’riyati"),
    ("Jahon adabiyoti", "jahon-adabiyoti", "Dunyo klassikasi va zamonaviy romanlar"),
    ("Biznes va moliya", "biznes", "Tadbirkorlik, boshqaruv va shaxsiy moliya"),
    ("Psixologiya", "psixologiya", "O‘zini anglash, odatlar va munosabatlar"),
    ("Bolalar uchun", "bolalar", "Ertaklar va bolalar sarguzashtlari"),
    ("Fan va texnologiya", "fan", "Ilm-fan, kosmos va dasturlash"),
    ("Tarix", "tarix", "Sivilizatsiyalar, shaxslar va voqealar"),
    ("Fantastika", "fantastika", "Fantastika, fentezi va distopiya"),
]

# (kategoriya slug, nomi, muallif, yil, sahifa, til, narx, qisqa tavsif)
BOOKS = [
    ("ozbek-adabiyoti", "O‘tkan kunlar", "Abdulla Qodiriy", 1926, 416, "uz", 69000,
     "O‘zbek romanchiligining ilk durdonasi: Otabek va Kumushning muhabbati XIX asr Toshkent va Marg‘ilon fonida."),
    ("ozbek-adabiyoti", "Mehrobdan chayon", "Abdulla Qodiriy", 1929, 320, "uz", 59000,
     "Qo‘qon xonligi saroyidagi fitnalar va Anvar bilan Ra’noning taqdiri haqida roman."),
    ("ozbek-adabiyoti", "Kecha va kunduz", "Cho‘lpon", 1936, 288, "uz", 55000,
     "Zebining fojiali qismati orqali mustamlaka davri jamiyati tasvirlangan roman."),
    ("ozbek-adabiyoti", "Sarob", "Abdulla Qahhor", 1937, 352, "uz", 58000,
     "Saidiyning ichki ziddiyatlari va davr bosimi haqidagi psixologik roman."),
    ("ozbek-adabiyoti", "Shum bola", "G‘afur G‘ulom", 1936, 192, "uz", 42000,
     "Sho‘x va zukko bolaning sarguzashtlari — kulgi va hayot haqiqati aralash qissa."),
    ("ozbek-adabiyoti", "Ufq", "Said Ahmad", 1964, 640, "uz", 89000,
     "Uch kitobdan iborat trilogiya: urush yillari va qishloq odamlarining hayoti."),
    ("ozbek-adabiyoti", "Ikki eshik orasi", "O‘tkir Hoshimov", 1986, 560, "uz", 79000,
     "Bir necha avlod taqdiri turli qahramonlar tilidan hikoya qilinadigan roman."),
    ("ozbek-adabiyoti", "Dunyoning ishlari", "O‘tkir Hoshimov", 1982, 224, "uz", 49000,
     "Ona haqidagi samimiy hikoyalar to‘plami, avloddan avlodga o‘qiladigan kitob."),
    ("ozbek-adabiyoti", "Ulug‘bek xazinasi", "Odil Yoqubov", 1973, 400, "uz", 65000,
     "Mirzo Ulug‘bekning so‘nggi kunlari va uning ilmiy merosi taqdiri haqida."),
    ("ozbek-adabiyoti", "Yulduzli tunlar", "Pirimqul Qodirov", 1978, 528, "uz", 75000,
     "Zahiriddin Muhammad Boburning hayoti va kurashlari haqidagi tarixiy roman."),
    ("ozbek-adabiyoti", "Otamdan qolgan dalalar", "Tog‘ay Murod", 1994, 336, "uz", 62000,
     "Dehqon Dehqonqulning yer bilan bog‘liq umri va o‘ziga xos tilda yozilgan roman."),
    ("ozbek-adabiyoti", "Xamsa (saylanma)", "Alisher Navoiy", 1485, 480, "uz", 99000,
     "Besh dostondan saylanma: Farhod va Shirin, Layli va Majnun va boshqalar."),
    ("ozbek-adabiyoti", "Boburnoma", "Zahiriddin Muhammad Bobur", 1530, 448, "uz", 85000,
     "Shoh va shoirning o‘z hayoti, yurishlari va ko‘rgan yurtlari haqidagi xotiralari."),

    ("jahon-adabiyoti", "Jinoyat va jazo", "Fyodor Dostoyevskiy", 1866, 608, "uz", 79000,
     "Raskolnikovning g‘oyasi, jinoyati va vijdon azobi haqidagi buyuk roman."),
    ("jahon-adabiyoti", "Usta va Margarita", "Mixail Bulgakov", 1967, 480, "ru", 89000,
     "Moskvaga kelgan Voland va sevgisi uchun hamma narsadan kechgan Margarita."),
    ("jahon-adabiyoti", "Yuz yillik yolg‘izlik", "Gabriel Garsia Markes", 1967, 432, "uz", 85000,
     "Buendia oilasining yetti avlodi va Makondo shahrining sehrli tarixi."),
    ("jahon-adabiyoti", "Chol va dengiz", "Ernest Xeminguey", 1952, 128, "uz", 39000,
     "Keksa baliqchi Santyago va ulkan baliq o‘rtasidagi sabr sinovi."),
    ("jahon-adabiyoti", "Alkimyogar", "Paulo Koelo", 1988, 208, "uz", 49000,
     "Cho‘pon Santyagoning orzusi ortidan qilgan sayohati haqidagi masal-roman."),
    ("jahon-adabiyoti", "Kichkina shahzoda", "Antuan de Sent-Ekzyuperi", 1943, 112, "uz", 35000,
     "Kattalar uchun yozilgan bolalar kitobi: do‘stlik, mas’uliyat va sevgi haqida."),
    ("jahon-adabiyoti", "1984", "Jorj Oruell", 1949, 352, "uz", 59000,
     "Katta Og‘a kuzatib turgan jamiyat va haqiqat uchun kurash haqidagi distopiya."),
    ("jahon-adabiyoti", "Hayvonlar xo‘jaligi", "Jorj Oruell", 1945, 144, "uz", 39000,
     "Hokimiyat qanday buzilishi haqidagi o‘tkir siyosiy masal."),
    ("jahon-adabiyoti", "Buyuk Getsbi", "Frensis Skott Fitsjerald", 1925, 224, "en", 55000,
     "Jaz asri Amerikasi, boylik va yetib bo‘lmas orzu haqida roman."),
    ("jahon-adabiyoti", "Martin Iden", "Jek London", 1909, 448, "uz", 65000,
     "Oddiy dengizchidan yozuvchiga aylangan yigitning g‘alaba va iztiroblari."),
    ("jahon-adabiyoti", "Uch og‘ayni", "Erix Mariya Remark", 1936, 480, "ru", 69000,
     "Urushdan keyingi Germaniyada do‘stlik va sevgi haqidagi roman."),
    ("jahon-adabiyoti", "Oq kema", "Chingiz Aytmatov", 1970, 176, "uz", 45000,
     "Bolaning ertaklarga ishonchi va kattalar dunyosining shafqatsizligi."),
    ("jahon-adabiyoti", "Asrga tatigulik kun", "Chingiz Aytmatov", 1980, 416, "uz", 69000,
     "Manqurt afsonasi va xotirani yo‘qotish xavfi haqidagi falsafiy roman."),
    ("jahon-adabiyoti", "Bashorat", "Nodar Dumbadze", 1971, 256, "uz", 52000,
     "Gruziya qishlog‘idagi bolalik, kulgi va mehr haqida iliq qissa."),
    ("jahon-adabiyoti", "Mag‘rurlik va g‘urur", "Jeyn Ostin", 1813, 400, "en", 59000,
     "Elizabet Bennet va janob Darsi — ingliz adabiyotining eng mashhur juftligi."),

    ("biznes", "Boy ota, kambag‘al ota", "Robert Kiyosaki", 1997, 336, "uz", 69000,
     "Pul haqida maktabda o‘rgatilmaydigan saboqlar: aktiv va passivlar farqi."),
    ("biznes", "Noldan birgacha", "Piter Til", 2014, 224, "uz", 65000,
     "Yangi narsa yaratish va monopoliya qurish haqida startap asoschisi fikrlari."),
    ("biznes", "Bobilning eng boy odami", "Jorj Kleyson", 1926, 160, "uz", 42000,
     "Qadimiy Bobil hikoyalari orqali jamg‘arish va sarmoya qoidalari."),
    ("biznes", "Fikrla va boy bo‘l", "Napoleon Xill", 1937, 320, "uz", 55000,
     "Muvaffaqiyatli odamlar tajribasidan chiqarilgan o‘n uch tamoyil."),
    ("biznes", "Yaxshidan buyukka", "Jim Kollinz", 2001, 400, "uz", 79000,
     "Oddiy kompaniyalarni buyuk qilgan qarorlar bo‘yicha tadqiqot."),
    ("biznes", "Tejamkor startap", "Erik Ris", 2011, 320, "uz", 72000,
     "Tez sinov, o‘lchash va o‘rganish orqali mahsulot yaratish usuli."),
    ("biznes", "Pul psixologiyasi", "Morgan Xauzel", 2020, 256, "uz", 69000,
     "Boylik formulalardan ko‘ra xulq-atvorga bog‘liq ekani haqida 19 hikoya."),
    ("biznes", "Shoe Dog", "Fil Nayt", 2016, 400, "en", 89000,
     "Nike asoschisining kompaniyani noldan qurgani haqidagi xotiralari."),
    ("biznes", "Muzokara san’ati", "Kris Voss", 2016, 288, "uz", 74000,
     "Sobiq FBI muzokarachisining kundalik suhbatlarda ishlatsa bo‘ladigan usullari."),

    ("psixologiya", "Atom odatlar", "Jeyms Klir", 2018, 320, "uz", 79000,
     "Kichik o‘zgarishlar qanday qilib katta natijaga olib kelishi haqida amaliy qo‘llanma."),
    ("psixologiya", "Sekin va tez fikrlash", "Daniel Kaneman", 2011, 512, "uz", 95000,
     "Ikki fikrlash tizimi va qaror qabul qilishdagi xatolarimiz."),
    ("psixologiya", "Inson ma’no izlab", "Viktor Frankl", 1946, 192, "uz", 49000,
     "Kontslager tajribasidan tug‘ilgan hayot ma’nosi haqidagi kitob."),
    ("psixologiya", "Emotsional intellekt", "Deniel Goulman", 1995, 384, "uz", 72000,
     "Hissiyotlarni boshqarish ish va munosabatlarda nega muhimligi."),
    ("psixologiya", "Samarali insonlarning 7 ko‘nikmasi", "Stiven Kovi", 1989, 432, "uz", 79000,
     "Shaxsiy va kasbiy samaradorlik uchun tamoyillarga asoslangan yondashuv."),
    ("psixologiya", "Qanday qilib do‘st orttirish mumkin", "Deyl Karnegi", 1936, 288, "uz", 52000,
     "Odamlar bilan muloqot va ishonch qozonishning vaqt sinovidan o‘tgan qoidalari."),
    ("psixologiya", "Diqqat", "Kal Nyuport", 2016, 304, "uz", 69000,
     "Chuqur ish — chalg‘ituvchilar ko‘p zamonda jamlanib ishlash mahorati."),
    ("psixologiya", "Hech narsaga parvo qilmaslikning nozik san’ati", "Mark Menson", 2016, 224, "uz", 59000,
     "Nimaga e’tibor berish kerakligini tanlash haqida ochiq va samimiy kitob."),

    ("bolalar", "O‘zbek xalq ertaklari", "Xalq og‘zaki ijodi", 2015, 256, "uz", 55000,
     "Zumrad va Qimmat, Ur to‘qmoq va boshqa sevimli ertaklar rasmlar bilan."),
    ("bolalar", "Sehrli qalpoqcha", "Xudoyberdi To‘xtaboyev", 1965, 224, "uz", 45000,
     "Hoshimjonning sehrli qalpoqcha bilan boshidan kechirgan sarguzashtlari."),
    ("bolalar", "Garri Potter va falsafiy tosh", "J. K. Rouling", 1997, 336, "uz", 89000,
     "O‘n bir yoshli sehrgar bolaning Xogvarts maktabidagi birinchi yili."),
    ("bolalar", "Alisa mo‘jizalar mamlakatida", "Lyuis Kerroll", 1865, 176, "uz", 49000,
     "Quyon ortidan inga tushgan qizchaning g‘aroyib sayohati."),
    ("bolalar", "Pippi Uzunpaypoq", "Astrid Lindgren", 1945, 192, "uz", 47000,
     "Dunyodagi eng kuchli va eng quvnoq qizcha haqidagi hikoyalar."),
    ("bolalar", "Buratinoning sarguzashtlari", "Aleksey Tolstoy", 1936, 160, "uz", 42000,
     "Yog‘och qo‘g‘irchoqning oltin kalit izlab qilgan sarguzashtlari."),
    ("bolalar", "Mitti yulduz", "Xudoyberdi To‘xtaboyev", 1980, 144, "uz", 39000,
     "Kichkintoylar uchun mehr va do‘stlik haqidagi qissalar."),

    ("fan", "Vaqtning qisqacha tarixi", "Stiven Xoking", 1988, 256, "uz", 69000,
     "Katta portlashdan qora tuynuklargacha — koinot haqida sodda tilda."),
    ("fan", "Kosmos", "Karl Sagan", 1980, 432, "uz", 85000,
     "Inson va koinot o‘rtasidagi bog‘liqlik haqidagi ilmiy-ommabop klassika."),
    ("fan", "Xudbin gen", "Richard Dokins", 1976, 400, "uz", 79000,
     "Evolyutsiyaga gen nuqtayi nazaridan qarash."),
    ("fan", "Toza kod", "Robert Martin", 2008, 464, "en", 149000,
     "O‘qilishi va qo‘llab-quvvatlanishi oson dastur yozish tamoyillari."),
    ("fan", "Python bilan dasturlash", "Erik Mattes", 2019, 544, "uz", 129000,
     "Noldan boshlab loyihalar orqali Python tilini o‘rganish."),
    ("fan", "Algoritmlarni tushunish", "Aditya Bxargava", 2016, 256, "uz", 99000,
     "Rasmlar yordamida algoritmlarni oson tushuntiruvchi qo‘llanma."),
    ("fan", "Gen: shaxsiy tarix", "Siddxarta Mukerji", 2016, 592, "uz", 109000,
     "Irsiyat fanining paydo bo‘lishi va kelajagi haqida."),

    ("tarix", "Sapiens: Insoniyatning qisqacha tarixi", "Yuval Noy Harariy", 2011, 512, "uz", 99000,
     "Ovchi-teruvchilardan bugungi kungacha — insoniyat qanday hukmron bo‘ldi."),
    ("tarix", "Temur tuzuklari", "Amir Temur", 1380, 224, "uz", 59000,
     "Davlat boshqaruvi va harbiy ish haqidagi mashhur yo‘riqnoma."),
    ("tarix", "Qurollar, mikroblar va po‘lat", "Jared Daymond", 1997, 528, "uz", 95000,
     "Nega ba’zi xalqlar boshqalardan oldinga ketgani haqidagi tadqiqot."),
    ("tarix", "Ipak yo‘li: dunyoning yangi tarixi", "Piter Frankopan", 2015, 640, "uz", 115000,
     "Tarixni Markaziy Osiyo va Sharq nigohidan qayta o‘qish."),
    ("tarix", "Buyuk ipak yo‘li shaharlari", "Mualliflar jamoasi", 2020, 288, "uz", 89000,
     "Samarqand, Buxoro va Xiva tarixi, me’moriy yodgorliklari bilan."),
    ("tarix", "Mustaqillik yo‘lida", "Mualliflar jamoasi", 2021, 320, "uz", 65000,
     "XX asr O‘zbekiston tarixidagi asosiy voqealar va shaxslar."),

    ("fantastika", "Dyuna", "Frenk Gerbert", 1965, 704, "uz", 119000,
     "Qum sayyorasi Arrakis, ziravor va Pol Atreydesning taqdiri."),
    ("fantastika", "Uzuklar hukmdori: Uzuk birodarligi", "J. R. R. Tolkin", 1954, 576, "uz", 109000,
     "Frodo va hamrohlarining Hukmdorlik uzugini yo‘q qilish safari boshlanadi."),
    ("fantastika", "Xobbit", "J. R. R. Tolkin", 1937, 320, "uz", 79000,
     "Bilbo Torbinsning mitti-gnomlar bilan ajdar xazinasi sari sayohati."),
    ("fantastika", "Asos", "Ayzek Azimov", 1951, 288, "uz", 72000,
     "Galaktika imperiyasi qulashi va ming yillik zulmatni qisqartirish rejasi."),
    ("fantastika", "Farengeyt bo‘yicha 451 daraja", "Rey Bredberi", 1953, 224, "uz", 55000,
     "Kitoblar yoqiladigan jamiyatda o‘t o‘chiruvchining uyg‘onishi."),
    ("fantastika", "Uch tana muammosi", "Lyu Sisin", 2008, 416, "uz", 89000,
     "Insoniyatning boshqa sivilizatsiya bilan birinchi aloqasi haqida."),
    ("fantastika", "Marslik", "Endi Vir", 2011, 384, "uz", 75000,
     "Marsda yolg‘iz qolgan astronavtning aql va hazil bilan omon qolishi."),
]


class Command(BaseCommand):
    help = "Do‘konni namunaviy kategoriyalar va kitoblar bilan to‘ldiradi"

    def add_arguments(self, parser):
        parser.add_argument("--reset", action="store_true", help="Avval eski kitoblarni o‘chirish")

    @transaction.atomic
    def handle(self, *args, **opts):
        rng = random.Random(42)  # har safar bir xil natija
        if opts["reset"]:
            Book.objects.all().delete()
            Category.objects.all().delete()

        cats = {}
        for i, (name, slug, desc) in enumerate(CATEGORIES):
            cats[slug], _ = Category.objects.update_or_create(
                slug=slug, defaults={"name": name, "description": desc, "order": i}
            )

        created = 0
        for i, (cat, title, author, year, pages, lang, price, desc) in enumerate(BOOKS):
            base, accent = PALETTES[(i * 7 + i // len(PALETTES)) % len(PALETTES)]
            slug = slugify(f"{title}-{author}".replace("‘", "").replace("’", ""), allow_unicode=False)
            old_price = round(price * rng.choice([1.15, 1.2, 1.25]), -3) if i % 5 == 0 else None
            _, was_created = Book.objects.update_or_create(
                slug=slug,
                defaults=dict(
                    title=title, author=author, category=cats[cat], description=desc,
                    price=price, old_price=old_price, pages=pages, year=year, language=lang,
                    cover_type="hard" if pages > 400 else "soft",
                    cover_color=base, accent_color=accent,
                    stock=rng.choice([0, 3, 8, 12, 20, 35]) if i % 11 == 7 else rng.choice([5, 12, 20, 35]),
                    rating=rng.choice([4.2, 4.4, 4.5, 4.6, 4.7, 4.8, 4.9]),
                    is_featured=i % 6 == 0,
                ),
            )
            created += was_created

        if opts["verbosity"]:
            self.stdout.write(self.style.SUCCESS(
                f"{len(CATEGORIES)} ta kategoriya, {len(BOOKS)} ta kitob tayyor ({created} tasi yangi)."
            ))
