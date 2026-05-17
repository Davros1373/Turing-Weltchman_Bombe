import lcddriver
from time import *
 
lcd = lcddriver.lcd()
lcd.lcd_clear()
 
lcd.lcd_display_string("", 1)
lcd.lcd_display_string("   ABCDEFGHIJKLMN", 2)
lcd.lcd_display_string("", 3)
lcd.lcd_display_string("    OPQRSTUVWXYZ", 4)
