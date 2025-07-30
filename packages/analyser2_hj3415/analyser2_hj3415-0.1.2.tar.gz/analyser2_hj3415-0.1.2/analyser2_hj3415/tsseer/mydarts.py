from analyser2_hj3415.tsseer.utils import *

def run_nbeats(ticker: str):
    df = get_raw_data(ticker)
    series_scaler_dict = preprocessing_for_darts(df)
    train_val_dict = prepare_train_val_series('scaled', series_scaler_dict)

    from analyser2_hj3415.tsseer.models.nbeats import train_and_forecast
    forecast_series = train_and_forecast(series_scaler_dict, train_val_dict)

    #print(timeseries_to_dataframe(forecast_series))

    show_graph('nbeats', series_scaler_dict, forecast_series)


def run_prophet(ticker: str):
    df = get_raw_data(ticker)
    series_scaler_dict = preprocessing_for_darts(df)
    train_val_dict = prepare_train_val_series('raw', series_scaler_dict)

    from analyser2_hj3415.tsseer.models.prophet import train_and_forecast
    forecast_series = train_and_forecast(train_val_dict)

    # print(timeseries_to_dataframe(forecast_series))

    show_graph('Prophet', series_scaler_dict, forecast_series)


if __name__ == '__main__':
    ticker = '005930.KQ'
    run_nbeats(ticker)
    #run_prophet(ticker)