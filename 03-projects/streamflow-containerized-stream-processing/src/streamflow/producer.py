from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
import json
import logging
from pathlib import Path
import random
import sys
from typing import Any

from .schemas import ALLOWED_EVENT_TYPES, ALLOWED_SOURCES, StreamFlowConfig


LOGGER = logging.getLogger("streamflow.producer")


def generate_events(count: int, *, seed: int = 7, invalid_rate: float = 0.1) -> list[dict[str, Any]]:
    rng = random.Random(seed)
    start = datetime(2026, 6, 30, 14, 30, tzinfo=timezone.utc)
    events: list[dict[str, Any]] = []

    for index in range(count):
        event_type = rng.choice(ALLOWED_EVENT_TYPES)
        amount = round(rng.uniform(5, 250), 2)
        event = {
            "event_id": f"evt_{index + 1:05d}",
            "event_type": event_type,
            "event_ts": (start + timedelta(seconds=index * 17)).isoformat().replace("+00:00", "Z"),
            "source": rng.choice(ALLOWED_SOURCES),
            "entity_id": f"user_{rng.randint(1, 25):03d}",
            "payload": {
                "amount": amount if event_type in {"purchase", "add_to_cart"} else 0,
                "currency": "USD",
                "page": rng.choice(["home", "product", "checkout", "watch"]),
            },
        }
        if rng.random() < invalid_rate:
            event = inject_invalid_shape(event, rng)
        events.append(event)

    return events


def inject_invalid_shape(event: dict[str, Any], rng: random.Random) -> dict[str, Any]:
    mutated = dict(event)
    mutation = rng.choice(["missing_event_id", "bad_type", "bad_timestamp", "bad_source", "bad_payload"])
    if mutation == "missing_event_id":
        mutated.pop("event_id", None)
    elif mutation == "bad_type":
        mutated["event_type"] = "unknown_event"
    elif mutation == "bad_timestamp":
        mutated["event_ts"] = "not-a-timestamp"
    elif mutation == "bad_source":
        mutated["source"] = "shadow-system"
    elif mutation == "bad_payload":
        mutated["payload"] = "not-an-object"
    return mutated


def write_jsonl(events: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for event in events:
            handle.write(json.dumps(event, sort_keys=True) + "\n")


def publish_events(events: list[dict[str, Any]], config: StreamFlowConfig) -> None:
    try:
        from kafka import KafkaProducer
    except ImportError as exc:
        raise RuntimeError("Install kafka-python or use --dry-run for local generation.") from exc

    producer = KafkaProducer(
        bootstrap_servers=config.broker,
        value_serializer=lambda value: json.dumps(value).encode("utf-8"),
    )
    LOGGER.info("streamflow.producer.start topic=%s broker=%s", config.topic, config.broker)
    for event in events:
        producer.send(config.topic, event)
    producer.flush()
    producer.close()
    LOGGER.info("streamflow.producer.end events=%s", len(events))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate and publish StreamFlow synthetic events.")
    parser.add_argument("--count", type=int, default=100)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--invalid-rate", type=float, default=0.1)
    parser.add_argument("--broker", default="redpanda:9092")
    parser.add_argument("--topic", default="streamflow.events")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--out", type=Path, default=Path("data/sample/events.jsonl"))
    return parser


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    args = build_parser().parse_args(argv)
    events = generate_events(args.count, seed=args.seed, invalid_rate=args.invalid_rate)

    if args.dry_run:
        write_jsonl(events, args.out)
        print(f"Wrote {len(events)} events to {args.out}")
        return 0

    publish_events(events, StreamFlowConfig(topic=args.topic, broker=args.broker))
    return 0


if __name__ == "__main__":
    sys.exit(main())

