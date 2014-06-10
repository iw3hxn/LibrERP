##############################################################################
# TRACCIATO FILE LISTINO METEL (ver 020)
#
# pos	descrizione campo				column	tipo e lunghezza del campo
# 1		Sigla Marchio					1		M	An 03
# 2		Codice Prodotto Produttore		4		M	An 16
# 3		Codice EAN						20		O	N 13
# 4		Descrizione prodotto			33		M	An 43
# 5		Quantita cartone				76		M	N 05
# 6		Quantita multipla ordinazione	81		M	N 05
# 7		Quantita minima ordinazione		86		M	N 05
# 8		Quantita massima ordinazione	91		M	N 06
# 9		Lead Time						97		M	An 1
# 10	Prezzo al grossista				98		M	N 11.2
# 11	Prezzo al Pubblico				109		M	N 11.2
# 12	Moltiplicatore prezzo			120		M	N 06
# 13	Codice Valuta					126		M	A 03
# 14	Unita di misura					129		M	An 03
# 15	Prodotto Composto				132		M	N 01
# 16	Stato del prodotto				133		M	An 01
# 17	Data ultima variazione			134		M	Dt
# 18	Famiglia di sconto				142		O	An 18
# 19	Famiglia statistica				160		O	An 18
# Lunghezza Record  177 bytes  seguito da un fine riga (CR+LF = Carriage Return e Line feed)
# 
##############################################################################

import datetime

f = open(r'Beclsp09.txt')

line = f.readline()
metel = line[0:20].strip()
prod = line[20:23]
desc = line[56:125].strip()
date_start = datetime.date(int(line[40:44]), int(line[44:46]), int(line[46:48]))
last_change = datetime.date(int(line[48:52]), int(line[52:54]), int(line[54:56]))

print prod, "\t", desc, "\t", date_start, " last changed ", last_change

for line in f:
	prod = line[0:3]
	code = line[3:19].strip()
	desc = line[32:75].strip()
	qmin = int(line[85:90].strip())
	leadtime = line[96:97]
	price1 = float(line[97:108].strip()) / 100
	price2 = float(line[108:119].strip()) / 100
	price_multi = float(line[119:125].strip());
	price1 /= price_multi
	price2 /= price_multi

	family_discount = line[141:159].strip()
	family_stat = line[159:177].strip()
	print prod, " ", code, "\t", qmin, "\t", leadtime, "\t", price_multi, "\t", family_discount, "\t", family_stat, "\t", price1, "\t", price2, "\t", desc
	

f.close()