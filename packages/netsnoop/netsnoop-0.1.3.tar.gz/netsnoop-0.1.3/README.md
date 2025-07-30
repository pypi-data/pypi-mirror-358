
# 🖥️ NetSnoop - Real-Time Linux System Monitor

NetSnoop is a real-time, low-level system activity visualizer for **Linux** systems. It detects process bursts, high CPU/memory usage, and memory usage — all displayed in a beautiful interactive dashboard built with Streamlit.

---

## 📦 Installation

```bash
pip install netsnoop
```

After installing the package, run the setup script to generate necessary files:

```bash
netsnoop-init
```

This will:
- Install required packages (if not already)
- Create `anomalies.csv` and `netsnoop_persistent.txt`
- Add sample data
- Create dashboard/monitor launcher scripts (`.sh` and `.bat`)

---

## 🛠️ How It Works

### 🔄 Architecture Flow:

```
acm_monitor.py → enhanced_anomaly_logger.py → dashboard.py
     ↓                      ↓                     ↓
  Detects              Stores to CSV         Displays data
 Anomalies                                   in Streamlit UI
```

---

## 🚀 Usage Guide

### Step 1: Start the Monitor
```bash
python3 -m netsnoop.acm_monitor
```

This will begin real-time detection of:
- High CPU/memory usage
- Process bursts
- System overloads

Anomalies will be saved to `anomalies.csv` and logs to `netsnoop_persistent.txt`.

---

### Step 2: Launch the Dashboard
In another terminal:

```bash
streamlit run netsnoop/dashboard.py
```

Then open your browser to: [http://localhost:8501](http://localhost:8501)

---

## 🧾 License

MIT License © 2025 Chitvi Joshi  
See the LICENSE file for details.

---

## 🧠 Made For:
- Linux users
- System monitoring and anomaly visualization
- Hackathons, research, devops dashboards

---

**Born to Track. Built with ❤️.**
