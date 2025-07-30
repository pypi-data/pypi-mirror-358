

class hotel:
    def __init__(self):
        self.mehmonlar = [{"ism": "akbarshox", "joy": "1", "turi": "lux"},
                          {"ism": "akobir", "joy": "2", "turi": "smart"},
                          {"ism": "arslan", "joy": '3', "turi": "smart"},
                          {"ism": "dilmurod", "joy": '4', "turi": "ekonom"},
                          {"ism": "abubakir", "joy": '5', "turi": "ekonom"},
                          {"ism": "asad", "joy": '16', "turi": "smart"},
                          {"ism": "bahodir", "joy": '24', "turi": "smart"},
                          {"ism": "nozliya", "joy": '8', "turi": "lux"},
                          {"ism": "abror", "joy": '9', "turi": "smart"},
                          {"ism": "akbar", "joy": '50', "turi": "lux"},
                          {"ism": "azim", "joy": '41', "turi": "lux"},
                          {"ism": "azamat", "joy": '12', "turi": "ekonom"},
                          {"ism": "ali", "joy": '13', "turi": "smart"},
                          {"ism": "alex", "joy": '34', "turi": "smart"},
                          {"ism": "robiya", "joy": '15', "turi": "lux"},
                          {"ism": "rasul", "joy": '36', "turi": "ekonom"},
                          {"ism": "anastasiya", "joy": '17', "turi": "ekonom"},
                          {"ism": "elbek", "joy": '18', "turi": "smart"},
                          {"ism": "javohir", "joy": '19', "turi": "lux"},
                          {"ism": "kamron", "joy": '20', "turi": "lux"},
                          {"ism": "begijon", "joy": '41', "turi": "lux"},
                          {"ism": "bek", "joy": '22', "turi": "ekonom"},
                          {"ism": "gulsanam", "joy": '23', "turi": "lux"},
                          {"ism": "ruhshona", "joy": '7', "turi": "exclusive"},
                          {"ism": "adam", "joy": '25', "turi": "smart"},
                          {"ism": "iqbol", "joy": '26', "turi": "ekonom"},
                          {"ism": "berdishukur", "joy": '27', "turi": "smart"},
                          {"ism": "mbappe", "joy": '28', "turi": "lux"}]

    def tulov(self, pul):
        if pul == "15000000":
            print('pulingiz qabul qilindi,marhamat')

        else:
            for _ in range(5):
                print('pulingiz yetmaydi, iltimos tulovni amalga oshiring')
            quit()


    def mehmon_qoshish(self, ism, joy, turi):
        for m in self.mehmonlar:
            if m["joy"] == joy:
                print(f"{joy} - xona band.")
                return
        self.mehmonlar.append({"ism": ism, "joy": joy, "turi": turi})
        print(f"{ism}, {joy} - xona, {turi} turiga qo‘shildi.")

    def mehmon_olib_tashlash(self, ism):
        for m in self.mehmonlar:
            if m["ism"].lower() == ism.lower():
                self.mehmonlar.remove(m)
                print(f"{ism} mehmonxonadan chiqdi.")
                return
        print(f"{ism} topilmadi.")

    def royxatni_korsatish(self):
        if not self.mehmonlar:
            print('mehmonhona bosh')
        else:
            print("Mehmonlar ro'yhati:")
            print("ismi".rjust(15), "joyi".rjust(15), "turi".rjust(15))
            print("-" * 60)
            for m in self.mehmonlar:
                print(m['ism'].rjust(15), m['joy'].rjust(15), m['turi'].rjust(19))

if __name__ == "__main__":
    Hotel = hotel()
    print("""       --Assalomu Alekum--
       Mehmonhonamizga hush kelibsiz
         Qanday yordam bera olaman!""")
    while True:

        print("o+ - Mehmon qo'shish")
        print("o- - Mehmon ro'yhatdan chiqarish")
        print("or - Mehmonlar ro'yhati")
        print("quit - Dastudan chiqish")
        buyruq1 = input("Buyruqni kiriting: ")


        if buyruq1 == "o+":
            Hotel.tulov(input('Iltimos avval tulovni amalga oshiring: '))
            tanlov = input('hona turini tanlang:  \ne - ekonom \ns - smart \nl - lux \nex - exclusive \n')
            turi = {
                "e": "ekonom",
                "s": "smart",
                "l": "lux",
                "ex": "exclusive"
            }.get(tanlov.lower(), "noaniq")

            if turi == "noaniq":
                print("Noto‘g‘ri xona turi!")
            else:
                Hotel.mehmon_qoshish(ism=input('ismingiz: '), joy=input('hona raqami: '), turi=turi)


        elif buyruq1 == "o-":
            Hotel.mehmon_olib_tashlash(input('kim ketmoqchi: '))

        elif buyruq1 == "or":
            Hotel.royxatni_korsatish()
        elif buyruq1 == "quit":
            print("Tugadi! Rahmat!")
            quit()
        else:
            print("Noto'g'ri iltimos qayta urinib kuring")

    # Hotel.tulov(input('tulovni amalga oshiring: '))
    # Hotel.mehmon_qoshish(ism=input('ismingiz: '), joy=input('hona raqami: '), turi=input('hona turini tanlang: '))
    # Hotel.royxatni_korsatish()
    # Hotel.mehmon_olib_tashlash(input('kim ketmoqchi: '))
