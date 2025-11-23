"""Test worker registry."""
import sys
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.worker_registry import (
    worker_registry,
    WorkerCategory,
    WorkerCapability,
    get_worker,
    list_workers
)


def test_registry_initialized():
    """Test that registry is initialized with all workers."""
    assert worker_registry.get_worker_count() == 17
    print(f"✅ Registry has {worker_registry.get_worker_count()} workers")


def test_get_worker_by_id():
    """Test getting worker by ID."""
    worker = get_worker("web_search_worker")
    assert worker is not None
    assert worker.name == "Web Search Worker"
    assert worker.category == WorkerCategory.RESEARCH
    print(f"✅ Retrieved worker: {worker.name}")


def test_get_workers_by_category():
    """Test getting workers by category."""
    research_workers = worker_registry.get_workers_by_category(WorkerCategory.RESEARCH)
    assert len(research_workers) == 5
    print(f"✅ Found {len(research_workers)} research workers")
    
    analysis_workers = worker_registry.get_workers_by_category(WorkerCategory.ANALYSIS)
    assert len(analysis_workers) == 4
    print(f"✅ Found {len(analysis_workers)} analysis workers")
    
    writing_workers = worker_registry.get_workers_by_category(WorkerCategory.WRITING)
    assert len(writing_workers) == 4
    print(f"✅ Found {len(writing_workers)} writing workers")
    
    quality_workers = worker_registry.get_workers_by_category(WorkerCategory.QUALITY)
    assert len(quality_workers) == 4
    print(f"✅ Found {len(quality_workers)} quality workers")


def test_get_workers_by_capability():
    """Test getting workers by capability."""
    web_search_workers = worker_registry.get_workers_by_capability(WorkerCapability.WEB_SEARCH)
    assert len(web_search_workers) >= 1
    print(f"✅ Found {len(web_search_workers)} workers with web search capability")


def test_parallel_workers():
    """Test getting parallel-capable workers."""
    parallel_workers = worker_registry.get_parallel_workers()
    assert len(parallel_workers) > 0
    print(f"✅ Found {len(parallel_workers)} parallel-capable workers")


def test_cost_estimation():
    """Test cost estimation."""
    worker_ids = ["web_search_worker", "article_writer_worker", "fact_checker_worker"]
    total_cost = worker_registry.estimate_total_cost(worker_ids)
    assert total_cost > 0
    print(f"✅ Estimated cost for 3 workers: ${total_cost:.2f}")


def test_time_estimation():
    """Test time estimation."""
    worker_ids = ["web_search_worker", "article_writer_worker"]
    
    # Sequential
    sequential_time = worker_registry.estimate_total_time(worker_ids, parallel=False)
    print(f"✅ Sequential time: {sequential_time} seconds")
    
    # Parallel
    parallel_time = worker_registry.estimate_total_time(worker_ids, parallel=True)
    print(f"✅ Parallel time: {parallel_time} seconds")


def test_list_all_workers():
    """Test listing all workers."""
    all_workers = list_workers()
    assert len(all_workers) == 17
    
    print("\n📋 All Registered Workers:")
    print("=" * 70)
    
    for category in WorkerCategory:
        workers_in_category = worker_registry.get_workers_by_category(category)
        print(f"\n{category.value.upper()} ({len(workers_in_category)} workers):")
        for worker in workers_in_category:
            print(f"  • {worker.name} ({worker.id})")
            print(f"    └─ {worker.description}")
    
    print("\n✅ All workers listed")


if __name__ == "__main__":
    test_registry_initialized()
    test_get_worker_by_id()
    test_get_workers_by_category()
    test_get_workers_by_capability()
    test_parallel_workers()
    test_cost_estimation()
    test_time_estimation()
    test_list_all_workers()
    print("\n✅ All worker registry tests passed!")