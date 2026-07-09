from __future__ import annotations

import argparse
import os

from pyspark.sql import SparkSession
from pyspark.sql import functions as F


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="StreamFlow Spark Structured Streaming ingest job.")
    parser.add_argument("--broker", default=os.getenv("STREAMFLOW_BROKER", "redpanda:9092"))
    parser.add_argument("--topic", default=os.getenv("STREAMFLOW_TOPIC", "streamflow.events"))
    parser.add_argument("--raw-output", default=os.getenv("STREAMFLOW_RAW_OUTPUT", "data/raw/events"))
    parser.add_argument("--rejects-output", default=os.getenv("STREAMFLOW_REJECTS_OUTPUT", "data/rejects/events"))
    parser.add_argument("--checkpoint", default=os.getenv("STREAMFLOW_CHECKPOINT", "data/checkpoints/events"))
    parser.add_argument("--trigger", choices=["availableNow", "once"], default="availableNow")
    return parser


def parse_events(stream_df):
    raw = stream_df.selectExpr("CAST(value AS STRING) AS raw_json", "timestamp AS kafka_ts")
    parsed = raw.select(
        "raw_json",
        "kafka_ts",
        F.get_json_object("raw_json", "$.event_id").alias("event_id"),
        F.get_json_object("raw_json", "$.event_type").alias("event_type"),
        F.get_json_object("raw_json", "$.event_ts").alias("event_ts"),
        F.to_timestamp(F.get_json_object("raw_json", "$.event_ts")).alias("event_timestamp"),
        F.get_json_object("raw_json", "$.source").alias("source"),
        F.get_json_object("raw_json", "$.entity_id").alias("entity_id"),
        F.get_json_object("raw_json", "$.payload").alias("payload_json"),
    )

    rejection_reason = F.concat_ws(
        ",",
        F.when(F.col("event_id").isNull(), F.lit("missing_event_id")),
        F.when(F.col("event_type").isNull(), F.lit("missing_event_type")),
        F.when(F.col("event_ts").isNull(), F.lit("missing_event_ts")),
        F.when(F.col("source").isNull(), F.lit("missing_source")),
        F.when(F.col("payload_json").isNull(), F.lit("missing_payload")),
        F.when(F.col("event_timestamp").isNull() & F.col("event_ts").isNotNull(), F.lit("invalid_event_ts")),
        F.when(~F.col("event_type").isin("page_view", "add_to_cart", "purchase", "video_play"), F.lit("unsupported_event_type")),
        F.when(~F.col("source").isin("simulator", "web", "mobile", "api"), F.lit("unsupported_source")),
    )
    return parsed.withColumn("rejection_reasons", rejection_reason).withColumn(
        "is_valid",
        F.col("rejection_reasons") == "",
    )


def write_batch(batch_df, batch_id: int, raw_output: str, rejects_output: str) -> None:
    valid = batch_df.filter(F.col("is_valid")).drop("is_valid", "rejection_reasons")
    rejected = batch_df.filter(~F.col("is_valid")).drop("is_valid")

    valid_count = valid.count()
    rejected_count = rejected.count()
    print(f"INFO streamflow.ingest.batch batch_id={batch_id} valid={valid_count} rejected={rejected_count}")

    if valid_count:
        valid.write.mode("append").parquet(raw_output)
    if rejected_count:
        rejected.write.mode("append").parquet(rejects_output)


def main() -> None:
    args = build_parser().parse_args()
    spark = SparkSession.builder.appName("StreamFlowPhase1StreamingIngest").getOrCreate()
    spark.sparkContext.setLogLevel("WARN")

    print(f"INFO streamflow.ingest.start topic={args.topic} broker={args.broker} checkpoint={args.checkpoint}")
    kafka_stream = (
        spark.readStream.format("kafka")
        .option("kafka.bootstrap.servers", args.broker)
        .option("subscribe", args.topic)
        .option("startingOffsets", "earliest")
        .load()
    )
    parsed = parse_events(kafka_stream)
    writer = (
        parsed.writeStream.option("checkpointLocation", args.checkpoint)
        .foreachBatch(lambda batch_df, batch_id: write_batch(batch_df, batch_id, args.raw_output, args.rejects_output))
    )
    if args.trigger == "once":
        query = writer.trigger(once=True).start()
    else:
        query = writer.trigger(availableNow=True).start()
    query.awaitTermination()
    print("INFO streamflow.ingest.end status=success")


if __name__ == "__main__":
    main()

