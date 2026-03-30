# 腾讯证券股票数据爬虫

爬取腾讯证券（通过东方财富网API）的所有股票代码、所属行业和概念数据。

## 功能

- 获取所有A股股票列表（代码、名称）
- 获取股票所属行业分类
- 获取股票所属概念板块

## 使用方法

```bash
# 获取完整数据（包括行业和概念）
python stock_spider_final.py

# 仅获取行业数据（跳过概念）
python stock_spider_final.py --skip-concept

# 使用已有数据跳过行业获取
python stock_spider_final.py --skip-industry
```

## 输出文件

| 文件 | 说明 |
|------|------|
| `stock_list.csv` | 股票列表（代码+名称） |
| `stock_industry.csv` | 股票行业映射 |
| `stock_concept.csv` | 股票概念映射 |
| `stock_all_data.csv` | 最终合并数据 |

## 数据统计

- 总股票数: 5,830
- 有行业数据的股票: 5,495 (94.3%)

## 依赖

```bash
pip install akshare pandas
```

## 数据来源

数据通过 AkShare 库从东方财富网获取。
