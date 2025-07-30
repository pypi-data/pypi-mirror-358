#!/usr/bin/env python3
import sys
from datetime import datetime
from nepali_datetime import date as nepali_date

def get_nepali_day_name(day_number):
    nepali_days = {
    0: "आइतबार",
    1: "सोमबार",
    2: "मंगलबार",
    3: "बुधबार",
    4: "बिहिबार",
    5: "शुक्रबार",
    6: "शनिबार"
    }
    return nepali_days.get(day_number, "")

def get_nepali_month_name(month_number):
    nepali_months = {
        1: "बैशाख",
        2: "जेठ",
        3: "असार",
        4: "श्रावण",
        5: "भदौ",
        6: "असोज",
        7: "कार्तिक",
        8: "मंसिर",
        9: "पुष",
        10: "माघ",
        11: "फाल्गुन",
        12: "चैत"
    }
    return nepali_months.get(month_number, "")

def get_english_month_name(month_number):
    english_months = {
        1: "January",
        2: "February",
        3: "March",
        4: "April",
        5: "May",
        6: "June",
        7: "July",
        8: "August",
        9: "September",
        10: "October",
        11: "November",
        12: "December"
    }
    return english_months.get(month_number, "")

def to_nepali_numerals(number):
    nepali_numerals = {
        '0': '०',
        '1': '१',
        '2': '२',
        '3': '३',
        '4': '४',
        '5': '५',
        '6': '६',
        '7': '७',
        '8': '८',
        '9': '९'
    }
    return ''.join(nepali_numerals.get(digit, digit) for digit in str(number))

def print_boxed_dates(nepali_day, nepali_date_str, nepali_month_name, nepali_day_num, english_day, english_date_str, english_month_name, english_day_num):
    title = "Today's Date"
    width = 65

    print("┌" + "─" * width + "┐")
    print("│" + title.center(width) + "│")
    print("├" + "─" * width + "┤")

    nepali_date_full = f"{nepali_date_str} ({nepali_month_name} {nepali_day_num})"
    line1 = f"नेपाली मिति".ljust(25) + nepali_date_full.ljust(25) + nepali_day.rjust(10)
    print(f"   {line1}")

    english_date_full = f"{english_date_str} ({english_month_name} {english_day_num})"
    line2 = f"English Date".ljust(25) + english_date_full.ljust(25) + english_day.rjust(10)
    print(f"   {line2}")

    print("└" + "─" * width + "┘")

def deprecated_main():
    """Deprecated main function that shows a warning and calls the main function"""
    print("    Warning: 'nepdate' command is deprecated and will be removed in a future version.")
    print("   Please use 'miti' instead for the same functionality.")
    print()
    main()

def main():
    try:
        # Get current date
        current_date = datetime.now()
        
        # Convert to Nepali date
        nepali_current = nepali_date.from_datetime_date(current_date.date())
        
        # Get day names
        nepali_day = get_nepali_day_name(nepali_current.weekday())
        english_day = current_date.strftime("%A")
        
        # Get month names
        nepali_month_name = get_nepali_month_name(nepali_current.month)
        english_month_name = get_english_month_name(current_date.month)
        
        # Format Nepali date with Nepali numerals
        nepali_year = to_nepali_numerals(nepali_current.year)
        nepali_month = to_nepali_numerals(nepali_current.month)
        nepali_day_num = to_nepali_numerals(nepali_current.day)
        nepali_date_str = f"{nepali_year}-{nepali_month}-{nepali_day_num}"
        
        # Format English date
        english_date_str = current_date.strftime("%Y-%m-%d")
        english_day_num = current_date.day
        
        # Print in boxed format
        print_boxed_dates(nepali_day, nepali_date_str, nepali_month_name, nepali_day_num, english_day, english_date_str, english_month_name, english_day_num)
        
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main() 