"""Nombres propios frecuentes en Nicaragua, usados para que el sexo sea coherente con el nombre.

Solo se incluyen nombres claramente masculinos o femeninos. Los nombres mixtos o ambiguos
(Guadalupe, Ariel, Alexis, Cruz, Jesús/Jesus, Concepción, etc.) se omiten a propósito para no
rechazar registros legítimos. Los nombres que no están en las listas no se rechazan.
"""
import unicodedata


def normalizar(texto: str) -> str:
    """Minúsculas y sin tildes, para comparar nombres."""
    t = unicodedata.normalize("NFD", texto.strip().lower())
    return "".join(c for c in t if unicodedata.category(c) != "Mn" or c == "\u0303").replace("n\u0303", "ñ")


_MASCULINOS = """
jose juan luis carlos jorge miguel manuel pedro pablo francisco antonio mario fernando ricardo roberto
alejandro daniel david javier sergio eduardo oscar victor hector raul rafael ramon julio cesar marvin
byron bayardo denis dennis erick erik freddy fredy guillermo gustavo henry hugo ivan jairo jaime jeffrey
jefferson jhonny johnny jonathan josue julian kevin lenin leonel lester lorenzo marcos mauricio max
melvin nelson nestor noel norman omar orlando osvaldo oswaldo patricio rene reynaldo rodolfo rodrigo
rolando ronald ruben salvador samuel santiago saul sebastian tomas ulises uriel vicente walter wilfredo
william wilmer yader yaser yasser alfredo alberto armando arturo augusto benjamin bernardo bismarck
camilo cristian cristobal damian dario diego domingo edgar edgard edwin elias emilio enrique ernesto
esteban eugenio fabian felipe felix fidel gabriel geovanny giovanni gerardo german gilberto gonzalo
gregorio horacio humberto ignacio isaac isaias israel ismael jacinto joaquin joel jonas leonardo lucas
marlon martin mateo matias maximo moises nicolas noe pascual ramiro reinaldo renato ricky rigoberto
rosendo rufino santos sandino silvio teodoro timoteo tito valentin wendell wilber wilson xavier yamil
adolfo adrian agustin alan alvaro anibal aurelio baltazar boanerges bryan brayan brandon carlos
cleto dagoberto danilo darwin deyvis donald douglas efrain elmer elvis emmanuel engel erasmo ezequiel
fausto fermin florentino frank franklin froilan genaro geraldo hernan hilario ivo jeremias joshua jhon
john kenneth kenny kleber lazaro lenyn leopoldo lisandro lucio luciano mardoqueo maycol michael
milton misael nahum napoleon nehemias nixon octavio olivier onelio orlin pastor porfirio quirino ramses
reyes robin rony sabino samir segundo selvin sixto stanley stiven steven tobias trinidad ubaldo urbano
valdemar vladimir wilmar yohan yonatan yoshua zacarias
""".split()

_FEMENINOS = """
maria ana carmen rosa luisa laura sofia isabel patricia gloria marta martha cecilia claudia lucia
elena teresa dolores juana josefa francisca margarita yolanda sandra silvia vanessa veronica
alejandra alicia amanda amparo andrea angela angelica antonia aracely araceli beatriz belkis blanca
brenda camila carolina catalina clara cristina daniela diana digna dina doris elba eliza
elizabeth elsa emilia erika eva fabiola fatima flor flora gabriela genesis graciela haydee
hilda ines irene iris irma isamar ivette jazmin jennifer jessica johana johanna julia juliana karen
karina katherine katia kenia keyla leticia liliana lidia lilian liliam linda lorena lourdes lupita
magaly marcela mariana maribel marisol marlene marlen mayra melissa mercedes mireya miriam mirna
monica nadia nancy natalia nelly nidia noemi nora norma olga paola paulina priscila raquel rebeca
regina reyna rita rocio rosario rosaura roxana ruth sara sarahi saray selena silvana sonia stephanie
susana tania tatiana valeria valentina vilma violeta virginia vivian wendy ximena xiomara yadira
yahaira yamileth yasmina yessenia yesenia yolanda zoila zulema abigail adela adriana agustina aida
alba alma amelia anabel anastasia argentina aura aurora azucena barbara bertha bianca candida
carla celia celeste chantal clarisa cleotilde consuelo corina cynthia dayana dayra delia denia
dominga edith elida eloisa elvira emelina esmeralda esperanza estela esther eugenia evelyn fanny
felicia fidelina gisela giselle gladys herminia ilse indira ingrid irina jacqueline jaqueline jeannette
jenny jimena johanny joselyn josselyn judith karla kimberly laila lesbia leyla lilibeth lisbeth
lissette lizeth madeline magdalena maite marbella marisela maritza marjorie matilde maura maylin
mirian mariela nathalia nicole noelia ondina otilia pamela petrona pilar rafaela reina ricarda
rosalia rosalinda rosibel rubi samantha sabrina scarlet scarleth selene shirley sheila sheyla soledad
tamara thelma toribia ursula vanesa victoria wilma yaritza yelitza yara yohana yuliana zaida
""".split()

# Nombres que pueden ser de ambos sexos: nunca se rechazan.
_AMBIGUOS = {"guadalupe", "trinidad", "ariel", "alexis", "jesus", "cruz", "concepcion", "dominique",
             "yael", "leslie", "kelly", "jordan", "cris", "alex", "sacramento", "natividad", "refugio",
             "merced", "paz", "rene", "noel", "angel"}

MASCULINOS = frozenset(normalizar(n) for n in _MASCULINOS) - _AMBIGUOS
FEMENINOS = frozenset(normalizar(n) for n in _FEMENINOS) - _AMBIGUOS

# Un nombre en ambas listas es ambiguo.
_AMBOS = MASCULINOS & FEMENINOS
MASCULINOS = MASCULINOS - _AMBOS
FEMENINOS = FEMENINOS - _AMBOS
