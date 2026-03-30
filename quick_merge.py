#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
腾讯证券股票数据爬虫 - 合并已有数据
"""

import pandas as pd
import os


def main():
    output_dir = "/workspace/stock_data"
    
    # 读取股票列表
    stock_list_file = os.path.join(output_dir, "stock_list.csv")
    stock_list_df = pd.read_csv(stock_list_file)
    print(f"已读取 {len(stock_list_df)} 只股票")
    
    # 读取行业数据
    industry_file = os.path.join(output_dir, "stock_industry.csv")
    industry_df = pd.read_csv(industry_file)
    print(f"已读取 {len(industry_df)} 条行业记录")
    
    # 合并行业数据（一只股票可能有多个行业）
    industry_grouped = industry_df.groupby('股票代码')['所属行业'].apply(
        lambda x: ','.join(x.dropna().unique())
    ).reset_index()
    print(f"合并后行业数据: {len(industry_grouped)} 只股票有行业信息")
    
    # 合并所有数据
    print("\n正在合并数据...")
    result_df = stock_list_df.merge(industry_grouped, on='股票代码', how='left')
    result_df['所属行业'] = result_df['所属行业'].fillna('')
    result_df['所属概念'] = ''  # 概念数据需要单独获取
    
    # 保存最终结果
    output_file = os.path.join(output_dir, "stock_all_data.csv")
    result_df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"\n数据已保存到: {output_file}")
    
    # 打印统计信息
    print("\n数据统计:")
    print(f"  总股票数: {len(result_df)}")
    print(f"  有行业数据的股票: {len(result_df[result_df['所属行业'] != ''])}")
    
    # 显示示例数据
    print("\n数据示例（前10条）:")
    print(result_df.head(10).to_string(index=False))
    
    # 显示有行业数据的示例
    print("\n有行业数据的示例（前10条）:")
    sample = result_df[result_df['所属行业'] != ''].head(10)
    print(sample.to_string(index=False))
    
    return result_df


if __name__ == "__main__":
    result = main()
