from random import randint


class RandomMessage:
    def __init__(self, author):
        self.frasesRandom = \
            {
                'frase1': '"me deixa top, to smurfando relaxa add na main lá"',
                'frase2': 'Vai um drink? :sunglasses:',
                'frase3': 'Misturar, misturar, girar, mexer',
                'frase4': 'Mexer, ou não mexer?',
                'frase5': 'Estou a caminho!',
                'frase6': 'Eu te ouço!',
                'frase7': 'Não misturado :(',
                'frase8': 'Batido!',
                'frase9': 'Já era hora!',
                'frase10': 'Está do seu agrado?',
                'frase11': 'Desculpa {0}, estou ocupado fazendo proxy :pray:'.format(author.mention),
                'frase12': 'Chamou? :flushed:',
                'frase13': 'Só tem elo porque é meta abuser 😒'
            }
        self.maxOption = len(self.frasesRandom)

    def randomoption(self):
        randomoption = "frase" + str(randint(1, self.maxOption))

        return self.frasesRandom[randomoption]


class Texts:
    def __init__(self, activity_type, activity_input):
        self.activity_type = str(activity_type)
        self.activity_input = tuple(activity_input)
        doing_auxiliar = self.activity_type[13:].lower()
        print(doing_auxiliar)

        if doing_auxiliar == "playing":
            self.doing = "jogando"

        elif doing_auxiliar == "listening":
            self.doing = "ouvindo"

        elif doing_auxiliar == "streaming":
            self.doing = "streamando"

        elif doing_auxiliar == "watching":
            self.doing = "assistindo"



        if self.doing != "streamando":
            self.title = ' '.join(self.activity_input)

        else:
            self.title = ' '.join(self.activity_input[:-1])
            self.url = ''.join(self.activity_input[-1])
            self.url_formatada = self.url.replace("http://", '').replace("https://", '')

    def set_text(self):
        if self.doing != "streamando":
            # If activity_type is "playing", "listening" or "watching"
            return f'''Agora estou ***{self.doing}*** ``{self.title}``'''


        # If activity_type is "streaming"
        else:
            self.title = ' '.join(self.activity_input[:-1])
            print("url(frases): " + self.url)

            # Final text
            # -------- I'm now *** streaming *** ` stream title ` at ** stream url **
            return f'''Agora estou ***{self.doing}*** `{self.title}` em: **{self.url_formatada}**'''


    def get_title(self):
        print("title (frases): ", end='')
        print(self.title)
        return self.title

    def get_url(self):
        print("url (frases): ", end='')
        print(self.url)
        return self.url
