import random
import time

from rich.console import Console

console = Console()

people = """
j.sered4
m_czikita
kaaczix
kinga.malekk
sugar_skull_
blood_infecti0ns
tapeta.szczepa
n__krol
ameljadonna
dragguss
fajnapusia1
hi_im_inga
xwrnao
nkvstka
bryksa_
madlitia
ryzu_g
m.galant_
mojeduzejaja3
ewciq.k
me_ry9012
zofka_s
pannkleks
santagatita
n_ludwiczakk
k0walewska
gadajdoreki
wwikuuu
inga16041
nikola_204
miarka
k0siur
applp.k3
_raczynska_aa
me3r1_
a_dziurko
natalkawhy
aala.png
victoriadabkowska
ostatkowna
duszek__lesny
bajoanka
melavvw
juliaviia
martsia.niedzielska
basiatko
marysiaszcz
mermaya_
zimnazupkachinska
jukea_
00jiwi
jablonskavv
winiary.pl
m_marthe_pv
jjulka66
mich4ll4k
sobiesiaczek
jpszczolak
e.banaszewska
kamilarywalska
w.wiatr0wka
julyyyiee
sandra_ksiezyc
asiaagabrys
just__nin4
_emily71_
nnoo_body_
kochamfrankocean
idziakada
swiezemaliny
Madziab.art
019em
bialasss__
mvrsxzy
femfataleas
chorypiesekdeluxe
agatawereszko
wiksevt
julia.jastak
eprajsnar
jowiisze
.kasiulajla.
didyousaychocolate_
rozalka_2010
jaciegaciealebezgaci
wikaa.buba
mvrsxzy
antecc_q
vicusiasiusia_123
ulqa_a
glowycareless__
6barely_human
karolinafoit_
nivvcolai
patiszonek
luv3rcat
pxti.sia
w1ku.
kedziorekjulia
kuskuskasza8
shrek_official_konto
dziedzic__kamila
aamelkavvv
martvna._
to.nieja1
twoja_pigula
jakupp.rz
amyma.l
fronczi_
.suzu..hipis._
malg.zielinska
maanamiaraa
kirkaaww
kreatyviai
stuck_inmy_mind
yosoytosia_
stxrvgirl
go_chaaaaa
manoretulis
julianowak123123
mazanaolga
l3n4.4
kinga.z_
przyczajony_ukrytysmok
rozaleczkapv_w333
noxcrucis
weronikaa_jaa
emakowskaa333
xo1oxxo
never_give_up_398
p0.pr0stu
oliviajania
w_wojtkowskaa
"""

people = people.strip().split("\n")

for i in range(10, -1, -1):
  time.sleep(1.0)
  console.print(f"{i}...\n", end="", style="green")

console.print(f"Biała mini: {random.choice(people)}!", style="red")
console.print(f"Połyskująca z fioletem : {random.choice(people)}!", style="blue")
