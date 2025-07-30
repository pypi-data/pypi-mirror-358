"""
Módulo de obtenção dos dados da SELIC por meio da API do BACEN.

Site com a explicação da API da SELIC:
https://dadosabertos.bcb.gov.br/dataset/11-taxa-de-juros---selic/resource/b73edc07-bbac-430c-a2cb-b1639e605fa8

# Dados de SELIC acumuladas mensalmente.
https://api.bcb.gov.br/dados/serie/bcdata.sgs.4390/dados?formato=json

4390 é o código da SELIC a.m.
11 é o código da SELIC a.d.

Neste site:
https://www.bcb.gov.br/htms/selic/selicacumul.asp?frame=1
Há os valores acumulados mensalmente para fins de conferência. Os dados mensais da SELIC constantes no arquivo "dados_selic_mensal.csv" foram obtidos neste site.

Legislação SELIC:
RESOLUÇÃO BCB Nº 46, DE 24 DE NOVEMBRO DE 2020
Dispõe sobre a metodologia de cálculo e a divulgação da Taxa Selic.
https://www.in.gov.br/en/web/dou/-/resolucao-bcb-n-46-de-24-de-novembro-de-2020-290037317

"""
import requests
import json

from datetime import datetime
from dateutil.relativedelta import relativedelta
from decimal import Decimal, ROUND_HALF_DOWN
from bs4 import BeautifulSoup

import csv


def get_daily_selic_from_bacen(
    init_date: datetime = datetime(year=1986, month=6, day=4),
    final_date: datetime = None,
):
    """
    Get SELIC data from the BACEN API.
    """
    URL = "http://api.bcb.gov.br/dados/serie/bcdata.sgs.11/dados?formato=json"
    INIT_DATE_PARAMETER = "&dataInicial={init_date}"
    FINAL_DATE_PARAMETER = "&dataFinal={final_date}"  # data_inicial e data_final são Strings no formato dd/mm/aaaa.

    final_date = datetime.today() if not final_date else final_date

    response = requests.get(
        URL
        + INIT_DATE_PARAMETER.format(init_date=init_date.strftime("%d/%m/%Y"))
        + FINAL_DATE_PARAMETER.format(final_date=final_date.strftime("%d/%m/%Y"))
    )
    if response.ok:
        return list(
            map(
                lambda selic_data: {
                    **selic_data,
                    "data_datetime": datetime.strptime(selic_data["data"], "%d/%m/%Y"),
                },
                json.loads(response.text),
            )
        )

    # TODO: Improve the exception message when the http response is not 200.
    return "Não foi possível obter os dados da SELIC."


def get_monthly_selic_from_bacen(
    init_date: datetime = datetime(year=1986, month=6, day=1),
    final_date: datetime = None,
):
    """
    Get SELIC data from the BACEN API.
    """
    URL = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.4390/dados?formato=json"
    INIT_DATE_PARAMETER = "&dataInicial={init_date}"
    FINAL_DATE_PARAMETER = "&dataFinal={final_date}"  # data_inicial e data_final são Strings no formato dd/mm/aaaa.

    final_date = datetime.today() if not final_date else final_date

    response = requests.get(
        URL
        + INIT_DATE_PARAMETER.format(init_date=init_date.strftime("%d/%m/%Y"))
        + FINAL_DATE_PARAMETER.format(final_date=final_date.strftime("%d/%m/%Y"))
    )
    if response.ok:
        return {
            datetime.strptime(selic_data["data"], "%d/%m/%Y"): Decimal(
                selic_data["valor"]
            )
            / Decimal("100")
            for selic_data in json.loads(response.text)
        }

    # TODO: Improve the exception message when the http response is not 200.
    return "Não foi possível obter os dados da SELIC."


def replace_month_name_with_number(month_name):
    if month_name == "Janeiro":
        return "01"
    elif month_name == "Fevereiro":
        return "02"
    elif month_name == "Março":
        return "03"
    elif month_name == "Abril":
        return "04"
    elif month_name == "Maio":
        return "05"
    elif month_name == "Junho":
        return "06"
    elif month_name == "Julho":
        return "07"
    elif month_name == "Agosto":
        return "08"
    elif month_name == "Setembro":
        return "09"
    elif month_name == "Outubro":
        return "10"
    elif month_name == "Novembro":
        return "11"
    elif month_name == "Dezembro":
        return "12"


def get_monthly_selic_from_rfb():
    """
    Get SELIC data from the Receita Federal do Brasil site.
    """
    URL = "https://www.gov.br/receitafederal/pt-br/assuntos/orientacao-tributaria/pagamentos-e-parcelamentos/taxa-de-juros-selic"
    response = requests.get(URL)
    if response.ok:
        soup = BeautifulSoup(response.text, "html.parser")
        data = []
        tables = soup.find_all("table")

        for table in tables:
            table_body = table.find("tbody")
            rows = table_body.find_all("tr")
            for row in rows:
                cols = row.find_all("td")
                cols = [ele.text.strip() for ele in cols]
                data.append([ele for ele in cols if ele])  # Get rid of empty values

            dict_years = {}
            dict_selic = {}
            for row in data:
                if row[0] == "Mês/Ano":
                    for i in range(len(row)):
                        if row[i].isdigit():
                            dict_years[i] = row[i]
                else:
                    for i in range(len(row)):
                        if "%" in row[i]:
                            dict_selic[
                                datetime.strptime(
                                    replace_month_name_with_number(row[0])
                                    + "/"
                                    + dict_years[i],
                                    "%m/%Y",
                                )
                            ] = Decimal(
                                row[i].replace(",", ".").replace("%", "")
                            ) / Decimal("100")
        return dict(sorted(dict_selic.items()))

    # TODO: Improve the exception message when the http response is not 200.
    return "Não foi possível obter os dados da SELIC."


def calc_selic_month(selic_data, month: datetime) -> Decimal:
    """
    Calculates the accumulated SELIC index on a given month.
    """
    selic_month_data = list(
        filter(
            lambda d: d["data_datetime"] >= month.replace(day=1)
            and d["data_datetime"] < (month + relativedelta(months=+1)).replace(day=1),
            selic_data,
        )
    )

    if not selic_month_data:
        raise Exception(
            f'Não existe dados da SELIC para o mês {month.strftime("%m/%Y")}'
        )

    selic_index = Decimal(1.0)
    for selic in selic_month_data:
        selic_index = selic_index * (1 + Decimal(selic["valor"]) / Decimal(100))

    return selic_index.quantize(Decimal(".00000001"), rounding=ROUND_HALF_DOWN)


def get_monthly_selic_hard_data():
    selic_monthly_data = {}
    with open("dados_selic_mensal.csv") as file:
        reader = csv.reader(file, delimiter=";")

        for line in reader:
            selic_monthly_data.update(
                {
                    datetime.strptime(line[0], "%b/%Y"): Decimal(
                        line[1].replace(",", ".")
                    )
                }
            )

    return selic_monthly_data


def get_monthly_acc_selic_in_period(init_date: datetime, final_date: datetime):
    """
    Get the monthly accumulated SELIC rate for a given period.
    """

    if final_date < init_date:
        raise Exception("A data final deve ser igual ou posterior à data inicial!")

    curr_date = init_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    final_date = final_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    months = [curr_date]

    while curr_date < final_date:
        curr_date = curr_date + relativedelta(months=+1)
        months.append(curr_date)

    selic_data = get_daily_selic_from_bacen(
        init_date.replace(day=1),
        final_date.replace(day=1) + relativedelta(months=+1) + relativedelta(days=-1),
    )  # Como a taxa é acumulada mensalmente, o dia da data final tem que ser o último dia do mês e o primeiro da data inicial.
    return {
        month: calc_selic_month(selic_data, month) - Decimal("1") for month in months
    }
