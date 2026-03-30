#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
腾讯证券股票数据爬虫
爬取所有股票代码、所属行业和概念
"""

import pandas as pd
import akshare as ak
import time
import os
from datetime import datetime


def get_stock_list():
    """
    获取所有A股股票列表
    返回: DataFrame包含股票代码和名称
    """
    print("正在获取股票列表...")
    try:
        # 使用akshare获取A股实时行情数据（包含所有股票）
        stock_df = ak.stock_zh_a_spot_em()
        # 只保留代码和名称
        stock_list = stock_df[['代码', '名称']].copy()
        stock_list.columns = ['股票代码', '股票名称']
        print(f"成功获取 {len(stock_list)} 只股票")
        return stock_list
    except Exception as e:
        print(f"获取股票列表失败: {e}")
        return pd.DataFrame()


def get_industry_data():
    """
    获取行业板块数据
    返回: 行业板块名称列表
    """
    print("正在获取行业板块数据...")
    try:
        industry_df = ak.stock_board_industry_name_em()
        print(f"成功获取 {len(industry_df)} 个行业板块")
        return industry_df
    except Exception as e:
        print(f"获取行业板块数据失败: {e}")
        return pd.DataFrame()


def get_concept_data():
    """
    获取概念板块数据
    返回: 概念板块名称列表
    """
    print("正在获取概念板块数据...")
    try:
        concept_df = ak.stock_board_concept_name_em()
        print(f"成功获取 {len(concept_df)} 个概念板块")
        return concept_df
    except Exception as e:
        print(f"获取概念板块数据失败: {e}")
        return pd.DataFrame()


def get_stock_industry_mapping():
    """
    获取股票与行业的映射关系
    返回: DataFrame包含股票代码和所属行业
    """
    print("正在获取股票行业映射...")
    stock_industry_list = []
    
    try:
        # 获取所有行业板块
        industry_df = ak.stock_board_industry_name_em()
        
        for idx, row in industry_df.iterrows():
            industry_name = row['板块名称']
            try:
                # 获取该行业下的所有股票
                stock_in_industry = ak.stock_board_industry_cons_em(symbol=industry_name)
                if not stock_in_industry.empty:
                    for _, stock_row in stock_in_industry.iterrows():
                        stock_industry_list.append({
                            '股票代码': stock_row['代码'],
                            '股票名称': stock_row['名称'],
                            '所属行业': industry_name
                        })
                print(f"已处理行业: {industry_name} ({idx + 1}/{len(industry_df)})")
                time.sleep(0.3)  # 避免请求过快
            except Exception as e:
                print(f"获取行业 {industry_name} 的股票失败: {e}")
                continue
        
        return pd.DataFrame(stock_industry_list)
    except Exception as e:
        print(f"获取股票行业映射失败: {e}")
        return pd.DataFrame()


def get_stock_concept_mapping():
    """
    获取股票与概念的映射关系
    返回: DataFrame包含股票代码和所属概念
    """
    print("正在获取股票概念映射...")
    stock_concept_list = []
    
    try:
        # 获取所有概念板块
        concept_df = ak.stock_board_concept_name_em()
        
        for idx, row in concept_df.iterrows():
            concept_name = row['板块名称']
            try:
                # 获取该概念下的所有股票
                stock_in_concept = ak.stock_board_concept_cons_em(symbol=concept_name)
                if not stock_in_concept.empty:
                    for _, stock_row in stock_in_concept.iterrows():
                        stock_concept_list.append({
                            '股票代码': stock_row['代码'],
                            '股票名称': stock_row['名称'],
                            '所属概念': concept_name
                        })
                print(f"已处理概念: {concept_name} ({idx + 1}/{len(concept_df)})")
                time.sleep(0.3)  # 避免请求过快
            except Exception as e:
                print(f"获取概念 {concept_name} 的股票失败: {e}")
                continue
        
        return pd.DataFrame(stock_concept_list)
    except Exception as e:
        print(f"获取股票概念映射失败: {e}")
        return pd.DataFrame()


def get_stock_industry_by_code(stock_code):
    """
    根据股票代码获取所属行业
    参数: stock_code - 股票代码
    返回: 行业列表
    """
    try:
        # 获取个股所属板块
        df = ak.stock_individual_info_em(symbol=stock_code)
        if not df.empty:
            industry_row = df[df['item'] == '行业']
            if not industry_row.empty:
                return industry_row['value'].values[0]
        return ""
    except:
        return ""


def merge_stock_data(stock_list_df, stock_industry_df, stock_concept_df):
    """
    合并股票数据：股票代码、名称、行业、概念
    """
    print("正在合并数据...")
    
    # 创建结果DataFrame
    result_df = stock_list_df.copy()
    
    # 合并行业数据（一只股票可能有多个行业，用逗号分隔）
    if not stock_industry_df.empty:
        industry_grouped = stock_industry_df.groupby('股票代码')['所属行业'].apply(
            lambda x: ','.join(x.dropna().unique())
        ).reset_index()
        result_df = result_df.merge(industry_grouped, on='股票代码', how='left')
    else:
        result_df['所属行业'] = ''
    
    # 合并概念数据（一只股票可能有多个概念，用逗号分隔）
    if not stock_concept_df.empty:
        concept_grouped = stock_concept_df.groupby('股票代码')['所属概念'].apply(
            lambda x: ','.join(x.dropna().unique())
        ).reset_index()
        result_df = result_df.merge(concept_grouped, on='股票代码', how='left')
    else:
        result_df['所属概念'] = ''
    
    # 填充空值
    result_df['所属行业'] = result_df['所属行业'].fillna('')
    result_df['所属概念'] = result_df['所属概念'].fillna('')
    
    return result_df


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
    stock_industry_df = get_stock_industry_mapping()
    if not stock_industry_df.empty:
        industry_file = os.path.join(output_dir, "stock_industry.csv")
        stock_industry_df.to_csv(industry_file, index=False, encoding='utf-8-sig')
        print(f"股票行业映射已保存到: {industry_file}")
    
    # 3. 获取股票概念映射
    stock_concept_df = get_stock_concept_mapping()
    if not stock_concept_df.empty:
        concept_file = os.path.join(output_dir, "stock_concept.csv")
        stock_concept_df.to_csv(concept_file, index=False, encoding='utf-8-sig')
        print(f"股票概念映射已保存到: {concept_file}")
    
    # 4. 合并所有数据
    result_df = merge_stock_data(stock_list_df, stock_industry_df, stock_concept_df)
    
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
    
    return result_df


if __name__ == "__main__":
    result = main()
