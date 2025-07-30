import logging
import os
import atexit # 用于捕捉程序退出
import signal # 处理系统函数，包括Ctrl + C等
import pandas as pd

from QuantDataCollector.Utils.mysql_utils import mysqlOps
from QuantDataCollector.Global.settings import *
from QuantDataCollector.Utils.file_utils import mkdir

class DataCollectorError(Exception):  # 继承自 Exception 基类
    """自定义异常的说明文档"""
    pass  # 通常不需要额外逻辑，用 pass 占位即可

class DataCollector:

    def __init__(self):
        signal.signal(signal.SIGINT, self.signal_exit) # 捕捉SIGINT事件，并在signal_exit函数中处理
        atexit.register(self.cleanUp) # 程序退出时执行cleanUp函数
        self.db = mysqlOps(STOCK_DATABASE_NAME)
        self.__config_logging()

    def __del__(self):
        pass

    def signal_exit(self,signum,frame):
        self.__logger.info("my_exit: interrupted by ctrl+c")
        self.cleanUp()
        exit()

    def cleanUp(self):
        pass

    def __config_logging(self, level = logging.WARNING):
        if level == logging.DEBUG:
            print("================= data collector info ==================")
            print(self.get_data_collector_info())
            print("================= end of collector info ==================")
        self.__logger = logging.getLogger('data_collector')
        
        if not os.path.exists(LOGGING_FILE_DIR):
            mkdir(LOGGING_FILE_DIR)
        ch = logging.FileHandler(LOGGING_FILE_NAME)
        formatter = logging.Formatter(fmt='%(asctime)s.%(msecs)03d - %(name)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        ch.setFormatter(formatter)
        self.__logger.addHandler(ch)
        self.__logger.setLevel(level)

    def get_data_collector_info(self):
        res = ""
        res += "log path:" + LOGGING_FILE_NAME + "\n"
        return res

    """
    获取股票基本信息
    """
    def get_stock_basic(self, code_list = None):
        filter = "1 = 1"
        if code_list is not None:
            filter += " AND code in ("
            for code in code_list:
                filter += "'" + code + "',"
            filter = filter[:-1] + ")"

        res, data = self.db.query(STOCK_BASIC_INFO_TABLE_NAME, None, filter)
        if res:
            columns = ['code', 'name', 'area', 'exchage','market', 'list_status', 'list_date', 'unlist_date','act_name', 'act_type']
            df = pd.DataFrame(data, columns=columns)
            return df
        self.__logger.error("获取股票基本信息失败，错误信息" + str(data))
        raise DataCollectorError("获取股票基本信息失败，错误信息：" + str(data))

    """
    获取每日指标
    """
    def get_daily_basic(self, code = None, date = None, start_date = None, end_date = None):
        filter = "1 = 1"
        if code:
                filter += " AND code ='" + code + "'"
        if date:
            filter += " AND date = '" + date + "'"

        if start_date:
                filter += " AND date >= '" + start_date + "'"

        if end_date:
                filter += " AND date <= '" + end_date + "'"
        columns = ['code', 'date', 'close', 'turnover_rate','turnover_rate_f', 'volume_ratio', 'pe', 'pe_ttm', 'pb', 'ps', 'ps_ttm', 'dv_ratio', 'dv_ttm', 'total_share', 'float_share', 'free_share', 'total_mv', 'circ_mv']
        res, data = self.db.query(STOCK_DAILY_BASIC_TABLE_NAME, columns, filter)
        if res:
            df = pd.DataFrame(data, columns=columns)
            return df
        else:
            self.__logger.error("从数据库获取每日指标信息失败：" + str(data))
            raise DataCollectorError("从数据库获取每日指标信息失败，错误信息：" + str(data))

    """
    获取日线数据
    """
    def get_daily(self, code=None, date=None, start_date=None, end_date=None):
        filter = "1 = 1"
        if code:
                filter += " AND code ='" + code + "'"
        if date:
            filter += " AND date = '" + date + "'"

        if start_date:
                filter += " AND date >= '" + start_date + "'"

        if end_date:
                filter += " AND date <= '" + end_date + "'"
        columns = ['code', 'date', 'open', 'close', 'high','low', 'change_amount', 'vol', 'amount']
        res, data = self.db.query(STOCK_DAILY_TABLE_NAME, columns, filter)
        if res:
            df = pd.DataFrame(data, columns=columns)
            return df
        else:
            self.__logger.error("从数据库获取历史日线失败：" + str(data))
            raise DataCollectorError("从数据库获取历史日线失败，错误信息：" + str(data))

    def get_limit_list(self, code = None, date = None, type = None, start_date = None, end_date = None):
        filter = "1 = 1"
        if date:
            filter += " and date = '" + date + "'"

        if code:
                filter += " and code ='" + code + "'"
        if type:
                filter += " and limit_type = '" + type + "'"

        if start_date:
                filter += " AND date >= '" + start_date + "'"

        if end_date:
                filter += " AND date <= '" + end_date + "'"

        columns = ['code', 'date', 'limit_amount', 'fd_amount','first_time', 'last_time', 'open_times', 'up_stat', 'limit_times', 'limit_type']
        res, data = self.db.query(STOCK_LIMIT_LIST_DAY_TABLE_NAME, columns, filter)
        if res:
            df = pd.DataFrame(data, columns=columns)
            return df
        else:
            self.__logger.error("从数据库获取涨跌幅及炸板信息失败：" + str(data))
            raise DataCollectorError("从数据库获取涨跌幅及炸板信息失败，错误信息：" + str(data))

    """
    获取股票的股东数量
    @Parameters:
    - code: 股票代码, 如果不传则查询所有股票的股东数量
    - cut_off_date: 指定数据统计的截止日期，格式为YYYY-MM-DD，返回数据统计的截止日期在该日期之前的所有数据，默认为查询所有截止日期的数据
    """
    def get_holder_number(self, code = None, cut_off_date = None):
        filter = None
        if cut_off_date:
            filter = "cut_off_date < '" + cut_off_date + "'"
        if code:
            if filter == None:
                filter = "code ='" + code + "'"
            else:
                filter += " and code ='" + code + "'"
        columns = ['code', 'ann_pub_date', 'cut_off_date', 'holder_num']
        res, data = self.db.query(STOCK_HOLDER_NUMBER_TABLE_NAME, columns, filter)
        if res:
            df = pd.DataFrame(data, columns=columns)
            # 假设 df 是原始 DataFrame，'date_column' 是日期列名
            df['cut_off_date'] = pd.to_datetime(df['cut_off_date'])  # 步骤1：转换日期格式
            df_sorted = df.sort_values(by='cut_off_date', ascending=False)          # 步骤2：按日期排序
            return df_sorted
        else:
            self.__logger.error("从数据库获取股东数量信息失败：" + str(data))
            raise DataCollectorError("从数据库获取股东数量信息失败，错误信息：" + str(data))

    """
    获取交易日历
    @Params:
    - is_open:不指定is_open表示开市/休市都要，指定is_open=1表示只要开市的日期，
    - start_date: 指定需要的起始日期，比如2020-01-01
    - end_date：指定需要的结束日期，比如2023-12-30
    - exchange：A股的不同交易所交易/休市日期相同，一般不用指定，默认为上海交易所

    @Returns:
    - pandas.DataFrame

    @Raise:
    - DataCollectorError
    """
    def get_trade_calendar(self, is_open = None, start_date = None, end_date = None, exchange = "SSE"):
        filter = "exchange = '" + exchange + "'"
        if is_open is not None:
            filter += " AND is_open = '" + str(is_open) + "'"
        if start_date is not None:
            filter += " AND date >= '" + start_date + "'"
        if end_date is not None:
            filter += " AND date <= '" + end_date + "'"
        columns = ['date', 'pre_trade_date','is_open']
        res, data = self.db.query(STOCK_TRADE_CALENDAR_TABLE_NAME, columns, filter)
        if res:
            df = pd.DataFrame(data, columns=columns)
            return df
        else:
            self.__logger.error("从数据库获取交易日历信息失败：" + str(data))
            raise DataCollectorError("从数据库获取交易日历信息失败，错误信息：" + str(data))

    """
    获取同花顺行业概念板块
    @Params
    - index_code: 行业板块代码
    - exchange： 交易所
    - type：指数类型 N-概念指数 I-行业指数 R-地域指数 S-同花顺特色指数 ST-同花顺风格指数 TH-同花顺主题指数 BB-同花顺宽基指数
    """
    def get_tonghuashun_index(self, index_code = None,exchange = None, type = None):
        filter = "1 = 1"
        if index_code:
            filter += " AND index_code = '" + index_code + "'"
        if exchange:
            filter += " AND exchange = '" + exchange + "'"
        if type:
            filter += " AND type = '" + type + "'"
        columns = ['index_code', 'name', 'count', 'exchange', 'list_date','type']
        res, data = self.db.query(STOCK_TONGHUASHUN_INDEX_TABLE_NAME, columns, filter)
        if res:
            df = pd.DataFrame(data, columns=columns)
            return df
        else:
            self.__logger.error("从数据库获取同花顺板块指数数据失败：" + str(data))
            raise DataCollectorError("从数据库获取同花顺板块指数数据失败，错误信息：" + str(data))

    """
    获取同花顺行业板块成分股
    @Params
    - index_code：行业板块代码
    - code：成分股代码
    """
    def get_tonghuashun_index_member(self, index_code = None, code = None):
        filter = "1 = 1"
        if index_code:
            filter += " AND index_code = '" + index_code + "'"
        if code:
            filter += " AND code = '" + code + "'"

        columns = ['index_code', 'code', 'name', 'weight', 'in_date', 'out_date','is_new']
        res, data = self.db.query(STOCK_TONGHUASHUN_INDEX_MEMBER_TABLE_NAME, columns, filter)
        if res:
            df = pd.DataFrame(data, columns=columns)
            return df
        else:
            self.__logger.error("从数据库获取同花顺板块成分股数据失败：" + str(data))
            raise DataCollectorError("从数据库获取同花顺板块成分股数据失败，错误信息：" + str(data))

    def get_chip_yardstick_quotient(self,code = None, date = None, start_date = None, end_date = None):
        filter = "1 = 1"
        if code:
                filter += " AND code ='" + code + "'"
        if date:
            filter += " AND date = '" + date + "'"

        if start_date:
                filter += " AND date >= '" + start_date + "'"

        if end_date:
                filter += " AND date <= '" + end_date + "'"
        columns = ['code', 'date', 'his_low', 'his_high', 'cost_5pct','cost_15pct','cost_50pct','cost_85pct','cost_95pct','weight_avg', 'winner_rate']
        res, data = self.db.query(STOCK_CHIP_YARDSTICK_QUOTIENT_TABLE_NAME, columns, filter)
        if res:
            df = pd.DataFrame(data, columns=columns)
            return df
        else:
            self.__logger.error("从数据库获取筹码数据失败：" + str(data))
            raise DataCollectorError("从数据库获取筹码数据失败，错误信息：" + str(data))

    """
    获取股票复权因子，可提取单只股票全部历史复权因子，也可以提取单日全部股票的复权因子
    """
    def get_adjust_factor(self, code = None, date = None, start_date = None, end_date = None):
        filter = "1 = 1"
        if code:
                filter += " AND code ='" + code + "'"
        if date:
            filter += " AND date = '" + date + "'"

        if start_date:
                filter += " AND date >= '" + start_date + "'"

        if end_date:
                filter += " AND date <= '" + end_date + "'"
        columns = ['code', 'date', 'adj_factor']
        res, data = self.db.query(STOCK_ADJUST_FACTOR_TABLE_NAME, columns, filter)
        if res:
            df = pd.DataFrame(data, columns=columns)
            return df
        else:
            self.__logger.error("从数据库获取复权因子失败：" + str(data))
            raise DataCollectorError("从数据库获取复权因子失败，错误信息：" + str(data))

if __name__ == '__main__':
    data_collector = DataCollector()