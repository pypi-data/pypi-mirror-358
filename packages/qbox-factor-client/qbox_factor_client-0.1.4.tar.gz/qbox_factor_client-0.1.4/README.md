# QBox Factor API

一个用于查询实时市场因子数据的高性能Python API，专为量化策略开发而设计。

## 🎯 这是什么？

QBox Factor API 提供实时的中国A股市场因子数据，包括：

- **市场状态数据** - 实时价格、涨跌幅、成交量、涨跌停状态等
- **因子数据** - 市场概览、涨跌停统计、连板分析、接力率等各类量化因子
- **市场微观结构** - 涨停板统计、连板分析、市场情绪指标

**适用场景：**
- 📈 量化策略开发
- 🔍 市场监控分析  
- 💹 实时交易决策
- 📊 风险管理评估

## 🚀 快速开始

### 安装

```bash
# 安装客户端 (包含pandas支持)
pip install qbox-factor-client

# 可选：安装额外分析工具
pip install qbox-factor-client[analysis]
```

### 基础用法

```python
from qbox_factor_client import FactorClient

# 初始化客户端
client = FactorClient("http://your-api-endpoint.com", token="your_token")

# 获取最新因子数据 (DataFrame格式)
factors_df = client.get_latest_factors(df=True)
print(f"获取到 {len(factors_df)} 条因子数据")

# 筛选大涨股票 (涨幅>3%)
gainers_df = client.query_stocks(pct_change_gt=0.03, df=True)
print(f"大涨股票: {len(gainers_df)} 只")
```

## 📊 核心功能

### 1. 市场状态查询

获取个股的实时市场状态信息。`MarketState` 是所有因子计算的核心输入数据结构，它整合了多种数据源，为单个证券在特定时间点提供统一的实时状态快照：

```python
# 查询所有股票的市场状态
market_df = client.query_stocks(df=True)

# 筛选涨停股票
limit_up_df = client.query_stocks(is_limit_up=True, df=True)

# 筛选昨日涨停今日调整的股票 (反转机会)
reversal_df = client.query_stocks(
    was_limit_up_yesterday=True,
    is_limit_up=False,
    df=True
)

# 筛选大跌股票 (跌幅<-5%)
losers_df = client.query_stocks(pct_change_lt=-0.05, df=True)

# 查询特定日期的市场状态
historical_df = client.query_stocks(tdate="2024-01-15", df=True)
```

**市场状态字段：**

| 字段 | 描述 | 类型 |
|------|------|------|
| `symbol` | 股票代码 | String |
| `tdate` | 交易日期 | Date |
| `ttime` | 交易所时间戳 | DateTime |
| `rtime` | 接收时间戳 | DateTime |
| `last_price` | 最新价 | Float |
| `high` | 当日最高价 | Float |
| `low` | 当日最低价 | Float |
| `volume` | 成交量 | Int |
| `turnover` | 成交额 | Float |
| `prev_close` | 昨收价 | Float |
| `open` | 开盘价 | Float |
| `upper_limit` | 涨停价 | Float |
| `lower_limit` | 跌停价 | Float |
| `is_st` | 是否ST股票 | Boolean |
| `asset_name` | 股票名称 | String |
| `is_limit_up` | 是否涨停 | Boolean |
| `is_limit_down` | 是否跌停 | Boolean |
| `pct_change` | 涨跌幅 (%) | Float |
| `was_limit_up_yesterday` | 昨日是否涨停 | Boolean |
| `was_limit_down_yesterday` | 昨日是否跌停 | Boolean |
| `consecutive_limit_up_streak_yesterday` | 昨日连板天数 | Int |

### 2. 因子数据查询

获取各类量化因子数据。系统使用以下计算常量：
- **TOLERANCE**: `1e-6` (0.0001%) - 浮点数比较容差，用于判断"平盘"
- **NEAR_LIMIT_THRESHOLD**: `0.01` (1%) - 接近涨跌停的阈值

```python
# 获取所有因子
all_factors_df = client.get_latest_factors(df=True)

# 按因子集筛选 - 获取市场概览统计
market_stats_df = client.get_latest_factors(
    set_names=["market_summary_stats", "limit_hit_stats"], 
    df=True
)

# 按具体因子名筛选 - 获取关键市场指标
key_factors_df = client.get_latest_factors(
    factor_names=["limit_up_count", "follow_through_rate", "bounce_ratio"], 
    df=True
)
```

**因子数据字段：**

| 字段 | 描述 | 类型 |
|------|------|------|
| `tdate` | 交易日期 | Date |
| `ttime` | 计算时间 | DateTime |
| `set_name` | 因子集名称 | String |
| `factor_name` | 因子名称 | String |
| `symbol` | 股票代码 (可选，部分因子为市场级别) | String |
| `value` | 因子值 | Float |

**完整因子集列表：**

#### 1. 市场概览统计 (`market_summary_stats`)
提供整个市场的宏观统计信息，帮助了解市场整体情绪

| 因子名称 | 计算公式 | 类型 | 描述 | 应用场景 |
|---------|----------|------|------|----------|
| `total_symbols` | `COUNT(所有股票)` | Int | 参与计算的总股票数量 | 市场覆盖度评估 |
| `up_count` | `COUNT(pct_change > 0.0001%)` | Int | 上涨股票数量（使用容差避免浮点误差） | 市场情绪判断 |
| `down_count` | `COUNT(pct_change < -0.0001%)` | Int | 下跌股票数量（使用容差避免浮点误差） | 市场情绪判断 |
| `flat_count` | `COUNT(-0.0001% ≤ pct_change ≤ 0.0001%)` | Int | 平盘股票数量（容差范围内） | 市场活跃度评估 |

**验证关系：** `up_count + down_count + flat_count = total_symbols`

#### 2. 市场成交统计 (`market_volume`, `market_turnover`)
| 因子名称 | 计算公式 | 类型 | 描述 |
|---------|----------|------|------|
| `total_market_volume` | `SUM(volume)` | Int | 整个市场的实时累计成交量 |
| `total_market_turnover` | `SUM(turnover)` | Float | 整个市场的实时累计成交额 |

#### 3. 涨跌停统计 (`limit_hit_stats`)
统计当前触及或接近涨跌停板的股票数量

| 因子名称 | 计算公式 | 类型 | 描述 |
|---------|----------|------|------|
| `limit_up_count` | `COUNT(is_limit_up = True)` | Int | 当前处于涨停状态的股票数量 |
| `limit_down_count` | `COUNT(is_limit_down = True)` | Int | 当前处于跌停状态的股票数量 |
| `near_limit_up_count` | `COUNT(price ≥ upper_limit × 0.99 且未涨停)` | Int | 接近涨停的股票数量（1%范围内） |
| `near_limit_down_count` | `COUNT(price ≤ lower_limit × 1.01 且未跌停)` | Int | 接近跌停的股票数量（1%范围内） |

**验证逻辑：** 涨停和接近涨停为互斥关系，跌停和接近跌停为互斥关系

#### 4. 涨停强度分析 (`limit_up_strength`)
分析涨停股的内部强度和质量

| 因子名称 | 计算公式 | 类型 | 描述 | 意义 |
|---------|----------|------|------|------|
| `limit_up_with_volume` | `COUNT(is_limit_up AND volume > 0)` | Int | 有成交量的涨停股数量 | 涨停的真实性 |
| `limit_up_avg_volume` | `AVG(volume WHERE is_limit_up)` | Float | 涨停股的平均成交量 | 涨停的活跃度 |
| `limit_up_total_turnover` | `SUM(turnover WHERE is_limit_up)` | Float | 所有涨停股的总成交额 | 涨停的资金关注度 |

**验证关系：** `limit_up_with_volume ≤ limit_up_count`

#### 5. 连续涨停统计 (`consecutive_limit_stats`)
追踪市场的连板梯队情况

| 因子名称 | 计算逻辑 | 类型 | 描述 |
|---------|----------|------|------|
| `consecutive_limit_up_2d_count` | `COUNT(is_limit_up AND consecutive_limit_up_streak_yesterday = 1)` | Int | 今日达成 2 连板的股票数量 |
| `consecutive_limit_up_3d_count` | `COUNT(is_limit_up AND consecutive_limit_up_streak_yesterday = 2)` | Int | 今日达成 3 连板的股票数量 |
| `consecutive_limit_up_{N}d_count` | `COUNT(is_limit_up AND consecutive_limit_up_streak_yesterday = N-1)` | Int | 今日达成 N 连板的股票数量 |

**计算逻辑：** 今日N连板 = 昨日(N-1)连板 且 今日涨停
**验证关系：** 通常 `Nd_count ≥ (N+1)d_count` (连板数越高，数量越少)

#### 6. 昨日涨停股表现 (`prev_day_limit_up_performance`)
分析昨日涨停股票的延续性，衡量市场情绪的持续性

| 因子名称 | 计算公式 | 类型 | 描述 |
|---------|----------|------|------|
| `yesterday_limit_up_count` | `COUNT(was_limit_up_yesterday = True)` | Int | T-1 日涨停的股票总数 |
| `positive_follow_count` | `COUNT(昨涨停 AND pct_change > 0)` | Int | T-1 日涨停股中，今日涨幅为正的数量 |
| `negative_follow_count` | `COUNT(昨涨停 AND pct_change < 0)` | Int | T-1 日涨停股中，今日涨幅为负的数量 |
| `flat_follow_count` | `COUNT(昨涨停 AND pct_change = 0)` | Int | T-1 日涨停股中，今日平盘的数量 |
| `still_limit_up_count` | `COUNT(昨涨停 AND is_limit_up = True)` | Int | T-1 日涨停股中，今日仍然涨停的数量 |
| `follow_through_rate` | `positive_follow_count / yesterday_limit_up_count` | Float | **接力率** - 衡量涨停板效应的延续性 |
| `continuation_strength` | `still_limit_up_count / yesterday_limit_up_count` | Float | **连板强度** - 衡量连续涨停的概率 |

**验证关系：** `positive_follow_count + negative_follow_count + flat_follow_count = yesterday_limit_up_count`
**关键指标意义：** 接力率 > 60% 通常表示市场情绪较强，连板强度反映资金追涨意愿

#### 7. 昨日跌停股表现 (`prev_day_limit_down_performance`)
分析昨日跌停股票的反弹情况

| 因子名称 | 计算公式 | 类型 | 描述 |
|---------|----------|------|------|
| `yesterday_limit_down_count` | `COUNT(was_limit_down_yesterday = True)` | Int | T-1 日跌停的股票总数 |
| `count_bounce_follow` | `COUNT(昨跌停 AND pct_change > 0)` | Int | T-1 日跌停股中，今日涨幅为正的数量（反弹） |
| `count_continued_decline` | `COUNT(昨跌停 AND pct_change < 0)` | Int | T-1 日跌停股中，今日涨幅为负的数量（持续下跌） |
| `count_still_limit_down` | `COUNT(昨跌停 AND is_limit_down = True)` | Int | T-1 日跌停股中，今日仍跌停的数量 |
| `bounce_ratio` | `count_bounce_follow / yesterday_limit_down_count` | Float | **反弹率** - 衡量超跌反弹的概率 |

**反弹率意义：** 反弹率 > 30% 通常表示市场存在超跌反弹机会

#### 8. 昨日非涨跌停股表现 (`prev_day_non_limit_performance`)
作为市场情绪的参照基准

| 因子名称 | 计算公式 | 类型 | 描述 |
|---------|----------|------|------|
| `non_limit_count` | `COUNT(was_limit_up_yesterday = False AND was_limit_down_yesterday = False)` | Int | T-1 日未触及涨跌停的股票总数 |
| `non_limit_up_movers` | `COUNT(昨非涨跌停 AND pct_change > 0)` | Int | T-1 日非涨跌停股中，今日上涨的数量 |
| `non_limit_down_movers` | `COUNT(昨非涨跌停 AND pct_change < 0)` | Int | T-1 日非涨跌停股中，今日下跌的数量 |
| `non_limit_up_ratio` | `non_limit_up_movers / non_limit_count` | Float | 普通股上涨比例（市场基准） |
| `non_limit_down_ratio` | `non_limit_down_movers / non_limit_count` | Float | 普通股下跌比例（市场基准） |

**验证关系：** `non_limit_count + yesterday_limit_up_count + yesterday_limit_down_count = total_symbols`

#### 9. 价格变动区间统计 (`price_change_range_stats`)
按涨跌幅区间统计股票分布，采用分箱算法按优先级分类

**分箱逻辑 (按优先级从高到低)：**
```
if pct_change > 0.09:       range = "up_gt_9"
elif pct_change > 0.07:     range = "up_7_to_9"  
elif pct_change > 0.05:     range = "up_5_to_7"
elif pct_change > 0.01:     range = "up_1_to_5"
elif pct_change > 0:        range = "up_0_to_1"
elif pct_change < -0.09:    range = "down_gt_9"
elif pct_change < -0.07:    range = "down_7_to_9"
elif pct_change < -0.05:    range = "down_5_to_7"
elif pct_change < -0.01:    range = "down_1_to_5"
elif pct_change < 0:        range = "down_0_to_1"
else:                       range = "flat"
```

**上涨区间：**
| 因子名称 | 涨跌幅区间 | 含义 |
|---------|------------|------|
| `up_gt_9_pct_count` | `pct_change > 9%` | 大幅上涨股票数量 |
| `up_7_to_9_pct_count` | `7% < pct_change ≤ 9%` | 较大幅度上涨股票数量 |
| `up_5_to_7_pct_count` | `5% < pct_change ≤ 7%` | 中等幅度上涨股票数量 |
| `up_1_to_5_pct_count` | `1% < pct_change ≤ 5%` | 小幅上涨股票数量 |
| `up_0_to_1_pct_count` | `0% < pct_change ≤ 1%` | 微涨股票数量 |

**下跌区间：**
| 因子名称 | 涨跌幅区间 | 含义 |
|---------|------------|------|
| `down_gt_9_pct_count` | `pct_change < -9%` | 大幅下跌股票数量 |
| `down_7_to_9_pct_count` | `-9% ≤ pct_change < -7%` | 较大幅度下跌股票数量 |
| `down_5_to_7_pct_count` | `-7% ≤ pct_change < -5%` | 中等幅度下跌股票数量 |
| `down_1_to_5_pct_count` | `-5% ≤ pct_change < -1%` | 小幅下跌股票数量 |
| `down_0_to_1_pct_count` | `-1% ≤ pct_change < 0%` | 微跌股票数量 |

**特殊统计：**
| 因子名称 | 计算公式 | 含义 |
|---------|---------|------|
| `flat_count` | `COUNT(pct_change = 0)` | 无变动股票数量 |
| `extreme_volatility_count` | `up_gt_9_pct_count + down_gt_9_pct_count` | 极端波动股票总数 |

**验证关系：** 所有区间股票数量之和应等于总股票数，每只股票只应被分类到一个区间

### 3. 环境变量配置

支持环境变量配置，便于部署：

```bash
# 设置环境变量
export FACTOR_ENDPOINT="http://your-api-endpoint.com"
export FACTOR_TOKEN="your_authentication_token"
```

```python
# 自动从环境变量读取配置
client = FactorClient()  # 无需传参
data_df = client.get_latest_factors(df=True)
```

## 💡 实战示例

### 动量反转策略

```python
from qbox_factor_client import FactorClient

def limit_up_analysis_strategy():
    client = FactorClient()
    
    # 1. 获取涨停相关因子
    limit_factors_df = client.get_latest_factors(
        set_names=["prev_day_limit_up_performance", "limit_up_strength"], 
        df=True
    )
    
    # 2. 获取市场状态  
    market_df = client.query_stocks(df=True)
    
    # 3. 合并数据
    strategy_df = limit_factors_df.merge(market_df, on='symbol', how='right')
    
    # 4. 策略筛选 - 寻找高质量的涨停延续机会
    # 获取接力率数据
    follow_through_rate = limit_factors_df[
        limit_factors_df['factor_name'] == 'follow_through_rate'
    ]['value'].iloc[0] if len(limit_factors_df) > 0 else 0.5
    
    selected = strategy_df[
        (strategy_df['pct_change'] >= 0) &                              # 今日上涨
        (strategy_df['pct_change'] <= 0.07) &                          # 涨幅适中
        (~strategy_df['is_limit_up']) &                                 # 非涨停
        (strategy_df['was_limit_up_yesterday']) &                       # 昨日涨停
        (follow_through_rate > 0.6)                                     # 市场接力率良好
    ]
    
    return selected[['symbol', 'pct_change', 'volume', 'was_limit_up_yesterday']].head(10)

# 执行策略
recommendations = limit_up_analysis_strategy()
print(recommendations)
```

### 市场监控面板

```python
def market_dashboard():
    client = FactorClient()
    
    # 市场概览
    market_df = client.query_stocks(df=True)
    
    print("📊 市场概览")
    print(f"总股票数: {len(market_df)}")
    print(f"上涨股票: {(market_df['pct_change'] > 0).sum()}")
    print(f"下跌股票: {(market_df['pct_change'] < 0).sum()}")
    print(f"平均涨跌幅: {market_df['pct_change'].mean():.2%}")
    
    # 涨停板分析
    limit_up_df = client.query_stocks(is_limit_up=True, df=True)
    print(f"\n🔴 涨停股票: {len(limit_up_df)} 只")
    
    # 连板分析
    consecutive_df = client.query_stocks(
        is_limit_up=True,
        was_limit_up_yesterday=True, 
        df=True
    )
    print(f"💎 连板股票: {len(consecutive_df)} 只")
    
    # 反转机会
    reversal_df = client.query_stocks(
        was_limit_up_yesterday=True,
        is_limit_up=False,
        pct_change_gt=0,
        df=True
    )
    print(f"⭐ 反转机会: {len(reversal_df)} 只")

market_dashboard()
```

## 🔧 API 参考

### FactorClient

```python
class FactorClient:
    def __init__(self, endpoint: str = "", token: str = "")
```

**参数：**
- `endpoint`: API服务地址，可通过环境变量`FACTOR_ENDPOINT`设置
- `token`: 认证令牌，可通过环境变量`FACTOR_TOKEN`设置

### 主要方法

#### get_latest_factors()

```python
def get_latest_factors(
    set_names: Optional[List[str]] = None,
    factor_names: Optional[List[str]] = None,
    limit: Optional[int] = None,
    df: bool = False
) -> Union[Dict[str, List[Any]], pd.DataFrame]
```

**参数：**
- `set_names`: 因子集名称列表
- `factor_names`: 具体因子名称列表  
- `limit`: 返回结果数量限制，None表示使用默认限制(1000)，最大3000
- `df`: 是否直接返回DataFrame格式

#### query_stocks()

```python
def query_stocks(
    tdate: Optional[str] = None,
    pct_change_gt: Optional[float] = None,
    pct_change_lt: Optional[float] = None,
    is_limit_up: Optional[bool] = None,
    was_limit_up_yesterday: Optional[bool] = None,
    is_limit_down: Optional[bool] = None,
    was_limit_down_yesterday: Optional[bool] = None,
    limit: Optional[int] = None,
    df: bool = False
) -> Union[Dict[str, List[Any]], pd.DataFrame]
```

**参数：**
- `tdate`: 交易日期，格式YYYY-MM-DD，默认为今日
- `pct_change_gt/lt`: 涨跌幅大于/小于指定值
- `is_limit_up/down`: 当前是否涨停/跌停
- `was_limit_up/down_yesterday`: 昨日是否涨停/跌停
- `limit`: 返回结果数量限制，None表示使用默认限制(1000)，最大3000
- `df`: 是否直接返回DataFrame格式

#### health_check()

```python
def health_check() -> Dict[str, str]
```

检查API服务状态，无需认证。

## 📖 API 文档

QBox Factor API 提供了完整的自描述式API文档：

- **📊 完整因子清单** - 所有9个因子集的详细说明，包含每个因子的含义和应用场景
- **🎯 策略示例** - 针对动量、反转、情绪分析等策略的即用型HTTP查询示例  
- **🌍 双语支持** - 英文和中文说明，适配中国市场语境
- **🔍 参数指导** - 详细的参数说明、示例和取值范围
- **📈 实战案例** - 可直接复制粘贴的查询语句

**访问方式：**
```bash
# 启动API服务后访问
http://your-api-endpoint.com/docs
```

所有API端点都包含完整的参数说明、响应格式和使用示例，无需外部文档即可快速上手。

## ⚡ 性能优化

### 1. 使用df=True参数

```python

# ✅ 高效方式  
df = client.get_latest_factors(df=True)
```

### 2. 客户端复用

```python
# ✅ 推荐：初始化一次，重复使用
client = FactorClient()

for i in range(100):
    data = client.get_latest_factors(df=True)  # 复用连接
```

### 3. 合理设置limit

```python
# 小数据集，获取默认数量
data = client.get_latest_factors(df=True)  # 默认limit=1000

# 需要更多数据时，明确指定 (最大3000)
large_data = client.get_latest_factors(limit=3000, df=True)
```

## 🔐 安全配置

### 环境变量设置

```bash
# .env 文件
FACTOR_ENDPOINT=https://your-secure-api.com
FACTOR_TOKEN=your_secure_token_here
```

### 认证管理

```python
# 动态更新token
client = FactorClient(endpoint="https://api.example.com")
client.set_token("new_token")
```

## 🚨 错误处理

```python
import httpx
from qbox_factor_client import FactorClient

try:
    client = FactorClient()
    data = client.get_latest_factors(df=True)
except httpx.HTTPStatusError as e:
    if e.response.status_code == 401:
        print("认证失败，请检查token")
    elif e.response.status_code == 404:
        print("API端点不存在")
    else:
        print(f"HTTP错误: {e}")
except httpx.RequestError as e:
    print(f"网络连接错误: {e}")
except Exception as e:
    print(f"未知错误: {e}")
```

## 🛠️ 开发环境

```bash
# 克隆项目
cd qbox-factor-api

# 安装开发依赖 (使用uv)
uv sync --extra dev

# 运行测试
python -m pytest tests/

# 运行示例
python examples/basic_usage.py
```
