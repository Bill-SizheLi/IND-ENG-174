# ICU Resource Optimization and Simulation Project

### Authors
- **Kenny Chan** - kennychan@berkeley.edu   
- **Sizhe Li** - sizheli@berkeley.edu  
- **Siqi Yao** - siqiyao2024@berkeley.edu  
- **Yiyao Li** - yiyaoli@berkeley.edu

---

## 📖 Project Overview

This project addresses the challenge of optimizing ICU (Intensive Care Unit) resources, including patient beds and caregivers, using a simulation framework. The goal is to minimize patient waiting times and operational penalties under varying demand conditions.  

Key components:
1. **ICU Queue Simulation**: Models patient arrivals, prioritization strategies, and bed allocations.  
2. **Caregiver Workflow Simulation**: Simulates caregiver-patient interactions and service processes.  
3. **Optimization Strategies**: Implements exhaustive, heuristic, and Pareto front-based approaches to resource allocation.  

---

## 📂 File Structure

```
.
├── Part_1_IcuQueue
│   ├── ArrivalProcess.py
│   ├── DepartureProcessWithFIFO.py
│   ├── DepartureProcessWithDPQandReservedBeds.py
│   ├── DepartureProcessWithDPQ.py
│   ├── DepartureProcessWithPQ.py
│   ├── DepartureProcessWithPQandReservedBeds.py
│   ├── DepartureProcessWithReservedBeds.py
│   ├── figures/ (output plots)
│   ├── penalties/ (output penalty results)
│   └── __init__.py
│
├── Part_2_CareGiver
│   ├── CareGiverMain.py
│   ├── CareRequest.py
│   ├── figures/ (output plots)
│   ├── penalties/ (output penalty results)
│   └── __init__.py
│
├── Sensitivity_Analysis
│   ├── SensitivityAnalysis.py
│   └── figures/ (output Tornado charts)
│
├── Simulation_Optimization
│   ├── ExhaustiveSearch.py
│   ├── ParetoFrontSearch.py
│   ├── TabuSearch.py
│   └── __init__.py
│
├── README.md
├── requirements.txt
└── __pycache__
```

---

## ⚙️ Requirements

### Prerequisites
- Python 3.8+
- Required Python libraries:
  - `numpy`
  - `pandas`
  - `matplotlib`
  - `scipy`

### Install Dependencies
To install all dependencies, run:
```bash
pip install -r requirements.txt
```

---

## 🚀 Running the Code

### 1. **ICU Queue Simulation**
Simulates patient arrival, prioritization, and ICU bed allocations using different queuing strategies.

**Steps**:
1. Navigate to the `Part_1_IcuQueue` directory:
   ```bash
   cd Part_1_IcuQueue
   ```
2. Run the main script:
   ```bash
   python IcuQueueMain.py
   ```
**Customizing Strategies**:
- The queuing strategy is determined by the implementation in `Part_1_IcuQueue.DepartureProcessWithFIFO`.
- To generate results under different strategies, modify or replace the function `simulate_departure_process_FIFO`. For example:


To Implement Priority Queue: 
 ```bash
  from Part_1_IcuQueue.DepartureProcessWithPQ import simultaneously_return
```
- The script dynamically imports the strategy through `simultaneously_return`.

3. **Outputs**:
   - Plots: Saved in `Part_1_IcuQueue/figures/`.
   - Penalty Results: Saved in `Part_1_IcuQueue/penalties/`.

---

### 2. **Caregiver Simulation**
Simulates caregiver workflows and patient service delivery, including penalties for delays.

**Steps**:
1. Navigate to the `Part_2_CareGiver` directory:
   ```bash
   cd Part_2_CareGiver
   ```
2. Run the main script:
   ```bash
   python CareGiverMain.py
   ```
**Customizing Strategies**:
- The queuing strategy is determined by the implementation in `Part_1_IcuQueue.DepartureProcessWithFIFO`.
- To generate results under different strategies, modify or replace the function `simulate_departure_process_FIFO`. For example:


To Implement Priority Queue: 
 ```bash
  from Part_1_IcuQueue.DepartureProcessWithPQ import simultaneously_return
```
- The script dynamically imports the strategy through `simultaneously_return`.

3. **Outputs**:
   - Plots: Saved in `Part_2_CareGiver/figures/`.
   - Penalty Results: Saved in `Part_2_CareGiver/penalties/`.

---

### 3. **Sensitivity Analysis**
Analyzes the sensitivity of key parameters such as arrival rates, length of stays, and service times.

**Steps**:
1. Navigate to the `Sensitivity_Analysis` directory:
   ```bash
   cd Sensitivity_Analysis
   ```
2. Run the sensitivity analysis script:
   ```bash
   python SensitivityAnalysis.py
   ```
3. **Outputs**:
   - Tornado Chart: Visualizes the sensitivity indices (saved in the `figures/` folder).
   - Results: Sensitivity indices and baseline penalties are displayed in the console.

---

### 4. **Optimization Strategies**
Explores resource allocation optimization using exhaustive, Pareto front, and Tabu search methods.

**Steps**:
1. Navigate to the `Simulation_Optimization` directory:
   ```bash
   cd Simulation_Optimization
   ```
2. Run an optimization script:
   ```bash
   python ExhaustiveSearch.py
   python ParetoFrontSearch.py
   python TabuSearch.py
   ```
3. **Outputs**:
   - Optimized resource allocation results (printed in the console).

---

## 📊 Key Features

### Simulation Strategies
- **FIFO (First-In, First-Out)**: Patients are served in the order of arrival.
- **Priority Queue**: Patients with higher severity are prioritized.
- **Reserved Beds**: Dedicated beds for severe cases.
- **Dynamic Priority Queue (DPQ)**: Combines severity and waiting times for dynamic prioritization.

### Sensitivity Analysis
- **Parameters analyzed**:
  - Patient arrival rates
  - Length of patient stays
  - Request frequencies
  - Mean service times
- Results visualized using Tornado charts.

### Optimization Techniques
- **Exhaustive Search**: Tests all parameter combinations for global optimization.
- **Pareto Front Search**: Optimizes trade-offs between resource constraints (beds, caregivers).
- **Tabu Search**: Heuristic approach for fast, near-optimal solutions.

---

## 📄 Outputs

### Plots
- Aggregated waiting times by severity level.
- Tornado charts for sensitivity indices.

### Results
- Average penalties with confidence intervals.
- Optimized resource allocation strategies.

---

## 📚 References
- **MIMIC-IV Dataset**: [PhysioNet](https://physionet.org/content/mimic-iv-demo/2.2/)

---

## 📝 License
This project is licensed under the MIT License.
