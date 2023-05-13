#!/usr/bin/env python3


"""
Basic date calendar
"""


import pandas as pd
import datetime as dt


def calendar_dates(start='01-01-2023', end='12-31-2023'):
    df = pd.DataFrame({"Date": pd.date_range(start, end)})
    df["Day"] = df.Date.dt.isocalendar().day
    df["Week"] = df.Date.dt.isocalendar().week
    df["Date"] = df["Date"].dt.strftime("%d-%m-%Y")  # format the Date column
    df = df[["Day", "Date", "Week"]]  # select columns in the desired order
    return df


print(calendar_dates())
