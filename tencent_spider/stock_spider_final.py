#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
腾讯证券股票数据爬虫 - 完整版
爬取所有股票代码、所属行业和概念

使用方法:
    python stock_spider_final.py [--skip-industry] [--skip-concept]

参数:
    --skip-industry: 跳过行业数据获取（使用已有数据）
    --skip-concept: 跳过概念数据获取

数据来源: 东方财富网（通过AkShare库）
"""

import pandas as pd
import akshare as ak
import time
import os
import argparse
from datetime import datetime


class StockDataSpider:
    """股票数据爬虫类"""
    
    def __init__(self, output_dir="/workspace/stock_data"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
    def get_stock_list(self):
        """获取所有A股股票列表"""
        print("\n" + "="*50)
        print("正在获取股票列表...")
        print("="*50)
        
        try:
            stock_df = ak.stock_zh_a_spot_em()
            stock_list = stock_df[['代码', '名称']].copy()
            stock_list.columns = ['股票代码', '股票名称']
            
            # 保存股票列表
            stock_list_file = os.path.join(self.output_dir, "stock_list.csv")
            stock_list.to_csv(stock_list_file, index=False, encoding='utf-8-sig')
            
            print(f"✓ 成功获取 {len(stock_list)} 只股票")
            print(f"✓ 已保存到: {stock_list_file}")
            return stock_list
        except Exception as e:
            print(f"✗ 获取股票列表失败: {e}")
            return pd.DataFrame()
    
    def get_industry_data(self):
        """获取股票行业分类数据"""
        print("\n" + "="*50)
        print("正在获取行业板块数据...")
        print("="*50)
        
        stock_industry_list = []
        
        try:
            # 获取所有行业板块
            industry_df = ak.stock_board_industry_name_em()
            total = len(industry_df)
            print(f"共有 {total} 个行业板块")
            
            for idx, row in industry_df.iterrows():
                industry_name = row['板块名称']
                try:
                    # 获取该行业下的所有股票
                    cons_df = ak.stock_board_industry_cons_em(symbol=industry_name)
                    if not cons_df.empty:
                        for _, stock_row in cons_df.iterrows():
                            stock_industry_list.append({
                                '股票代码': stock_row['代码'],
                                '股票名称': stock_row['名称'],
                                '所属行业': industry_name
                            })
                    
                    # 显示进度
                    if (idx + 1) % 50 == 0 or idx + 1 == total:
                        print(f"进度: {idx + 1}/{total} 行业 ({(idx+1)*100//total}%)")
                    time.sleep(0.05)
                except Exception as e:
                    continue
            
            industry_result_df = pd.DataFrame(stock_industry_list)
            
            # 保存行业数据
            industry_file = os.path.join(self.output_dir, "stock_industry.csv")
            industry_result_df.to_csv(industry_file, index=False, encoding='utf-8-sig')
            
            print(f"\n✓ 成功获取 {len(industry_result_df)} 条行业记录")
            print(f"✓ 已保存到: {industry_file}")
            return industry_result_df
        except Exception as e:
            print(f"✗ 获取行业数据失败: {e}")
            return pd.DataFrame()
    
    def get_concept_data(self):
        """获取股票概念分类数据"""
        print("\n" + "="*50)
        print("正在获取概念板块数据...")
        print("="*50)
        
        stock_concept_list = []
        
        try:
            # 获取所有概念板块
            concept_df = ak.stock_board_concept_name_em()
            total = len(concept_df)
            print(f"共有 {total} 个概念板块")
            
            for idx, row in concept_df.iterrows():
                concept_name = row['板块名称']
                try:
                    # 获取该概念下的所有股票
                    cons_df = ak.stock_board_concept_cons_em(symbol=concept_name)
                    if not cons_df.empty:
                        for _, stock_row in cons_df.iterrows():
                            stock_concept_list.append({
                                '股票代码': stock_row['代码'],
                                '股票名称': stock_row['名称'],
                                '所属概念': concept_name
                            })
                    
                    # 显示进度
                    if (idx + 1) % 20 == 0 or idx + 1 == total:
                        print(f"进度: {idx + 1}/{total} 概念 ({(idx+1)*100//total}%)")
                    time.sleep(0.05)
                except Exception as e:
                    continue
            
            concept_result_df = pd.DataFrame(stock_concept_list)
            
            # 保存概念数据
            concept_file = os.path.join(self.output_dir, "stock_concept.csv")
            concept_result_df.to_csv(concept_file, index=False, encoding='utf-8-sig')
            
            print(f"\n✓ 成功获取 {len(concept_result_df)} 条概念记录")
            print(f"✓ 已保存到: {concept_file}")
            return concept_result_df
        except Exception as e:
            print(f"✗ 获取概念数据失败: {e}")
            return pd.DataFrame()
    
    def merge_all_data(self, stock_list_df, industry_df=None, concept_df=None):
        """合并所有数据"""
        print("\n" + "="*50)
        print("正在合并数据...")
        print("="*50)
        
        if stock_list_df.empty:
            print("✗ 股票列表为空，无法合并")
            return pd.DataFrame()
        
        result_list = []
        
        # 处理行业数据
        industry_map = {}
        if industry_df is not None and not industry_df.empty:
            for _, row in industry_df.iterrows():
                code = row['股票代码']
                if code not in industry_map:
                    industry_map[code] = []
                industry_map[code].append(row['所属行业'])
        
        # 处理概念数据
        concept_map = {}
        if concept_df is not None and not concept_df.empty:
            for _, row in concept_df.iterrows():
                code = row['股票代码']
                if code not in concept_map:
                    concept_map[code] = []
                concept_map[code].append(row['所属概念'])
        
        # 合并数据
        for _, row in stock_list_df.iterrows():
            code = row['股票代码']
            name = row['股票名称']
            
            industries = industry_map.get(code, [])
            industry_str = ','.join(industries) if industries else ''
            
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
        output_file = os.path.join(self.output_dir, "stock_all_data.csv")
        result_df.to_csv(output_file, index=False, encoding='utf-8-sig')
        
        print(f"✓ 成功合并 {len(result_df)} 条记录")
        print(f"✓ 已保存到: {output_file}")
        
        return result_df
    
    def print_summary(self, result_df):
        """打印数据统计摘要"""
        print("\n" + "="*60)
        print("数据统计摘要")
        print("="*60)
        print(f"  总股票数: {len(result_df)}")
        print(f"  有行业数据的股票: {len(result_df[result_df['所属行业'] != ''])}")
        print(f"  有概念数据的股票: {len(result_df[result_df['所属概念'] != ''])}")
        print(f"  有完整数据的股票: {len(result_df[(result_df['所属行业'] != '') & (result_df['所属概念'] != '')])}")
        print("="*60)
        
        # 显示示例数据
        print("\n示例数据（前5条）:")
        print(result_df.head(5).to_string(index=False))
        
        # 显示有完整数据的示例
        complete_data = result_df[(result_df['所属行业'] != '') & (result_df['所属概念'] != '')]
        if len(complete_data) > 0:
            print("\n有完整数据的示例（前5条）:")
            print(complete_data.head(5).to_string(index=False))


def main():
    parser = argparse.ArgumentParser(description='腾讯证券股票数据爬虫')
    parser.add_argument('--skip-industry', action='store_true', help='跳过行业数据获取')
    parser.add_argument('--skip-concept', action='store_true', help='跳过概念数据获取')
    args = parser.parse_args()
    
    print("="*60)
    print("腾讯证券股票数据爬虫")
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    spider = StockDataSpider()
    
    # 1. 获取股票列表
    stock_list_df = spider.get_stock_list()
    if stock_list_df.empty:
        print("无法获取股票列表，程序退出")
        return
    
    # 2. 获取行业数据
    industry_df = None
    if not args.skip_industry:
        industry_df = spider.get_industry_data()
    
    # 3. 获取概念数据
    concept_df = None
    if not args.skip_concept:
        concept_df = spider.get_concept_data()
    
    # 4. 合并所有数据
    result_df = spider.merge_all_data(stock_list_df, industry_df, concept_df)
    
    # 5. 打印统计摘要
    if not result_df.empty:
        spider.print_summary(result_df)
    
    print(f"\n结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n输出文件:")
    print(f"  - {spider.output_dir}/stock_list.csv (股票列表)")
    print(f"  - {spider.output_dir}/stock_industry.csv (行业数据)")
    print(f"  - {spider.output_dir}/stock_concept.csv (概念数据)")
    print(f"  - {spider.output_dir}/stock_all_data.csv (完整数据)")


if __name__ == "__main__":
    main()
