from __future__ import annotations

import argparse
import os

from pyspark.sql import SparkSession
from pyspark.sql import functions as F


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="StreamFlow bounded Spark batch summary job.")
    parser.add_argument("--input", default=os.getenv("STREAMFLOW_RAW_OUTPUT", "data/raw/events"))
    parser.add_argument("--output", default=os.getenv("STREAMFLOW_SUMMARY_OUTPUT", "data/curated/daily_summary"))
    return parser


def main() -> None:
    args = build_parser().parse_args()
    spark = SparkSession.builder.appName("StreamFlowPhase1DailySummary").getOrCreate()
    spark.sparkContext.setLogLevel("WARN")

    print(f"INFO streamflow.summary.start input={args.input} output={args.output}")
    events = spark.read.parquet(args.input)
    summary = (
        events.withColumn("event_date", F.to_date("event_timestamp"))
        .groupBy("event_date", "event_type", "source")
        .agg(
            F.count("*").alias("event_count"),
            F.countDistinct("entity_id").alias("unique_entities"),
            F.min("event_timestamp").alias("first_event_ts"),
            F.max("event_timestamp").alias("last_event_ts"),
        )
        .orderBy("event_date", "event_type", "source")
    )
    summary.write.mode("overwrite").parquet(args.output)
    print(f"INFO streamflow.summary.write output={args.output}")
    print("INFO streamflow.summary.end status=success")


if __name__ == "__main__":
    main()

