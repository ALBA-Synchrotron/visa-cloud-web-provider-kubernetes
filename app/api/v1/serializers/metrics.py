import orjson


def metrics_to_dict(f) -> dict:
    return {
        "maxTotalRamSize": f.get("max_ram"),
        "maxTotalCores": f.get("max_cpus"),
        "maxTotalInstances": f.get("max_instances"),
        "totalRamUsed": f.get("in_use_ram"),
        "totalCoresUsed": f.get("in_use_cpus"),
        "totalInstancesUsed": f.get("instances_count"),
    }


def metrics_to_json(metrics: dict) -> bytes:
    return orjson.dumps(metrics_to_dict(metrics))
