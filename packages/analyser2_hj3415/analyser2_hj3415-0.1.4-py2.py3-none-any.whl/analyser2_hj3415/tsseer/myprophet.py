from prophet import Prophet
from analyser2_hj3415.tsseer.utils import *
from utils_hj3415 import setup_logger

mylogger = setup_logger(__name__,'WARNING')

def run(ticker: str):
    df = get_raw_data(ticker)

    # ds, y, volume, volume_scaled 열로 구성된 데이터프레임 반환
    df_scaler_dict = preprocessing_for_prophet(df)
    mylogger.debug(df_scaler_dict['prepared_df'])

    past_and_forecast_df = forecast(df_scaler_dict)

    print(past_and_forecast_df)
    print(past_and_forecast_df.columns)


def forecast(df_scaler_dict: dict) -> pd.DataFrame:
    prepared_df: pd.DataFrame = df_scaler_dict.get('prepared_df')
    volume_scaler: StandardScaler = df_scaler_dict.get('volume_scaler')

    model = Prophet()
    # covariate 추가 - 데이터프레임 외생변수 열이름
    model.add_regressor('volume_scaled')
    model.fit(prepared_df)

    future_data_df = model.make_future_dataframe(periods=180)

    # 과거 데이터에서 거래량의 평균을 구해 새 데이터프레임을 만든단.
    past_volume_mean = prepared_df['volume'].mean()
    future_volume = pd.DataFrame({'volume': [past_volume_mean] * len(future_data_df)})
    # 미래거래량을 정규화해서 새로운 열로 첨가한다.
    future_data_df['volume_scaled'] = volume_scaler.transform(future_volume[['volume']])

    past_and_forecast_df = model.predict(future_data_df)
    mylogger.debug(past_and_forecast_df)
    return past_and_forecast_df




if __name__ == '__main__':
    ticker = '005930.KQ'
    run(ticker)




