import datetime
import time
from typing import Literal
import matplotlib.pyplot as plt
import yfinance as yf
import pandas as pd

from darts import TimeSeries
from darts.dataprocessing.transformers import Scaler
import numpy as np
from darts.dataprocessing.transformers import MissingValuesFiller
from sklearn.preprocessing import StandardScaler

from utils_hj3415 import setup_logger

mylogger = setup_logger(__name__,'INFO')


def get_raw_data(ticker: str, max_retries: int = 3, delay_sec: int = 2) -> pd.DataFrame:
    """
    Yahoo Finance에서 특정 티커의 최근 4년간 주가 데이터를 가져옵니다.

    Args:
        ticker (str): 조회할 종목의 티커 (예: "005930.KQ").
        max_retries (int, optional): 최대 재시도 횟수. 기본값은 3.
        delay_sec (int, optional): 재시도 전 대기 시간 (초). 기본값은 2초.

    Returns:
        pd.DataFrame: 주가 데이터프레임. 실패 시 빈 DataFrame 반환.
    """
    today = datetime.datetime.today()
    four_years_ago = today - datetime.timedelta(days=365 * 4)

    for attempt in range(1, max_retries + 1):
        try:
            data = yf.download(
                tickers=ticker,
                start=four_years_ago.strftime('%Y-%m-%d'),
                # end=today.strftime('%Y-%m-%d')  # 생략 시 최신 날짜까지 자동 포함
            )

            if not data.empty:
                return data
            else:
                print(f"[{attempt}/{max_retries}] '{ticker}' 데이터가 비어 있습니다. {delay_sec}초 후 재시도합니다...")

        except Exception as e:
            print(f"[{attempt}/{max_retries}] '{ticker}' 다운로드 중 오류 발생: {e}. {delay_sec}초 후 재시도합니다...")

        time.sleep(delay_sec)

    mylogger.error(f"'{ticker}' 주가 데이터를 최대 {max_retries}회 시도했지만 실패했습니다.")
    return pd.DataFrame()


def preprocessing_for_darts(df: pd.DataFrame) -> dict[str, TimeSeries | Scaler]:
    df.columns = df.columns.get_level_values(0)
    df.columns.name = None
    df = df[['Close', 'Volume']].dropna()
    df.index = df.index.tz_localize(None)  # 타임존 제거
    df.index.name = "time"  # darts는 index가 datetime이어야 함

    target_series = TimeSeries.from_dataframe(df, value_cols='Close', fill_missing_dates=True, freq='B')
    volume_series = TimeSeries.from_dataframe(df, value_cols='Volume', fill_missing_dates=True, freq='B')

    # 휴장일등으로 nan값을 가지는 데이터를 직전값으로 채운다.
    target_series = MissingValuesFiller().transform(target_series)
    volume_series = MissingValuesFiller().transform(volume_series)

    # 스케일링 (0~1)
    target_scaler = Scaler()
    volume_scaler = Scaler()

    target_scaled = target_scaler.fit_transform(target_series)
    volume_scaled = volume_scaler.fit_transform(volume_series)

    mylogger.debug(f"target_scaled : {target_scaled}")
    mylogger.debug(f"volume_scaled : {volume_scaled}")

    return {
        'target_series': target_series,
        'volume_series': volume_series,
        'target_scaled': target_scaled,
        'volume_scaled': volume_scaled,
        'target_scaler': target_scaler,
        'volume_scaler': volume_scaler,
    }

def preprocessing_for_prophet(df: pd.DataFrame) -> dict[str, pd.DataFrame | StandardScaler]:
    df.columns = df.columns.get_level_values(0)
    df.columns.name = None
    df.index = df.index.tz_localize(None)  # 타임존 제거
    df.index.name = "time"

    df = df[['Close', 'Volume']].dropna().reset_index()
    df.columns = ['ds', 'y', 'volume']  # Prophet의 형식에 맞게 열 이름 변경


    volume_scaler = StandardScaler()
    df['volume_scaled'] = volume_scaler.fit_transform(df[['volume']])
    mylogger.debug(df)
    return {
        'prepared_df': df,
        'volume_scaler': volume_scaler,
    }

def prepare_train_val_series(
        target_type:Literal['raw', 'scaled'],
        series_scaler_dict: dict[str, TimeSeries | Scaler]) -> dict[str, TimeSeries | Scaler]:
    target_series = series_scaler_dict.get('target_series')
    target_scaled = series_scaler_dict.get('target_scaled')
    volume_scaled = series_scaler_dict.get('volume_scaled')
    if target_type == 'raw':
        target_train, target_val = target_series.split_before(0.9)
        volume_train, volume_val = volume_scaled.split_before(0.9)
    elif target_type == 'scaled':
        target_train, target_val = target_scaled.split_before(0.9)
        volume_train, volume_val = volume_scaled.split_before(0.9)
    else:
        raise ValueError(f"'{target_type}' 오류")

    mylogger.debug(f"target_train / target_val: {len(target_train)} / {len(target_val)}")
    mylogger.debug(f"target_train: {target_train}")
    mylogger.debug(f"target_val: {target_val}")
    mylogger.debug(f"volume_train / volume_val: {len(volume_train)} / {len(volume_val)}")
    mylogger.debug(f"volume_train: {volume_train}")
    mylogger.debug(f"volume_val: {volume_val}")

    return {
        'target_train': target_train,
        'volume_train': volume_train,
        'target_val': target_val,
        'volume_val': volume_val,
    }


def timeseries_to_dataframe(forecast: TimeSeries) -> pd.DataFrame:
    forecast_df = forecast.to_dataframe()
    mylogger.debug(forecast_df)
    return forecast_df


def show_graph(title: str, series_scaler_dict: dict[str, TimeSeries | Scaler], forecast_series: TimeSeries) -> None:
    target_series = series_scaler_dict.get('target_series')

    target_series.plot(label='close')

    if title == 'nbeats':
        forecast_series.plot(label='predict', low_quantile=0.05, high_quantile=0.95, color="orange")
    else:
        forecast_series.plot(label='predict')

    plt.axvline(target_series.end_time(), color="gray", ls="--", lw=1)  # 학습/검증 경계
    plt.legend()
    plt.title(title)
    plt.show()


def extend_future_covariates(need_steps: int, volume_series: TimeSeries) -> TimeSeries:
    """
    주어진 시계열(volume_series)의 마지막 값을 기준으로 미래 구간을 일정 길이(need_steps)만큼 확장합니다.

    이 함수는 Darts 모델에서 future covariates가 예측 구간만큼 충분히 존재해야 할 때 사용됩니다.
    마지막 값을 복제하여 미래 값을 생성하므로, future covariates가 일정하고 단순할 경우 유용합니다.

    Parameters:
        need_steps (int): 확장할 미래 구간의 스텝 수 (예: 180 - output_chunk_length)
        volume_series (TimeSeries): 기준이 되는 시계열 (예: 거래량)

    Returns:
        TimeSeries: 기존 시계열에 미래 구간이 덧붙여진 확장된 TimeSeries 객체

    Example:
        >>> extended = extend_future_covariates(45, volume_series)
        >>> print(extended.end_time())  # 기존보다 45 스텝 뒤 시간 출력
    """
    last_val = volume_series.last_value()
    future_dates = pd.date_range(
        start=volume_series.end_time() + volume_series.freq,
        periods=need_steps, freq=volume_series.freq
    )
    future_vals = np.full((need_steps, 1), last_val)

    extra_ts = TimeSeries.from_times_and_values(
        future_dates, future_vals, columns=volume_series.components
    )
    extended_volume_scaled = volume_series.append(extra_ts)
    return extended_volume_scaled



