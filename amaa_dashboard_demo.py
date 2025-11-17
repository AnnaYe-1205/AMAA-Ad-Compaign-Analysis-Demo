import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os

# 页面配置
st.set_page_config(
    page_title="营销效果分析平台",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 添加CSS样式
st.markdown("""
<style>
    /* 指标卡片样式 */
    .metric-card {
        padding: 15px;
        margin: 8px 0;
        border-radius: 10px;
        border-left: 5px solid;
        background: white;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        height: 120px;
    }
    
    .metric-above {
        border-left-color: #28a745;
        background: linear-gradient(135deg, #e8f5e8 0%, #c8e6c9 100%);
    }
    
    .metric-below {
        border-left-color: #dc3545;
        background: linear-gradient(135deg, #ffebee 0%, #ffcdd2 100%);
    }
</style>
""", unsafe_allow_html=True)

# 加载默认数据
@st.cache_data
def load_default_data():
    """加载默认数据"""
    try:
        if os.path.exists('amaa_demo_data.csv'):
            encodings = ['utf-8', 'gbk', 'gb2312', 'latin1']
            for encoding in encodings:
                try:
                    df = pd.read_csv('amaa_demo_data.csv', encoding=encoding)
                    # 确保日期格式正确
                    date_columns = [col for col in df.columns if '日期' in col or 'date' in col.lower()]
                    if date_columns:
                        df[date_columns[0]] = pd.to_datetime(df[date_columns[0]]).dt.strftime('%Y-%m-%d')
                    return df
                except:
                    continue
            return pd.read_csv('amaa_demo_data.csv', encoding='utf-8', errors='ignore')
        else:
            dates = pd.date_range(start='2024-01-01', end='2024-03-31', freq='D')
            data = {
                '日期': [date.strftime('%Y-%m-%d') for date in dates],
                '抖音_koc': np.random.randint(1000, 5000, len(dates)),
                '抖音_kol': np.random.randint(800, 4000, len(dates)),
                '微博_koc': np.random.randint(600, 3000, len(dates)),
                '微博_kol': np.random.randint(500, 2500, len(dates)),
                '销售额': np.random.randint(5000, 20000, len(dates)),
                '转化率': np.random.uniform(0.01, 0.05, len(dates)),
                '新用户数': np.random.randint(50, 300, len(dates))
            }
            df = pd.DataFrame(data)
            df.to_csv('amaa_demo_data.csv', index=False, encoding='utf-8')
            return df
    except Exception as e:
        return pd.DataFrame()

# 处理上传的文件 - 添加缓存和清理机制
@st.cache_data(ttl=3600)
def process_uploaded_file(uploaded_file):
    """处理上传的文件"""
    try:
        if uploaded_file.name.endswith('.csv'):
            encodings = ['utf-8', 'gbk', 'gb2312', 'latin1']
            for encoding in encodings:
                try:
                    uploaded_file.seek(0)
                    df = pd.read_csv(uploaded_file, encoding=encoding)
                    # 确保日期格式正确
                    date_columns = [col for col in df.columns if '日期' in col or 'date' in col.lower()]
                    if date_columns:
                        df[date_columns[0]] = pd.to_datetime(df[date_columns[0]]).dt.strftime('%Y-%m-%d')
                    return df
                except:
                    continue
            uploaded_file.seek(0)
            return pd.read_csv(uploaded_file, encoding='utf-8', errors='ignore')
        elif uploaded_file.name.endswith('.xlsx'):
            df = pd.read_excel(uploaded_file)
            # 确保日期格式正确
            date_columns = [col for col in df.columns if '日期' in col or 'date' in col.lower()]
            if date_columns:
                df[date_columns[0]] = pd.to_datetime(df[date_columns[0]]).dt.strftime('%Y-%m-%d')
            return df
    except:
        return None

def generate_unified_effect_data(targets, features, delays, date_range_key, control_vars):
    """生成统一的效应数据，确保趋势图和指标数据一致"""
    unified_data = {}
    
    # 为每个特征-目标组合生成独立的影响因子 (±15%)
    influence_factors = {}
    for target in targets:
        influence_factors[target] = {}
        for feature in features:
            # 基于特征、目标和控制变量生成独立的影响因子
            seed_value = hash(feature + target + date_range_key + '_'.join(control_vars)) % 10000
            np.random.seed(seed_value)
            # 生成0.85到1.15之间的随机影响因子
            influence_factor = 0.85 + np.random.random() * 0.3
            influence_factors[target][feature] = influence_factor
    
    # 生成基础数据
    base_data = {}
    for target in targets:
        base_data[target] = {}
        for feature in features:
            # 使用统一的随机种子
            seed_value = hash(feature + target + date_range_key) % 10000
            np.random.seed(seed_value)
            
            # 1. 先生成基础趋势数据
            base_trend = np.random.uniform(0.5, 2.5, len(delays))
            
            # 2. 基于趋势数据计算基础ROI（趋势的平均值加上一些随机波动）
            trend_mean = np.mean(base_trend)
            base_roi = trend_mean * np.random.uniform(0.8, 1.2)
            
            # 3. 基于趋势数据和ROI生成贡献值（保持合理的比例关系）
            base_contribution = (trend_mean / 2.5) * 30  # 将趋势值映射到5-30的范围
            
            # 确保贡献值在合理范围内
            base_contribution = max(5, min(30, base_contribution))
            
            # 应用控制变量影响 - 每个特征目标组合使用独立的影响因子
            influence_factor = influence_factors[target][feature]
            adjusted_roi = base_roi * influence_factor
            adjusted_contribution = base_contribution * influence_factor
            adjusted_trend = base_trend * influence_factor
            
            base_data[target][feature] = {
                'roi': adjusted_roi,
                'contribution': adjusted_contribution,
                'trend': adjusted_trend
            }
    
    # 调整贡献度确保每个目标的总贡献不超过100%
    for target in targets:
        total_contribution = sum(base_data[target][feature]['contribution'] for feature in features)
        if total_contribution > 100:
            scale_factor = 100 / total_contribution
            for feature in features:
                base_data[target][feature]['contribution'] *= scale_factor
    
    # 构建返回数据格式
    unified_data['metrics'] = {}
    unified_data['simulation'] = {}
    
    for feature in features:
        unified_data['metrics'][feature] = {}
        for target in targets:
            unified_data['metrics'][feature][target] = {
                'roi': base_data[target][feature]['roi'],
                'contribution': base_data[target][feature]['contribution']
            }
    
    for target in targets:
        unified_data['simulation'][target] = {}
        for feature in features:
            unified_data['simulation'][target][feature] = base_data[target][feature]['trend']
    
    return unified_data


def show_history_analysis():
    """显示历史效果分析页面"""
    st.title("📊 历史投放效果分析")
    
    # 初始化上传状态
    if 'upload_expanded' not in st.session_state:
        st.session_state.upload_expanded = False
    if 'current_file_name' not in st.session_state:
        st.session_state.current_file_name = None
    
    # 根据当前使用的数据源设置expander标题
    expander_title = "📁 上传数据文件"
    if st.session_state.current_file_name:
        expander_title = f"📁 {st.session_state.current_file_name}"
    else:
        expander_title = "📁 默认数据文件"
    
    # 数据上传 - 使用expander
    with st.expander(expander_title, expanded=st.session_state.upload_expanded):
        uploaded_file = st.file_uploader("选择文件", type=['csv', 'xlsx'])
        
        if uploaded_file is not None:
            # 如果上传了新文件，处理数据
            if uploaded_file.name != st.session_state.current_file_name:
                with st.spinner('正在处理上传的数据...'):
                    processed_data = process_uploaded_file(uploaded_file)
                    if processed_data is not None:
                        st.session_state.current_data = processed_data
                        st.session_state.current_file_name = uploaded_file.name
                        st.session_state.upload_expanded = False
                        st.success(f"已上传文件: {uploaded_file.name}")
                        st.rerun()
        else:
            if st.session_state.current_file_name is None:
                st.info("使用默认数据")
            else:
                st.info(f"当前使用: {st.session_state.current_file_name}")
    
    # 侧边栏筛选配置
    st.sidebar.markdown("---")
    st.sidebar.header("模型配置")
    
    # 日期选择
    if not st.session_state.current_data.empty:
        date_columns = [col for col in st.session_state.current_data.columns 
                       if '日期' in col or 'date' in col.lower()]
        
        if date_columns:
            date_col = date_columns[0]
            try:
                # 确保数据中的日期是datetime类型用于过滤
                if not pd.api.types.is_datetime64_any_dtype(st.session_state.current_data[date_col]):
                    st.session_state.current_data[date_col] = pd.to_datetime(st.session_state.current_data[date_col])
                
                min_date = st.session_state.current_data[date_col].min().date()
                max_date = st.session_state.current_data[date_col].max().date()
                
                selected_dates = st.sidebar.date_input(
                    "选择日期范围",
                    value=(min_date, max_date),
                    min_value=min_date,
                    max_value=max_date
                )
                
                if len(selected_dates) == 2:
                    start_date, end_date = selected_dates
                    # 使用datetime类型进行过滤
                    filtered_data = st.session_state.current_data[
                        (st.session_state.current_data[date_col].dt.date >= start_date) & 
                        (st.session_state.current_data[date_col].dt.date <= end_date)
                    ].copy()
                    
                    # 将过滤后的数据格式化为字符串显示
                    filtered_data_display = filtered_data.copy()
                    filtered_data_display[date_col] = filtered_data_display[date_col].dt.strftime('%Y-%m-%d')
                    
                    # 创建日期范围key用于效应值刷新
                    date_range_key = f"{start_date}_{end_date}"
                else:
                    filtered_data = st.session_state.current_data
                    filtered_data_display = st.session_state.current_data.copy()
                    filtered_data_display[date_col] = filtered_data_display[date_col].dt.strftime('%Y-%m-%d')
                    date_range_key = "default"
                    
            except Exception as e:
                filtered_data = st.session_state.current_data
                filtered_data_display = st.session_state.current_data
                date_range_key = "default"
        else:
            filtered_data = st.session_state.current_data
            filtered_data_display = st.session_state.current_data
            date_range_key = "default"
    else:
        filtered_data = pd.DataFrame()
        filtered_data_display = pd.DataFrame()
        date_range_key = "default"
    
    # 研究周期选择
    granularity = st.sidebar.selectbox("数据颗粒度", ["日", "周"])
    
    # 研究时延周期选择
    if granularity == "日":
        max_delay = 30
        delay_options = list(range(1, max_delay + 1))
    else:
        max_delay = 12
        delay_options = list(range(1, max_delay + 1))
    
    selected_delays = st.sidebar.multiselect(
        f"研究时延周期选择 ({granularity})",
        options=delay_options,
        default=delay_options[:3] if delay_options else []
    )
    
    # 研究特征筛选
    if not filtered_data.empty:
        exclude_cols = [col for col in filtered_data.columns if '日期' in col or 'date' in col.lower()]
        feature_options = [col for col in filtered_data.columns if col not in exclude_cols]
        
        selected_features = st.sidebar.multiselect(
            "研究特征筛选",
            options=feature_options,
            default=feature_options[:3] if len(feature_options) >= 3 else feature_options
        )
        
        # 研究控制变量
        control_options = [col for col in filtered_data.columns if col not in exclude_cols and col not in selected_features]
        selected_controls = st.sidebar.multiselect(
            "研究控制变量",
            options=control_options,
            default=[]
        )
        
        # 研究目标值选择 - 默认选择倒数两个列
        target_options = [col for col in filtered_data.columns if col not in exclude_cols and col not in selected_features and col not in selected_controls]
        default_targets = target_options[-2:] if len(target_options) >= 2 else target_options
        
        selected_targets = st.sidebar.multiselect(
            "研究目标值选择",
            options=target_options,
            default=default_targets
        )
    else:
        selected_features = []
        selected_controls = []
        selected_targets = []
    
    # 主布局
    col1, col2 = st.columns([3, 2])
    
    with col1:
        # 数据预览容器
        with st.container():
            # 使用列布局在标题右侧紧凑排列
            col_title, col_help = st.columns([8, 1])
            with col_title:
                st.subheader("数据预览")
            with col_help:
                st.markdown("""
                <div style="text-align: right; margin-top: 25px;">
                    <span title="数据要求：日期列、投放载体列（颗粒度一致）、总投放量、目标值列（与投放颗粒度一致）">ℹ️</span>
                </div>
                """, unsafe_allow_html=True)
            
            if not filtered_data_display.empty:
                # 确定要显示的列，按正确顺序：日期列 > 目标值 > 控制变量 > 研究特征
                display_columns = []
                
                # 1. 日期列（最前）
                date_columns = [col for col in filtered_data_display.columns if '日期' in col or 'date' in col.lower()]
                if date_columns:
                    display_columns.append(date_columns[0])
                
                # 2. 研究目标值
                display_columns.extend(selected_targets)
                
                # 3. 研究控制变量
                display_columns.extend(selected_controls)
                
                # 4. 研究特征筛选（最后）
                display_columns.extend(selected_features)
                
                # 去重并确保列存在
                display_columns = [col for col in display_columns if col in filtered_data_display.columns]
                
                # 只显示选中的列
                if display_columns:
                    st.dataframe(filtered_data_display[display_columns], height=200, use_container_width=True)
                else:
                    st.info("请选择要显示的列")
        
        # 效应值趋势图容器
        with st.container():
            st.subheader("效应值趋势图")
            if not filtered_data.empty and selected_targets and selected_features and selected_delays:
                # 生成统一的效应数据
                unified_effect_data = generate_unified_effect_data(
                    selected_targets, selected_features, selected_delays, 
                    date_range_key, selected_controls
                )
                
                simulation_data = unified_effect_data['simulation']
                
                # 固定高度的容器
                with st.container(height=400):
                    for target in selected_targets:
                        st.write(f"**{target}**")
                        fig = go.Figure()
                        
                        for feature in selected_features:
                            y_values = simulation_data[target][feature]
                            
                            fig.add_trace(go.Scatter(
                                x=[f"{delay}{'天' if granularity == '日' else '周'}" for delay in selected_delays],
                                y=y_values,
                                mode='lines+markers',
                                name=feature,
                                line=dict(width=2)
                            ))
                        
                        fig.update_layout(
                            height=350,
                            xaxis_title=f"研究周期 ({granularity})",
                            yaxis_title="效应值",
                            yaxis_range=[0, 3],
                            showlegend=True,
                            margin=dict(l=0, r=0, t=20, b=0)
                        )
                        
                        st.plotly_chart(fig, use_container_width=True, key=f"chart_{target}_{date_range_key}")
    
    with col2:
        # 效应值指标容器
        with st.container():
            st.subheader("📈 效应值指标")
            if not filtered_data.empty and selected_targets and selected_features:
                # 生成统一的效应数据
                unified_effect_data = generate_unified_effect_data(
                    selected_targets, selected_features, selected_delays, 
                    date_range_key, selected_controls
                )
                
                effect_metrics = unified_effect_data['metrics']
                
                # 先计算每个目标在所有特征上的平均值
                target_avg_values = {}
                for target in selected_targets:
                    target_roi_values = [effect_metrics[feature][target]['roi'] for feature in selected_features]
                    target_contrib_values = [effect_metrics[feature][target]['contribution'] for feature in selected_features]
                    target_avg_values[target] = {
                        'roi': np.mean(target_roi_values),
                        'contribution': np.mean(target_contrib_values)
                    }
                
                # 可滚动容器
                with st.container(height=680):
                    for feature in selected_features:
                        # 特征标题
                        st.markdown(f"### {feature}")
                        
                        # 为每个目标创建两列布局：ROI和贡献分开
                        for target in selected_targets:
                            roi_value = effect_metrics[feature][target]['roi']
                            contribution = effect_metrics[feature][target]['contribution']
                            
                            # 获取该目标的平均值
                            target_avg_roi = target_avg_values[target]['roi']
                            target_avg_contribution = target_avg_values[target]['contribution']
                            
                            # 创建两列布局
                            col_roi, col_contribution = st.columns(2)
                            
                            with col_roi:
                                # ROI指标卡片
                                is_above_avg_roi = roi_value > target_avg_roi
                                card_class = "metric-above" if is_above_avg_roi else "metric-below"
                                
                                st.markdown(f"""
                                <div class="metric-card {card_class}">
                                    <div style="font-size: 14px; font-weight: bold;">
                                        {target} ROI
                                    </div>
                                    <div style="font-size: 20px; font-weight: bold; margin: 8px 0;">{roi_value:.2f}</div>
                                    <div style="font-size: 12px;">目标平均: {target_avg_roi:.2f}</div>
                                </div>
                                """, unsafe_allow_html=True)
                            
                            with col_contribution:
                                # 贡献指标卡片
                                is_above_avg_contrib = contribution > target_avg_contribution
                                card_class = "metric-above" if is_above_avg_contrib else "metric-below"
                                
                                st.markdown(f"""
                                <div class="metric-card {card_class}">
                                    <div style="font-size: 14px; font-weight: bold;">
                                        {target} 贡献
                                    </div>
                                    <div style="font-size: 20px; font-weight: bold; margin: 8px 0;">{contribution:.1f}%</div>
                                    <div style="font-size: 12px;">目标平均: {target_avg_contribution:.1f}%</div>
                                </div>
                                """, unsafe_allow_html=True)
                        
                        st.markdown("---")

def show_future_simulation():
    """显示未来效果模拟页面"""
    st.title("🔮 未来投放效果模拟")
    
    # 数据准备阶段
    def prepare_simulation_data():
        """从第一页获取原始数据，独立计算第二页需要的统计信息"""
        raw_data = st.session_state.current_data.copy()
        
        # 排除日期列
        exclude_cols = [col for col in raw_data.columns if '日期' in col or 'date' in col.lower()]
        available_columns = [col for col in raw_data.columns if col not in exclude_cols]
        
        # 计算所有可用列的统计信息
        stats = {}
        for column in available_columns:
            col_data = raw_data[column]
            stats[column] = {
                'min': float(col_data.min()),
                'max': float(col_data.max()),
                'mean': float(col_data.mean()),
                'std': float(col_data.std())
            }
        
        return {
            'raw_data': raw_data,
            'available_columns': available_columns,
            'stats': stats
        }
    
    # 侧边栏配置
    st.sidebar.markdown("---")
    st.sidebar.header("模拟配置")
    
    prepared_data = prepare_simulation_data()
    available_columns = prepared_data['available_columns']
    stats = prepared_data['stats']
    
    # 数据颗粒度选择
    granularity = st.sidebar.selectbox("数据颗粒度", ["日", "周"])
    
    # 收割目标值选择
    selected_targets = st.sidebar.multiselect(
        "收割目标值选择",
        options=available_columns,
        default=available_columns[-1:] if available_columns else [],
        help="选择要优化的目标指标"
    )
    
    # 收割周期选择
    if granularity == "日":
        max_harvest = 30
        harvest_options = list(range(1, max_harvest + 1))
    else:
        max_harvest = 12
        harvest_options = list(range(1, max_harvest + 1))
    
    selected_harvest = st.sidebar.selectbox(
        f"收割周期 ({granularity})",
        options=harvest_options,
        index=2 if len(harvest_options) > 2 else 0
    )
    
    # 投放载体选择
    available_features = [col for col in available_columns if col not in selected_targets]
    selected_features = st.sidebar.multiselect(
        "投放载体",
        options=available_features,
        default=available_features[:3] if len(available_features) >= 3 else available_features,
        help="选择可调整投入的投放渠道"
    )
    
    # 最大预算设置
    reference_budget = 0
    if selected_features:
        reference_budget = sum(stats[feature]['mean'] for feature in selected_features)

    max_budget = st.sidebar.number_input(
        "最大预算",
        min_value=0.0,
        value=float(reference_budget),  # 默认值为选中投放载体历史均值的总和
        step=1000.0,
        help=f"投放载体总投入上限（参考值: {reference_budget:.2f}）"
    )
    
    # 主页面布局
    if not selected_features or not selected_targets:
        st.warning("请先在侧边栏选择投放载体和收割目标值")
        return
    
    # 生成模拟数据函数 - 不依赖selected_targets
    def generate_simulation_table(selected_features, cost_ranges, stats, n_rows=5):
        """生成投放组合推荐数据"""
        import random
        
        # 使用不依赖selected_targets的随机种子
        config_key = f"{granularity}_{selected_harvest}_{str(sorted(selected_features))}_{str(cost_ranges)}"
        seed_value = hash(config_key) % 10000
        random.seed(seed_value)
        
        simulation_data = []
        
        # 生成所有可用列的数据（包括可能成为目标值的列）
        for i in range(n_rows):
            row = {}
            
            # 为所有可用列生成数据（0到历史最大值的随机数）
            for column in available_columns:
                column_max = stats[column]['max']
                row[column] = random.uniform(0, column_max)
            
            # 覆盖投放载体数据（在成本范围内的随机数）
            for feature in selected_features:
                min_cost, max_cost = cost_ranges[feature]
                row[feature] = random.uniform(min_cost, max_cost)
            
            simulation_data.append(row)
        
        # 转换为DataFrame
        df = pd.DataFrame(simulation_data)
        
        return df.reset_index(drop=True)
    
    # 创建两列布局
    left_col, right_col = st.columns([1, 2])
    
    # 载体投放预算部分
    with left_col:
        # 载体投放预算容器
        with st.container():
            st.subheader("💰 载体投放预算")
            
            # 固定高度的容器
            with st.container(height=700):
                cost_ranges = {}
                
                for feature in selected_features:
                    st.markdown(f"**{feature}**")
                    
                    # 获取该投放载体的统计信息
                    feature_stats = stats[feature]
                    min_val = feature_stats['min']
                    max_val = feature_stats['max']
                    mean_val = feature_stats['mean']
                    
                    # 创建投入滑块
                    cost_range = st.slider(
                        f"投入范围",
                        min_value=0.0,
                        max_value=float(max_val),
                        value=(0.0, float(mean_val)),
                        key=f"slider_{feature}",
                        help=f"{feature}投入范围: {min_val:.2f} - {max_val:.2f}"
                    )
                    
                    cost_ranges[feature] = cost_range
                    
                    # 只展示历史均值，紧凑显示
                    st.caption(f"📈 历史均值: {mean_val:.1f}")
                    st.markdown("<div style='margin-top: 5px; margin-bottom: 5px;'>", unsafe_allow_html=True)
                    st.divider()
                    st.markdown("</div>", unsafe_allow_html=True)
    
    with right_col:
        # 生成模拟数据 - 不依赖selected_targets
        simulation_df = generate_simulation_table(selected_features, cost_ranges, stats)
        
        # 创建显示数据（排序后）- 统一数据源
        display_columns = selected_targets + selected_features
        display_df = simulation_df[display_columns].copy()
        
        # 按所有目标值的均值从大到小排序（如果选择了目标值）
        if selected_targets:
            display_df['targets_mean'] = display_df[selected_targets].mean(axis=1)
            display_df = display_df.sort_values(by='targets_mean', ascending=False)
            display_df = display_df.drop('targets_mean', axis=1)
        
        # 上部分：目标值仪表盘 - 使用排序后数据
        with st.container():
            st.subheader("📈 目标值仪表盘")
            
            # 紧凑的仪表盘容器
            with st.container(height=300):
                if len(selected_targets) > 0:
                    # 根据目标值数量动态调整列数
                    n_targets = len(selected_targets)
                    cols = st.columns(n_targets)
                    
                    for idx, target in enumerate(selected_targets):
                        with cols[idx]:
                            # 获取目标值的统计信息
                            target_stats = stats[target]
                            target_min = target_stats['min']
                            target_max = target_stats['max']
                            target_mean = target_stats['mean']
                            
                            # 使用排序后数据的第一行 - 确保与表格一致
                            current_value = display_df[target].iloc[0]
                            
                            # 计算提升幅度
                            improvement = ((current_value - target_mean) / target_mean) * 100
                            
                            # 根据与均值的比较确定颜色和箭头
                            if current_value >= target_mean:
                                color = "green"
                                arrow = "▲"
                                improvement_text = f"+{improvement:.1f}%"
                            else:
                                color = "red"
                                arrow = "▼"
                                improvement_text = f"{improvement:.1f}%"
                            
                            # 创建紧凑的油表盘
                            fig = go.Figure(go.Indicator(
                                mode="gauge+number",
                                value=current_value,
                                domain={'x': [0, 1], 'y': [0, 1]},
                                title={'text': f"{target} {arrow}", 'font': {'size': 12, 'color': color}},
                                gauge={
                                    'axis': {'range': [target_min, target_max]},
                                    'bar': {'color': color},
                                    'steps': [
                                        {'range': [target_min, current_value], 'color': "lightgreen" if current_value >= target_mean else "lightcoral"},
                                        {'range': [current_value, target_max], 'color': "lightgray"}
                                    ],
                                    'threshold': {
                                        'line': {'color': "red", 'width': 3},
                                        'thickness': 0.6,
                                        'value': target_mean
                                    }
                                },
                                number={'font': {'size': 16, 'color': color}}
                            ))
                            
                            # 增加上边距，给标题更多空间
                            fig.update_layout(
                                height=180,
                                margin=dict(t=50, b=10, l=10, r=10)
                            )
                            
                            st.plotly_chart(fig, use_container_width=True)
                            
                            # 显示提升幅度 - 与油表同宽且有底色
                            st.markdown(
                                f"""
                                <div style="
                                    background-color: #f0f2f6; 
                                    padding: 8px; 
                                    border-radius: 8px; 
                                    text-align: center;
                                    margin: 0px;
                                    font-size: 14px;
                                    color: {color};
                                    font-weight: bold;
                                ">
                                    📈 提升幅度: {improvement_text}
                                </div>
                                """, 
                                unsafe_allow_html=True
                            )
                else:
                    st.info("请选择至少一个收割目标值")
        
        # 下部分：投放组合推荐 - 使用同一份排序后数据
        with st.container():
            st.subheader("🏆 投放组合推荐 Top 5")
            
            # 固定高度的容器
            with st.container(height=325):
                if len(display_df) > 0:
                    # 计算每行的总投入
                    row_costs = []
                    for idx, row in display_df.iterrows():
                        row_cost = sum(row[feature] for feature in selected_features)
                        row_costs.append(row_cost)
                    
                    # 取最大行投入作为总投入参考
                    max_row_cost = max(row_costs)
                    
                    # 预算状态显示
                    if max_row_cost > max_budget:
                        st.error(f"⚠️ 最大行投入超过预算！ (最大行投入: {max_row_cost:.2f} > 最大预算: {max_budget:.2f})")
                    else:
                        st.success(f"✅ 所有行投入都在预算内 (最大行投入: {max_row_cost:.2f} ≤ 最大预算: {max_budget:.2f})")
                    
                    # 创建可编辑的数据框
                    edited_df = st.data_editor(
                        display_df,
                        use_container_width=True,
                        height=225,
                        num_rows="fixed"
                    )
                    
                    # 如果用户编辑了数据，重新计算预算
                    if not edited_df.equals(display_df):
                        edited_row_costs = []
                        for idx, row in edited_df.iterrows():
                            row_cost = sum(row[feature] for feature in selected_features)
                            edited_row_costs.append(row_cost)
                        
                        edited_max_cost = max(edited_row_costs)
                        if edited_max_cost > max_budget:
                            st.error(f"⚠️ 编辑后最大行投入超过预算！ (最大行投入: {edited_max_cost:.2f} > 最大预算: {max_budget:.2f})")
                        else:
                            st.success(f"✅ 编辑后所有行投入都在预算内 (最大行投入: {edited_max_cost:.2f} ≤ 最大预算: {max_budget:.2f})")
                else:
                    st.info("暂无推荐数据")


def show_optimization_recommendation():
    """显示最优投放组合推荐页面"""
    st.title("🎯 最优投放组合推荐")
    
    # 添加CSS样式
    st.markdown("""
    <style>
    .stats-card-positive {
        background: linear-gradient(135deg, #a8e6cf 0%, #dcedc1 100%);
        color: #2e7d32;
        border-radius: 10px;
        padding: 20px;
        border: 1px solid #c8e6c9;
        text-align: center;
        width: 100%;
        height: 100%;  /* 关键：让卡片高度100% */
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        box-sizing: border-box;
    }
    .stats-title {
        font-size: 14px;
        font-weight: bold;
        margin-bottom: 8px;
        opacity: 0.9;
        text-align: center;
        width: 100%;
    }
    .stats-value {
        font-size: 20px;
        font-weight: bold;
        margin-bottom: 5px;
        text-align: center;
        width: 100%;
    }
    .stats-change {
        font-size: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 4px;
        text-align: center;
        width: 100%;
        color: #2e7d32;
    }
    /* 确保油表容器也填满高度 */
    [data-testid="stVerticalBlock"] {
        height: 100%;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # 数据准备阶段
    def prepare_simulation_data():
        """从第一页获取原始数据，独立计算统计信息"""
        raw_data = st.session_state.current_data.copy()
        
        # 排除日期列
        exclude_cols = [col for col in raw_data.columns if '日期' in col or 'date' in col.lower()]
        available_columns = [col for col in raw_data.columns if col not in exclude_cols]
        
        # 计算所有可用列的统计信息
        stats = {}
        for column in available_columns:
            col_data = raw_data[column]
            stats[column] = {
                'min': float(col_data.min()),
                'max': float(col_data.max()),
                'mean': float(col_data.mean()),
                'std': float(col_data.std()),
                'q75': float(col_data.quantile(0.75))  # 75%分位数
            }
        
        return {
            'raw_data': raw_data,
            'available_columns': available_columns,
            'stats': stats
        }
    
    # 侧边栏配置
    st.sidebar.markdown("---")
    st.sidebar.header("优化配置")
    
    prepared_data = prepare_simulation_data()
    available_columns = prepared_data['available_columns']
    stats = prepared_data['stats']
    
    # 数据颗粒度选择
    granularity = st.sidebar.selectbox("数据颗粒度", ["日", "周"])
    
    # 收割目标值选择
    selected_targets = st.sidebar.multiselect(
        "收割目标值选择",
        options=available_columns,
        default=available_columns[-1:] if available_columns else [],
        help="选择要优化的目标指标"
    )
    
    # 收割周期选择
    if granularity == "日":
        max_harvest = 30
        harvest_options = list(range(1, max_harvest + 1))
    else:
        max_harvest = 12
        harvest_options = list(range(1, max_harvest + 1))
    
    selected_harvest = st.sidebar.selectbox(
        f"收割周期 ({granularity})",
        options=harvest_options,
        index=4 if len(harvest_options) > 4 else 0
    )
    
    # 投放载体选择
    available_features = [col for col in available_columns if col not in selected_targets]
    selected_features = st.sidebar.multiselect(
        "投放载体",
        options=available_features,
        default=available_features[:3] if len(available_features) >= 3 else available_features,
        help="选择可调整投入的投放渠道"
    )
    
    # 全域投放量限制
    reference_total = 0
    if selected_features:
        reference_total = sum(stats[feature]['mean'] for feature in selected_features) * 1.2
    
    global_limit = st.sidebar.number_input(
        f"全域投放量限制 ({granularity})",
        min_value=0.0,
        value=float(reference_total),
        step=1000.0,
        help=f"全域总投放量上限（参考值: {reference_total:.2f}）"
    )
    
    # 主页面布局
    if not selected_features or not selected_targets:
        st.warning("请先在侧边栏选择投放载体和收割目标值")
        return
    
    # 生成最优投放组合数据
    def generate_optimization_table(selected_targets, selected_features, stats, harvest_period, global_limit):
        """生成最优投放组合数据"""
        import random
        
        # 使用固定随机种子
        seed_value = hash(str(sorted(selected_targets)) + str(sorted(selected_features)) + str(harvest_period)) % 10000
        random.seed(seed_value)
        
        optimization_data = []
        
        for period in range(1, harvest_period + 1):
            row = {'投放顺序': f'第{period}{"天" if granularity == "日" else "周"}'}
            
            # 生成投放载体数据（总和必须小于全域投放量限制）
            total_platform_cost = 0
            platform_costs = {}
            
            # 首先生成各个投放载体的成本
            for feature in selected_features:
                feature_max = stats[feature]['max']
                # 生成0到历史最大值的随机数
                cost = random.uniform(0, feature_max)
                platform_costs[feature] = cost
            
            # 计算总成本并调整比例
            current_total = sum(platform_costs.values())
            if current_total > 0:
                # 调整比例，确保总成本在合理范围内
                scale_factor = min(1.0, global_limit / current_total * random.uniform(0.8, 1.0))
                for feature in platform_costs:
                    platform_costs[feature] *= scale_factor
            
            # 添加投放载体数据到行
            for feature, cost in platform_costs.items():
                row[feature] = cost
            
            # 计算实际总投放量
            actual_total = sum(platform_costs.values())
            row['全域投放量限制'] = actual_total
            
            # 生成目标值数据（不低于75%分位数）
            for target in selected_targets:
                target_q75 = stats[target]['q75']
                target_max = stats[target]['max']
                # 生成不低于75%分位数的随机数
                target_value = random.uniform(target_q75, target_max)
                row[f'{target}_预计'] = target_value
            
            optimization_data.append(row)
        
        # 转换为DataFrame
        df = pd.DataFrame(optimization_data)
        
        return df
    
    # 生成最优投放组合数据
    optimization_df = generate_optimization_table(selected_targets, selected_features, stats, selected_harvest, global_limit)
    
    # 创建主布局：上半部分1/2，下半部分1/2
    top_col1, top_col2 = st.columns([1, 1])

    # 左上角1/4：KPI油表
    with top_col1:
        with st.container():
            st.subheader("📊 KPI指标仪表盘")
            
            # 使用固定高度的容器
            with st.container(height=225):
                if len(selected_targets) > 0:
                    # 根据目标值数量动态调整列数 - 关键修改！
                    n_targets = len(selected_targets)
                    cols = st.columns(n_targets)
                    
                    for idx, target in enumerate(selected_targets):
                        with cols[idx]:
                            target_stats = stats[target]
                            target_min = target_stats['min']
                            target_max = target_stats['max']
                            target_mean = target_stats['mean']
                            
                            current_value = optimization_df[f'{target}_预计'].mean()
                            improvement = ((current_value - target_mean) / target_mean) * 100
                            
                            if current_value >= target_mean:
                                color = "green"
                                arrow = "▲"
                                improvement_text = f"+{improvement:.1f}%"
                            else:
                                color = "red"
                                arrow = "▼"
                                improvement_text = f"{improvement:.1f}%"
                            
                            # 创建紧凑的油表盘
                            fig = go.Figure(go.Indicator(
                                mode="gauge+number",
                                value=current_value,
                                domain={'x': [0, 1], 'y': [0, 1]},
                                title={'text': f"{target} {arrow}", 'font': {'size': 12, 'color': color}},
                                gauge={
                                    'axis': {'range': [target_min, target_max]},
                                    'bar': {'color': color},
                                    'steps': [
                                        {'range': [target_min, current_value], 'color': "lightgreen" if current_value >= target_mean else "lightcoral"},
                                        {'range': [current_value, target_max], 'color': "lightgray"}
                                    ],
                                    'threshold': {
                                        'line': {'color': "red", 'width': 3},
                                        'thickness': 0.6,
                                        'value': target_mean
                                    }
                                },
                                number={'font': {'size': 16, 'color': color}}
                            ))
                            
                            fig.update_layout(
                                height=180,
                                margin=dict(t=50, b=10, l=10, r=10)
                            )
                            
                            st.plotly_chart(fig, use_container_width=True)

    # 右上角1/4：投放效果统计摘要
    with top_col2:
        with st.container():
            st.subheader("📈 投放效果统计摘要")
            
            # 使用固定高度的容器
            with st.container(height=225):
                if len(selected_targets) > 0:
                    # 根据目标值数量动态调整列数 - 关键修改！
                    n_targets = len(selected_targets)
                    cols = st.columns(n_targets)
                    
                    for idx, target in enumerate(selected_targets):
                        with cols[idx]:
                            target_col = f'{target}_预计'
                            avg_target = optimization_df[target_col].mean()
                            target_mean = stats[target]['mean']
                            improvement = ((avg_target - target_mean) / target_mean) * 100
                            
                            st.markdown(f"""
                            <div class="stats-card-positive" style="height: 180px; display: flex; flex-direction: column; align-items: center; justify-content: center;">
                                <div class="stats-title">{target}均值</div>
                                <div class="stats-value">{avg_target:.2f}</div>
                                <div class="stats-change">
                                    <span>▲</span>
                                    <span>+{improvement:.1f}% vs 历史</span>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
    
    # 下半部分1/2：最优投放组合详情
    with st.container():
        st.subheader("🏆 最优投放组合详情")
        
        # 使用固定高度的容器
        with st.container(height=350):
            # 确保列顺序正确：投放顺序 > 全域投放量限制 > 目标值_预计 > 投放载体
            display_columns = ['投放顺序', '全域投放量限制']
            
            # 添加目标值预计列
            for target in selected_targets:
                display_columns.append(f'{target}_预计')
            
            # 添加投放载体列
            display_columns.extend(selected_features)
            
            # 确保所有列都存在
            display_df = optimization_df[[col for col in display_columns if col in optimization_df.columns]]
            
            # 格式化数值显示
            formatted_df = display_df.round(2)
            
            # 显示表格
            st.dataframe(
                formatted_df,
                use_container_width=True,
                column_config={
                    col: st.column_config.Column(
                        col,
                        help=f"{col}数据",
                    ) for col in formatted_df.columns
                }
            )

# 初始化数据
if 'current_data' not in st.session_state:
    st.session_state.current_data = load_default_data()

# 设置默认页面
if 'current_page' not in st.session_state:
    st.session_state.current_page = "历史投放效果分析"

# 侧边栏导航 - 使用按钮式导航
st.sidebar.markdown("## 📑 页面导航")

# 创建三个页面按钮 - 上下排列
page1_btn = st.sidebar.button("📊 历史投放效果分析", use_container_width=True, key="page1")
page2_btn = st.sidebar.button("🔮 未来投放效果模拟", use_container_width=True, key="page2")
page3_btn = st.sidebar.button("🎯 最佳投放组合推荐", use_container_width=True, key="page3")

# 处理按钮点击
if page1_btn:
    st.session_state.current_page = "历史投放效果分析"
if page2_btn:
    st.session_state.current_page = "未来投放效果模拟"
if page3_btn:
    st.session_state.current_page = "最佳投放组合推荐"

# 显示对应页面
if st.session_state.current_page == "历史投放效果分析":
    show_history_analysis()
elif st.session_state.current_page == "未来投放效果模拟":
    show_future_simulation()
else:
    show_optimization_recommendation()