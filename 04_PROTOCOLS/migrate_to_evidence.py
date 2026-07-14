#!/usr/bin/env python3
"""
Migrate Performance Data to Evidence - 将现有推荐数据转换为 Evidence

Usage:
    python migrate_to_evidence.py --run

This script reads performance_db.json and converts each record to Evidence format,
storing them in 02_MEMORY/evidence/ directory.
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

# Add paths
sys.path.insert(0, str(Path(__file__).parent.parent / "05_TOOLS" / "advisor"))

from law_discovery import Observation, Evidence, EvidenceStore, LawDiscoveryEngine


def load_performance_db() -> Dict[str, Any]:
    """Load existing performance database"""
    db_path = Path(__file__).parent.parent / "05_TOOLS" / "mine_output" / "advisor" / "performance_db.json"
    if not db_path.exists():
        return {}
    
    return json.loads(db_path.read_text(encoding='utf-8'))


def load_trace_file(date_str: str) -> Dict[str, Any]:
    """Load trace file for a specific date"""
    trace_path = Path(__file__).parent.parent / "05_TOOLS" / "mine_output" / "advisor" / f"advisor_{date_str}_trace.json"
    if not trace_path.exists():
        return {}
    
    return json.loads(trace_path.read_text(encoding='utf-8'))


def convert_record_to_observation(key: str, record: Dict, trace_data: Dict) -> Observation:
    """Convert a performance record to Observation"""
    date_str = record.get('recommend_date', '')
    code = record.get('code', '')
    name = record.get('name', '')
    
    # Get trace data for this ticker
    layer1_reasons = []
    layer1_reject_flags = []
    layer2_reasons = []
    layer3_reasons = []
    tech_signals = []
    
    if trace_data:
        for candidate in trace_data.get('cco2_selection_trace', []):
            if candidate.get('symbol') == code:
                layer1_reasons = candidate.get('layer1_reasons', [])
                layer1_reject_flags = candidate.get('layer1_reject_flags', [])
                layer2_reasons = candidate.get('layer2_reasons', [])
                layer3_reasons = candidate.get('layer3_reasons', [])
                break
    
    observation = Observation(
        observation_id=key,
        timestamp=f"{date_str}T09:30:00",
        recommendation_id=f"sa_{date_str}_{code}",
        ticker=code,
        ticker_name=name,
        recommend_price=record.get('recommend_price', 0),
        close_price=record.get('close_price'),
        max_price=None,
        min_price=None,
        volume=record.get('volume'),
        return_t1=record.get('return_t1'),
        return_t3=record.get('return_t3'),
        return_t5=record.get('return_t5'),
        return_t10=record.get('return_t10'),
        return_t20=record.get('return_t20'),
        industry=None,
        market_sentiment=None,
        turnover_rate=record.get('turnover_rate'),
        pe=record.get('pe'),
        total_capital=record.get('total_capital'),
        layer1_reasons=layer1_reasons,
        layer1_reject_flags=layer1_reject_flags,
        layer2_reasons=layer2_reasons,
        layer3_reasons=layer3_reasons,
        tech_signals=tech_signals,
        status=record.get('status', 'pending')
    )
    
    return observation


def migrate():
    """Main migration function"""
    print("=" * 60)
    print("Migrating Performance Data to Evidence")
    print("=" * 60)
    
    # Load performance database
    perf_db = load_performance_db()
    print(f"Loaded {len(perf_db)} records from performance_db.json")
    
    if not perf_db:
        print("No records to migrate")
        return
    
    # Initialize engine
    engine = LawDiscoveryEngine()
    
    # Track statistics
    stats = {
        "total_records": len(perf_db),
        "evidence_created": 0,
        "errors": 0
    }
    
    # Process each record
    for key, record in perf_db.items():
        try:
            date_str = record.get('recommend_date', '')
            
            # Load trace data for this date
            trace_data = load_trace_file(date_str)
            
            # Convert to observation
            observation = convert_record_to_observation(key, record, trace_data)
            
            # Convert to evidence
            evidences = engine.convert_observation_to_evidence(observation)
            
            stats["evidence_created"] += len(evidences)
            
            if len(evidences) > 0:
                print(f"  ✓ {key}: {len(evidences)} evidence created")
        
        except Exception as e:
            print(f"  ✗ {key}: {e}")
            stats["errors"] += 1
    
    # Print summary
    print("\n" + "=" * 60)
    print("Migration Summary")
    print("=" * 60)
    print(f"Total records: {stats['total_records']}")
    print(f"Evidence created: {stats['evidence_created']}")
    print(f"Errors: {stats['errors']}")
    print(f"Evidence stored in: {engine.evidence_store.evidence_dir}")
    print("=" * 60)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Migrate Performance Data to Evidence")
    parser.add_argument("--run", action="store_true", help="Run migration")
    parser.add_argument("--status", action="store_true", help="Show current status")
    args = parser.parse_args()
    
    if args.run:
        migrate()
    
    if args.status:
        engine = LawDiscoveryEngine()
        evidence = engine.evidence_store.get_all_evidence(limit=1000)
        print(f"Current Evidence Count: {len(evidence)}")
        
        # Show sample
        if evidence:
            print("\nSample Evidence:")
            for e in evidence[:3]:
                print(f"  {e.evidence_id}: {e.ticker} {e.outcome_period} {e.evidence_type} ({e.outcome_return:+.2f}%)")
    
    if not args.run and not args.status:
        parser.print_help()


if __name__ == "__main__":
    main()