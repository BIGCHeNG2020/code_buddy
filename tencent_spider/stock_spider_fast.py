#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
腾讯证券股票数据爬虫 - 简化版
快速爬取所有股票代码、所属行业和概念
"""

import pandas as pd
import akshare as ak
import time
import os
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading


def get_stock_list():
    """
    获取所有A股股票列表
    返回: DataFrame包含股票代码和名称
    """
    print("正在获取股票列表...")
    try:
        stock_df = ak.stock_zh_a_spot_em()
        stock_list = stock_df[['代码', '名称']].copy()
        stock_list.columns = ['股票代码', '股票名称']
        print(f"成功获取 {len(stock_list)} 只股票")
        return stock_list
    except Exception as e:
        print(f"获取股票列表失败: {e}")
        return pd.DataFrame()


def get_stock_info_batch():
    """
    批量获取股票的详细信息（包含行业）
    返回: DataFrame包含股票代码、名称、行业
    """
    print("正在获取股票详细信息（含行业）...")
    try:
        # 获取A股实时行情（包含所有股票）
        stock_df = ak.stock_zh_a_spot_em()
        
        result_list = []
        for _, row in stock_df.iterrows():
            result_list.append({
                '股票代码': row['代码'],
                '股票名称': row['名称'],
                '最新价': row['最新价'],
                '涨跌幅': row['涨跌幅'],
                '成交量': row['成交量'],
                '成交额': row['成交额'],
                '所属行业': '',  # 行业信息需要单独获取
                '所属概念': ''   # 概念信息需要单独获取
            })
        
        return pd.DataFrame(result_list)
    except Exception as e:
        print(f"获取股票详细信息失败: {e}")
        return pd.DataFrame()


def get_stock_industry_cons():
    """
    获取股票行业分类数据
    通过遍历行业板块获取股票与行业的对应关系
    """
    print("正在获取股票行业分类...")
    stock_industry_map = {}
    
    try:
        # 获取所有行业板块
        industry_df = ak.stock_board_industry_name_em()
        print(f"共有 {len(industry_df)} 个行业板块")
        
        total = len(industry_df)
        for idx, row in industry_df.iterrows():
            industry_name = row['板块名称']
            try:
                # 获取该行业下的所有股票
                cons_df = ak.stock_board_industry_cons_em(symbol=industry_name)
                if not cons_df.empty:
                    for _, stock_row in cons_df.iterrows():
                        code = stock_row['代码']
                        if code not in stock_industry_map:
                            stock_industry_map[code] = []
                        stock_industry_map[code].append(industry_name)
                
                if (idx + 1) % 50 == 0 or idx + 1 == total:
                    print(f"已处理行业: {idx + 1}/{total}")
                time.sleep(0.1)
            except Exception as e:
                continue
        
        return stock_industry_map
    except Exception as e:
        print(f"获取行业分类失败: {e}")
        return {}


def get_stock_concept_cons():
    """
    获取股票概念分类数据
    通过遍历概念板块获取股票与概念的对应关系
    """
    print("正在获取股票概念分类...")
    stock_concept_map = {}
    
    try:
        # 获取所有概念板块
        concept_df = ak.stock_board_concept_name_em()
        print(f"共有 {len(concept_df)} 个概念板块")
        
        total = len(concept_df)
        for idx, row in concept_df.iterrows():
            concept_name = row['板块名称']
            try:
                # 获取该概念下的所有股票
                cons_df = ak.stock_board_concept_cons_em(symbol=concept_name)
                if not cons_df.empty:
                    for _, stock_row in cons_df.iterrows():
                        code = stock_row['代码']
                        if code not in stock_concept_map:
                            stock_concept_map[code] = []
                        stock_concept_map[code].append(concept_name)
                
                if (idx + 1) % 50 == 0 or idx + 1 == total:
                    print(f"已处理概念: {idx + 1}/{total}")
                time.sleep(0.1)
            except Exception as e:
                continue
        
        return stock_concept_map
    except Exception as e:
        print(f"获取概念分类失败: {e}")
        return {}


def main():
    """
    主函数：爬取腾讯证券的所有股票代码、行业和概念
    """
    print("=" * 60)
    print("腾讯证券股票数据爬虫")
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 创建输出目录
    output_dir = "/workspace/stock_data"
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. 获取股票列表
    stock_list_df = get_stock_list()
    if stock_list_df.empty:
        print("无法获取股票列表，程序退出")
        return
    
    # 保存股票列表
    stock_list_file = os.path.join(output_dir, "stock_list.csv")
    stock_list_df.to_csv(stock_list_file, index=False, encoding='utf-8-sig')
    print(f"股票列表已保存到: {stock_list_file}")
    
    # 2. 获取股票行业映射
    industry_map = get_stock_industry_cons()
    
    # 3. 获取股票概念映射
    concept_map = get_stock_concept_cons()
    
    # 4. 合并数据
    print("正在合并数据...")
    result_list = []
    for _, row in stock_list_df.iterrows():
        code = row['股票代码']
        name = row['股票名称']
        
        # 获取行业
        industries = industry_map.get(code, [])
        industry_str = ','.join(industries) if industries else ''
        
        # 获取概念
        concepts = concept_map.get(code, [])
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
