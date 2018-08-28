# -*- coding: utf-8 -*-

import SDL_DS3231 as sdl

REG_ALARM1_S=7
REG_ALARM1_M=8
REG_ALARM1_H=9
REG_ALARM1_D=10
REG_ALARM2_M=11
REG_ALARM2_H=12
REG_ALARM2_D=13
REG_CONTROL=14
REG_STATUS=15

def byte_to_bits(b):
	"""Wandelt Byte (Int 0-255) in ein Array mit 8 True/False-Werten um. Achtung, das niederwertige Bit ist links
	"""
	bits = [False,False,False,False,False,False,False,False]
	i=7
	while b>0:
		while b>=2**i:
			bits[i]=True
			b=b-2**i
			break
		else:
			i=i-1
	return bits

def bits_to_byte(bits):
	"""Wandelt Bits-Array in Integer um
	"""
	byte=0
	for i in range(8):
		if bits[i]:
			byte=byte+2**i
	return byte

def test_bit(rtc, register, bit):
	"""Gibt True zurueck wenn Bit <bit> des Registers <register> des RTC-Objekts <rtc> gesetzt ist
	"""
	bits = byte_to_bits(rtc._read(register))
	return bits[bit]

def set_bit(rtc, register, bit):
	"""Setzt das Bit <bit> eines Registers <register> des RTC-Objekts <rtc>
	"""
	bits = byte_to_bits(rtc._read(register))
	if not bits[bit]:
		bits[bit]=True
		rtc._write(register, bits_to_byte(bits))

def reset_bit(rtc, register, bit):
	"""Setzt das Bit <bit> eines Registers <register> des RTC-Objekts <rtc> zurück
	"""
	bits = byte_to_bits(rtc._read(register))
	if bits[bit]:
		bits[bit]=False
		rtc._write(register, bits_to_byte(bits))

def enable_alarm1(rtc):
	"""Aktiviert den Alarm 1 des RTC-Objekts <rtc> indem Control-Bit A1IE gesetzt wird
	"""
	set_bit(rtc,REG_CONTROL,0)
	
def enable_alarm2(rtc):
	"""Aktiviert den Alarm 2 des RTC-Objekts <rtc> indem Control-Bit A2IE gesetzt wird
	"""
	set_bit(rtc,REG_CONTROL,1)
	
def disable_alarm1(rtc):
	"""Deaktiviert den Alarm 1 des RTC-Objekts <rtc>
	"""
	reset_bit(rtc,REG_CONTROL,0)
	
def disable_alarm2(rtc):
	"""Deaktiviert den Alarm 2 des RTC-Objekts <rtc>
	"""
	reset_bit(rtc,REG_CONTROL,1)	

def reset_alarm1_indicator(rtc):
	"""Setzt das Alarm-Indikations-Bit A1F zurück
	"""
	reset_bit(rtc,REG_STATUS,0)	
	
def reset_alarm2_indicator(rtc):
	"""Setzt das Alarm-Indikations-Bit A1F zurück
	"""
	reset_bit(rtc,REG_STATUS,1)	

def set_alarm1_datetime(rtc, dt):
	"""Setzt den Alarm 1 mit Hilfe eines Datetime-Objekts
	"""
	set_alarm1_time(rtc, dt.day, dt.hour, dt.minute, dt.second)
	
def set_alarm1_time(rtc,d,h,m,s):
	"""Setzt den Alarm 1 des RTC-Objekts <rtc> mit den Werten Tag <d>, Stunde <h>, Minute <m> und Sekunde <s>
	"""
	#  Die Parameter werden im BCD-Format erwartet (z.B.Minute 54 = 5 im oberem halben Byte und 4 im unteren halben
	#  Byte = 0101 0100). Deshalb Umrechnng in Integer notwendig. Außerdem muss geprüft werden, ob Bit 7 gesetzt ist 
	#  (siehe Alarmmodus) und dieses ggf. erhalten bleiben
	if test_bit(rtc, REG_ALARM1_D, 7):
		rtc._write(REG_ALARM1_D, sdl.int_to_bcd(d)+128)
	else:
		rtc._write(REG_ALARM1_D, sdl.int_to_bcd(d))
	if test_bit(rtc, REG_ALARM1_H, 7):
		rtc._write(REG_ALARM1_H, sdl.int_to_bcd(h)+128)
	else:
		rtc._write(REG_ALARM1_H, sdl.int_to_bcd(h))
	if test_bit(rtc, REG_ALARM1_M, 7):
		rtc._write(REG_ALARM1_M, sdl.int_to_bcd(m)+128)
	else:
		rtc._write(REG_ALARM1_M, sdl.int_to_bcd(m))
	if test_bit(rtc, REG_ALARM1_S, 7):
		rtc._write(REG_ALARM1_S, sdl.int_to_bcd(s)+128)
	else:
		rtc._write(REG_ALARM1_S, sdl.int_to_bcd(s))
	
def set_alarm2_time(rtc,d,h,m):
	"""Setzt den Alarm 2 des RTC-Objekts <rtc> mit den Werten Tag <d>, Stunde <h>, Minute <m> 
	"""
	#  Die Parameter werden im BCD-Format erwartet (z.B.Minute 54 = 5 im oberem halben Byte und 4 im unteren halben
	#  Byte = 0101 0100). Deshalb Umrechnng in Integer notwendig. Außerdem muss geprüft werden, ob Bit 7 gesetzt ist 
	#  (siehe Alarmmodus) und dieses ggf. erhalten bleiben
	if test_bit(rtc, REG_ALARM2_D, 7):
		rtc._write(REG_ALARM2_D, sdl.int_to_bcd(d)+128)
	else:
		rtc._write(REG_ALARM2_D, sdl.int_to_bcd(d))
	if test_bit(rtc, REG_ALARM2_H, 7):
		rtc._write(REG_ALARM2_H, sdl.int_to_bcd(h)+128)
	else:
		rtc._write(REG_ALARM2_H, sdl.int_to_bcd(h))
	if test_bit(rtc, REG_ALARM2_M, 7):
		rtc._write(REG_ALARM2_M, sdl.int_to_bcd(m)+128)
	else:
		rtc._write(REG_ALARM2_M, sdl.int_to_bcd(m))

	
def set_alarm1_rate_each_minute(rtc):
	"""Setzt die Frequenz des Alarm 1 des RTC-Objekts <rtc> auf minütlich
	"""
	reset_bit(rtc,REG_ALARM1_S,7)
	set_bit(rtc,REG_ALARM1_M,7)
	set_bit(rtc,REG_ALARM1_H,7)
	set_bit(rtc,REG_ALARM1_D,7)
	
def set_alarm1_rate_each_hour(rtc):
	"""Setzt die Frequenz des Alarm 1 des RTC-Objekts <rtc> auf stündlich
	"""
	reset_bit(rtc,REG_ALARM1_S,7)
	reset_bit(rtc,REG_ALARM1_M,7)
	set_bit(rtc,REG_ALARM1_H,7)
	set_bit(rtc,REG_ALARM1_D,7)
	
def set_alarm1_rate_each_day(rtc):
	"""Setzt die Frequenz des Alarm 1 des RTC-Objekts <rtc> auf täglich
	"""
	reset_bit(rtc,REG_ALARM1_S,7)
	reset_bit(rtc,REG_ALARM1_M,7)
	reset_bit(rtc,REG_ALARM1_H,7)
	set_bit(rtc,REG_ALARM1_D,7)
	
def set_alarm2_rate_each_minute(rtc):
	"""Setzt die Frequenz des Alarm 2 des RTC-Objekts <rtc> auf minütlich
	"""
	set_bit(rtc,REG_ALARM2_M,7)
	set_bit(rtc,REG_ALARM2_H,7)
	set_bit(rtc,REG_ALARM2_D,7)
	
def set_alarm2_rate_each_hour(rtc):
	"""Setzt die Frequenz des Alarm 2 des RTC-Objekts <rtc> auf stündlich
	"""
	reset_bit(rtc,REG_ALARM2_M,7)
	set_bit(rtc,REG_ALARM2_H,7)
	set_bit(rtc,REG_ALARM2_D,7)
	
def set_alarm2_rate_each_day(rtc):
	"""Setzt die Frequenz des Alarm 3 des RTC-Objekts <rtc> auf täglich
	"""
	reset_bit(rtc,REG_ALARM2_M,7)
	reset_bit(rtc,REG_ALARM2_H,7)
	set_bit(rtc,REG_ALARM2_D,7)
	

def get_alarm1_rate(rtc):
	bits = (test_bit(rtc,REG_ALARM1_S,7), test_bit(rtc,REG_ALARM1_M,7),
			test_bit(rtc,REG_ALARM1_H,7), test_bit(rtc,REG_ALARM1_D,7))
	if bits==(False,True,True,True):
		return("each minute")
	elif bits==(False,False,True,True):
		return("each hour")
	elif bits==(False,False,False,True):
		return("each day")
	else:
		return("?")

def get_alarm2_rate(rtc):
	bits = (test_bit(rtc,REG_ALARM2_M,7), test_bit(rtc,REG_ALARM2_H,7), test_bit(rtc,REG_ALARM2_D,7))
	if bits==(True,True,True):
		return("each minute")
	elif bits==(False,True,True):
		return("each hour")
	elif bits==(False,False,True):
		return("each day")
	else:
		return("?")
