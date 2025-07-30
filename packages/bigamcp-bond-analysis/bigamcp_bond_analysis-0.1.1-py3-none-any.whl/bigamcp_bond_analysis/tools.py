# -*- coding: utf-8 -*-
"""
可转债分析核心工具函数
"""
import akshare as ak
import pandas as pd
from functools import lru_cache
from typing import List, Dict, Any
from datetime import datetime, timedelta
import traceback


# --- 内部辅助函数 ---

@lru_cache(maxsize=1)
def _get_all_bonds_list() -> pd.DataFrame:
    """
    获取并缓存全市场可转债的全面数据。
    该函数是所有其他数据分析函数的基础。
    使用 ak.bond_cov_comparison() 一次性获取所有需要的数据，以提高健壮性。
    """
    try:
        print("Fetching all-in-one bond data from ak.bond_cov_comparison()...")
        df = ak.bond_cov_comparison()
        
        # 重命名列以匹配项目内部的命名约定
        df.rename(columns={
            '转债代码': 'bond_code',
            '转债名称': 'bond_name',
            '转债最新价': 'bond_price',
            '正股代码': 'stock_code',
            '正股名称': 'stock_name',
            '正股最新价': 'stock_price',
            '转股价': 'conversion_price',
            '强赎触发价': 'redemption_trigger_price',
            '回售触发价': 'put_trigger_price',
        }, inplace=True)

        # 选择我们需要的核心列
        required_cols = [
            'bond_code', 'bond_name', 'bond_price',
            'stock_code', 'stock_name', 'stock_price',
            'conversion_price', 'redemption_trigger_price', 'put_trigger_price'
        ]
        # 检查所需列是否存在，以防API变更
        for col in required_cols:
            if col not in df.columns:
                raise ValueError(f"Required column '{col}' is missing from ak.bond_cov_comparison() result.")
        
        final_df = df[required_cols]

        # 数据清洗和转换
        numeric_cols = ['bond_price', 'stock_price', 'conversion_price']
        for col in numeric_cols:
            final_df[col] = pd.to_numeric(final_df[col], errors='coerce')
        
        # 删除任何在核心数值列中包含NaN的行
        final_df.dropna(subset=numeric_cols, inplace=True)
        
        print("Successfully fetched and processed all bond data.")
        return final_df

    except Exception as e:
        print(f"[_get_all_bonds_list] FATAL ERROR: {e}")
        print(traceback.format_exc())
        return pd.DataFrame()


# --- 核心工具函数 ---

def find_bond_code_by_name(bond_name_query: str) -> List[Dict[str, str]]:
    """
    根据债券名称查找债券代码。
    
    Args:
        bond_name_query: 债券名称查询字符串（支持模糊匹配）
        
    Returns:
        匹配的债券列表，包含债券代码和名称
    """
    if not bond_name_query: 
        return []
    all_bonds_df = _get_all_bonds_list()
    if all_bonds_df.empty: 
        return []
    try:
        matched = all_bonds_df[all_bonds_df['bond_name'].str.contains(bond_name_query, case=False, na=False)]
        return matched[['bond_code', 'bond_name']].to_dict('records')
    except Exception as e:
        print(f"[find_bond_code_by_name] Error: {e}")
        return []


def get_convertible_bond_realtime_metrics(bond_codes: List[str]) -> Dict[str, Dict[str, Any]]:
    """
    获取指定可转债的实时指标。
    
    Args:
        bond_codes: 债券代码列表
        
    Returns:
        债券代码到指标字典的映射
    """
    if not bond_codes: 
        return {}
    all_bonds_df = _get_all_bonds_list()
    if all_bonds_df.empty: 
        return {}
    try:
        target_df = all_bonds_df[all_bonds_df['bond_code'].isin(bond_codes)].copy()
        if target_df.empty: 
            return {}

        target_df = target_df[target_df['conversion_price'] > 0].copy()
        target_df['conversion_value'] = (100 / target_df['conversion_price']) * target_df['stock_price']
        target_df['premium_rate'] = (target_df['bond_price'] / target_df['conversion_value']) - 1

        result = {}
        for _, row in target_df.iterrows():
            result[row['bond_code']] = {
                "bond_name": row['bond_name'],
                "bond_price": float(row['bond_price']),
                "stock_code": row['stock_code'],
                "stock_name": row['stock_name'],
                "stock_price": float(row['stock_price']),
                "conversion_price": float(row['conversion_price']),
                "conversion_value": float(row['conversion_value']),
                "premium_rate": float(row['premium_rate'])
            }
        return result
    except Exception as e:
        print(f"[get_convertible_bond_realtime_metrics] Error: {e}")
        return {}


def screen_discount_arbitrage_opportunities(min_discount_rate: float = -0.01) -> List[Dict[str, Any]]:
    """
    筛选折价套利机会。
    
    Args:
        min_discount_rate: 最小折价率阈值（负数表示折价）
        
    Returns:
        符合条件的债券列表
    """
    all_bonds_df = _get_all_bonds_list()
    if all_bonds_df.empty: 
        return []
    try:
        df = all_bonds_df[all_bonds_df['conversion_price'] > 0].copy()
        df['conversion_value'] = (100 / df['conversion_price']) * df['stock_price']
        df['premium_rate'] = (df['bond_price'] / df['conversion_value']) - 1
        
        # 增加诊断日志，用于分析溢价率分布
        print(f"[screen_discount_arbitrage_opportunities] Premium rate stats:\n{df['premium_rate'].describe()}")
        
        discount_df = df[df['premium_rate'] < min_discount_rate].copy()
        discount_df.sort_values(by='premium_rate', ascending=True, inplace=True)

        result = []
        for _, row in discount_df.iterrows():
            result.append({
                "bond_code": row['bond_code'],
                "bond_name": row['bond_name'],
                "bond_price": float(row['bond_price']),
                "stock_code": row['stock_code'],
                "stock_name": row['stock_name'],
                "stock_price": float(row['stock_price']),
                "conversion_price": float(row['conversion_price']),
                "conversion_value": float(row['conversion_value']),
                "premium_rate": float(row['premium_rate']),
                "discount_rate": float(-row['premium_rate'])
            })
        return result
    except Exception as e:
        print(f"[screen_discount_arbitrage_opportunities] Error: {e}")
        return []


def track_clause_triggers(bond_code: str) -> Dict[str, Any]:
    """
    跟踪指定债券的条款触发情况。

    Args:
        bond_code: 债券代码

    Returns:
        条款触发分析结果
    """
    if not bond_code:
        return {"error": "Bond code cannot be empty"}

    all_bonds_df = _get_all_bonds_list()
    if all_bonds_df.empty:
        return {"error": "Could not fetch bond data"}

    try:
        bond_info = all_bonds_df[all_bonds_df['bond_code'] == bond_code]
        if bond_info.empty:
            return {"error": f"Bond {bond_code} not found in current data"}

        info = bond_info.iloc[0]

        # 从我们的内部数据模型中获取数据
        stock_code_raw = str(info['stock_code'])
        redemption_price = pd.to_numeric(info['redemption_trigger_price'], errors='coerce')
        put_price = pd.to_numeric(info['put_trigger_price'], errors='coerce')

        if pd.isna(redemption_price) or pd.isna(put_price):
            return {"error": "Trigger prices not available for this bond."}

        end_date = datetime.now().strftime('%Y%m%d')
        start_date = (datetime.now() - timedelta(days=45)).strftime('%Y%m%d')

        # ak.stock_zh_a_hist 需要的是不带前缀的纯数字代码
        hist_df = ak.stock_zh_a_hist(symbol=stock_code_raw, period="daily", start_date=start_date, end_date=end_date, adjust="qfq")
        if hist_df.empty:
            return {"error": f"Could not fetch historical stock data for {stock_code_raw}."}

        last_30_close = hist_df['收盘'].tail(30)
        days_above = (last_30_close > redemption_price).sum()
        days_below = (last_30_close < put_price).sum()

        return {
            "bond_code": bond_code,
            "bond_name": info['bond_name'],
            "stock_code": stock_code_raw,
            "stock_name": info['stock_name'],
            "current_stock_price": float(info['stock_price']),
            "redemption_trigger_price": float(redemption_price),
            "days_above_redemption_price": int(days_above),
            "redemption_status": f"{int(days_above)}/15 days",
            "redemption_close_to_trigger": bool(days_above >= 12),
            "put_trigger_price": float(put_price),
            "days_below_put_price": int(days_below),
            "put_status": f"{int(days_below)}/30 days",
            "put_close_to_trigger": bool(days_below >= 24)
        }
    except Exception as e:
        return {"error": f"[track_clause_triggers] Error: {e}"}


def get_upcoming_convertible_bonds(days_ahead: int = 30) -> Dict[str, List[Dict[str, Any]]]:
    """
    获取未来一段时间内即将发行或可申购的可转债信息。

    Args:
        days_ahead: 向前查看的天数

    Returns:
        分类的即将发生的债券事件
    """
    results = {"未来上市": [], "即将申购": [], "即将配售登记": []}
    try:
        print("Fetching all bond overview data from ak.bond_zh_cov()...")
        df = ak.bond_zh_cov()
        if df.empty:
            return results

        # 重命名列以方便处理
        df.rename(columns={
            '债券代码': 'bond_code',
            '债券简称': 'bond_name',
            '申购日期': 'sub_date',
            '上市时间': 'list_date',
            '正股代码': 'stock_code',
            '正股简称': 'stock_name',
            '原股东配售-股权登记日': 'rec_date'  # 股权登记日 for rights issue
        }, inplace=True)

        today = datetime.now().date()
        future_date_limit = today + timedelta(days=days_ahead)

        # 统一处理日期列
        date_cols = ['sub_date', 'list_date', 'rec_date']
        for col in date_cols:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')

        # 1. 筛选未来上市
        upcoming_listing_df = df[
            df['list_date'].notna() &
            (df['list_date'].dt.date >= today) &
            (df['list_date'].dt.date <= future_date_limit)
        ].copy()

        for _, row in upcoming_listing_df.iterrows():
            results["未来上市"].append({
                "bond_code": row['bond_code'],
                "bond_name": row['bond_name'],
                "list_date": row['list_date'].strftime('%Y-%m-%d'),
                "stock_code": row.get('stock_code', ''),
                "stock_name": row.get('stock_name', '')
            })

        # 2. 筛选即将申购
        upcoming_sub_df = df[
            df['sub_date'].notna() &
            (df['sub_date'].dt.date >= today) &
            (df['sub_date'].dt.date <= future_date_limit)
        ].copy()

        for _, row in upcoming_sub_df.iterrows():
            results["即将申购"].append({
                "bond_code": row['bond_code'],
                "bond_name": row['bond_name'],
                "sub_date": row['sub_date'].strftime('%Y-%m-%d'),
                "stock_code": row.get('stock_code', ''),
                "stock_name": row.get('stock_name', '')
            })

        # 3. 筛选即将配售登记
        upcoming_rec_df = df[
            df['rec_date'].notna() &
            (df['rec_date'].dt.date >= today) &
            (df['rec_date'].dt.date <= future_date_limit)
        ].copy()

        for _, row in upcoming_rec_df.iterrows():
            results["即将配售登记"].append({
                "bond_code": row['bond_code'],
                "bond_name": row['bond_name'],
                "rec_date": row['rec_date'].strftime('%Y-%m-%d'),
                "stock_code": row.get('stock_code', ''),
                "stock_name": row.get('stock_name', '')
            })

        return results
    except Exception as e:
        print(f"[get_upcoming_convertible_bonds] Error: {e}")
        traceback.print_exc()
        return {"error": f"An error occurred: {e}"}


def monitor_intraday_spread(bond_code: str) -> Dict[str, Any]:
    """
    监控单个债券的日内价差。

    Args:
        bond_code: 债券代码

    Returns:
        债券的实时指标
    """
    if not bond_code:
        return {"error": "Bond code cannot be empty"}
    metrics = get_convertible_bond_realtime_metrics([bond_code])
    if bond_code in metrics:
        return metrics[bond_code]
    return {"error": f"Could not fetch intraday spread data for {bond_code}"}


def screen_for_special_opportunities(
    discount_threshold: float = -0.01,
    trigger_proximity_threshold: float = 0.8,
    redemption_clause_days: int = 15,
    put_clause_days: int = 30
) -> List[Dict[str, Any]]:
    """
    筛选市场上即将发生特殊事件且存在套利机会的可转债。

    Args:
        discount_threshold: 折价率筛选阈值，低于此值的债券被视为有套利机会。
                            例如-0.01代表折价率小于-1%。
        trigger_proximity_threshold: 条款"即将触发"的接近度阈值。
                                    例如0.8代表满足条件的天数达到了规定天数的80%。
        redemption_clause_days: 强赎条款要求的总天数（例如15天）。
        put_clause_days: 回售条款要求的总天数（例如30天）。

    Returns:
        符合所有条件的债券的详细信息列表。
    """
    print("Starting to screen for special opportunities...")
    all_bonds_df = _get_all_bonds_list()
    if all_bonds_df.empty:
        return []

    # --- 1. 筛选折价套利机会 ---
    print("Step 1: Screening for discount arbitrage opportunities...")
    df = all_bonds_df[all_bonds_df['conversion_price'] > 0].copy()
    df['conversion_value'] = (100 / df['conversion_price']) * df['stock_price']
    df['premium_rate'] = (df['bond_price'] / df['conversion_value']) - 1

    discount_bonds_df = df[df['premium_rate'] < discount_threshold].copy()
    if discount_bonds_df.empty:
        print("No bonds found with discount arbitrage opportunities.")
        return []

    print(f"Found {len(discount_bonds_df)} bonds with discount arbitrage opportunities.")

    # --- 2. 检查条款触发情况 ---
    print("Step 2: Checking clause trigger conditions...")
    special_opportunities = []

    end_date = datetime.now().strftime('%Y%m%d')
    start_date = (datetime.now() - timedelta(days=45)).strftime('%Y%m%d')

    for _, row in discount_bonds_df.iterrows():
        bond_code = row['bond_code']
        stock_code_raw = str(row['stock_code'])
        redemption_price = pd.to_numeric(row['redemption_trigger_price'], errors='coerce')
        put_price = pd.to_numeric(row['put_trigger_price'], errors='coerce')

        try:
            # 避免在循环中打印过多日志，只在出错时打印
            hist_df = ak.stock_zh_a_hist(symbol=stock_code_raw, period="daily", start_date=start_date, end_date=end_date, adjust="qfq")
            if hist_df.empty:
                continue

            last_30_close = hist_df['收盘'].tail(30)

            # 检查强赎
            is_upcoming_redemption = False
            days_above = 0
            if pd.notna(redemption_price):
                days_above = (last_30_close > redemption_price).sum()
                if days_above >= (redemption_clause_days * trigger_proximity_threshold):
                    is_upcoming_redemption = True

            # 检查回售
            is_upcoming_put = False
            days_below = 0
            if pd.notna(put_price):
                days_below = (last_30_close < put_price).sum()
                if days_below >= (put_clause_days * trigger_proximity_threshold):
                    is_upcoming_put = True

            # 如果有任何一个条款即将触发，则加入结果
            if is_upcoming_redemption or is_upcoming_put:
                special_opportunities.append({
                    "bond_code": bond_code,
                    "bond_name": row['bond_name'],
                    "bond_price": float(row['bond_price']),
                    "stock_code": stock_code_raw,
                    "stock_name": row['stock_name'],
                    "stock_price": float(row['stock_price']),
                    "conversion_price": float(row['conversion_price']),
                    "conversion_value": float(row['conversion_value']),
                    "premium_rate": float(row['premium_rate']),
                    "discount_rate": float(-row['premium_rate']),
                    "redemption_trigger_price": float(redemption_price) if pd.notna(redemption_price) else None,
                    "days_above_redemption": int(days_above),
                    "is_upcoming_redemption": is_upcoming_redemption,
                    "put_trigger_price": float(put_price) if pd.notna(put_price) else None,
                    "days_below_put": int(days_below),
                    "is_upcoming_put": is_upcoming_put,
                    "opportunity_type": "redemption" if is_upcoming_redemption else "put" if is_upcoming_put else "discount"
                })

        except Exception as e:
            print(f"Error processing {bond_code}: {e}")
            continue

    print(f"Found {len(special_opportunities)} special opportunities.")
    return special_opportunities
