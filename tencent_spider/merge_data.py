#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
腾讯证券股票数据爬虫 - 最终版
快速爬取所有股票代码、所属行业和概念
使用已有的行业数据，并继续获取概念数据
"""

import pandas as pd
import akshare as ak
import time
import os
from datetime import datetime


def main():
    """
    主函数：合并已有数据并生成最终结果
    """
    print("=" * 60)
    print("腾讯证券股票数据爬虫 - 合并数据")
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
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
    print(f"合并后行业数据: {len(industry_grouped)} 只股票")
    
    # 获取概念数据
    print("\n正在获取概念板块数据...")
    stock_concept_map = {}
    
    try:
        concept_df = ak.stock_board_concept_name_em()
        print(f"共有 {len(concept_df)} 个概念板块")
        
        total = len(concept_df)
        for idx, row in concept_df.iterrows():
            concept_name = row['板块名称']
            try:
                cons_df = ak.stock_board_concept_cons_em(symbol=concept_name)
                if not cons_df.empty:
                    for _, stock_row in cons_df.iterrows():
                        code = stock_row['代码']
                        if code not in stock_concept_map:
                            stock_concept_map[code] = []
                        stock_concept_map[code].append(concept_name)
                
                if (idx + 1) % 20 == 0 or idx + 1 == total:
                    print(f"已处理概念: {idx + 1}/{total}")
                time.sleep(0.05)
            except:
                continue
    except Exception as e:
        print(f"获取概念数据时出错: {e}")
    
    # 合并所有数据
    print("\n正在合并所有数据...")
    result_list = []
    for _, row in stock_list_df.iterrows():
        code = row['股票代码']
        name = row['股票名称']
        
        # 获取行业
        industry_row = industry_grouped[industry_grouped['股票代码'] == code]
        industry_str = industry_row['所属行业'].values[0] if len(industry_row) > 0 else ''
        
        # 获取概念
        concepts = stock_concept_map.get(code, [])
        concept_str = ','.join(concepts) if concepts else ''
        
        result_list.append({
            '股票代码': code,
            '股票名称': name,
            '所属行业': industry_str,
            '所属概念': concept_str
        })
    
    result_df = pd.DataFrame(result_list)
    
    # 保存最终结果
    output_file = os.path.join(output_dir, "stock_all_data.csv")
    result_df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"\n最终数据已保存到: {output_file}")
    
    # 打印统计信息
    print("\n" + "=" * 60)
    print("数据统计:")
    print(f"  总股票数: {len(result_df)}")
    print(f"  有行业数据的股票: {len(result_df[result_df['所属行业'] != ''])}")
    print(f"  有概念数据的股票: {len(result_df[result_df['所属概念'] != ''])}")
    print("=" * 60)
    print(f"结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 显示前10条数据示例
    print("\n数据示例（前10条）:")
    print(result_df.head(10).to_string(index=False))
    
    return result_df


if __name__ == "__main__":
    result = main()
