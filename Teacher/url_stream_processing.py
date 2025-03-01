# Teacher/url_stream_processing.py
from pyflink.table import StreamTableEnvironment, EnvironmentSettings
from pyflink.table.expressions import col
import re

# 创建 Flink 表环境
settings = EnvironmentSettings.new_instance().in_streaming_mode().use_blink_planner().build()
table_env = StreamTableEnvironment.create(settings)

# 配置 HDFS 连接器读取数据
hdfs_path = 'hdfs://localhost:9000/user/hdfs/pending_urls.txt'
table_env.execute_sql(f"""
    CREATE TABLE source_table (
        url STRING
    ) WITH (
        'connector' = 'filesystem',
        'path' = '{hdfs_path}',
        'format' = 'csv'
    )
""")

# 从 HDFS 读取数据
source_table = table_env.from_path("source_table")

# 过滤无效的 URL
def is_valid_url(url):
    pattern = re.compile(r'^https?://\S+$')
    return pattern.match(url) is not None

valid_url_table = source_table.filter(col("url").is_not_null() & (is_valid_url(col("url"))))

# 进行一些处理，比如去重
dedup_table = valid_url_table.distinct()

# 配置 HDFS 连接器写回数据
output_hdfs_path = 'hdfs://localhost:9000/user/hdfs/processed_urls.txt'
table_env.execute_sql(f"""
    CREATE TABLE sink_table (
        url STRING
    ) WITH (
        'connector' = 'filesystem',
        'path' = '{output_hdfs_path}',
        'format' = 'csv'
    )
""")

# 将处理后的数据写回到 HDFS
dedup_table.execute_insert("sink_table")