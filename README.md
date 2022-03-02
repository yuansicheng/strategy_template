# 轻量级策略回测项目模板

*苑思成，20220226*  
*https://github.com/yuansicheng/strategy_templete/tree/master*

## 模板用途
在实现策略及回测时，通常包含大量重复的工作，比如载入数据、画图等，耗费大量的时间，本项目将这些重复的工作定义在基类中，用户实现一个新策略时，只需要实现策略的核心代码即可。  
v1.x版本使用`data_loader - strategy_controller - evaluator`的模型，将三部分解耦，用户只需要继承`Strategy`类，实现其中的两个接口即可。  
随着需求增加，框架代码量越来越大的同时，v1.x版本出现了模块之间耦合、存在重复代码等问题，因此作者在v2.x版本进行了重构，增加了参数管理器、日期管理器，进一步封装数据集类，同时使用逻辑和v1.x版本保持一致。
比如在框架中实现风险平价策略仅需要两行代码：  
``` python
std = self.daily_yield.loc[:this_date].iloc[-self.DAY_OF_YEAR:].std()
self.weights.loc[this_date] = (1/std) / (1/std).sum()
```    

## 基类
定义在`scripts/baseclasses`文件夹中，一般情况无需修改。
1. `Asset`：单个资产的抽象类，用于存放资产名（`asset_name`）、数据文件路径（`asset_file`）和交易成本（`transection_cost`），提供加载指定日期数据（lazy loading）的功能，一般情况下用户无需单独使用该类。
   
2. `Dataset`：数据集类，使用有序字典（`collections.OrderedDict`，保证进行矩阵操作时columns的顺序一致）存放每个资产（`asset_dict`，{`asset_name`: `Asset实体`}，具体功能如下：
   - `addAsset`函数通过传入资产数据文件和交易成本，产生一个`Asset`实体并存入`asset_dict`，其中资产名从文件中解析，如果资产已经添加进`asset_dict`，不再重复添加；
   - `getTransectionCost`函数用于获取`asset_dict`中资产的交易成本，常用于更新权重后净值的计算；
   - `getData`函数通过调用每个资产的`getData`方法，获取特定日期序列的原始数据`raw_data`字典和缺失收盘价数据（`CLOSE`）的日期`missing_date`集合；
   - `dict2CloseDf`函数提取`raw_data`字典中的收盘价数据组成一个`DataFrame`，并除以第一个净值。
   
3. `Benchmark`：业绩基准，继承自`Dataset`，本质上benchmark是一个中间不调仓的策略，因此只需要在第一天扣除交易成本，后续净值可通过矩阵计算得到，即`getValue`函数。
   
4. `DateManager`：封装所有日期相关操作，
   - `setAllDateList`函数从文件中读取所有交易日序列；
   - `getDateList`函数返回日期区间中所有交易日，可设置buffer，即向前多读取一些数据用于计算；
   - `getUpdateDateList`函数按照用户设置的交易频率获取需要调仓的日期序列。
   
5. `ArgManager`：参数管理器，全局管理策略需要的参数，`loadArgsFromFile`用于从文件中读取参数，支持int、float格式，不满足上述格式的参数保存为str。
   
6. `Strategy`：策略基类，对于任何策略，其运行结果都是相同的格式，即各资产在每个时刻的权重（历史权重）和策略的历史净值。具体功能如下，
   - 维护3个`DataFrame`保存策略回测情况：
     - `weights`：策略在每个调仓日更新后的资产权重；
     - `values`：扣除交易成本后的净值，回测期第一天设为1；
     - `asset_states`：保存组合中每个资产的仓位（`position`）、成本（`cost`）、收益（`return`）。
   - 调用策略生成函数`generate`（如果需要）；
   - 对回测区间内的每一天（可设置权重更新频率）执行`backtestOneDay`函数，
     - 更新策略净值`values`；
     - 更新`asset_states`；
     - 如果该日需要更新权重，
       - 执行`backtestOneDay`函数；
       - 更新`asset_states`；
       - 计算交易成本并扣除。
   
7. Evaluator：评估器，输入策略或资产净值（一个DataFrame），输出如下指标计算结果，保存在csv文件中，
   - 每年的收益率（不足一年的由这部分数据计算年化收益）；
   - 累计收益率=$100 \times (回测期内最后一个净值/第一个净值-1)$；
   - 年化收益率=$100 \times ((回测期内最后一个净值/回测期内第一个净值)^{DAYOFYEAR/回测天数}-1)$；
   - 年化波动率=$100 \times std(日收益) \times \sqrt{DAYOFYEAR}$；
   - 最大回撤；
   - 最大回撤发生区间；
   - 最长回撤持续时间；
   - 最长回撤发生区间；
   - sharp比率=$(年化收益率-RFR)/年化波动率$；
   - calmar比率=$(年化收益率-RFR)/最大回撤$；
   - sortino比率=$(年化收益率-RFR)/下行波动率$；
   - 信息比率=$(年化收益率-业绩基准年化收益率)/跟踪误差$ （DataFrame中存储策略相对于各个资产的信息比率）。
  
## 参数文件、交易日文件和画图脚本
在`scripts/baseclasses`文件夹中，

1. 常数文件`constants.txt`，
   - 使用`#`作为注释；
   - 必须设置年交易日数`DAY_OF_YEAR`和无风险利率`RFR`。
2. 交易日文件`transection_date.csv`，
   - 一列数据，title为`日期序列`；
   - 可使用choice的Excel插件生成，公式为`EM_TRADEDATES("1990-01-01","2029-12-31","Period=1,Order=1,MarketType=CNSESH,Format=1,Layout=1,ClearNumber=0")`。
3. 画图脚本`draw.py`，提供画权重面积图和净值折线图的函数。


## 使用方法
1. 复制模板文件夹并重命名，运行结果和文件名无关，模板中的路径均使用相对路径；
2. 在scripts文件夹下新建一个策略子类，继承Strategy基类，
``` python
from base_classes.strategy import Strategy 
class YourStrategy(Strategy):  
def __init__(self, *args, **kwargs) -> None:  
    super().__init__(*args, **kwargs)
```

3. 继承generate函数，将生成的策略超参数保存在成员变量中，该函数将在策略运行时先执行，  
``` python
def generate(self):
    # your code
    pass
```

4. 继承backtestOneDay函数，该函数在策略生成后执行，函数默认传入当前的时间`this_date`，执行结束将计算得到当天的权重存入`self.weights.loc[this_date]`中，
``` python
def backtestOneDay(self, this_date):
    # yourcode
    pass
```

5. 在`scripts/run.py`中，
   - 第1个`#`之间为策略参数，
     - `strategy_name`：策略名；
     - `generation_date_range`：策略生成期；
     - `backtest_date_range`：策略回测期；
     - `result_path`：回测结果的存储路径；
     - `buffer`：读取数据的缓冲区大小。
   - 第2个`#`之间为策略包含的资产，可以精确指定或使用通配符模糊指定；
   - 第3个`#`之间为benchmark，可以同时设置多个benchmark；
   - 初始化`DateManager`，使用`getValue`方法获取benchmark的净值；
   - 初始化策略子类并运行；
   - 权重和净值分别保存并画图；
   - 拼接策略、benchmark、资产的净值，使用`Evaluator`评估性能并保存。


## 更新日志

20220226，v2.0
- 完成重构及初步测试，需要使用更多策略测试。

20220302，v2.1
- 为`frequency`参数添加每季度更新的选项，`quarterly`。


