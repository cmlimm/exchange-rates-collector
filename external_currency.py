import pandas as pd
import json
import requests


def get_aoa_to_usd(date_start, date_end):
	date_start = date_start.strftime('%Y-%m-%d')
	date_end = date_end.strftime('%Y-%m-%d')

	request_string = "https://www.bna.ao/service/rest/taxas/get/evolucao/taxa/intervalo?datainicio={}&datafim={}&tipocambio=M&moeda=USD"
    request_string = request_string.format(date_start, date_end)
    request = requests.get(request_string, verify=False)

    df = pd.read_json(request.text[19:-16], orient='records')
    df = df[['data', 'taxa']]

    df = df.rename(columns={"data": "Дата", "taxa": "Курс"})
    df['Дата'] = pd.to_datetime(df['Date'], format='%Y-%m-%d')
    df['Валюта 1'] = 'AOA'

    return df


def get_bam_to_usd(date_start, date_end):
	date_start = date_start.strftime('%m.%d.%Y')
	date_end = date_end.strftime('%m.%d.%Y')

	request_string = requests.get('https://cbbh.ba/CurrencyExchange/GetJsonForPeriod?dateFrom={}&dateTo={}')
	request_string = request_string.format(date_start, date_end)
    request = requests.get(request_string)

    df = pd.json_normalize(request.json(), "CurrencyExchangeItems", ["Date"])
    df = df[df["AlphaCode"] == "USD"][["Date", "Middle"]]
    df = df.rename(columns={"Date": "Дата", "Middle": "Курс"})

    df['Дата'] = pd.to_datetime(df['Дата'])
	df['Курс'] = df['Курс'].str.replace(',', '.')
	df['Курс'] = df['Курс'].astype(float)
	df['Валюта 1'] = 'BAM'

	return df


def get_hrk_to_usd(date_start, date_end):
	pass


def get_rsd_to_usd(date_start, date_end):
	pass


def get_exchange_rates(date_start, date_end, currency):

	date_start = pd.to_datetime(start_date, format='%d/%m/%Y')
	date_end = pd.to_datetime(finish_date, format='%d/%m/%Y')
	date_range = pd.date_range(start=date_start, end=date_end)

	if currency == "AOA":
		df = get_aoa_to_usd(date_start, date_end)
	elif currency == "RSD":
		df = get_rsd_to_usd(date_start, date_end)
	elif currency == "HRK":
		df = get_hrk_to_usd(date_start, date_end)
	elif currency == "BAM":
		df = get_bam_to_usd(date_start, date_end)

	df = df.set_index('Дата')
    df = df.reindex(date_range, fill_value=None)
    df = df.reset_index(names='Дата')
    df = df.fillna(method='bfill')

    df['Дата'] = df['Дата'].dt.strftime('%d/%m/%Y')
    df['Курс'] = df['Курс'].astype(float)

    return df