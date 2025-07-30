import httpx
import os
import pandas as pd
from typing import List, Optional, Dict, Any, Tuple, Union


class FactorClient:
    """
    QBox因子API的Python客户端。

    该客户端提供了与QBox因子API交互的便捷接口，
    允许您获取最新的因子数据和查询市场状态信息。

    示例:
        策略应用启动时初始化一次:
        >>> client = FactorClient()  # 自动从环境变量读取配置
        >>>
        >>> # 直接获取DataFrame格式
        >>> df = client.get_latest_factors(df=True)
        >>>
        >>> # 获取特定因子集
        >>> limit_stats = client.get_latest_factors(set_names=["limit_hit_stats"], df=True)
        >>>
        >>> # 查询大涨股票，直接返回DataFrame
        >>> gainers_df = client.query_stocks(pct_change_gt=0.05, df=True)
        >>>
        >>> # 查询今日涨停股票
        >>> limit_up_df = client.query_stocks(is_limit_up=True, df=True)
        >>>
        >>> # 查询昨日涨停股票
        >>> yesterday_limit_up = client.query_stocks(was_limit_up_yesterday=True, df=True)
    """

    def __init__(self, endpoint: str = "", token: str = ""):
        """
        初始化客户端。

        参数:
            endpoint: 因子API服务的基础URL (例如: "http://localhost:8000")。
                     如果为空，将从环境变量FACTOR_ENDPOINT读取。
            token: 认证用的Bearer token。
                  如果为空，将从环境变量FACTOR_TOKEN读取。

        异常:
            ValueError: 如果endpoint为空或无效。
        """
        # 从环境变量读取配置
        if not endpoint:
            endpoint = os.getenv("FACTOR_ENDPOINT", "")
        if not token:
            token = os.getenv("FACTOR_TOKEN", "")

        if not endpoint:
            raise ValueError(
                "API endpoint不能为空。请设置endpoint参数或FACTOR_ENDPOINT环境变量。"
            )

        self.endpoint = endpoint.rstrip("/")
        self.token = token
        self._client = httpx.Client(
            base_url=self.endpoint,
            timeout=30.0,
            follow_redirects=True,
        )
        self._update_headers()

    def _update_headers(self):
        """更新客户端的认证头。"""
        headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
        self._client.headers.update(headers)

    def set_token(self, token: str):
        """
        设置或更新认证token。

        参数:
            token: 新的认证token。
        """
        self.token = token
        self._update_headers()

    def to_df(self, data: Dict[str, List[Any]]) -> pd.DataFrame:
        """
        将扁平字典数据转换为pandas DataFrame。

        注意: 推荐直接使用 df=True 参数，这个方法主要用于向后兼容。

        参数:
            data: 由get_latest_factors()或query_stocks()返回的扁平字典数据。

        返回:
            pandas DataFrame。
        """
        return pd.DataFrame(data)

    def get_latest_factors(
        self,
        set_names: Optional[List[str]] = None,
        factor_names: Optional[List[str]] = None,
        limit: Optional[int] = None,
        df: bool = False,
    ) -> Union[Dict[str, List[Any]], pd.DataFrame]:
        """
        获取最新的因子数据。

        参数:
            set_names: 按因子集名称过滤。
                可用因子集: market_summary_stats, limit_hit_stats,
                          market_volume, market_turnover, limit_up_strength,
                          consecutive_limit_stats, prev_day_limit_up_performance,
                          prev_day_limit_down_performance, prev_day_non_limit_performance,
                          price_change_range_stats
                例如: ["market_summary_stats", "limit_hit_stats"]
            factor_names: 按具体因子名称过滤 (例如: ["up_count", "limit_up_count"])。
            limit: 返回的最大结果数，None表示返回全部。
            df: 如果为True，直接返回pandas DataFrame；否则返回字典。

        返回:
            如果df=True，返回pandas DataFrame；否则返回扁平字典格式的因子数据。

        异常:
            httpx.HTTPError: 如果API请求失败。
        """
        params: List[Tuple[str, Any]] = []
        if limit is not None:
            params.append(("limit", limit))
        else:
            params.append(("limit", 1000))  # 默认获取适量数据
        if set_names:
            for name in set_names:
                params.append(("set_names", name))
        if factor_names:
            for name in factor_names:
                params.append(("factor_names", name))

        response = self._client.get("/api/v1/factors/latest", params=params)
        response.raise_for_status()
        raw_data = response.json()

        # 转换为扁平字典格式
        if not raw_data:
            result = {}
        else:
            # 获取所有字段
            fields = set()
            for item in raw_data:
                fields.update(item.keys())

            # 创建扁平字典
            result = {field: [] for field in fields}
            for item in raw_data:
                for field in fields:
                    result[field].append(item.get(field))

        # 根据df参数决定返回格式
        if df:
            return pd.DataFrame(result)
        else:
            return result

    def query_stocks(
        self,
        tdate: Optional[str] = None,
        pct_change_gt: Optional[float] = None,
        pct_change_lt: Optional[float] = None,
        is_limit_up: Optional[bool] = None,
        was_limit_up_yesterday: Optional[bool] = None,
        is_limit_down: Optional[bool] = None,
        was_limit_down_yesterday: Optional[bool] = None,
        limit: Optional[int] = None,
        df: bool = False,
    ) -> Union[Dict[str, List[Any]], pd.DataFrame]:
        """
        根据市场状态条件查询股票。

        参数:
            tdate: 交易日期过滤 (格式: "YYYY-MM-DD")，默认为今日。
            pct_change_gt: 涨幅大于此值的股票 (例如: 0.05 表示 5%)。
            pct_change_lt: 涨幅小于此值的股票 (例如: -0.03 表示 -3%)。
            is_limit_up: 当前是否涨停。
            was_limit_up_yesterday: 昨日是否涨停。
            is_limit_down: 当前是否跌停。
            was_limit_down_yesterday: 昨日是否跌停。
            limit: 返回的最大结果数，None表示返回全部。
            df: 如果为True，直接返回pandas DataFrame；否则返回字典。

        返回:
            如果df=True，返回pandas DataFrame；否则返回扁平字典格式的股票市场状态信息。

        异常:
            httpx.HTTPError: 如果API请求失败。
        """
        params: Dict[str, Any] = {}
        if limit is not None:
            params["limit"] = limit
        else:
            params["limit"] = 1000  # 默认获取适量数据
        if tdate is not None:
            params["tdate"] = tdate
        if pct_change_gt is not None:
            params["pct_change_gt"] = pct_change_gt
        if pct_change_lt is not None:
            params["pct_change_lt"] = pct_change_lt
        if is_limit_up is not None:
            params["is_limit_up"] = is_limit_up
        if was_limit_up_yesterday is not None:
            params["was_limit_up_yesterday"] = was_limit_up_yesterday
        if is_limit_down is not None:
            params["is_limit_down"] = is_limit_down
        if was_limit_down_yesterday is not None:
            params["was_limit_down_yesterday"] = was_limit_down_yesterday

        response = self._client.get("/api/v1/market_state/query", params=params)
        response.raise_for_status()
        raw_data = response.json()

        # 转换为扁平字典格式
        if not raw_data:
            result = {}
        else:
            # 获取所有字段
            fields = set()
            for item in raw_data:
                fields.update(item.keys())

            # 创建扁平字典
            result = {field: [] for field in fields}
            for item in raw_data:
                for field in fields:
                    result[field].append(item.get(field))

        # 根据df参数决定返回格式
        if df:
            return pd.DataFrame(result)
        else:
            return result

    def health_check(self) -> Dict[str, str]:
        """
        执行API服务健康检查。
        此操作不需要认证。

        返回:
            包含状态信息的字典。

        异常:
            httpx.HTTPError: 如果健康检查失败。
        """
        with httpx.Client(base_url=self.endpoint) as client:
            response = client.get("/health")
            response.raise_for_status()
            return response.json()

    def close(self):
        """关闭底层HTTP客户端。"""
        self._client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# 向后兼容
__all__ = ["FactorClient"]
