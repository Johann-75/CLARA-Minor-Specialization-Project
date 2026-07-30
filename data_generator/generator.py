import os
import json
import uuid
import numpy as np
import pandas as pd
from datetime import datetime, date, timedelta
from config import RANDOM_SEED, SYNTHETIC_INSTANCE_COUNT, SYNTHETIC_DAYS_OF_METRICS

class SyntheticDataGenerator:
    """
    Generates a realistic synthetic cloud dataset simulating AWS, Azure, and GCP resources.
    Uses numpy.random.default_rng for reproducible randomness.
    """
    # Distribution ratios and profile definitions
    PROVIDER_RATIOS = [0.5, 0.3, 0.2]  # AWS, Azure, GCP
    OVERUTILIZED_RATIO = 0.15
    UNDERUTILIZED_RATIO = 0.20
    
    # Vulnerability rates
    EXPOSED_RATIO = 0.10
    UNENCRYPTED_RATIO = 0.05
    EXCESSIVE_IAM_RATIO = 0.15
    BRUTE_FORCE_RATIO = 0.05
    
    # Profile parameters (mean, std)
    PROFILE_CPU_MEM_PARAMS = {
        "overutilized": (85, 8),
        "underutilized": (4, 2),
        "normal": (45, 15)
    }
    
    # Noise events count
    NOISE_EVENTS_COUNT = 50

    def __init__(self):
        self.rng = np.random.default_rng(RANDOM_SEED)
        self.anomaly_manifest = []
        self.profiles = {}

    def generate_instances(self, count=300) -> pd.DataFrame:
        """
        Generates synthetic cloud instance metadata records.

        Parameters:
            count (int): The number of instances to generate. Defaults to 300.

        Returns:
            pd.DataFrame: A DataFrame with the columns:
                - instance_id (str): format "i-" + 12 random hex chars
                - cloud_provider (str): AWS (50%), Azure (30%), GCP (20%)
                - instance_type (str): t3.micro, t3.small, etc.
                - region (str): region name
                - cpu_cores (int): cores based on instance size
                - memory_gb (int): memory based on instance size
                - launch_date (date): date between 730 and 30 days ago
                - status (str): "running" (90%) or "stopped" (10%)
                - hourly_rate_usd (float): AWS-like price rate
        """
        providers = self.rng.choice(["AWS", "Azure", "GCP"], size=count, p=self.PROVIDER_RATIOS)
        
        types_list = ["t3.micro", "t3.small", "t3.medium", "m5.large", "m5.xlarge", "c5.large", "c5.xlarge", "r5.large"]
        regions_list = ["us-east-1", "us-west-2", "eu-west-1", "ap-southeast-1", "ap-south-1"]
        
        inst_types = self.rng.choice(types_list, size=count)
        regions = self.rng.choice(regions_list, size=count)
        
        cores_map = {
            "t3.micro": 2, "t3.small": 2, "t3.medium": 2, "m5.large": 2,
            "m5.xlarge": 4, "c5.large": 2, "c5.xlarge": 4, "r5.large": 2
        }
        mem_map = {
            "t3.micro": 1, "t3.small": 2, "t3.medium": 4, "m5.large": 8,
            "m5.xlarge": 16, "c5.large": 8, "c5.xlarge": 16, "r5.large": 8
        }
        rates_map = {
            "t3.micro": 0.0104, "t3.small": 0.0208, "t3.medium": 0.0416,
            "m5.large": 0.096, "m5.xlarge": 0.192, "c5.large": 0.085,
            "c5.xlarge": 0.17, "r5.large": 0.126
        }
        
        today = date.today()
        start_date = today - timedelta(days=730)
        offsets = self.rng.integers(0, 701, size=count)
        
        status_list = self.rng.choice(["running", "stopped"], size=count, p=[0.9, 0.1])
        
        records = []
        for i in range(count):
            hex_chars = "".join(self.rng.choice(list("0123456789abcdef"), size=12))
            inst_id = f"i-{hex_chars}"
            itype = inst_types[i]
            
            records.append({
                "instance_id": inst_id,
                "cloud_provider": str(providers[i]),
                "instance_type": str(itype),
                "region": str(regions[i]),
                "cpu_cores": int(cores_map[itype]),
                "memory_gb": int(mem_map[itype]),
                "launch_date": start_date + timedelta(days=int(offsets[i])),
                "status": str(status_list[i]),
                "hourly_rate_usd": float(rates_map[itype])
            })
            
        return pd.DataFrame(records)

    def _assign_profiles(self, instances_df):
        """
        Assigns utilization profiles (overutilized, underutilized, normal) to all instances.
        """
        inst_ids = instances_df["instance_id"].tolist()
        count = len(inst_ids)
        
        num_over = int(count * self.OVERUTILIZED_RATIO)
        num_under = int(count * self.UNDERUTILIZED_RATIO)
        num_normal = count - num_over - num_under
        
        profile_list = (
            ["overutilized"] * num_over + 
            ["underutilized"] * num_under + 
            ["normal"] * num_normal
        )
        self.rng.shuffle(profile_list)
        
        self.profiles = {inst_ids[i]: profile_list[i] for i in range(count)}

    def _prepare_anomalies(self, instances_df, days):
        """
        Pre-calculates exactly 15 anomaly events distributed across the time series.
        """
        if len(self.anomaly_manifest) > 0:
            return
            
        inst_ids = instances_df["instance_id"].tolist()
        anomaly_inst_ids = list(self.rng.choice(inst_ids, size=15, replace=False))
        
        end_date = date.today()
        start_date_base = end_date - timedelta(days=days - 1)
        
        # 3 CPU Spikes (Type 1)
        for i in range(3):
            inst_id = anomaly_inst_ids[i]
            offset = int(self.rng.integers(10, days - 10))
            start_dt = start_date_base + timedelta(days=offset)
            end_dt = start_dt + timedelta(days=1)
            self.anomaly_manifest.append({
                "instance_id": inst_id,
                "anomaly_type": "cpu_spike",
                "start_date": start_dt,
                "end_date": end_dt,
                "description": f"CPU spike anomaly: cpu_utilization_pct jumped to 95-100% on instance {inst_id}."
            })
            
        # 3 Memory Leaks (Type 2)
        for i in range(3, 6):
            inst_id = anomaly_inst_ids[i]
            offset = int(self.rng.integers(10, days - 10))
            start_dt = start_date_base + timedelta(days=offset)
            end_dt = start_dt + timedelta(days=4)
            self.anomaly_manifest.append({
                "instance_id": inst_id,
                "anomaly_type": "memory_leak",
                "start_date": start_dt,
                "end_date": end_dt,
                "description": f"Memory leak anomaly: memory_utilization_pct increased steadily by 5%/day for 5 days on instance {inst_id}."
            })
            
        # 3 Network Exfiltrations (Type 3)
        for i in range(6, 9):
            inst_id = anomaly_inst_ids[i]
            offset = int(self.rng.integers(10, days - 10))
            start_dt = start_date_base + timedelta(days=offset)
            self.anomaly_manifest.append({
                "instance_id": inst_id,
                "anomaly_type": "network_exfiltration",
                "start_date": start_dt,
                "end_date": start_dt,
                "description": f"Network exfiltration anomaly: outbound network traffic spiked to 20x normal on instance {inst_id}."
            })
            
        # 3 Brute Force Attacks (Type 4)
        for i in range(9, 12):
            inst_id = anomaly_inst_ids[i]
            offset = int(self.rng.integers(10, days - 10))
            start_dt = start_date_base + timedelta(days=offset)
            self.anomaly_manifest.append({
                "instance_id": inst_id,
                "anomaly_type": "brute_force",
                "start_date": start_dt,
                "end_date": start_dt,
                "description": f"Brute force anomaly: high failed logins and unauthorized access attempt event on instance {inst_id}."
            })
            
        # 3 Misconfigurations (Type 5)
        for i in range(12, 15):
            inst_id = anomaly_inst_ids[i]
            offset = int(self.rng.integers(10, days - 10))
            start_dt = start_date_base + timedelta(days=offset)
            self.anomaly_manifest.append({
                "instance_id": inst_id,
                "anomaly_type": "misconfiguration",
                "start_date": start_dt,
                "end_date": start_dt,
                "description": f"Misconfiguration anomaly: instance {inst_id} port exposure flipped to internet_exposed=True."
            })

    def _inject_anomalies(self, df_or_list, target_type):
        """
        Shared internal method to inject anomalies into metrics or events.
        """
        if target_type == "metrics":
            metrics_df = df_or_list
            for anom in self.anomaly_manifest:
                inst_id = anom["instance_id"]
                start_date = anom["start_date"]
                end_date = anom["end_date"]
                anom_type = anom["anomaly_type"]
                
                if anom_type == "cpu_spike":
                    mask = (metrics_df["instance_id"] == inst_id) & (metrics_df["date"] >= start_date) & (metrics_df["date"] <= end_date)
                    for idx in metrics_df[mask].index:
                        cpu_val = float(self.rng.uniform(95.0, 100.0))
                        metrics_df.at[idx, "cpu_utilization_pct"] = round(cpu_val, 4)
                        mem_val = np.clip(cpu_val + self.rng.uniform(-10.0, 10.0), 0.0, 100.0)
                        metrics_df.at[idx, "memory_utilization_pct"] = round(float(mem_val), 4)
                        
                elif anom_type == "memory_leak":
                    mask = (metrics_df["instance_id"] == inst_id) & (metrics_df["date"] >= start_date) & (metrics_df["date"] <= end_date)
                    leak_indices = metrics_df[mask].sort_values("date").index
                    for d, idx in enumerate(leak_indices):
                        mem_val = min(100.0, 75.0 + d * 5.0)
                        metrics_df.at[idx, "memory_utilization_pct"] = round(float(mem_val), 4)
                        
                elif anom_type == "network_exfiltration":
                    mask = (metrics_df["instance_id"] == inst_id) & (metrics_df["date"] == start_date)
                    for idx in metrics_df[mask].index:
                        current_out = metrics_df.at[idx, "network_out_mb"]
                        metrics_df.at[idx, "network_out_mb"] = round(float(max(current_out * 20.0, 10000.0)), 4)
                        
        elif target_type == "events":
            events_list = df_or_list
            for anom in self.anomaly_manifest:
                inst_id = anom["instance_id"]
                start_date = anom["start_date"]
                anom_type = anom["anomaly_type"]
                
                hr = int(self.rng.integers(0, 24))
                mn = int(self.rng.integers(0, 60))
                ts = datetime.combine(start_date, datetime.min.time()) + timedelta(hours=hr, minutes=mn)
                
                if anom_type == "cpu_spike":
                    events_list.append({
                        "event_id": str(uuid.uuid4()),
                        "instance_id": inst_id,
                        "event_type": "anomalous_traffic",
                        "severity": "high",
                        "description": f"Critical CPU spike detected on instance {inst_id}: utilization reached 95-100%.",
                        "timestamp": ts
                    })
                elif anom_type == "memory_leak":
                    events_list.append({
                        "event_id": str(uuid.uuid4()),
                        "instance_id": inst_id,
                        "event_type": "anomalous_traffic",
                        "severity": "medium",
                        "description": f"Potential memory leak detected on instance {inst_id}: steady increase over 5 days.",
                        "timestamp": ts
                    })
                elif anom_type == "network_exfiltration":
                    events_list.append({
                        "event_id": str(uuid.uuid4()),
                        "instance_id": inst_id,
                        "event_type": "anomalous_traffic",
                        "severity": "critical",
                        "description": f"Data exfiltration signature: outbound network traffic spiked 20x normal on instance {inst_id}.",
                        "timestamp": ts
                    })
                elif anom_type == "brute_force":
                    events_list.append({
                        "event_id": str(uuid.uuid4()),
                        "instance_id": inst_id,
                        "event_type": "unauthorized_access_attempt",
                        "severity": "critical",
                        "description": f"Brute force security alert: unauthorized access attempt following failed logins on instance {inst_id}.",
                        "timestamp": ts
                    })
                elif anom_type == "misconfiguration":
                    events_list.append({
                        "event_id": str(uuid.uuid4()),
                        "instance_id": inst_id,
                        "event_type": "port_opened",
                        "severity": "high",
                        "description": f"Security configuration change: instance {inst_id} port exposure changed to public internet.",
                        "timestamp": ts
                    })

    def generate_metrics(self, instances_df, days=90) -> pd.DataFrame:
        """
        Generates 90 days of metrics telemetry (27,000 rows for 300 instances).

        Parameters:
            instances_df (pd.DataFrame): Instances DataFrame.
            days (int): Number of days of historical telemetry. Defaults to 90.

        Returns:
            pd.DataFrame: Metrics DataFrame.
        """
        self._assign_profiles(instances_df)
        self._prepare_anomalies(instances_df, days)
        
        end_date = date.today()
        start_date = end_date - timedelta(days=days - 1)
        
        records = []
        for _, inst_row in instances_df.iterrows():
            inst_id = inst_row["instance_id"]
            profile = self.profiles[inst_id]
            
            if profile in self.PROFILE_CPU_MEM_PARAMS:
                mean, std = self.PROFILE_CPU_MEM_PARAMS[profile]
            else:
                mean, std = self.PROFILE_CPU_MEM_PARAMS["normal"]
                
            for d in range(days):
                cur_date = start_date + timedelta(days=d)
                
                # Business hours multiplier
                is_weekend = cur_date.weekday() >= 5
                mult = 0.70 if is_weekend else 1.20
                
                cpu = self.rng.normal(loc=mean * mult, scale=std)
                cpu = np.clip(cpu, 0.0, 100.0)
                
                mem = cpu + self.rng.uniform(-10.0, 10.0)
                mem = np.clip(mem, 0.0, 100.0)
                
                # Base metrics depending on utilization profile
                if profile == "overutilized":
                    net_in = self.rng.uniform(500.0, 2000.0)
                    net_out = self.rng.uniform(800.0, 3000.0)
                    read_iops = self.rng.integers(1000, 5000)
                    write_iops = self.rng.integers(500, 2000)
                elif profile == "underutilized":
                    net_in = self.rng.uniform(0.1, 5.0)
                    net_out = self.rng.uniform(0.1, 8.0)
                    read_iops = self.rng.integers(0, 10)
                    write_iops = self.rng.integers(0, 5)
                else:
                    net_in = self.rng.uniform(10.0, 200.0)
                    net_out = self.rng.uniform(15.0, 300.0)
                    read_iops = self.rng.integers(50, 500)
                    write_iops = self.rng.integers(20, 200)
                    
                records.append({
                    "instance_id": inst_id,
                    "date": cur_date,
                    "cpu_utilization_pct": round(float(cpu), 4),
                    "memory_utilization_pct": round(float(mem), 4),
                    "network_in_mb": round(float(net_in), 4),
                    "network_out_mb": round(float(net_out), 4),
                    "disk_read_iops": int(read_iops),
                    "disk_write_iops": int(write_iops)
                })
                
        metrics_df = pd.DataFrame(records)
        self._inject_anomalies(metrics_df, target_type="metrics")
        
        return metrics_df

    def generate_security_configs(self, instances_df) -> pd.DataFrame:
        """
        Generates configuration audits per instance with specified vulnerability rates.

        Parameters:
            instances_df (pd.DataFrame): Instances metadata DataFrame.

        Returns:
            pd.DataFrame: Security configurations DataFrame.
        """
        count = len(instances_df)
        inst_ids = instances_df["instance_id"].tolist()
        
        self._prepare_anomalies(instances_df, SYNTHETIC_DAYS_OF_METRICS)
        
        # Extract anomaly IDs
        brute_anom_ids = [a["instance_id"] for a in self.anomaly_manifest if a["anomaly_type"] == "brute_force"]
        misconfig_anom_ids = [a["instance_id"] for a in self.anomaly_manifest if a["anomaly_type"] == "misconfiguration"]
        
        num_exposed = int(count * self.EXPOSED_RATIO)
        num_no_encrypt = int(count * self.UNENCRYPTED_RATIO)
        num_exc_iam = int(count * self.EXCESSIVE_IAM_RATIO)
        num_brute = int(count * self.BRUTE_FORCE_RATIO)
        
        # 1. Exposed group (includes brute force & misconfig anomalies)
        forced_exposed = list(set(brute_anom_ids + misconfig_anom_ids))
        remaining_pool = [i for i in inst_ids if i not in forced_exposed]
        num_remaining_exposed = max(0, num_exposed - len(forced_exposed))
        chosen_exposed = list(self.rng.choice(remaining_pool, size=num_remaining_exposed, replace=False)) if num_remaining_exposed > 0 else []
        exposed_set = set(forced_exposed + chosen_exposed)
        
        # 2. Brute logins group (must include brute force anomalies and overlap with exposed group)
        forced_brute = list(set(brute_anom_ids))
        exposed_non_brute = [i for i in exposed_set if i not in forced_brute]
        num_remaining_brute = max(0, num_brute - len(forced_brute))
        chosen_brute = list(self.rng.choice(exposed_non_brute, size=num_remaining_brute, replace=False)) if num_remaining_brute > 0 and len(exposed_non_brute) >= num_remaining_brute else list(self.rng.choice(exposed_non_brute, size=len(exposed_non_brute), replace=False))
        brute_set = set(forced_brute + chosen_brute)
        
        # 3. Encryption disabled group (independent selection)
        no_encrypt_set = set(self.rng.choice(inst_ids, size=num_no_encrypt, replace=False))
        
        # 4. Excessive IAM permission group (independent selection)
        exc_iam_set = set(self.rng.choice(inst_ids, size=num_exc_iam, replace=False))
        
        records = []
        today = date.today()
        
        for inst_id in inst_ids:
            # Determine ports
            if inst_id in exposed_set:
                internet_exposed = True
                port_choice = self.rng.choice(["22,80,443", "3389,80,443", "22,3389,443", "22,3306,80,443"])
                open_ports = port_choice
            else:
                internet_exposed = False
                open_ports = self.rng.choice(["80", "443", "80,443", "80,443,8080"])
                
            encryption_enabled = inst_id not in no_encrypt_set
            
            if inst_id in exc_iam_set:
                iam_permission_level = "excessive"
            else:
                iam_permission_level = self.rng.choice(["least-privilege", "standard"], p=[0.6, 0.4])
                
            if inst_id in brute_set:
                failed_logins_7d = int(self.rng.integers(15, 41))
            else:
                failed_logins_7d = int(self.rng.integers(0, 4))
                
            days_ago = int(self.rng.integers(0, 181))
            last_patch_date = today - timedelta(days=days_ago)
            
            records.append({
                "instance_id": inst_id,
                "open_ports": open_ports,
                "internet_exposed": bool(internet_exposed),
                "encryption_enabled": bool(encryption_enabled),
                "iam_permission_level": iam_permission_level,
                "failed_logins_7d": int(failed_logins_7d),
                "last_patch_date": last_patch_date
            })
            
        return pd.DataFrame(records)

    def generate_cost_data(self, instances_df, metrics_df) -> pd.DataFrame:
        """
        Generates daily cost data linked directly to actual instance usage patterns.

        Parameters:
            instances_df (pd.DataFrame): Instances DataFrame.
            metrics_df (pd.DataFrame): Metrics DataFrame.

        Returns:
            pd.DataFrame: Cost data DataFrame.
        """
        # Merge metrics and instances to align rates
        df_merged = pd.merge(metrics_df, instances_df, on="instance_id")
        
        records = []
        for _, row in df_merged.iterrows():
            hourly = float(row["hourly_rate_usd"])
            running = row["status"] == "running"
            daily = hourly * 24.0 if running else 0.0
            
            cpu = float(row["cpu_utilization_pct"])
            
            # Compute waste score based on CPU utilization
            if cpu < 10.0:
                waste = 90.0 + float(self.rng.uniform(0.0, 10.0))
            elif cpu < 30.0:
                waste = 50.0 + (30.0 - cpu) * 1.5
            else:
                waste = max(0.0, 30.0 - cpu * 0.3)
                
            records.append({
                "instance_id": row["instance_id"],
                "date": row["date"],
                "hourly_cost_usd": round(hourly, 4),
                "daily_cost_usd": round(daily, 4),
                "utilization_pct": round(cpu, 4),
                "waste_score": round(waste, 4)
            })
            
        return pd.DataFrame(records)

    def generate_security_events(self, instances_df, days=90) -> pd.DataFrame:
        """
        Generates security events containing noise logs and 15 consistent anomalies.

        Parameters:
            instances_df (pd.DataFrame): Instances DataFrame.
            days (int): Number of days of security logs. Defaults to 90.

        Returns:
            pd.DataFrame: Security events DataFrame.
        """
        self._prepare_anomalies(instances_df, days)
        
        # 1. Create noise events
        inst_ids = instances_df["instance_id"].tolist()
        event_types = ["failed_login", "config_change", "port_opened", "anomalous_traffic"]
        severities = {
            "failed_login": "medium",
            "config_change": "low",
            "port_opened": "high",
            "anomalous_traffic": "medium"
        }
        descriptions = {
            "failed_login": "Audit alert: failed user login attempt.",
            "config_change": "Audit alert: minor service configuration adjustment.",
            "port_opened": "Audit alert: port settings updated.",
            "anomalous_traffic": "Audit alert: minor metric fluctuation warning."
        }
        
        records = []
        end_date = date.today()
        start_date_base = end_date - timedelta(days=days - 1)
        
        # Generate background noise logs
        for _ in range(self.NOISE_EVENTS_COUNT):
            inst_id = self.rng.choice(inst_ids)
            etype = self.rng.choice(event_types)
            sev = severities[etype]
            desc = descriptions[etype]
            
            offset = int(self.rng.integers(0, days))
            hr = int(self.rng.integers(0, 24))
            mn = int(self.rng.integers(0, 60))
            ts = datetime.combine(start_date_base + timedelta(days=offset), datetime.min.time()) + timedelta(hours=hr, minutes=mn)
            
            records.append({
                "event_id": str(uuid.uuid4()),
                "instance_id": inst_id,
                "event_type": etype,
                "severity": sev,
                "description": desc,
                "timestamp": ts
            })
            
        # 2. Inject the 15 anomalies
        self._inject_anomalies(records, target_type="events")
        
        return pd.DataFrame(records)

    def export_all(self, output_dir="data/synthetic/") -> dict:
        """
        Runs all generation methods in dependency order and exports outputs as CSV and JSON manifest.

        Parameters:
            output_dir (str): Directory where outputs are written. Defaults to "data/synthetic/".

        Returns:
            dict: Summary shapes of generated tables.
        """
        if not os.path.isabs(output_dir):
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            output_dir = os.path.abspath(os.path.join(project_root, output_dir))
        os.makedirs(output_dir, exist_ok=True)
        
        # Run methods in order
        instances_df = self.generate_instances(count=SYNTHETIC_INSTANCE_COUNT)
        metrics_df = self.generate_metrics(instances_df, days=SYNTHETIC_DAYS_OF_METRICS)
        configs_df = self.generate_security_configs(instances_df)
        cost_df = self.generate_cost_data(instances_df, metrics_df)
        events_df = self.generate_security_events(instances_df, days=SYNTHETIC_DAYS_OF_METRICS)
        
        # Export as CSV
        instances_df.to_csv(os.path.join(output_dir, "instances.csv"), index=False)
        metrics_df.to_csv(os.path.join(output_dir, "metrics.csv"), index=False)
        configs_df.to_csv(os.path.join(output_dir, "security_configs.csv"), index=False)
        cost_df.to_csv(os.path.join(output_dir, "cost_data.csv"), index=False)
        events_df.to_csv(os.path.join(output_dir, "security_events.csv"), index=False)
        
        # Serialize anomaly manifest as JSON
        manifest_serializable = []
        for item in self.anomaly_manifest:
            manifest_serializable.append({
                "instance_id": item["instance_id"],
                "anomaly_type": item["anomaly_type"],
                "start_date": str(item["start_date"]),
                "end_date": str(item["end_date"]),
                "description": item["description"]
            })
            
        with open(os.path.join(output_dir, "anomaly_manifest.json"), "w", encoding="utf-8") as f:
            json.dump(manifest_serializable, f, indent=2)
            
        return {
            "instances_shape": instances_df.shape,
            "metrics_shape": metrics_df.shape,
            "security_configs_shape": configs_df.shape,
            "cost_data_shape": cost_df.shape,
            "security_events_shape": events_df.shape
        }

if __name__ == "__main__":
    generator = SyntheticDataGenerator()
    shapes = generator.export_all()
    print(f"Generated {shapes['instances_shape'][0]} instances, {shapes['metrics_shape'][0]} metric rows, {len(generator.anomaly_manifest)} injected anomalies.")
    print("Files written to data/synthetic/")
