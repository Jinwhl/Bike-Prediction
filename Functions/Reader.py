import pandas as pd
import matplotlib.pyplot as plt

# pd.set_option('display.max_rows', None)
# pd.set_option('display.max_columns', None)

newColumns = ['Date', 'HHMM', 'ST-start', 'ST-end', 'Use', 'Minute[min]', 'Distance[m]']

def showCSV(file_path):
    data = pd.read_csv(file_path, encoding='cp949')
    data.columns = newColumns

    return data
# ======================================================================== #


def dataOptimization(DataFrame):
    DataFrame = selectLocation(DataFrame)
    DataFrame = sameST(DataFrame) # 대여한 곳에서 바로 자전거를 반납한 케이스 제거
    DataFrame = brokenBike(DataFrame) # 자전거가 고장나서 센터로 반납되는 케이스 제거
    DataFrame.reset_index(drop=True, inplace=True) # row 개수에 맞는 index 초기화

    print(DataFrame)

    return DataFrame
def selectLocation(DataFrame):
    bikeStationInfo = pd.read_csv('./bikeStationInfo(23.06).csv')
    codeList = bikeStationInfo['Code'].tolist()

    fullCase = DataFrame['ST-start'].isin(codeList) | DataFrame['ST-end'].isin(codeList)

    # other Conditions
    circular = DataFrame['ST-start'].isin(codeList) & DataFrame['ST-end'].isin(codeList)
    outflow = DataFrame['ST-start'].isin(codeList) & ~DataFrame['ST-end'].isin(codeList)
    inflow  = DataFrame['ST-end'].isin(codeList) & ~DataFrame['ST-start'].isin(codeList)

    DataFrame = DataFrame[fullCase]

    return DataFrame
def sameST(DataFrame):
    min_t = 5
    min_dst = 10

    sameST_condition = (DataFrame['ST-start'] == DataFrame['ST-end'])
    shortTime_condition = (DataFrame['Minute[min]'] <= min_t)
    shortDist_condition = (DataFrame['Distance[m]'] <= min_dst)

    # Set of Conditions
    drops = sameST_condition & shortTime_condition & shortDist_condition

    # Apply conditions and return the modified DataFrame
    return DataFrame[~drops]
def brokenBike(DataFrame):
    drops = DataFrame['ST-end'] == 'CENTER'

    # Apply conditions and return the modified DataFrame
    return DataFrame[~drops]
# ======================================================================== #


def showGraph(DataFrame):
    interval = int(input("Input Interval : "))
    usageOverTime(DataFrame, interval)
def usageOverTime(DataFrame, interval):
    DataFrame = DataFrame.drop(['ST-start', 'ST-end', 'Minute[min]', 'Distance[m]'], axis=1)
    resultDF = DataFrame.groupby(['Date', 'HHMM'], as_index=False)['Use'].sum()

    # 'HHMM' changes to str
    resultDF['HHMM'] = resultDF['HHMM'].astype(str).str.zfill(4)
    resultDF['Datetime'] = pd.to_datetime(resultDF['Date'].astype(str) + resultDF['HHMM'], format='%Y%m%d%H%M')

    # set index to 'Datetime'
    resultDF.set_index('Datetime', inplace=True)

    # set interval
    itVL = str(interval) + 'T'
    resampledDF = resultDF.resample(itVL).sum()

    # reset index
    resampledDF.reset_index(inplace=True)
    resampledDF['HHMM'] = resampledDF['Datetime'].dt.strftime('%H%M').astype(int)

    resampledDF = resampledDF[['Date', 'HHMM', 'Use']]

    print(resampledDF)

    # graph Settings
    plt.figure(figsize=(12, 6))
    plt.plot(resampledDF['HHMM'], resampledDF['Use'], linestyle='solid')

    # graph title, label
    plt.title('Hourly Use Over Time', fontsize=16)
    plt.xlabel('HHMM', fontsize=14)
    plt.ylabel('Use', fontsize=14)

    # show Graph
    plt.grid(True)
    plt.show()


# ======================================================================== #
